#!/usr/bin/env python3
"""Render two DOCX files and retain visual diffs only for changed pages."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageChops


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"


def find_render_script(explicit: Path | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(explicit)
    if os.environ.get("CODEX_RENDER_DOCX"):
        candidates.append(Path(os.environ["CODEX_RENDER_DOCX"]))
    candidates.append(Path(__file__).resolve().parents[1] / "render_docx.py")
    cache_root = Path.home() / ".codex" / "plugins" / "cache"
    if cache_root.is_dir():
        candidates.extend(cache_root.glob("**/documents/*/skills/documents/render_docx.py"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        "render_docx.py was not found. Pass --render-script or set CODEX_RENDER_DOCX."
    )


def reset_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def fallback_render(docx: Path, output_dir: Path, env: dict[str, str]) -> str:
    soffice = shutil.which("soffice", path=env.get("PATH"))
    if not soffice:
        raise FileNotFoundError("LibreOffice soffice was not found for fallback rendering.")
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for fallback rendering.") from exc
    with tempfile.TemporaryDirectory(prefix="docx-diff-profile-") as profile_dir, tempfile.TemporaryDirectory(
        prefix="docx-diff-pdf-"
    ) as pdf_dir:
        profile_uri = Path(profile_dir).resolve().as_uri()
        command = [
            soffice,
            f"-env:UserInstallation={profile_uri}",
            "--invisible",
            "--headless",
            "--norestore",
            "--convert-to",
            "pdf",
            "--outdir",
            pdf_dir,
            str(docx),
        ]
        completed = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
        pdf_path = Path(pdf_dir) / f"{docx.stem}.pdf"
        if completed.returncode != 0 or not pdf_path.is_file():
            details = (completed.stdout + "\n" + completed.stderr).strip()
            raise RuntimeError(f"LibreOffice fallback rendering failed: {details or completed.returncode}")
        pdf = fitz.open(pdf_path)
        try:
            matrix = fitz.Matrix(150 / 72, 150 / 72)
            for page_number, page in enumerate(pdf, start=1):
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                pixmap.save(output_dir / f"page-{page_number}.png")
        finally:
            pdf.close()
    return "libreoffice+pymupdf"


def run_render(render_script: Path, docx: Path, output_dir: Path) -> str:
    reset_directory(output_dir)
    env = os.environ.copy()
    native_dirs = [
        Path(sys.executable).resolve().parents[1] / "bin",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "LibreOffice" / "program",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "LibreOffice" / "program",
    ]
    existing = env.get("PATH", "").split(os.pathsep)
    env["PATH"] = os.pathsep.join(
        [str(path) for path in native_dirs if path.is_dir()] + [item for item in existing if item]
    )
    completed = subprocess.run(
        [sys.executable, str(render_script), str(docx), "--output_dir", str(output_dir)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0 and page_map(output_dir):
        return "canonical"
    reset_directory(output_dir)
    return fallback_render(docx, output_dir, env)


def page_map(directory: Path) -> dict[int, Path]:
    pages: dict[int, Path] = {}
    for path in directory.glob("page-*.png"):
        match = path.stem.split("-")[-1]
        if match.isdigit():
            pages[int(match)] = path
    return pages


def diff_images(before: Path, after: Path, output: Path) -> tuple[bool, float]:
    image_a = Image.open(before).convert("RGB")
    image_b = Image.open(after).convert("RGB")
    if image_a.size != image_b.size:
        width = max(image_a.width, image_b.width)
        height = max(image_a.height, image_b.height)
        canvas_a = Image.new("RGB", (width, height), "white")
        canvas_b = Image.new("RGB", (width, height), "white")
        canvas_a.paste(image_a, (0, 0))
        canvas_b.paste(image_b, (0, 0))
        image_a, image_b = canvas_a, canvas_b
    difference = ImageChops.difference(image_a, image_b)
    bbox = difference.getbbox()
    if bbox is None:
        return False, 0.0
    grayscale = difference.convert("L")
    changed_pixels = sum(1 for value in grayscale.getdata() if value)
    ratio = changed_pixels / (image_a.width * image_a.height)
    output.parent.mkdir(parents=True, exist_ok=True)
    difference.save(output)
    return True, ratio


def extract_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    paragraphs = []
    for paragraph in root.iter(f"{W}p"):
        text = "".join(node.text or "" for node in paragraph.iter(f"{W}t"))
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs) + "\n"


def compare(before: Path, after: Path, outdir: Path, render_script: Path) -> dict[str, object]:
    before_render = outdir / "approved_render"
    after_render = outdir / "candidate_render"
    diff_dir = outdir / "changed_pages"
    before_backend = run_render(render_script, before, before_render)
    after_backend = run_render(render_script, after, after_render)
    reset_directory(diff_dir)

    pages_before = page_map(before_render)
    pages_after = page_map(after_render)
    changed_pages: list[int] = []
    changed_ratios: dict[str, float] = {}
    for page_number in sorted(set(pages_before) | set(pages_after)):
        path_before = pages_before.get(page_number)
        path_after = pages_after.get(page_number)
        if path_before is None or path_after is None:
            changed_pages.append(page_number)
            changed_ratios[str(page_number)] = 1.0
            continue
        changed, ratio = diff_images(
            path_before,
            path_after,
            diff_dir / f"diff-page-{page_number:03d}.png",
        )
        if changed:
            changed_pages.append(page_number)
            changed_ratios[str(page_number)] = round(ratio, 8)

    text_before = extract_text(before)
    text_after = extract_text(after)
    text_diff = "".join(
        difflib.unified_diff(
            text_before.splitlines(keepends=True),
            text_after.splitlines(keepends=True),
            fromfile="approved",
            tofile="candidate",
        )
    )
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "text_diff.txt").write_text(text_diff, encoding="utf-8")
    summary: dict[str, object] = {
        "approved_docx": str(before.resolve()),
        "candidate_docx": str(after.resolve()),
        "pages_approved": len(pages_before),
        "pages_candidate": len(pages_after),
        "changed_pages": changed_pages,
        "changed_page_count": len(changed_pages),
        "changed_pixel_ratios": changed_ratios,
        "text_changed": text_before != text_after,
        "render_script": str(render_script),
        "render_backends": {"approved": before_backend, "candidate": after_backend},
    }
    (outdir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render and diff an approved and candidate DOCX.")
    parser.add_argument("approved", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--render-script", type=Path)
    parser.add_argument("--render_py", dest="render_script", type=Path, help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    try:
        render_script = find_render_script(args.render_script)
        summary = compare(
            args.approved.resolve(),
            args.candidate.resolve(),
            args.outdir.resolve(),
            render_script,
        )
    except (FileNotFoundError, OSError, RuntimeError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Import a DOCX manuscript without changing it and split validated chapters."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


DOCUMENT_TYPES = ("teaching-notes", "book", "textbook")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")


@dataclass
class Block:
    kind: str
    text: str
    style: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, dest="input_path")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--document-type", required=True, choices=DOCUMENT_TYPES)
    parser.add_argument("--rebuild", action="store_true")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_profile_type(path: Path) -> str:
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        match = re.match(r"\s*-\s*Document type\s*:\s*([^|\s]+)", line, re.I)
        if match:
            return match.group(1).strip()
    return ""


def load_styles(archive: zipfile.ZipFile) -> dict[str, str]:
    try:
        root = ET.fromstring(archive.read("word/styles.xml"))
    except KeyError:
        return {}
    styles: dict[str, str] = {}
    for style in root.findall(f".//{W}style"):
        style_id = style.get(f"{W}styleId", "")
        name = style.find(f"{W}name")
        if style_id and name is not None:
            styles[style_id] = name.get(f"{W}val", style_id)
    return styles


def node_text(node: ET.Element) -> str:
    chunks: list[str] = []
    for item in node.iter():
        if item.tag == f"{W}t" and item.text:
            chunks.append(item.text)
        elif item.tag in {f"{W}tab", f"{W}br", f"{W}cr"}:
            chunks.append(" ")
    return re.sub(r"\s+", " ", "".join(chunks)).strip()


def table_markdown(table: ET.Element) -> str:
    rows: list[list[str]] = []
    for tr in table.findall(f"{W}tr"):
        cells = [node_text(tc).replace("|", "\\|") for tc in tr.findall(f"{W}tc")]
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    lines = ["| " + " | ".join(rows[0]) + " |"]
    lines.append("| " + " | ".join(["---"] * width) + " |")
    lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return "\n".join(lines)


def extract_blocks(path: Path) -> list[Block]:
    with zipfile.ZipFile(path) as archive:
        styles = load_styles(archive)
        root = ET.fromstring(archive.read("word/document.xml"))
    body = root.find(f"{W}body")
    if body is None:
        return []
    blocks: list[Block] = []
    for child in body:
        if child.tag == f"{W}p":
            text = node_text(child)
            if not text:
                continue
            style_id = ""
            p_style = child.find(f"{W}pPr/{W}pStyle")
            if p_style is not None:
                style_id = p_style.get(f"{W}val", "")
            blocks.append(Block("paragraph", text, styles.get(style_id, style_id)))
        elif child.tag == f"{W}tbl":
            markdown = table_markdown(child)
            if markdown:
                blocks.append(Block("table", markdown))
    return blocks


def heading_level(style: str) -> int | None:
    normalized = re.sub(r"\s+", "", style).casefold()
    match = re.search(r"(?:heading|หัวเรื่อง)([1-6])", normalized)
    return int(match.group(1)) if match else None


def chapter_number(block: Block) -> int | None:
    if block.kind != "paragraph":
        return None
    text = block.text.translate(THAI_DIGITS)
    match = re.match(r"^บทที่\s*(\d+)\b", text, re.I)
    if not match:
        match = re.match(r"^chapter\s+(\d+)\b", text, re.I)
    if not match and heading_level(block.style) == 1:
        match = re.match(r"^(\d+)[.)]?\s+\S", text)
    return int(match.group(1)) if match else None


def block_markdown(block: Block) -> str:
    if block.kind == "table":
        return block.text
    level = heading_level(block.style)
    if level:
        return f"{'#' * level} {block.text}"
    return block.text


def approval_text() -> str:
    return """# Approval Record

- Task: import-manuscript
- Artifact: source/import-report.md
- Status: PENDING
- Approved by:
- Approval message:
- Approved date:
- Notes:
"""


def main() -> int:
    args = parse_args()
    source_path = args.input_path.resolve()
    root = args.project_root.resolve()
    if not source_path.is_file() or source_path.suffix.lower() != ".docx":
        print(f"Input must be an existing DOCX: {source_path}", file=sys.stderr)
        return 2
    profile_type = read_profile_type(root / "project" / "manuscript-profile.md")
    if profile_type != args.document_type:
        print(
            f"Profile type {profile_type or 'EMPTY'} does not match {args.document_type}.",
            file=sys.stderr,
        )
        return 2

    source_dir = root / "source"
    original = source_dir / "original-manuscript.docx"
    report_path = source_dir / "import-report.md"
    approval_path = source_dir / "approval.md"
    if not args.rebuild and (original.exists() or report_path.exists()):
        print("Import artifacts already exist; use --rebuild only after explicit approval.", file=sys.stderr)
        return 2

    blocks = extract_blocks(source_path)
    starts = [(index, chapter_number(block)) for index, block in enumerate(blocks)]
    starts = [(index, number) for index, number in starts if number is not None]
    numbers = [number for _, number in starts]
    blockers: list[str] = []
    if not blocks:
        blockers.append("No readable paragraphs or tables were extracted from the DOCX.")
    if not starts:
        blockers.append("No numbered chapter headings were detected; chapter structure was not guessed.")
    if len(numbers) != len(set(numbers)):
        blockers.append("Duplicate chapter numbers were detected; chapter files were not created.")
    if numbers and numbers != list(range(1, len(numbers) + 1)):
        blockers.append(
            f"Chapter numbers are not sequential from 1: {', '.join(map(str, numbers))}."
        )

    source_hash = sha256(source_path)
    source_dir.mkdir(parents=True, exist_ok=True)
    if original.exists():
        if sha256(original) != source_hash:
            print(
                "The preserved original differs from the requested input; use a new project ID instead of replacing it.",
                file=sys.stderr,
            )
            return 2
    else:
        shutil.copyfile(source_path, original)
    original_hash = sha256(original)
    if source_hash != original_hash:
        print("Copied manuscript checksum mismatch.", file=sys.stderr)
        return 3

    created: list[str] = []
    if not blockers:
        chapter_paths = [
            root / "chapters" / f"chapter-{number:02d}" / "draft.md"
            for _, number in starts
        ]
        if not args.rebuild:
            existing = [str(path) for path in chapter_paths if path.exists()]
            if existing:
                blockers.append(
                    "Chapter artifacts already exist: " + ", ".join(existing)
                )

    if not blockers:
        for position, (start, number) in enumerate(starts):
            end = starts[position + 1][0] if position + 1 < len(starts) else len(blocks)
            chapter_path = root / "chapters" / f"chapter-{number:02d}" / "draft.md"
            chapter_path.parent.mkdir(parents=True, exist_ok=True)
            markdown = "\n\n".join(block_markdown(block) for block in blocks[start:end]).strip() + "\n"
            chapter_path.write_text(markdown, encoding="utf-8")
            created.append(str(chapter_path.relative_to(root)))

    status = "BLOCKED" if blockers else "READY_FOR_REVIEW"
    report = [
        "# Manuscript Import Report",
        "",
        f"- Input: `{source_path}`",
        f"- Preserved original: `source/original-manuscript.docx`",
        f"- SHA-256: `{original_hash}`",
        f"- Document type: {args.document_type}",
        f"- Import status: {status}",
        f"- Detected chapters: {len(numbers)}",
        "- Extraction note: DOCX tables were converted to Markdown for review; the original DOCX remains authoritative for layout.",
        "",
        "## Chapter Artifacts",
        "",
    ]
    report.extend(f"- `{path}`" for path in created)
    if not created:
        report.append("- None")
    report.extend(["", "## Blockers", ""])
    report.extend(f"- {item}" for item in blockers)
    if not blockers:
        report.append("- None")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    approval_path.write_text(approval_text(), encoding="utf-8")
    print(report_path)
    return 2 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compile and validate local PDF references without replacing curated rules.

The compiler performs page-level extraction, sanitization, provenance capture,
incremental caching, and risk routing. Sanitized page text is stored only in the
excluded cache directory. Curated Markdown remains authoritative until a human
checks a proposed change against the recorded source pages.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
VENDOR_DIR = SCRIPT_DIR / "vendor"
if str(VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(VENDOR_DIR))

from book_to_skill.sanitize import sanitize_extracted_text  # noqa: E402
from book_to_skill.utils import detect_structure  # noqa: E402


UPSTREAM_COMMIT = "e087255f187c4fd3a5cdbb1cf1a11e09cdb84b46"
UPSTREAM_VERSION = "1.3.0"
MANIFEST_VERSION = 1
REPLACEMENT_GLYPH = "\ufffd"
UNI_THAI_ARTIFACT = re.compile(r"uni0e[0-9a-f]{2}", re.IGNORECASE)
THAI_CHARACTER = re.compile(r"[\u0e00-\u0e7f]")
VISIBLE_CHARACTER = re.compile(r"\S")

SOURCE_ROUTING = {
    "ตำราหนังสือ.pdf": {
        "curated_references": [
            "document-types-and-quality.md",
            "source-map.md",
        ],
        "segments": [
            {
                "id": "definitions-and-quality-levels",
                "pages": [1, 4],
                "topics": ["document type", "definition", "B", "A", "A+", "quality"],
            }
        ],
    },
    "ประกาศประเมินการสอน.pdf": {
        "curated_references": [
            "teaching-document-criteria.md",
            "qc-rubric.md",
            "source-map.md",
        ],
        "segments": [
            {
                "id": "teaching-regulations",
                "pages": [1, 4],
                "topics": ["teaching evaluation", "regulation", "definition"],
            },
            {
                "id": "teaching-document-rubric",
                "pages": [7, 11],
                "topics": ["teaching document", "rubric", "score", "criteria"],
            },
        ],
    },
    "แนวทางการประเมิน.pdf": {
        "curated_references": [
            "editorial-standards.md",
            "qc-rubric.md",
            "source-map.md",
        ],
        "segments": [
            {
                "id": "evaluation-practice",
                "pages": [6, 20],
                "topics": [
                    "evaluation",
                    "ethics",
                    "copyright",
                    "failure pattern",
                    "length",
                ],
            }
        ],
    },
    "คู่มือการเขียนตำราหนังสือมหิดล.pdf": {
        "curated_references": [
            "editorial-standards.md",
            "source-map.md",
        ],
        "segments": [
            {
                "id": "book-components-and-chapters",
                "pages": [7, 28],
                "topics": ["book component", "chapter", "Thai", "figure", "table"],
            },
            {
                "id": "references-and-index",
                "pages": [31, 36],
                "topics": ["citation", "reference", "bibliography", "index"],
            },
        ],
    },
    "คู่มือการเขียนตำราหนังสือ.pdf": {
        "curated_references": [
            "editorial-standards.md",
            "source-map.md",
        ],
        "segments": [
            {
                "id": "structure-and-layout",
                "pages": [5, 20],
                "topics": [
                    "structure",
                    "page layout",
                    "heading",
                    "figure",
                    "table",
                    "Thai writing",
                ],
            },
            {
                "id": "citation-and-bibliography",
                "pages": [21, 9999],
                "topics": ["citation", "bibliography", "reference"],
            },
        ],
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def display_path(path: Path, base: Path = SKILL_DIR) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def analyze_text(raw_text: str) -> tuple[str, dict[str, Any]]:
    """Sanitize one page and return its quality/security findings."""
    sanitized, invisible_removed = sanitize_extracted_text(raw_text or "")
    flags: list[str] = []
    if not VISIBLE_CHARACTER.search(sanitized):
        flags.append("EMPTY_EXTRACTION")
    if REPLACEMENT_GLYPH in sanitized:
        flags.append("REPLACEMENT_GLYPH")
    if UNI_THAI_ARTIFACT.search(sanitized):
        flags.append("UNI0E_ARTIFACT")
    if invisible_removed:
        flags.append("SUSPICIOUS_INVISIBLE_TEXT")
    return sanitized, {
        "characters": len(sanitized),
        "thai_characters": len(THAI_CHARACTER.findall(sanitized)),
        "invisible_removed": invisible_removed,
        "flags": flags,
    }


def extract_pages_with_pypdf(pdf_path: Path) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf is required to compile PDF references") from exc

    with pdf_path.open("rb") as stream:
        reader = PdfReader(stream)
        pages: list[str] = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                pages.append("")
        return pages


def ocr_page_with_docling(pdf_path: Path, page_index: int) -> str | None:
    """OCR one failed page with Docling when its optional runtime is available."""
    try:
        from pypdf import PdfReader, PdfWriter
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ImportError:
        return None

    with tempfile.TemporaryDirectory(prefix="reference-ocr-") as temp_name:
        page_pdf = Path(temp_name) / "page.pdf"
        reader = PdfReader(str(pdf_path))
        writer = PdfWriter()
        writer.add_page(reader.pages[page_index])
        with page_pdf.open("wb") as stream:
            writer.write(stream)

        options = PdfPipelineOptions()
        options.do_ocr = True
        options.do_table_structure = True
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=options)
            }
        )
        try:
            result = converter.convert(str(page_pdf))
            return result.document.export_to_markdown()
        except Exception:
            return None


def _safe_cache_directory(cache_root: Path, sha256: str) -> Path:
    resolved_root = cache_root.resolve()
    target = (resolved_root / sha256).resolve()
    if target.parent != resolved_root:
        raise RuntimeError(f"Unsafe cache target: {target}")
    return target


def write_sanitized_cache(
    cache_root: Path,
    source_hash: str,
    source_name: str,
    page_texts: list[str],
) -> str:
    target = _safe_cache_directory(cache_root, source_hash)
    if target.exists():
        shutil.rmtree(target)
    pages_dir = target / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    for number, text in enumerate(page_texts, start=1):
        (pages_dir / f"{number:04d}.md").write_text(text, encoding="utf-8")
    (target / "cache.json").write_text(
        json.dumps(
            {
                "source": source_name,
                "sha256": source_hash,
                "pages": len(page_texts),
                "content": "sanitized page extraction; not authoritative",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return display_path(target)


def bounded_segments(source_name: str, page_count: int) -> list[dict[str, Any]]:
    route = SOURCE_ROUTING.get(source_name, {})
    segments: list[dict[str, Any]] = []
    for segment in route.get("segments", []):
        first, last = segment["pages"]
        if first > page_count:
            continue
        item = dict(segment)
        item["pages"] = [first, min(last, page_count)]
        segments.append(item)
    if not segments and page_count:
        for first in range(1, page_count + 1, 20):
            segments.append(
                {
                    "id": f"pages-{first:04d}-{min(first + 19, page_count):04d}",
                    "pages": [first, min(first + 19, page_count)],
                    "topics": ["unclassified source segment"],
                }
            )
    return segments


def compile_source(
    pdf_path: Path,
    cache_root: Path,
    previous: dict[str, Any] | None,
    changed_only: bool,
    allow_ocr: bool,
    mark_verified: bool,
) -> tuple[dict[str, Any], bool]:
    source_hash = sha256_file(pdf_path)
    if changed_only and previous and previous.get("sha256") == source_hash:
        kept = dict(previous)
        kept["incremental_action"] = "unchanged"
        return kept, False

    raw_pages = extract_pages_with_pypdf(pdf_path)
    page_texts: list[str] = []
    page_map: list[dict[str, Any]] = []
    methods = {"pypdf"}
    source_flags: set[str] = set()

    for page_index, raw_text in enumerate(raw_pages):
        sanitized, analysis = analyze_text(raw_text)
        if "EMPTY_EXTRACTION" in analysis["flags"] and allow_ocr:
            ocr_text = ocr_page_with_docling(pdf_path, page_index)
            if ocr_text:
                sanitized, analysis = analyze_text(ocr_text)
                methods.add("docling-ocr")
        if "EMPTY_EXTRACTION" in analysis["flags"]:
            analysis["flags"].append("OCR_REQUIRED")
        if any(
            flag in analysis["flags"]
            for flag in (
                "EMPTY_EXTRACTION",
                "REPLACEMENT_GLYPH",
                "UNI0E_ARTIFACT",
                "SUSPICIOUS_INVISIBLE_TEXT",
            )
        ):
            analysis["flags"].append("VISUAL_REVIEW_REQUIRED")
        analysis["flags"] = sorted(set(analysis["flags"]))
        source_flags.update(analysis["flags"])
        page_texts.append(sanitized)
        page_map.append({"page": page_index + 1, **analysis})

    combined = "\n\n".join(page_texts)
    structure = detect_structure(combined)
    cache_path = write_sanitized_cache(
        cache_root, source_hash, pdf_path.name, page_texts
    )
    route = SOURCE_ROUTING.get(pdf_path.name, {})
    verification_status = (
        "VERIFIED"
        if mark_verified and not source_flags
        else "VISUAL_REVIEW_REQUIRED"
        if "VISUAL_REVIEW_REQUIRED" in source_flags
        else "EXTRACTED_PENDING_VERIFICATION"
    )
    return (
        {
            "filename": pdf_path.name,
            "sha256": source_hash,
            "bytes": pdf_path.stat().st_size,
            "page_count": len(raw_pages),
            "extraction_method": sorted(methods),
            "cache": cache_path,
            "page_map": page_map,
            "segments": bounded_segments(pdf_path.name, len(raw_pages)),
            "curated_references": route.get("curated_references", []),
            "chapters_detected": structure["chapters_detected"],
            "chapter_headings_sample": structure["chapter_headings_sample"],
            "has_toc": structure["has_toc"],
            "flags": sorted(source_flags),
            "verification_status": verification_status,
            "curated_replacement_allowed": False,
            "incremental_action": "rebuilt",
        },
        True,
    )


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def compile_references(
    source_dir: Path,
    manifest_path: Path,
    cache_root: Path,
    changed_only: bool = True,
    allow_ocr: bool = True,
    mark_verified: set[str] | None = None,
) -> dict[str, Any]:
    previous_manifest = load_manifest(manifest_path)
    previous_by_name = {
        item["filename"]: item for item in previous_manifest.get("sources", [])
    }
    pdfs = sorted(source_dir.glob("*.pdf"), key=lambda path: path.name.casefold())
    if not pdfs:
        raise RuntimeError(f"No PDF references found in {source_dir}")

    sources: list[dict[str, Any]] = []
    rebuilt = 0
    for pdf_path in pdfs:
        item, changed = compile_source(
            pdf_path=pdf_path,
            cache_root=cache_root,
            previous=previous_by_name.get(pdf_path.name),
            changed_only=changed_only,
            allow_ocr=allow_ocr,
            mark_verified=pdf_path.name in (mark_verified or set()),
        )
        sources.append(item)
        rebuilt += int(changed)

    manifest = {
        "version": MANIFEST_VERSION,
        "generated_at": utc_now(),
        "policy": {
            "curated_markdown_authoritative": True,
            "automatic_replacement": False,
            "quality_before_token_reduction": True,
            "token_counts_are_diagnostic_only": True,
            "raw_intermediates_persisted": False,
            "sanitized_cache_excluded_from_distribution": True,
        },
        "upstream": {
            "name": "book-to-skill",
            "version": UPSTREAM_VERSION,
            "commit": UPSTREAM_COMMIT,
            "license": "MIT",
            "license_file": "../scripts/vendor/LICENSE.md",
        },
        "source_directory": display_path(source_dir),
        "source_count": len(sources),
        "total_pages": sum(item["page_count"] for item in sources),
        "rebuilt_sources": rebuilt,
        "sources": sources,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=SKILL_DIR / "references" / "source-pdfs",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=SKILL_DIR / "references" / "source-manifest.json",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=SKILL_DIR / ".reference-cache",
    )
    parser.add_argument(
        "--rebuild-all",
        action="store_true",
        help="Ignore unchanged SHA-256 entries and rebuild every source.",
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Do not attempt optional Docling OCR for failed pages.",
    )
    parser.add_argument(
        "--mark-verified",
        action="append",
        default=[],
        metavar="PDF_NAME",
        help="Mark a clean extraction verified after visual source-page review.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = compile_references(
        source_dir=args.source_dir.resolve(),
        manifest_path=args.manifest.resolve(),
        cache_root=args.cache_dir.resolve(),
        changed_only=not args.rebuild_all,
        allow_ocr=not args.no_ocr,
        mark_verified=set(args.mark_verified),
    )
    print(
        json.dumps(
            {
                "sources": manifest["source_count"],
                "pages": manifest["total_pages"],
                "rebuilt": manifest["rebuilt_sources"],
                "manifest": str(args.manifest.resolve()),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

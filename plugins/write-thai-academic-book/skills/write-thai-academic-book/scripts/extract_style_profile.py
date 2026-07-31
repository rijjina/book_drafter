#!/usr/bin/env python3
"""Deterministically extract a style profile from DOCX, Markdown, or text."""

from __future__ import annotations

import argparse
import hashlib
import re
import statistics
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SUPPORTED_SUFFIXES = {".docx", ".md", ".txt"}
TRANSITIONS = (
    "ดังนั้น",
    "อย่างไรก็ตาม",
    "นอกจากนี้",
    "กล่าวคือ",
    "ในทางตรงกันข้าม",
    "ประการแรก",
    "ประการที่สอง",
    "สรุปได้ว่า",
)
ACADEMIC_TERMS = (
    "การวิเคราะห์",
    "การสังเคราะห์",
    "แนวคิด",
    "หลักการ",
    "กระบวนการ",
    "ระบบ",
    "ผลการวิจัย",
    "หลักฐาน",
    "ข้อจำกัด",
    "การประยุกต์ใช้",
)
FIRST_PERSON = ("ผู้เขียน", "ข้าพเจ้า", "กระผม", "ดิฉัน", "ผม", "เรา")
COMMON_LATIN_WORDS = {
    "and",
    "for",
    "from",
    "that",
    "the",
    "this",
    "with",
}
REFERENCE_HEADING = re.compile(
    r"^(?:\d+(?:\.\d+)*\s+)?(?:บรรณานุกรม|เอกสารอ้างอิง|references|bibliography)\s*$",
    re.I,
)
SHORT_SECTION_HEADING = re.compile(
    r"^(?:บทนำ|สรุป|สรุปท้ายบท|ความเข้าใจ|ประเด็นทบทวน|คำถามท้ายบท)\s*$"
)


@dataclass(frozen=True)
class SourceDocument:
    paragraphs: tuple[str, ...]
    headings: tuple[str, ...]
    table_count: int = 0
    list_count: int = 0
    reference_count: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, dest="input_path")
    parser.add_argument("--output", required=True, type=Path, dest="output_path")
    parser.add_argument("--template", type=Path)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def node_text(node: ET.Element) -> str:
    chunks: list[str] = []
    for item in node.iter():
        if item.tag == f"{W}t" and item.text:
            chunks.append(item.text)
        elif item.tag in {f"{W}tab", f"{W}br", f"{W}cr"}:
            chunks.append(" ")
    return normalize_text("".join(chunks))


def is_reference_heading(text: str) -> bool:
    return bool(REFERENCE_HEADING.match(normalize_text(text)))


def is_heading_like(text: str, style_name: str = "") -> bool:
    normalized = normalize_text(text)
    if re.search(r"(?:heading|หัวเรื่อง)\s*[1-6]", style_name, re.I):
        return True
    if len(normalized) > 180:
        return False
    return bool(
        re.match(r"^(?:บทที่|chapter)\s*[๐-๙\d]+\b", normalized, re.I)
        or re.match(r"^\d+(?:\.\d+){0,5}\s+\S", normalized)
        or SHORT_SECTION_HEADING.match(normalized)
        or REFERENCE_HEADING.match(normalized)
    )


def docx_source(path: Path) -> SourceDocument:
    with zipfile.ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        try:
            styles_root = ET.fromstring(archive.read("word/styles.xml"))
        except KeyError:
            styles_root = None
    styles: dict[str, str] = {}
    if styles_root is not None:
        for style in styles_root.findall(f".//{W}style"):
            style_id = style.get(f"{W}styleId", "")
            name = style.find(f"{W}name")
            if style_id and name is not None:
                styles[style_id] = name.get(f"{W}val", style_id)
    paragraphs: list[str] = []
    headings: list[str] = []
    table_count = 0
    list_count = 0
    reference_count = 0
    in_references = False
    previous_was_chapter_heading = False
    body = document.find(f"{W}body")
    if body is None:
        return SourceDocument((), ())
    for child in body:
        if child.tag == f"{W}tbl":
            table_count += 1
            continue
        if child.tag != f"{W}p":
            continue
        text = node_text(child)
        if not text:
            continue
        style_id = ""
        p_style = child.find(f"{W}pPr/{W}pStyle")
        if p_style is not None:
            style_id = p_style.get(f"{W}val", "")
        style_name = styles.get(style_id, style_id)
        chapter_heading = bool(re.match(r"^(?:บทที่|chapter)\s*[๐-๙\d]+\b", text, re.I))
        inferred_chapter_title = (
            previous_was_chapter_heading
            and len(text) <= 140
            and not re.search(r"[.!?。！？]$", text)
        )
        if is_heading_like(text, style_name) or inferred_chapter_title:
            headings.append(text)
            if is_reference_heading(text):
                in_references = True
            previous_was_chapter_heading = chapter_heading
            continue
        previous_was_chapter_heading = False
        if in_references:
            reference_count += 1
            continue
        if child.find(f"{W}pPr/{W}numPr") is not None:
            list_count += 1
            continue
        paragraphs.append(text)
    return SourceDocument(
        tuple(paragraphs), tuple(headings), table_count, list_count, reference_count
    )


def text_source(path: Path) -> SourceDocument:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = [line.rstrip() for line in raw.splitlines()]
    headings: list[str] = []
    paragraphs: list[str] = []
    list_count = 0
    table_rows = 0
    reference_count = 0
    in_references = False
    previous_was_chapter_heading = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        markdown_heading = path.suffix.lower() == ".md" and re.match(r"^#{1,6}\s+\S", stripped)
        heading_text = re.sub(r"^#{1,6}\s+", "", stripped) if markdown_heading else stripped
        chapter_heading = bool(re.match(r"^(?:บทที่|chapter)\s*[๐-๙\d]+\b", heading_text, re.I))
        inferred_chapter_title = (
            previous_was_chapter_heading
            and len(heading_text) <= 140
            and not re.search(r"[.!?。！？]$", heading_text)
        )
        if markdown_heading or is_heading_like(heading_text) or inferred_chapter_title:
            headings.append(heading_text)
            if is_reference_heading(heading_text):
                in_references = True
            previous_was_chapter_heading = chapter_heading
            continue
        previous_was_chapter_heading = False
        if in_references:
            reference_count += 1
            continue
        if re.match(r"^(?:[-*+] |\d+[.)]\s+)", stripped):
            list_count += 1
            continue
        if path.suffix.lower() == ".md" and stripped.startswith("|") and stripped.endswith("|"):
            table_rows += 1
            continue
        if path.suffix.lower() == ".md" and re.match(r"^\|?\s*:?-{3,}", stripped):
            continue
        paragraphs.append(normalize_text(stripped))
    table_count = 1 if table_rows >= 2 else 0
    return SourceDocument(
        tuple(paragraphs), tuple(headings), table_count, list_count, reference_count
    )


def load_source(path: Path) -> SourceDocument:
    if path.suffix.lower() == ".docx":
        return docx_source(path)
    return text_source(path)


def median_int(values: list[int]) -> int:
    return int(round(statistics.median(values))) if values else 0


def count_terms(text: str, terms: tuple[str, ...]) -> str:
    counts = Counter({term: text.count(term) for term in terms})
    found = [(term, count) for term, count in counts.items() if count]
    found.sort(key=lambda item: (-item[1], item[0]))
    return ", ".join(f"{term} ({count})" for term, count in found[:5]) or "None detected"


def sentence_lengths(paragraphs: tuple[str, ...]) -> list[int]:
    lengths: list[int] = []
    for paragraph in paragraphs:
        for sentence in re.split(r"(?<=[.!?。！？])\s+|[\n]+", paragraph):
            sentence = sentence.strip()
            if sentence:
                lengths.append(len(sentence))
    return lengths


def repeated_domain_terms(text: str) -> str:
    thai_terms = [(term, text.count(term)) for term in ACADEMIC_TERMS if text.count(term)]
    latin_counts = Counter(
        word.casefold()
        for word in re.findall(r"\b[A-Za-z][A-Za-z'-]{2,}\b", text)
        if word.casefold() not in COMMON_LATIN_WORDS
    )
    combined = thai_terms + [(term, count) for term, count in latin_counts.items() if count > 1]
    combined.sort(key=lambda item: (-item[1], item[0]))
    return ", ".join(f"{term} ({count})" for term, count in combined[:8]) or "None detected"


def excerpt(value: str) -> str:
    normalized = normalize_text(value)
    if not normalized:
        return "Not available"
    return normalized if len(normalized) <= 240 else normalized[:237].rstrip() + "..."


def is_representative_prose(value: str) -> bool:
    normalized = normalize_text(value)
    if len(normalized) < 80:
        return False
    if re.match(
        r"^(?:ผลงานที่เกี่ยวข้องประจำบท|วัตถุประสงค์|คำสำคัญ|keywords?|doi\s*:)",
        normalized,
        re.I,
    ):
        return False
    return True


def render_profile(path: Path, source: SourceDocument, template: str) -> str:
    text = "\n".join(source.paragraphs)
    representative = tuple(item for item in source.paragraphs if is_representative_prose(item)) or source.paragraphs
    paragraph_lengths = [len(item) for item in source.paragraphs]
    thai_count = len(re.findall(r"[ก-๙]", text))
    latin_count = len(re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", text))
    extraction_status = (
        "COMPLETE" if len(source.paragraphs) >= 3 and len(text) >= 300 else "SPARSE"
    )
    author_year = len(re.findall(r"\([^()\n]*[A-Za-zก-๙][^()\n]*,?\s*(?:19|20|25)\d{2}[a-z]?\)", text))
    numeric_citations = len(re.findall(r"\[(?:\d+[,-]?\s*)+\]", text))
    heading_pattern = (
        f"Detected {len(source.headings)} explicit headings; preserve their hierarchy and concise naming pattern."
        if source.headings
        else "No explicit heading hierarchy detected; do not invent one without the approved outline or governing standard."
    )
    paragraph_pattern = (
        f"Median {median_int(paragraph_lengths)} characters across {len(source.paragraphs)} non-empty paragraphs."
    )
    list_pattern = "Used" if source.list_count else "Not detected"
    table_pattern = "Used" if source.table_count else "Not detected"
    dominant_script = "Thai" if thai_count >= latin_count else "Latin or mixed"
    endings = Counter(re.findall(r"([.!?。！？])(?:\s|$)", text))
    ending_pattern = ", ".join(f"{mark} ({count})" for mark, count in sorted(endings.items())) or "No explicit sentence-ending punctuation detected"
    replacements = {
        "SOURCE_FILE": path.name,
        "SOURCE_FORMAT": path.suffix.lower().lstrip(".").upper(),
        "SOURCE_SHA256": sha256(path),
        "EXTRACTION_STATUS": extraction_status,
        "PARAGRAPH_COUNT": str(len(source.paragraphs)),
        "HEADING_COUNT": str(len(source.headings)),
        "TABLE_COUNT": str(source.table_count),
        "LIST_COUNT": str(source.list_count),
        "REFERENCE_COUNT": str(source.reference_count),
        "THAI_CHARACTER_COUNT": str(thai_count),
        "LATIN_WORD_COUNT": str(latin_count),
        "MEDIAN_PARAGRAPH_LENGTH": str(median_int(paragraph_lengths)),
        "MEDIAN_SENTENCE_LENGTH": str(median_int(sentence_lengths(source.paragraphs))),
        "FIRST_PERSON_MARKERS": count_terms(text, FIRST_PERSON),
        "AUTHOR_YEAR_CITATIONS": str(author_year),
        "NUMERIC_CITATIONS": str(numeric_citations),
        "HEADING_PATTERN": heading_pattern,
        "PARAGRAPH_PATTERN": paragraph_pattern,
        "LIST_PATTERN": f"{list_pattern}; {source.list_count} list paragraphs detected.",
        "TABLE_PATTERN": f"{table_pattern}; {source.table_count} tables detected.",
        "REFERENCE_PATTERN": (
            f"Excluded {source.reference_count} paragraphs after an explicit reference heading."
            if source.reference_count
            else "No explicit terminal reference section detected."
        ),
        "DOMINANT_SCRIPT": dominant_script,
        "TRANSITION_MARKERS": count_terms(text, TRANSITIONS),
        "ACADEMIC_TERMS": repeated_domain_terms(text),
        "SENTENCE_ENDING_PATTERN": ending_pattern,
        "OPENING_SAMPLE": excerpt(representative[0] if representative else ""),
        "TRANSITION_SAMPLE": excerpt(
            next(
                (paragraph for paragraph in representative if any(term in paragraph for term in TRANSITIONS)),
                representative[len(representative) // 2] if representative else "",
            )
        ),
        "CLOSING_SAMPLE": excerpt(representative[-1] if representative else ""),
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered.rstrip() + "\n"


def default_template_path() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "style-profile-template.md"


def extract_style_profile(input_path: Path, output_path: Path, template_path: Path | None = None) -> Path:
    source_path = input_path.resolve()
    if not source_path.is_file() or source_path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Input must be DOCX, Markdown, or text: {source_path}")
    selected_template = (template_path or default_template_path()).resolve()
    template = selected_template.read_text(encoding="utf-8-sig")
    source = load_source(source_path)
    if not source.paragraphs:
        raise ValueError(f"No readable prose paragraphs found in source: {source_path}")
    rendered = render_profile(source_path, source, template)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return output_path


def main() -> int:
    args = parse_args()
    try:
        result = extract_style_profile(args.input_path, args.output_path, args.template)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

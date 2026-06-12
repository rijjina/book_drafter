#!/usr/bin/env python3
"""Structural preflight for Thai academic manuscripts.

This checker finds omissions and consistency risks. It cannot validate academic
correctness, originality, permissions, or compliance with local regulations.
"""

from __future__ import annotations

import argparse
import re
import statistics
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


SUPPORTED = {".md", ".txt", ".docx"}
TYPE_LABELS = {
    "textbook": "ตำรา",
    "book": "หนังสือ",
    "teaching-notes": "เอกสารคำสอน",
}


@dataclass
class Finding:
    severity: str
    check: str
    evidence: str
    action: str


def read_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs = []
    for paragraph in root.iter(f"{ns}p"):
        chunks = []
        for node in paragraph.iter():
            if node.tag == f"{ns}t" and node.text:
                chunks.append(node.text)
            elif node.tag in {f"{ns}tab", f"{ns}br", f"{ns}cr"}:
                chunks.append(" ")
        if chunks:
            paragraphs.append("".join(chunks))
    return "\n".join(paragraphs)


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        return read_docx(path)
    return path.read_text(encoding="utf-8-sig", errors="replace")


def collect_inputs(input_path: Path, output_path: Path | None) -> list[Path]:
    if input_path.is_file():
        return [input_path] if input_path.suffix.lower() in SUPPORTED else []
    files = []
    for path in input_path.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        if output_path and path.resolve() == output_path.resolve():
            continue
        files.append(path)
    return sorted(files)


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def find_chapters(text: str) -> list[tuple[str, int]]:
    matches = list(
        re.finditer(
            r"(?im)^(?:#{1,3}\s*)?(บทที่\s*[0-9๐-๙]+(?:\s*[:.-])?[^\n]*)$",
            text,
        )
    )
    if not matches:
        return []
    chapters = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        size = len(re.findall(r"\S+", text[match.end() : end]))
        chapters.append((normalized(match.group(1)), size))
    return chapters


def add_required_component_checks(doc_type: str, text: str, findings: list[Finding]) -> None:
    common = [
        ("สารบัญ", [r"สารบัญ"], "Add or plan a table of contents."),
        (
            "รายการอ้างอิง",
            [r"บรรณานุกรม", r"เอกสารอ้างอิง", r"references?"],
            "Add a bibliography/reference section and cross-check citations.",
        ),
    ]
    for name, patterns, action in common:
        if not contains_any(text, patterns):
            findings.append(Finding("WARN", name, "Not detected", action))

    if doc_type in {"textbook", "book"}:
        checks = [
            ("คำนำ", [r"ค(?:ำ|ํา)น(?:ำ|ํา)"], "Add a preface stating purpose, scope, and readers."),
            ("ดัชนี", [r"ดัชนี", r"\bindex\b"], "Create an index plan; finalize after pagination."),
        ]
    else:
        checks = [
            (
                "ผลลัพธ์/วัตถุประสงค์",
                [r"ผลลัพธ์การเรียนรู้", r"วัตถุประสงค์", r"จุดประสงค์"],
                "Add measurable chapter or course outcomes.",
            ),
            ("สรุป", [r"สรุป(?:ท้าย)?บท"], "Add a synthesis-oriented chapter summary."),
            (
                "กิจกรรมประเมิน",
                [r"คำถามทบทวน", r"แบบฝึกหัด", r"กิจกรรม", r"แบบทดสอบ"],
                "Add questions, exercises, or assessment aligned with outcomes.",
            ),
        ]
    for name, patterns, action in checks:
        if not contains_any(text, patterns):
            findings.append(Finding("WARN", name, "Not detected", action))

    if doc_type == "book":
        book_checks = [
            (
                "ขอบเขตทางวิชาการ",
                [r"ขอบเขต(?:ทาง)?วิชาการ", r"ขอบเขตของหนังสือ", r"แนวคิดแกน"],
                "State the disciplinary scope and central concept without course mapping.",
            ),
            (
                "มุมมองหรือคุณูปการของผู้เขียน",
                [r"มุมมองของผู้เขียน", r"ข้อสังเคราะห์ของผู้เขียน", r"คุณูปการ", r"ข้อเสนอของผู้เขียน"],
                "Identify the author's viewpoint, synthesis, or disciplinary contribution required for Level A.",
            ),
        ]
        for name, patterns, action in book_checks:
            if not contains_any(text, patterns):
                findings.append(Finding("WARN", name, "Not detected", action))

    if doc_type in {"textbook", "teaching-notes"} and not contains_any(
        text, [r"รหัสวิชา", r"course\s*code", r"[A-Z]{2,}\s*[- ]?\d{3,}"]
    ):
        findings.append(
            Finding(
                "WARN",
                "ข้อมูลรายวิชา",
                "Course code not detected",
                "Identify the related course and verify the author's teaching scope.",
            )
        )


def run_checks(doc_type: str, files: list[Path], text: str) -> list[Finding]:
    findings: list[Finding] = []
    if not normalized(text):
        return [Finding("BLOCKER", "Readable content", "No text extracted", "Check the input file.")]

    add_required_component_checks(doc_type, text, findings)

    placeholders = re.findall(
        r"(?im)(?:\bTODO\b|\bTBD\b|\bXXX\b|\[ต้อง[^\]]+\]|\[เติม[^\]]*\]|\[ยืนยัน[^\]]*\])",
        text,
    )
    if placeholders:
        sample = ", ".join(dict.fromkeys(normalized(item) for item in placeholders[:8]))
        findings.append(
            Finding(
                "BLOCKER",
                "Unresolved placeholders",
                sample,
                "Resolve each source, author-confirmation, or drafting placeholder.",
            )
        )

    chapters = find_chapters(text)
    if not chapters:
        findings.append(
            Finding("WARN", "Chapter structure", "No numbered Thai chapters detected", "Verify chapter headings and numbering.")
        )
    elif len(chapters) > 1:
        sizes = [size for _, size in chapters if size > 0]
        if sizes:
            median = statistics.median(sizes)
            short = [(title, size) for title, size in chapters if size < max(120, median * 0.35)]
            if short:
                evidence = "; ".join(f"{title}: {size} words" for title, size in short[:6])
                findings.append(
                    Finding(
                        "WARN",
                        "Chapter balance",
                        evidence,
                        "Check whether short chapters are incomplete or should be merged.",
                    )
                )

    citation_like = len(
        re.findall(
            r"(?:\([^\n()]{1,80}(?:19|20|25)\d{2}[^\n()]*\)|\[[0-9]{1,3}\])",
            text,
        )
    )
    if citation_like == 0:
        findings.append(
            Finding(
                "WARN",
                "In-text citations",
                "No common author-year or numeric citation pattern detected",
                "Verify that all non-original claims are cited using the governing style.",
            )
        )

    figure_count = len(re.findall(r"ภาพที่\s*[0-9๐-๙]+(?:[.-][0-9๐-๙]+)?", text))
    table_count = len(re.findall(r"ตารางที่\s*[0-9๐-๙]+(?:[.-][0-9๐-๙]+)?", text))
    source_count = len(re.findall(r"(?:ที่มา|ดัดแปลงจาก|เรียบเรียงโดย|วาดโดย|ถ่ายภาพโดย)\s*:", text))
    if figure_count + table_count and source_count < figure_count + table_count:
        findings.append(
            Finding(
                "WARN",
                "Figure/table source ledger",
                f"Detected {figure_count} figure labels, {table_count} table labels, and {source_count} source notes",
                "Check every figure and table for in-text mention, source, creator, adaptation, and permission status.",
            )
        )

    slash_count = len(re.findall(r"(?<=[ก-๙])/(?=[ก-๙])", text))
    if slash_count:
        findings.append(
            Finding(
                "INFO",
                "Thai slash usage",
                f"Detected {slash_count} Thai word joins using '/'",
                "Consider replacing '/' with และ or หรือ where appropriate.",
            )
        )

    duplicate_headings = []
    headings = re.findall(r"(?im)^#{1,6}\s+(.+?)\s*$", text)
    counts: dict[str, int] = {}
    for heading in headings:
        key = normalized(heading).casefold()
        counts[key] = counts.get(key, 0) + 1
    for heading, count in counts.items():
        if count > max(3, len(chapters)):
            duplicate_headings.append(f"{heading} ({count})")
    if duplicate_headings:
        findings.append(
            Finding(
                "INFO",
                "Repeated headings",
                "; ".join(duplicate_headings[:8]),
                "Confirm that repetition is intentional and structurally consistent.",
            )
        )

    findings.append(
        Finding(
            "INFO",
            "Input coverage",
            f"Scanned {len(files)} file(s), {len(normalized(text).split())} whitespace-delimited words, {len(chapters)} chapter(s)",
            "Perform expert academic, citation, copyright, and governing-rubric review after this preflight.",
        )
    )
    return findings


def render_report(doc_type: str, input_path: Path, findings: list[Finding]) -> str:
    blockers = sum(item.severity == "BLOCKER" for item in findings)
    warnings = sum(item.severity == "WARN" for item in findings)
    decision = "FAIL" if blockers else ("CONDITIONAL PASS" if warnings else "PASS")
    lines = [
        "# Draft Preflight Report",
        "",
        f"- Input: `{input_path}`",
        f"- Document type: `{TYPE_LABELS[doc_type]}` (`{doc_type}`)",
        f"- Structural decision: **{decision}**",
        f"- Blockers: {blockers}",
        f"- Warnings: {warnings}",
        "",
        "> This report checks structure and detectable consistency only. It does not validate academic correctness, originality, permissions, or institutional eligibility.",
        "",
        "## Findings",
        "",
        "| Severity | Check | Evidence | Action |",
        "| --- | --- | --- | --- |",
    ]
    for item in findings:
        evidence = item.evidence.replace("|", "\\|").replace("\n", " ")
        action = item.action.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {item.severity} | {item.check} | {evidence} | {action} |")
    lines.extend(["", "## Next Review", "", "Apply the governing rubric and record evidence for every criterion before declaring the manuscript compliant.", ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", choices=sorted(TYPE_LABELS), required=True, dest="doc_type")
    parser.add_argument("--input", required=True, type=Path, dest="input_path")
    parser.add_argument("--output", type=Path, dest="output_path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input_path.exists():
        print(f"Input does not exist: {args.input_path}", file=sys.stderr)
        return 2
    files = collect_inputs(args.input_path, args.output_path)
    if not files:
        print("No supported .md, .txt, or .docx files found.", file=sys.stderr)
        return 2
    chunks = []
    for path in files:
        try:
            chunks.append(f"\n\n===== FILE: {path} =====\n\n{read_text(path)}")
        except Exception as exc:  # pragma: no cover - defensive reporting
            chunks.append(f"\n\n===== FILE ERROR: {path} =====\n\n[UNREADABLE: {exc}]")
    text = "".join(chunks)
    findings = run_checks(args.doc_type, files, text)
    report = render_report(args.doc_type, args.input_path, findings)
    if args.output_path:
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text(report, encoding="utf-8")
        print(args.output_path)
    else:
        print(report)
    return 2 if any(item.severity == "BLOCKER" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

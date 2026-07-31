#!/usr/bin/env python3
"""Fast structural DOCX audit with concise JSON output.

This preflight inspects the OOXML package without rendering pages. It catches
broken relationships, heading/list/style problems, table geometry defects,
image metadata gaps, stale-field risks, and missing core metadata. It also
identifies layout-sensitive features that still require render QA.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"

W = f"{{{W_NS}}}"
R = f"{{{R_NS}}}"
REL = f"{{{REL_NS}}}"
WP = f"{{{WP_NS}}}"
A = f"{{{A_NS}}}"


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    location: str | None = None


class AuditError(RuntimeError):
    """Raised when the DOCX package cannot be audited."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_xml(archive: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        return ET.fromstring(archive.read(name))
    except KeyError:
        return None
    except ET.ParseError as exc:
        raise AuditError(f"Invalid XML in {name}: {exc}") from exc


def paragraph_text(paragraph: ET.Element) -> str:
    chunks: list[str] = []
    for node in paragraph.iter():
        if node.tag == f"{W}t" and node.text:
            chunks.append(node.text)
        elif node.tag in {f"{W}tab", f"{W}br", f"{W}cr"}:
            chunks.append(" ")
    return re.sub(r"\s+", " ", "".join(chunks)).strip()


def style_id(paragraph: ET.Element) -> str:
    node = paragraph.find(f"{W}pPr/{W}pStyle")
    return node.get(f"{W}val", "") if node is not None else ""


def heading_level(style: str) -> int | None:
    match = re.fullmatch(r"Heading\s*([1-9])", style, re.IGNORECASE)
    return int(match.group(1)) if match else None


def relationship_source(rel_name: str) -> str:
    if rel_name == "_rels/.rels":
        return ""
    directory, filename = posixpath.split(rel_name)
    if not directory.endswith("/_rels"):
        return ""
    source_dir = directory[: -len("/_rels")]
    source_name = filename[: -len(".rels")] if filename.endswith(".rels") else filename
    return posixpath.join(source_dir, source_name)


def resolve_relationship_target(rel_name: str, target: str) -> str:
    source = relationship_source(rel_name)
    source_dir = posixpath.dirname(source)
    return posixpath.normpath(posixpath.join(source_dir, target)).lstrip("/")


def audit_relationships(
    archive: zipfile.ZipFile, names: set[str], findings: list[Finding]
) -> tuple[int, int, dict[str, dict[str, ET.Element]]]:
    internal = 0
    external = 0
    relationships: dict[str, dict[str, ET.Element]] = {}
    for rel_name in sorted(name for name in names if name.endswith(".rels")):
        root = parse_xml(archive, rel_name)
        if root is None:
            continue
        source = relationship_source(rel_name)
        relationships[source] = {}
        for rel in root.findall(f"{REL}Relationship"):
            rel_id = rel.get("Id", "")
            relationships[source][rel_id] = rel
            target = rel.get("Target", "")
            if rel.get("TargetMode") == "External":
                external += 1
                if not re.match(r"^(?:https?|mailto):", target, re.IGNORECASE):
                    findings.append(
                        Finding("WARN", "UNUSUAL_EXTERNAL_LINK", f"External relationship has an unusual target: {target}", rel_name)
                    )
                continue
            internal += 1
            resolved = resolve_relationship_target(rel_name, target)
            if target and resolved not in names:
                findings.append(
                    Finding("ERROR", "BROKEN_RELATIONSHIP", f"Relationship {rel_id} targets missing part {resolved}", rel_name)
                )
    return internal, external, relationships


def audit_headings_and_lists(
    document: ET.Element, styles_root: ET.Element | None, findings: list[Finding]
) -> tuple[int, int, int, int]:
    paragraphs = document.findall(f".//{W}body/{W}p")
    defined_styles: set[str] = set()
    if styles_root is not None:
        for style in styles_root.findall(f"{W}style"):
            value = style.get(f"{W}styleId")
            if value:
                defined_styles.add(value)

    heading_count = 0
    list_count = 0
    manual_lists = 0
    previous_level = 0
    for index, paragraph in enumerate(paragraphs, start=1):
        text = paragraph_text(paragraph)
        style = style_id(paragraph)
        level = heading_level(style)
        if level:
            heading_count += 1
            if previous_level and level > previous_level + 1:
                findings.append(
                    Finding(
                        "WARN",
                        "HEADING_LEVEL_SKIP",
                        f"Heading level jumps from {previous_level} to {level}: {text[:80]}",
                        f"paragraph:{index}",
                    )
                )
            previous_level = level
            if defined_styles and style not in defined_styles:
                findings.append(
                    Finding("ERROR", "MISSING_HEADING_STYLE", f"Heading uses undefined style {style}", f"paragraph:{index}")
                )
        num_pr = paragraph.find(f"{W}pPr/{W}numPr")
        is_list_style = style.lower().startswith("list")
        if num_pr is not None or is_list_style:
            list_count += 1
        elif text and re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)", text):
            manual_lists += 1
            if manual_lists <= 5:
                findings.append(
                    Finding("WARN", "MANUAL_LIST", f"List-like text has no Word numbering: {text[:80]}", f"paragraph:{index}")
                )

    if heading_count and styles_root is None:
        findings.append(Finding("ERROR", "MISSING_STYLES_PART", "Document has headings but word/styles.xml is missing."))
    return len(paragraphs), heading_count, list_count, manual_lists


def field_instructions(root: ET.Element) -> list[str]:
    instructions = []
    for node in root.iter(f"{W}instrText"):
        if node.text and node.text.strip():
            instructions.append(re.sub(r"\s+", " ", node.text).strip().upper())
    for simple in root.iter(f"{W}fldSimple"):
        value = simple.get(f"{W}instr")
        if value:
            instructions.append(re.sub(r"\s+", " ", value).strip().upper())
    return instructions


def audit_fields(story_roots: dict[str, ET.Element], findings: list[Finding], render_reasons: set[str]) -> dict[str, int]:
    counts = {"PAGE": 0, "TOC": 0, "REF": 0, "PAGEREF": 0, "SEQ": 0, "OTHER": 0}
    for root in story_roots.values():
        for instruction in field_instructions(root):
            command = instruction.split(maxsplit=1)[0] if instruction else "OTHER"
            command = command if command in counts else "OTHER"
            counts[command] += 1
    for field in ("TOC", "REF", "PAGEREF", "SEQ"):
        if counts[field]:
            render_reasons.add(f"FIELD_{field}")
    document = story_roots["word/document.xml"]
    if counts["TOC"] and not document.findall(f".//{W}pPr/{W}pStyle[@{W}val='Heading1']"):
        findings.append(Finding("WARN", "TOC_WITHOUT_HEADINGS", "A TOC field exists but no Heading1 paragraphs were detected."))
    return counts


def tc_width(cell: ET.Element) -> tuple[str, str] | None:
    node = cell.find(f"{W}tcPr/{W}tcW")
    if node is None:
        return None
    return node.get(f"{W}w", ""), node.get(f"{W}type", "")


def audit_tables(document: ET.Element, findings: list[Finding], render_reasons: set[str]) -> int:
    tables = document.findall(f".//{W}tbl")
    if tables:
        render_reasons.add("TABLES")
    for table_index, table in enumerate(tables, start=1):
        grid = [int(node.get(f"{W}w", "0")) for node in table.findall(f"{W}tblGrid/{W}gridCol")]
        tbl_w = table.find(f"{W}tblPr/{W}tblW")
        declared = int(tbl_w.get(f"{W}w", "0")) if tbl_w is not None and tbl_w.get(f"{W}w", "").isdigit() else 0
        rows = table.findall(f"{W}tr")
        if not grid:
            findings.append(Finding("WARN", "TABLE_GRID_MISSING", "Table has no explicit tblGrid.", f"table:{table_index}"))
        elif declared and sum(grid) != declared:
            findings.append(
                Finding(
                    "WARN",
                    "TABLE_WIDTH_MISMATCH",
                    f"tblW={declared} but tblGrid sums to {sum(grid)}.",
                    f"table:{table_index}",
                )
            )
        for row_index, row in enumerate(rows, start=1):
            cells = row.findall(f"{W}tc")
            if grid and len(cells) != len(grid):
                findings.append(
                    Finding(
                        "WARN",
                        "TABLE_COLUMN_MISMATCH",
                        f"Row has {len(cells)} cells but grid has {len(grid)} columns.",
                        f"table:{table_index}/row:{row_index}",
                    )
                )
                continue
            for cell_index, cell in enumerate(cells):
                width = tc_width(cell)
                if width is None or width[1] != "dxa":
                    findings.append(
                        Finding(
                            "WARN",
                            "TABLE_CELL_WIDTH_MISSING",
                            "Cell width is missing or is not DXA.",
                            f"table:{table_index}/row:{row_index}/cell:{cell_index + 1}",
                        )
                    )
                elif grid and width[0].isdigit() and int(width[0]) != grid[cell_index]:
                    findings.append(
                        Finding(
                            "WARN",
                            "TABLE_CELL_WIDTH_MISMATCH",
                            f"Cell width {width[0]} does not match grid width {grid[cell_index]}.",
                            f"table:{table_index}/row:{row_index}/cell:{cell_index + 1}",
                        )
                    )
    return len(tables)


def audit_images(
    story_roots: dict[str, ET.Element],
    relationships: dict[str, dict[str, ET.Element]],
    names: set[str],
    findings: list[Finding],
    render_reasons: set[str],
) -> int:
    image_count = 0
    if any(root.findall(f".//{WP}docPr") or root.findall(f".//{A}blip") for root in story_roots.values()):
        render_reasons.add("IMAGES")
    for part_name, root in story_roots.items():
        doc_prs = root.findall(f".//{WP}docPr")
        blips = root.findall(f".//{A}blip")
        image_count += max(len(doc_prs), len(blips))
        for index, doc_pr in enumerate(doc_prs, start=1):
            if not (doc_pr.get("descr") or doc_pr.get("title")):
                findings.append(
                    Finding("WARN", "IMAGE_ALT_MISSING", "Image has no alt text or title.", f"{part_name}/image:{index}")
                )
        part_rels = relationships.get(part_name, {})
        for index, blip in enumerate(blips, start=1):
            rel_id = blip.get(f"{R}embed") or blip.get(f"{R}link")
            rel = part_rels.get(rel_id or "")
            if rel is None:
                findings.append(
                    Finding(
                        "ERROR",
                        "IMAGE_RELATIONSHIP_MISSING",
                        f"Image relationship {rel_id!r} is missing.",
                        f"{part_name}/image:{index}",
                    )
                )
                continue
            if rel.get("TargetMode") != "External":
                source_dir = posixpath.dirname(part_name)
                target = posixpath.normpath(posixpath.join(source_dir, rel.get("Target", ""))).lstrip("/")
                if target not in names:
                    findings.append(
                        Finding("ERROR", "IMAGE_PART_MISSING", f"Image part {target} is missing.", f"{part_name}/image:{index}")
                    )
    return image_count


def audit_captions(document: ET.Element, table_count: int, image_count: int, findings: list[Finding]) -> tuple[int, int]:
    figure_captions = 0
    table_captions = 0
    for paragraph in document.findall(f".//{W}p"):
        text = paragraph_text(paragraph)
        style = style_id(paragraph).lower()
        if style == "caption" or re.match(r"^(?:figure|ภาพ(?:ที่)?)[\s.:0-9๐-๙-]+", text, re.IGNORECASE):
            if re.match(r"^(?:table|ตาราง(?:ที่)?)[\s.:0-9๐-๙-]+", text, re.IGNORECASE):
                table_captions += 1
            else:
                figure_captions += 1
        elif re.match(r"^(?:table|ตาราง(?:ที่)?)[\s.:0-9๐-๙-]+", text, re.IGNORECASE):
            table_captions += 1
    if image_count > figure_captions:
        findings.append(
            Finding("WARN", "FIGURE_CAPTION_MISSING", f"Detected {image_count} images but only {figure_captions} figure captions.")
        )
    if table_count > table_captions:
        findings.append(
            Finding("WARN", "TABLE_CAPTION_MISSING", f"Detected {table_count} tables but only {table_captions} table captions.")
        )
    return figure_captions, table_captions


def audit_sections(
    document: ET.Element,
    document_relationships: dict[str, ET.Element],
    findings: list[Finding],
    render_reasons: set[str],
) -> int:
    sections = document.findall(f".//{W}sectPr")
    if not sections:
        findings.append(Finding("ERROR", "SECTION_MISSING", "No section properties were found."))
        return 0
    if len(sections) > 1:
        render_reasons.add("MULTIPLE_SECTIONS")
    for index, section in enumerate(sections, start=1):
        size = section.find(f"{W}pgSz")
        margins = section.find(f"{W}pgMar")
        if size is None or not size.get(f"{W}w") or not size.get(f"{W}h"):
            findings.append(Finding("WARN", "PAGE_SIZE_MISSING", "Section has no explicit page size.", f"section:{index}"))
        if margins is None:
            findings.append(Finding("WARN", "PAGE_MARGINS_MISSING", "Section has no explicit margins.", f"section:{index}"))
        for reference in section.findall(f"{W}headerReference") + section.findall(f"{W}footerReference"):
            rel_id = reference.get(f"{R}id", "")
            if rel_id not in document_relationships:
                findings.append(
                    Finding(
                        "ERROR",
                        "HEADER_FOOTER_RELATIONSHIP_MISSING",
                        f"Section references missing relationship {rel_id!r}.",
                        f"section:{index}",
                    )
                )
    if document.findall(f".//{W}br[@{W}type='page']") or document.findall(f".//{W}pageBreakBefore"):
        render_reasons.add("PAGE_BREAKS")
    return len(sections)


def audit_direct_formatting(document: ET.Element, findings: list[Finding]) -> tuple[int, int]:
    runs = document.findall(f".//{W}r")
    paragraphs = document.findall(f".//{W}p")
    direct_runs = 0
    direct_paragraphs = 0
    for run in runs:
        rpr = run.find(f"{W}rPr")
        if rpr is None:
            continue
        meaningful = [child for child in rpr if child.tag not in {f"{W}rStyle", f"{W}lang"}]
        if meaningful:
            direct_runs += 1
    for paragraph in paragraphs:
        ppr = paragraph.find(f"{W}pPr")
        if ppr is None:
            continue
        meaningful = [
            child
            for child in ppr
            if child.tag not in {f"{W}pStyle", f"{W}numPr", f"{W}keepNext", f"{W}keepLines"}
        ]
        if meaningful:
            direct_paragraphs += 1
    run_ratio = direct_runs / len(runs) if runs else 0
    paragraph_ratio = direct_paragraphs / len(paragraphs) if paragraphs else 0
    if run_ratio > 0.35 and direct_runs > 20:
        findings.append(
            Finding("WARN", "RUN_DIRECT_FORMATTING_HIGH", f"{direct_runs}/{len(runs)} runs use direct formatting ({run_ratio:.0%}).")
        )
    if paragraph_ratio > 0.50 and direct_paragraphs > 20:
        findings.append(
            Finding(
                "WARN",
                "PARAGRAPH_DIRECT_FORMATTING_HIGH",
                f"{direct_paragraphs}/{len(paragraphs)} paragraphs use direct formatting ({paragraph_ratio:.0%}).",
            )
        )
    return direct_runs, direct_paragraphs


def audit_metadata(archive: zipfile.ZipFile, findings: list[Finding]) -> dict[str, str]:
    root = parse_xml(archive, "docProps/core.xml")
    if root is None:
        findings.append(Finding("WARN", "CORE_METADATA_MISSING", "docProps/core.xml is missing."))
        return {"title": "", "creator": "", "subject": ""}
    values = {
        "title": (root.findtext(f"{{{DC_NS}}}title") or "").strip(),
        "creator": (root.findtext(f"{{{DC_NS}}}creator") or "").strip(),
        "subject": (root.findtext(f"{{{DC_NS}}}subject") or "").strip(),
    }
    if not values["title"]:
        findings.append(Finding("WARN", "TITLE_METADATA_MISSING", "Core metadata title is empty."))
    return values


def audit_docx(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AuditError(f"DOCX not found: {path}")
    findings: list[Finding] = []
    render_reasons: set[str] = set()
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile as exc:
        raise AuditError(f"Invalid DOCX ZIP package: {exc}") from exc
    with archive:
        bad_member = archive.testzip()
        if bad_member:
            raise AuditError(f"Corrupt ZIP member: {bad_member}")
        names = set(archive.namelist())
        required = {"[Content_Types].xml", "_rels/.rels", "word/document.xml"}
        missing = sorted(required - names)
        if missing:
            raise AuditError(f"Missing required DOCX parts: {', '.join(missing)}")
        document = parse_xml(archive, "word/document.xml")
        if document is None:
            raise AuditError("word/document.xml is missing.")
        styles = parse_xml(archive, "word/styles.xml")
        internal_rels, external_rels, relationships = audit_relationships(archive, names, findings)
        story_roots = {"word/document.xml": document}
        for name in sorted(names):
            if re.fullmatch(r"word/(?:header|footer)\d+\.xml", name):
                root = parse_xml(archive, name)
                if root is not None:
                    story_roots[name] = root
        paragraph_count, heading_count, list_count, manual_lists = audit_headings_and_lists(document, styles, findings)
        fields = audit_fields(story_roots, findings, render_reasons)
        table_count = audit_tables(document, findings, render_reasons)
        image_count = audit_images(story_roots, relationships, names, findings, render_reasons)
        figure_captions, table_captions = audit_captions(document, table_count, image_count, findings)
        section_count = audit_sections(document, relationships.get("word/document.xml", {}), findings, render_reasons)
        direct_runs, direct_paragraphs = audit_direct_formatting(document, findings)
        metadata = audit_metadata(archive, findings)
        if "word/footnotes.xml" in names or "word/endnotes.xml" in names:
            render_reasons.add("FOOTNOTES_OR_ENDNOTES")
        if document.findall(f".//{W}txbxContent"):
            render_reasons.add("TEXT_BOXES")

    status = "RENDER_REQUIRED" if render_reasons else ("WARN" if findings else "PASS")
    return {
        "status": status,
        "file": str(path.resolve()),
        "sha256": sha256_file(path),
        "summary": {
            "paragraphs": paragraph_count,
            "headings": heading_count,
            "lists": list_count,
            "manual_lists": manual_lists,
            "tables": table_count,
            "images": image_count,
            "figure_captions": figure_captions,
            "table_captions": table_captions,
            "sections": section_count,
            "fields": fields,
            "internal_relationships": internal_rels,
            "external_relationships": external_rels,
            "direct_formatting_runs": direct_runs,
            "direct_formatting_paragraphs": direct_paragraphs,
            "metadata": metadata,
        },
        "render_reasons": sorted(render_reasons),
        "findings": [asdict(item) for item in findings],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit DOCX structure and report whether render QA is required.")
    parser.add_argument("docx", type=Path, help="DOCX file to inspect")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    try:
        report = audit_docx(args.docx.resolve())
        exit_code = 0
    except (AuditError, OSError) as exc:
        report = {
            "status": "WARN",
            "file": str(args.docx.resolve()),
            "render_reasons": [],
            "findings": [asdict(Finding("ERROR", "PACKAGE_INVALID", str(exc)))],
        }
        exit_code = 2
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate a Markdown Evidence Package and its Outline Matrix handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


METADATA_KEYS = [
    "package_id",
    "mode",
    "project_id",
    "scope_id",
    "scope_type",
    "title",
    "main_question",
    "intended_reader",
    "scope",
    "exclusions",
    "source_outline",
    "source_matrix",
    "research_cutoff",
    "status",
    "human_subject_review",
]
MODES = {"SCOPING", "GAP_FILL"}
SCOPE_TYPES = {"BOOK", "CHAPTER", "SECTION", "ARTICLE", "COURSE", "OTHER"}
MODE_STATUSES = {
    "SCOPING": {"READY_FOR_MATRIX", "NEEDS_REVISION", "BLOCKED"},
    "GAP_FILL": {"READY_FOR_HANDOFF", "NEEDS_EVIDENCE", "NEEDS_REVISION", "BLOCKED"},
}
HUMAN_REVIEW = {"PENDING", "PASS"}
SOURCE_TYPES = {
    "LOCAL_USER_SOURCE",
    "PRIMARY_RESEARCH",
    "SYSTEMATIC_REVIEW",
    "GUIDELINE_STANDARD",
    "OFFICIAL_REPORT",
    "AUTHORITATIVE_BOOK",
    "INSTITUTIONAL_WEB",
    "OTHER",
}
VERIFICATIONS = {
    "VERIFIED_FULL_TEXT",
    "VERIFIED_OFFICIAL_TEXT",
    "VERIFIED_LOCAL_SOURCE",
    "ABSTRACT_ONLY",
    "METADATA_ONLY",
    "INACCESSIBLE",
}
VERIFIED = {"VERIFIED_FULL_TEXT", "VERIFIED_OFFICIAL_TEXT", "VERIFIED_LOCAL_SOURCE"}
RELATIONS = {"SUPPORTS", "QUALIFIES", "CONTRADICTS", "CONTEXT_ONLY"}
SUFFICIENCY = {"ADEQUATE", "PARTIAL", "NONE"}
HANDOFF_STATUSES = {"READY", "HOLD", "AUTHOR_DECISION"}
PLACEHOLDER = re.compile(r"\{\{|\}\}|<[^>]+>|\b(?:TODO|TBD)\b", re.I)
ID_PATTERNS = {
    "query": re.compile(r"^Q\d{3,}$"),
    "source": re.compile(r"^S\d{3,}$"),
    "claim": re.compile(r"^C\d{3,}$"),
    "matrix": re.compile(r"^OM-R\d{2,}$"),
    "fingerprint": re.compile(r"^sha256:[0-9a-f]{12}$"),
}
EVIDENCE_GAP = re.compile(r"ต้องค้นหลักฐาน|needs? evidence|unverified|pending|รอตรวจ", re.I)
UNRESOLVED_COVERAGE = re.compile(
    r"(?:ยัง)?ไม่ครอบคลุม|ไม่แทน(?:หลักการ|ข้ออ้าง)|"
    r"ต้อง(?:ค้น|เพิ่ม|หา).*(?:หลักฐาน|แหล่ง|งานวิจัย|review|systematic review|หนังสือ)|"
    r"does not cover|case(?: study)? only|needs? (?:another|additional) (?:source|evidence)",
    re.I,
)
VAGUE_LOCATOR = re.compile(r"^(?:-|n/?a|none|whole (?:source|document)|ทั้งฉบับ|ดูเอกสาร)$", re.I)

TABLE_HEADERS = {
    "search log": [
        "Query ID",
        "Channel",
        "Query",
        "Searched on",
        "Results screened",
        "Decision/notes",
    ],
    "source ledger": [
        "Source ID",
        "Citation/title",
        "Type",
        "DOI/URL/path",
        "Exact locator",
        "Verification",
        "Currency/currentness",
        "Rights/use",
        "Query ID",
        "Disposition/reason",
    ],
    "claim-evidence map": [
        "Claim ID",
        "Outline anchor",
        "Matrix anchor",
        "Claim",
        "Fingerprint",
        "Evidence",
        "Relation",
        "Synthesis/limits",
        "Sufficiency",
        "Gap/action",
    ],
    "matrix handoff": [
        "Matrix anchor",
        "Claim ID",
        "Fingerprint",
        "Proposed evidence cell",
        "Proposed claim adjustment",
        "Handoff status",
    ],
}
MATRIX_HEADERS = ["ลำดับ", "หัวข้อ", "ผู้อ่านต้องทำได้", "Claim", "หลักฐาน", "ตัวอย่าง/กิจกรรม"]


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def claim_fingerprint(claim: str) -> str:
    digest = hashlib.sha256(normalize(claim).encode("utf-8")).hexdigest()[:12]
    return f"sha256:{digest}"


def substantive(value: str | None, allow_dash: bool = False) -> bool:
    if value is None:
        return False
    stripped = value.strip()
    if not stripped or PLACEHOLDER.search(stripped):
        return False
    if stripped == "-" and not allow_dash:
        return False
    return True


def parse_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def parse_metadata(text: str) -> tuple[dict[str, str], list[str]]:
    match = re.search(r"```yaml\s*\r?\n(.*?)\r?\n```", text, re.S | re.I)
    if not match:
        return {}, ["Missing fenced yaml metadata block"]
    metadata: dict[str, str] = {}
    errors: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        item = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)", line)
        if not item:
            errors.append(f"Malformed metadata line: {raw_line}")
            continue
        key, raw_value = item.groups()
        value = raw_value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key in metadata:
            errors.append(f"Duplicate metadata key: {key}")
        metadata[key] = value
    return metadata, errors


def split_markdown_row(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in value:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def parse_table_after_heading(text: str, heading: str) -> tuple[list[str], list[list[str]]]:
    lines = text.splitlines()
    heading_re = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.I)
    start = next((i + 1 for i, line in enumerate(lines) if heading_re.match(line.strip())), None)
    if start is None:
        return [], []
    end = next((i for i in range(start, len(lines)) if lines[i].strip().startswith("## ")), len(lines))
    for index in range(start, end - 1):
        if not lines[index].strip().startswith("|") or not lines[index + 1].strip().startswith("|"):
            continue
        headers = split_markdown_row(lines[index])
        separator = split_markdown_row(lines[index + 1])
        if len(headers) != len(separator) or not separator_row(separator):
            continue
        rows: list[list[str]] = []
        for row_line in lines[index + 2 : end]:
            if not row_line.strip().startswith("|"):
                if rows:
                    break
                continue
            row = split_markdown_row(row_line)
            if len(row) == len(headers):
                rows.append(row)
        return headers, rows
    return [], []


def rows_as_dicts(headers: list[str], rows: list[list[str]]) -> list[dict[str, str]]:
    return [dict(zip(headers, row)) for row in rows]


def canonical_source_key(value: str) -> str:
    raw = value.strip().lower()
    raw = re.sub(r"^doi:\s*", "", raw)
    raw = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", raw)
    if re.match(r"^10\.\d{4,9}/\S+$", raw):
        return f"doi:{raw.rstrip('/')}"
    if re.match(r"^https?://", raw):
        parts = urlsplit(raw)
        path = parts.path.rstrip("/") or "/"
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))
    return re.sub(r"[\\/]+", "/", raw).rstrip("/")


def path_reference_matches(reference: str, actual: Path) -> bool:
    normalized_reference = reference.strip().replace("\\", "/").lower()
    normalized_actual = str(actual.resolve()).replace("\\", "/").lower()
    if Path(reference).is_absolute():
        return normalized_reference == normalized_actual
    return normalized_actual == normalized_reference or normalized_actual.endswith(f"/{normalized_reference}")


def parse_evidence(value: str) -> tuple[list[str], bool]:
    if value.strip() == "-":
        return [], True
    source_ids: list[str] = []
    valid = True
    for segment in [item.strip() for item in value.split(";") if item.strip()]:
        match = re.fullmatch(r"(S\d{3,})\s*@\s*(.+)", segment)
        if not match or not substantive(match.group(2)) or VAGUE_LOCATOR.fullmatch(match.group(2).strip()):
            valid = False
            continue
        source_ids.append(match.group(1))
    return source_ids, valid


def parse_relations(value: str) -> tuple[dict[str, str], bool]:
    if value.strip() == "-":
        return {}, True
    mappings: dict[str, str] = {}
    valid = True
    for segment in [item.strip() for item in value.split(";") if item.strip()]:
        match = re.fullmatch(r"(S\d{3,})\s*=\s*([A-Z_]+)", segment)
        if not match or match.group(2) not in RELATIONS:
            valid = False
            continue
        mappings[match.group(1)] = match.group(2)
    return mappings, valid


def parse_matrix(path: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    expected = [normalize(item) for item in MATRIX_HEADERS]
    headers: list[str] = []
    rows: list[list[str]] = []
    for index in range(len(lines) - 1):
        if not lines[index].strip().startswith("|") or not lines[index + 1].strip().startswith("|"):
            continue
        candidate = split_markdown_row(lines[index])
        separator = split_markdown_row(lines[index + 1])
        if [normalize(item) for item in candidate] == expected and separator_row(separator):
            headers = candidate
            for row_line in lines[index + 2 :]:
                if not row_line.strip().startswith("|"):
                    break
                row = split_markdown_row(row_line)
                if len(row) == 6:
                    rows.append(row)
            break
    if not headers:
        return {}, ["Matrix must contain exactly the six expected semantic columns in order"]
    if not rows:
        return {}, ["Matrix contains no data rows"]

    result: dict[str, dict[str, str]] = {}
    for index, row in enumerate(rows, 1):
        anchor = f"OM-R{index:02d}"
        expected_order = str(index)
        order_digits = re.sub(r"\D", "", row[0])
        if order_digits != expected_order:
            errors.append(f"{anchor}: Matrix order must be contiguous from 1")
        if not substantive(row[3]):
            errors.append(f"{anchor}: Matrix Claim is empty or a placeholder")
        result[anchor] = {
            "claim": row[3],
            "fingerprint": claim_fingerprint(row[3]),
        }
    return result, errors


def validate(
    package_path: Path,
    outline_path: Path | None = None,
    matrix_path: Path | None = None,
) -> dict[str, object]:
    text = package_path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    warnings: list[str] = []
    evidence_gaps: list[str] = []

    metadata, metadata_errors = parse_metadata(text)
    errors.extend(metadata_errors)
    missing_keys = [key for key in METADATA_KEYS if key not in metadata]
    extra_keys = [key for key in metadata if key not in METADATA_KEYS]
    if missing_keys:
        errors.append(f"Missing metadata keys: {', '.join(missing_keys)}")
    if extra_keys:
        errors.append(f"Unexpected metadata keys: {', '.join(extra_keys)}")
    for key in METADATA_KEYS:
        allow_dash = key == "source_matrix" and metadata.get("mode") == "SCOPING"
        if key in metadata and not substantive(metadata[key], allow_dash=allow_dash):
            errors.append(f"Missing or placeholder metadata value: {key}")

    mode = metadata.get("mode", "")
    declared_status = metadata.get("status", "")
    if mode not in MODES:
        errors.append(f"Invalid mode: {mode or '<missing>'}")
    if metadata.get("scope_type") not in SCOPE_TYPES:
        errors.append(f"Invalid scope_type: {metadata.get('scope_type', '<missing>')}")
    if mode in MODE_STATUSES and declared_status not in MODE_STATUSES[mode]:
        errors.append(f"Status {declared_status or '<missing>'} is not allowed for mode {mode}")
    if metadata.get("human_subject_review") not in HUMAN_REVIEW:
        errors.append("human_subject_review must be PENDING or PASS")
    if metadata.get("research_cutoff") and not parse_iso_date(metadata["research_cutoff"]):
        errors.append("research_cutoff must be an ISO YYYY-MM-DD date")
    if mode == "SCOPING" and metadata.get("source_matrix") != "-":
        errors.append("SCOPING source_matrix must be -")
    if mode == "GAP_FILL" and metadata.get("source_matrix") == "-":
        errors.append("GAP_FILL requires a source_matrix path")

    if outline_path is not None and not outline_path.is_file():
        errors.append(f"Outline file not found: {outline_path}")
    elif outline_path is not None and metadata.get("source_outline") and not path_reference_matches(
        metadata["source_outline"], outline_path
    ):
        errors.append("source_outline metadata does not match --outline")
    if matrix_path is not None and not matrix_path.is_file():
        errors.append(f"Matrix file not found: {matrix_path}")
    elif matrix_path is not None and metadata.get("source_matrix") and not path_reference_matches(
        metadata["source_matrix"], matrix_path
    ):
        errors.append("source_matrix metadata does not match --matrix")
    if mode == "GAP_FILL" and matrix_path is None:
        errors.append("GAP_FILL validation requires --matrix")

    parsed_tables: dict[str, list[dict[str, str]]] = {}
    for heading, expected_headers in TABLE_HEADERS.items():
        headers, rows = parse_table_after_heading(text, heading)
        if not headers:
            errors.append(f"Missing table: {heading}")
            parsed_tables[heading] = []
            continue
        if [normalize(item) for item in headers] != [normalize(item) for item in expected_headers]:
            errors.append(f"{heading}: headers do not match the integration contract")
        parsed_tables[heading] = rows_as_dicts(headers, rows)
        for number, row in enumerate(rows, 1):
            if any(not substantive(cell, allow_dash=True) for cell in row):
                errors.append(f"{heading} row {number}: empty or placeholder cell")

    queries = parsed_tables.get("search log", [])
    query_ids: set[str] = set()
    for number, row in enumerate(queries, 1):
        query_id = row.get("Query ID", "")
        if not ID_PATTERNS["query"].fullmatch(query_id):
            errors.append(f"search log row {number}: invalid Query ID {query_id}")
        elif query_id in query_ids:
            errors.append(f"search log row {number}: duplicate Query ID {query_id}")
        query_ids.add(query_id)
        if not parse_iso_date(row.get("Searched on", "")):
            errors.append(f"{query_id or f'search row {number}'}: Searched on must be YYYY-MM-DD")
        try:
            if int(row.get("Results screened", "")) < 0:
                raise ValueError
        except ValueError:
            errors.append(f"{query_id or f'search row {number}'}: Results screened must be a non-negative integer")

    sources = parsed_tables.get("source ledger", [])
    source_by_id: dict[str, dict[str, str]] = {}
    source_keys: dict[str, str] = {}
    source_titles: dict[str, str] = {}
    included_verified: set[str] = set()
    for number, row in enumerate(sources, 1):
        source_id = row.get("Source ID", "")
        if not ID_PATTERNS["source"].fullmatch(source_id):
            errors.append(f"source ledger row {number}: invalid Source ID {source_id}")
        elif source_id in source_by_id:
            errors.append(f"source ledger row {number}: duplicate Source ID {source_id}")
        source_by_id[source_id] = row
        source_type = row.get("Type", "")
        verification = row.get("Verification", "")
        currency = row.get("Currency/currentness", "")
        disposition = row.get("Disposition/reason", "")
        locator = row.get("Exact locator", "")
        query_id = row.get("Query ID", "")
        if source_type not in SOURCE_TYPES:
            errors.append(f"{source_id}: invalid source Type {source_type}")
        if verification not in VERIFICATIONS:
            errors.append(f"{source_id}: invalid Verification {verification}")
        if not re.fullmatch(
            r"(?:CURRENT_AS_OF:\s*\d{4}-\d{2}-\d{2}|PUBLISHED:\s*\d{4}|FOUNDATIONAL|HISTORICAL|NOT_CHECKED)",
            currency,
        ):
            errors.append(f"{source_id}: invalid Currency/currentness")
        elif currency.startswith("CURRENT_AS_OF:"):
            currency_date = currency.split(":", 1)[1].strip()
            if not parse_iso_date(currency_date):
                errors.append(f"{source_id}: CURRENT_AS_OF must use YYYY-MM-DD")
            elif parse_iso_date(metadata.get("research_cutoff", "")) and currency_date > metadata["research_cutoff"]:
                errors.append(f"{source_id}: CURRENT_AS_OF cannot be later than research_cutoff")
        if query_id not in query_ids:
            errors.append(f"{source_id}: unknown Query ID {query_id}")
        if not re.fullmatch(r"(?:INCLUDED|PROVISIONAL:\s*.+|EXCLUDED:\s*.+)", disposition):
            errors.append(f"{source_id}: invalid Disposition/reason")
        if disposition == "INCLUDED":
            if verification not in VERIFIED:
                errors.append(f"{source_id}: INCLUDED source must have a verified full/local/official state")
            if not substantive(locator) or VAGUE_LOCATOR.fullmatch(locator.strip()):
                errors.append(f"{source_id}: INCLUDED source requires an exact locator")
            if verification in VERIFIED:
                included_verified.add(source_id)
            if source_type in {"GUIDELINE_STANDARD", "INSTITUTIONAL_WEB"} and not currency.startswith("CURRENT_AS_OF:"):
                errors.append(f"{source_id}: included current official/web source requires CURRENT_AS_OF")
        if verification in {"ABSTRACT_ONLY", "METADATA_ONLY", "INACCESSIBLE"} and disposition == "INCLUDED":
            errors.append(f"{source_id}: provisional verification cannot be INCLUDED")

        canonical = canonical_source_key(row.get("DOI/URL/path", ""))
        if substantive(canonical):
            if canonical in source_keys:
                errors.append(f"{source_id}: duplicate DOI/URL/path also used by {source_keys[canonical]}")
            source_keys[canonical] = source_id
        canonical_title = normalize(row.get("Citation/title", ""))
        if substantive(canonical_title):
            if canonical_title in source_titles:
                errors.append(f"{source_id}: duplicate Citation/title also used by {source_titles[canonical_title]}")
            source_titles[canonical_title] = source_id

    claims = parsed_tables.get("claim-evidence map", [])
    claim_by_id: dict[str, dict[str, str]] = {}
    claim_by_anchor: dict[str, dict[str, str]] = {}
    for number, row in enumerate(claims, 1):
        claim_id = row.get("Claim ID", "")
        matrix_anchor = row.get("Matrix anchor", "")
        fingerprint = row.get("Fingerprint", "")
        sufficiency = row.get("Sufficiency", "")
        if not ID_PATTERNS["claim"].fullmatch(claim_id):
            errors.append(f"claim-evidence row {number}: invalid Claim ID {claim_id}")
        elif claim_id in claim_by_id:
            errors.append(f"claim-evidence row {number}: duplicate Claim ID {claim_id}")
        claim_by_id[claim_id] = row
        if not re.fullmatch(r"OUT-[A-Z0-9-]+", row.get("Outline anchor", "")):
            errors.append(f"{claim_id}: invalid Outline anchor")
        if sufficiency not in SUFFICIENCY:
            errors.append(f"{claim_id}: invalid Sufficiency {sufficiency}")

        if mode == "SCOPING":
            if matrix_anchor != "-" or fingerprint != "-":
                errors.append(f"{claim_id}: SCOPING must use - for Matrix anchor and Fingerprint")
        elif mode == "GAP_FILL":
            if not ID_PATTERNS["matrix"].fullmatch(matrix_anchor):
                errors.append(f"{claim_id}: invalid Matrix anchor {matrix_anchor}")
            elif matrix_anchor in claim_by_anchor:
                errors.append(f"{claim_id}: duplicate Matrix anchor {matrix_anchor}")
            claim_by_anchor[matrix_anchor] = row
            if not ID_PATTERNS["fingerprint"].fullmatch(fingerprint):
                errors.append(f"{claim_id}: invalid claim Fingerprint")

        evidence_ids, evidence_valid = parse_evidence(row.get("Evidence", ""))
        relations, relations_valid = parse_relations(row.get("Relation", ""))
        if not evidence_valid:
            errors.append(f"{claim_id}: Evidence must use `S### @ exact locator` segments")
        if not relations_valid:
            errors.append(f"{claim_id}: Relation must map `S###=CONTROLLED_VALUE` segments")
        for source_id in evidence_ids:
            if source_id not in source_by_id:
                errors.append(f"{claim_id}: Evidence references unknown source {source_id}")
        if set(evidence_ids) != set(relations):
            errors.append(f"{claim_id}: Evidence and Relation must reference the same source IDs")
        if sufficiency == "ADEQUATE":
            if not evidence_ids:
                errors.append(f"{claim_id}: ADEQUATE requires evidence")
            unverified = sorted(set(evidence_ids) - included_verified)
            if unverified:
                errors.append(f"{claim_id}: ADEQUATE uses non-included or unverified sources: {', '.join(unverified)}")
            if relations and set(relations.values()) <= {"CONTEXT_ONLY"}:
                errors.append(f"{claim_id}: CONTEXT_ONLY evidence cannot be ADEQUATE")
            coverage_text = f"{row.get('Synthesis/limits', '')} {row.get('Gap/action', '')}"
            if UNRESOLVED_COVERAGE.search(coverage_text):
                warnings.append(
                    f"{claim_id}: ADEQUATE conflicts with text indicating incomplete claim coverage; use PARTIAL or narrow the Claim"
                )
        else:
            evidence_gaps.append(f"{claim_id}: {sufficiency}")
            if not substantive(row.get("Gap/action", "")) or row.get("Gap/action", "") == "-":
                errors.append(f"{claim_id}: {sufficiency} requires a precise Gap/action")
        if "CONTRADICTS" in relations.values() and not substantive(row.get("Synthesis/limits", "")):
            errors.append(f"{claim_id}: contradictory evidence requires synthesis/limits")

    handoffs = parsed_tables.get("matrix handoff", [])
    handoff_by_anchor: dict[str, dict[str, str]] = {}
    for number, row in enumerate(handoffs, 1):
        anchor = row.get("Matrix anchor", "")
        claim_id = row.get("Claim ID", "")
        handoff_status = row.get("Handoff status", "")
        if mode == "SCOPING":
            errors.append("SCOPING Matrix handoff table must contain no data rows")
            break
        if not ID_PATTERNS["matrix"].fullmatch(anchor):
            errors.append(f"matrix handoff row {number}: invalid Matrix anchor {anchor}")
        elif anchor in handoff_by_anchor:
            errors.append(f"matrix handoff row {number}: duplicate Matrix anchor {anchor}")
        handoff_by_anchor[anchor] = row
        if claim_id not in claim_by_id:
            errors.append(f"{anchor}: unknown Claim ID {claim_id}")
        elif claim_by_id[claim_id].get("Matrix anchor") != anchor:
            errors.append(f"{anchor}: Claim ID {claim_id} is mapped to a different Matrix anchor")
        if not ID_PATTERNS["fingerprint"].fullmatch(row.get("Fingerprint", "")):
            errors.append(f"{anchor}: invalid handoff Fingerprint")
        if handoff_status not in HANDOFF_STATUSES:
            errors.append(f"{anchor}: invalid Handoff status {handoff_status}")
        evidence_cell = row.get("Proposed evidence cell", "")
        if handoff_status == "READY" and EVIDENCE_GAP.search(evidence_cell):
            errors.append(f"{anchor}: READY handoff cannot contain an evidence-gap marker")
        if handoff_status == "HOLD" and not EVIDENCE_GAP.search(evidence_cell):
            warnings.append(f"{anchor}: HOLD should state a precise evidence requirement")

    matrix_rows: dict[str, dict[str, str]] = {}
    if matrix_path is not None and matrix_path.is_file():
        matrix_rows, matrix_errors = parse_matrix(matrix_path)
        errors.extend(matrix_errors)
        if mode == "GAP_FILL":
            for anchor, matrix_row in matrix_rows.items():
                mapped = claim_by_anchor.get(anchor)
                if mapped is None:
                    errors.append(f"{anchor}: Matrix row has no claim-evidence mapping")
                    continue
                expected_fingerprint = matrix_row["fingerprint"]
                if mapped.get("Fingerprint") != expected_fingerprint:
                    errors.append(f"{anchor}: stale claim Fingerprint; Matrix claim changed")
                if normalize(mapped.get("Claim", "")) != normalize(matrix_row["claim"]):
                    errors.append(f"{anchor}: mapped Claim does not match the current Matrix Claim")
                handoff = handoff_by_anchor.get(anchor)
                if handoff is None:
                    errors.append(f"{anchor}: Matrix row has no handoff")
                elif handoff.get("Fingerprint") != expected_fingerprint:
                    errors.append(f"{anchor}: handoff Fingerprint does not match the current Matrix Claim")
            for anchor in sorted(set(claim_by_anchor) - set(matrix_rows)):
                errors.append(f"{anchor}: mapping refers to a Matrix row that does not exist")
            for anchor in sorted(set(handoff_by_anchor) - set(matrix_rows)):
                errors.append(f"{anchor}: handoff refers to a Matrix row that does not exist")

    if declared_status == "READY_FOR_MATRIX":
        if not queries:
            errors.append("READY_FOR_MATRIX requires at least one Search log row")
        if not sources:
            errors.append("READY_FOR_MATRIX requires at least one screened Source ledger row")
        if not claims:
            errors.append("READY_FOR_MATRIX requires at least one claim-evidence mapping")
    elif declared_status == "READY_FOR_HANDOFF":
        for claim_id, row in claim_by_id.items():
            if row.get("Sufficiency") != "ADEQUATE":
                errors.append(f"{claim_id}: READY_FOR_HANDOFF requires ADEQUATE sufficiency")
        for anchor, row in handoff_by_anchor.items():
            if row.get("Handoff status") != "READY":
                errors.append(f"{anchor}: READY_FOR_HANDOFF requires READY handoff status")
        if not claims or not handoffs:
            errors.append("READY_FOR_HANDOFF requires claim mappings and Matrix handoffs")
    elif declared_status == "NEEDS_EVIDENCE":
        has_hold = any(row.get("Handoff status") == "HOLD" for row in handoff_by_anchor.values())
        if not evidence_gaps and not has_hold:
            warnings.append("NEEDS_EVIDENCE should contain PARTIAL/NONE mappings or a HOLD handoff")

    if errors:
        validator_status, exit_code = "BLOCKED", 2
    elif warnings:
        validator_status, exit_code = "NEEDS_REVISION", 1
    else:
        validator_status = declared_status or "NEEDS_REVISION"
        exit_code = 0 if validator_status in {"READY_FOR_MATRIX", "READY_FOR_HANDOFF"} else 1
        if validator_status == "BLOCKED":
            exit_code = 2

    return {
        "validator_status": validator_status,
        "declared_status": declared_status,
        "mode": mode,
        "queries": len(queries),
        "sources": len(sources),
        "included_verified_sources": len(included_verified),
        "claims": len(claims),
        "matrix_rows": len(matrix_rows),
        "errors": errors,
        "warnings": warnings,
        "evidence_gaps": evidence_gaps,
        "human_checks": [
            "Evidence supports each exact claim",
            "Disciplinary interpretation is accurate",
            "Time-sensitive official sources are current",
            "Material contrary findings and limitations are represented",
            "Citation and reuse-rights decisions are appropriate",
        ],
        "exit_code": exit_code,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Evidence Package Markdown")
    parser.add_argument("--outline", type=Path, help="Source outline for provenance checking")
    parser.add_argument("--matrix", type=Path, help="Current six-column Outline Matrix")
    parser.add_argument("--json-output", type=Path, help="Optional derived JSON validation report")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input file not found: {args.input}")
    result = validate(args.input, args.outline, args.matrix)
    payload = json.dumps({key: value for key, value in result.items() if key != "exit_code"}, ensure_ascii=False, indent=2)
    print(payload)
    if args.json_output:
        args.json_output.write_text(payload + "\n", encoding="utf-8")
    return int(result["exit_code"])


if __name__ == "__main__":
    sys.exit(main())

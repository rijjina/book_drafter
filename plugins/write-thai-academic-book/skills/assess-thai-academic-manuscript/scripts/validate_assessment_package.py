#!/usr/bin/env python3
"""Validate a three-part Thai academic manuscript assessment package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from xml.etree import ElementTree


REQUIRED_FILES = (
    "rule-register.md",
    "assessment-report.md",
    "author-revision-plan.md",
)
TASKS = {
    "ASSESS_OUTLINE",
    "ASSESS_CHAPTER",
    "ASSESS_MANUSCRIPT",
    "ASSESS_ROUTE_READINESS",
}
MODES = {"REFERENCE_ONLY", "CURRENT_RULES"}
DOCUMENT_TYPES = {"BOOK", "TEXTBOOK", "TEACHING_HANDOUT", "TEACHING_NOTES"}
PACKAGE_STATUSES = {
    "READY_FOR_AUTHOR_REVIEW",
    "NEEDS_RULE_REFRESH",
    "NEEDS_EVIDENCE",
    "BLOCKED_RULE_SELECTION",
    "BLOCKED_INPUT",
}
RULE_STATUSES = {"REFERENCE_ONLY", "CURRENT", "STALE", "UNRESOLVED"}
CRITERION_STATUSES = {"PASS", "PARTIAL", "FAIL", "NOT_APPLICABLE"}
SEVERITIES = {"BLOCKER", "MAJOR", "MINOR", "NOTE"}
VERIFICATIONS = {
    "VERIFIED_OFFICIAL_TEXT",
    "VERIFIED_LOCAL_SOURCE",
    "ADVISORY_ONLY",
    "METADATA_ONLY",
    "INACCESSIBLE",
}
RULE_DISPOSITIONS = {"IN_FORCE", "SUPERSEDED", "AMENDS", "ADVISORY", "EXCLUDED"}
CURRENT_RULE_DISPOSITIONS = {"IN_FORCE", "AMENDS"}
APPROVAL_STATUS = "PENDING_AUTHOR_APPROVAL"
PLACEHOLDER = re.compile(r"\{\{|\}\}|<[^>]+>|\b(?:TODO|TBD)\b", re.I)
VAGUE_LOCATOR = re.compile(
    r"^(?:-|n/?a|none|unknown|whole (?:document|manuscript|source)|all|ทั้งฉบับ|ทั้งเอกสาร)$",
    re.I,
)
ID_PATTERNS = {
    "package": re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$"),
    "rule": re.compile(r"^R\d{3,}$"),
    "query": re.compile(r"^Q\d{3,}$"),
    "criterion": re.compile(r"^CR-\d{3,}$"),
    "revision": re.compile(r"^RV-\d{3,}$"),
    "sha256": re.compile(r"^[0-9a-f]{64}$"),
}

TABLE_HEADERS = {
    "Search log": [
        "Query ID",
        "Channel",
        "Query",
        "Searched on",
        "Results screened",
        "Decision/notes",
    ],
    "Rule ledger": [
        "Rule ID",
        "Issuing authority",
        "Title",
        "Rank/route",
        "Effective/superseded",
        "URL/path",
        "Exact locator",
        "Verification",
        "Rights/use",
        "Status/disposition",
    ],
    "Criteria assessment": [
        "Criterion ID",
        "Scope anchor",
        "Manuscript locator",
        "Rule ID/locator",
        "Status",
        "Severity",
        "Finding/evidence",
        "Limitation/conflict",
        "Author action",
        "Verification condition",
    ],
    "Official numeric scores": [
        "Metric",
        "Score/result",
        "Rule ID/locator",
        "Evidence basis",
        "Status",
    ],
    "Revision sequence": [
        "Revision ID",
        "Criterion ID",
        "Priority",
        "Dependency",
        "Affected locator",
        "Proposed action",
        "Acceptance check",
    ],
}

COMMON_METADATA = ("schema_version", "package_id", "assessment_id", "input_path", "input_sha256")
RULE_METADATA = COMMON_METADATA + (
    "project_id",
    "task",
    "mode",
    "document_type",
    "institution",
    "target_rank",
    "field",
    "submission_route",
    "intended_filing_date",
    "assessment_cutoff",
    "rules_status",
    "package_status",
)
REPORT_METADATA = COMMON_METADATA + (
    "task",
    "scope_id",
    "mode",
    "rules_status",
    "package_status",
    "numeric_scores",
)
PLAN_METADATA = COMMON_METADATA + ("approval_status",)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def substantive(value: str | None, *, allow_dash: bool = False) -> bool:
    if value is None:
        return False
    cleaned = value.strip()
    if not cleaned or PLACEHOLDER.search(cleaned):
        return False
    if not allow_dash and cleaned in {"-", "—"}:
        return False
    return True


def exact_locator(value: str | None) -> bool:
    return bool(substantive(value) and not VAGUE_LOCATOR.fullmatch(value.strip()))


def same_path(recorded: str, actual: Path) -> bool:
    """Compare a recorded input path with the CLI input without requiring one slash style."""
    try:
        candidate = Path(recorded).expanduser()
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        return candidate.resolve() == actual.resolve()
    except (OSError, RuntimeError, ValueError):
        return False


def locator_matches_input(locator: str, input_path: Path) -> tuple[bool, str | None]:
    """Best-effort locator verification for stable text/Markdown and DOCX anchors.

    Unsupported formats and directory inputs remain structurally validated only.
    """
    if not input_path.is_file():
        return True, None
    suffix = input_path.suffix.casefold()
    if suffix in {".md", ".markdown", ".txt"}:
        text = input_path.read_text(encoding="utf-8-sig", errors="replace")
        line_count = len(text.splitlines())
        line_numbers = [
            int(value)
            for value in re.findall(r"(?:\bline|บรรทัด)\s*#?\s*(\d+)", locator, re.I)
        ]
        if line_numbers and max(line_numbers) > line_count:
            return False, f"line {max(line_numbers)} exceeds input length {line_count}"
        quoted_anchors = re.findall(r"`([^`]+)`", locator)
        missing = [anchor for anchor in quoted_anchors if anchor not in text]
        if missing:
            return False, "quoted anchor not found: " + ", ".join(missing)
        return True, None
    if suffix == ".docx":
        paragraph_numbers = [int(value) for value in re.findall(r"\bP(\d{4,})\b", locator, re.I)]
        if not paragraph_numbers:
            return True, None
        try:
            with zipfile.ZipFile(input_path) as archive:
                root = ElementTree.fromstring(archive.read("word/document.xml"))
            paragraph_count = sum(1 for item in root.iter() if item.tag.endswith("}p"))
        except (KeyError, OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
            return True, f"could not verify DOCX paragraph locator: {exc}"
        if max(paragraph_numbers) > paragraph_count:
            return False, (
                f"paragraph P{max(paragraph_numbers):04d} exceeds DOCX paragraph count "
                f"{paragraph_count}"
            )
    return True, None


def parse_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def input_sha256(path: Path) -> str:
    """Hash one file or a stable, path-aware snapshot of a manuscript directory."""
    digest = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    ignored_dirs = {"assessments", "rendered", "__pycache__", ".pytest_cache"}
    files = sorted(
        item
        for item in path.rglob("*")
        if item.is_file() and not any(part in ignored_dirs for part in item.relative_to(path).parts)
    )
    for item in files:
        relative = item.relative_to(path).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(item.stat().st_size.to_bytes(8, "big"))
        with item.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


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
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", value)]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def parse_table(text: str, heading: str) -> tuple[list[dict[str, str]], list[str]]:
    heading_match = re.search(rf"(?im)^##\s+{re.escape(heading)}\s*$", text)
    if not heading_match:
        return [], [f"Missing section: {heading}"]
    remainder = text[heading_match.end() :]
    next_heading = re.search(r"(?m)^##\s+", remainder)
    section = remainder[: next_heading.start()] if next_heading else remainder
    table_lines = [line for line in section.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return [], [f"Missing Markdown table in section: {heading}"]
    headers = split_markdown_row(table_lines[0])
    separator = split_markdown_row(table_lines[1])
    expected = TABLE_HEADERS[heading]
    errors: list[str] = []
    if headers != expected:
        errors.append(f"{heading} headers must be exactly: {' | '.join(expected)}")
    if len(separator) != len(headers) or not is_separator_row(separator):
        errors.append(f"Malformed separator row in section: {heading}")
    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(table_lines[2:], 1):
        cells = split_markdown_row(line)
        if len(cells) != len(headers):
            errors.append(
                f"{heading} row {line_number} has {len(cells)} cells; expected {len(headers)}"
            )
            continue
        rows.append(dict(zip(headers, cells)))
    return rows, errors


def canonical_locator(value: str) -> str:
    cleaned = value.strip()
    if re.match(r"^https?://", cleaned, re.I):
        parts = urlsplit(cleaned)
        path = parts.path.rstrip("/") or "/"
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))
    return normalize(cleaned.replace("\\", "/"))


def parse_profile(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        match = re.match(r"^\s*(?:[-*]\s*)?([A-Za-z][A-Za-z /_-]+)\s*:\s*(.+?)\s*$", raw_line)
        if match:
            fields[normalize(match.group(1))] = match.group(2).strip()
    return fields


def check_required_metadata(
    name: str, metadata: dict[str, str], required: tuple[str, ...], errors: list[str]
) -> None:
    for key in required:
        if not substantive(metadata.get(key), allow_dash=key in {
            "institution", "target_rank", "field", "submission_route", "intended_filing_date"
        }):
            errors.append(f"{name}: missing or placeholder metadata '{key}'")


def validate(
    package: Path,
    input_path: Path,
    project_profile: Path | None = None,
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    package = package.resolve()
    input_path = input_path.resolve()

    if not package.is_dir():
        return {"valid": False, "errors": [f"Package directory does not exist: {package}"], "warnings": []}
    if not input_path.exists() or not (input_path.is_file() or input_path.is_dir()):
        return {"valid": False, "errors": [f"Input file or directory does not exist: {input_path}"], "warnings": []}
    if project_profile is not None and not project_profile.is_file():
        return {"valid": False, "errors": [f"Project profile does not exist: {project_profile}"], "warnings": []}

    package_files = sorted(item.name for item in package.iterdir() if item.is_file())
    unexpected_files = sorted(set(package_files) - set(REQUIRED_FILES))
    if unexpected_files:
        errors.append(
            "Assessment package must contain only the three contract artifacts; unexpected files: "
            + ", ".join(unexpected_files)
        )

    texts: dict[str, str] = {}
    metadata_by_file: dict[str, dict[str, str]] = {}
    for filename in REQUIRED_FILES:
        path = package / filename
        if not path.is_file():
            errors.append(f"Missing package artifact: {path}")
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        texts[filename] = text
        metadata, parse_errors = parse_metadata(text)
        metadata_by_file[filename] = metadata
        errors.extend(f"{filename}: {item}" for item in parse_errors)

    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings, "package": str(package)}

    rule_meta = metadata_by_file["rule-register.md"]
    report_meta = metadata_by_file["assessment-report.md"]
    plan_meta = metadata_by_file["author-revision-plan.md"]
    check_required_metadata("rule-register.md", rule_meta, RULE_METADATA, errors)
    check_required_metadata("assessment-report.md", report_meta, REPORT_METADATA, errors)
    check_required_metadata("author-revision-plan.md", plan_meta, PLAN_METADATA, errors)

    for filename, metadata in metadata_by_file.items():
        if metadata.get("schema_version") != "1.0":
            errors.append(f"{filename}: schema_version must be 1.0")
        for key in ("package_id", "assessment_id"):
            value = metadata.get(key, "")
            if value and not ID_PATTERNS["package"].fullmatch(value):
                errors.append(f"{filename}: invalid {key}: {value}")
        digest = metadata.get("input_sha256", "").lower()
        if digest and not ID_PATTERNS["sha256"].fullmatch(digest):
            errors.append(f"{filename}: input_sha256 must be 64 lowercase hex characters")

    for key in COMMON_METADATA:
        values = {metadata.get(key, "") for metadata in metadata_by_file.values()}
        if len(values) != 1:
            errors.append(f"Package artifacts disagree on metadata '{key}': {sorted(values)}")
    for key in ("task", "mode", "rules_status", "package_status"):
        if rule_meta.get(key) != report_meta.get(key):
            errors.append(f"rule-register.md and assessment-report.md disagree on '{key}'")

    task = rule_meta.get("task", "")
    mode = rule_meta.get("mode", "")
    doc_type = rule_meta.get("document_type", "")
    package_status = rule_meta.get("package_status", "")
    rules_status = rule_meta.get("rules_status", "")
    if task not in TASKS:
        errors.append(f"Invalid task: {task}")
    if mode not in MODES:
        errors.append(f"Invalid mode: {mode}")
    if doc_type not in DOCUMENT_TYPES:
        errors.append(f"Invalid document_type: {doc_type}")
    if package_status not in PACKAGE_STATUSES:
        errors.append(f"Invalid package_status: {package_status}")
    if rules_status not in RULE_STATUSES:
        errors.append(f"Invalid rules_status: {rules_status}")

    cutoff = rule_meta.get("assessment_cutoff", "")
    if cutoff and not parse_iso_date(cutoff):
        errors.append("rule-register.md: assessment_cutoff must be an ISO date")
    filing_date = rule_meta.get("intended_filing_date", "")
    if substantive(filing_date) and not parse_iso_date(filing_date):
        errors.append("rule-register.md: intended_filing_date must be an ISO date or '-'")

    route_fields = ("institution", "target_rank", "field", "submission_route", "intended_filing_date")
    missing_route = [key for key in route_fields if not substantive(rule_meta.get(key))]
    if task == "ASSESS_ROUTE_READINESS" or mode == "CURRENT_RULES":
        if missing_route and package_status != "BLOCKED_RULE_SELECTION":
            errors.append(
                "Missing route metadata requires package_status BLOCKED_RULE_SELECTION: "
                + ", ".join(missing_route)
            )
        if not missing_route and package_status == "BLOCKED_RULE_SELECTION":
            warnings.append("Route metadata is complete but package remains BLOCKED_RULE_SELECTION")

    if mode == "REFERENCE_ONLY":
        if rules_status != "REFERENCE_ONLY":
            errors.append("REFERENCE_ONLY mode requires rules_status REFERENCE_ONLY")
        allowed_reference_statuses = {"NEEDS_RULE_REFRESH", "BLOCKED_INPUT"}
        if task == "ASSESS_ROUTE_READINESS" and missing_route:
            allowed_reference_statuses.add("BLOCKED_RULE_SELECTION")
        if package_status not in allowed_reference_statuses:
            errors.append(
                "REFERENCE_ONLY mode requires NEEDS_RULE_REFRESH, or "
                "BLOCKED_RULE_SELECTION when route metadata is incomplete"
            )
    elif rules_status == "REFERENCE_ONLY":
        errors.append("CURRENT_RULES mode cannot use rules_status REFERENCE_ONLY")
    if rules_status in {"STALE", "UNRESOLVED"} and package_status == "READY_FOR_AUTHOR_REVIEW":
        errors.append("STALE or UNRESOLVED rules cannot produce READY_FOR_AUTHOR_REVIEW")

    actual_hash = input_sha256(input_path)
    recorded_hash = rule_meta.get("input_sha256", "").lower()
    if recorded_hash and recorded_hash != actual_hash:
        errors.append(
            f"Input fingerprint is stale: package records {recorded_hash}, current input is {actual_hash}"
        )
    recorded_path = rule_meta.get("input_path", "")
    if substantive(recorded_path) and not same_path(recorded_path, input_path):
        errors.append(
            f"Recorded input_path does not match --input: '{recorded_path}' != '{input_path}'"
        )

    search_rows, table_errors = parse_table(texts["rule-register.md"], "Search log")
    errors.extend(f"rule-register.md: {item}" for item in table_errors)
    rule_rows, table_errors = parse_table(texts["rule-register.md"], "Rule ledger")
    errors.extend(f"rule-register.md: {item}" for item in table_errors)
    criterion_rows, table_errors = parse_table(texts["assessment-report.md"], "Criteria assessment")
    errors.extend(f"assessment-report.md: {item}" for item in table_errors)
    score_rows, table_errors = parse_table(texts["assessment-report.md"], "Official numeric scores")
    errors.extend(f"assessment-report.md: {item}" for item in table_errors)
    revision_rows, table_errors = parse_table(texts["author-revision-plan.md"], "Revision sequence")
    errors.extend(f"author-revision-plan.md: {item}" for item in table_errors)

    if mode == "CURRENT_RULES" and not search_rows:
        errors.append("CURRENT_RULES mode requires at least one Search log row")
    if mode == "REFERENCE_ONLY" and search_rows:
        errors.append("REFERENCE_ONLY mode must not contain Search log rows")
    query_ids: set[str] = set()
    for index, row in enumerate(search_rows, 1):
        query_id = row.get("Query ID", "")
        if not ID_PATTERNS["query"].fullmatch(query_id):
            errors.append(f"Search log row {index}: invalid Query ID '{query_id}'")
        elif query_id in query_ids:
            errors.append(f"Duplicate Query ID: {query_id}")
        query_ids.add(query_id)
        if not substantive(row.get("Channel")) or not substantive(row.get("Query")):
            errors.append(f"Search log row {index}: channel and query are required")
        searched_on = row.get("Searched on", "")
        if not parse_iso_date(searched_on):
            errors.append(f"Search log row {index}: Searched on must be an ISO date")
        try:
            if int(row.get("Results screened", "")) < 0:
                raise ValueError
        except ValueError:
            errors.append(f"Search log row {index}: Results screened must be a non-negative integer")
        if not substantive(row.get("Decision/notes")):
            errors.append(f"Search log row {index}: Decision/notes is required")

    if not rule_rows:
        errors.append("Rule ledger must contain at least one rule row")
    rules: dict[str, dict[str, str]] = {}
    seen_locations: dict[str, str] = {}
    verified_current_rules: set[str] = set()
    usable_rule_ids: set[str] = set()
    for index, row in enumerate(rule_rows, 1):
        rule_id = row.get("Rule ID", "")
        if not ID_PATTERNS["rule"].fullmatch(rule_id):
            errors.append(f"Rule ledger row {index}: invalid Rule ID '{rule_id}'")
        elif rule_id in rules:
            errors.append(f"Duplicate Rule ID: {rule_id}")
        rules[rule_id] = row
        for key in ("Issuing authority", "Title", "Rank/route", "Effective/superseded", "URL/path", "Rights/use"):
            if not substantive(row.get(key)):
                errors.append(f"Rule {rule_id or index}: missing {key}")
        if not exact_locator(row.get("Exact locator")):
            errors.append(f"Rule {rule_id or index}: exact locator is missing or vague")
        verification = row.get("Verification", "")
        disposition = row.get("Status/disposition", "")
        if verification not in VERIFICATIONS:
            errors.append(f"Rule {rule_id or index}: invalid Verification '{verification}'")
        if disposition not in RULE_DISPOSITIONS:
            errors.append(f"Rule {rule_id or index}: invalid Status/disposition '{disposition}'")
        location = row.get("URL/path", "")
        if substantive(location):
            canonical = canonical_locator(location)
            if canonical in seen_locations:
                errors.append(
                    f"Duplicate rule URL/path: {location} also used by {seen_locations[canonical]}"
                )
            else:
                seen_locations[canonical] = rule_id
        if verification not in {"METADATA_ONLY", "INACCESSIBLE"} and disposition not in {"EXCLUDED", "SUPERSEDED"}:
            usable_rule_ids.add(rule_id)
        if verification == "VERIFIED_OFFICIAL_TEXT" and disposition in CURRENT_RULE_DISPOSITIONS:
            verified_current_rules.add(rule_id)
        if disposition in CURRENT_RULE_DISPOSITIONS and verification in {"METADATA_ONLY", "INACCESSIBLE"}:
            errors.append(f"Rule {rule_id}: metadata-only or inaccessible source cannot be included as current evidence")

    if mode == "CURRENT_RULES" and rules_status == "CURRENT" and not verified_current_rules:
        errors.append("CURRENT rules_status requires at least one VERIFIED_OFFICIAL_TEXT rule in force")

    if not criterion_rows:
        errors.append("Criteria assessment must contain at least one criterion row")
    criteria: dict[str, dict[str, str]] = {}
    actionable_criteria: set[str] = set()
    referenced_rule_ids: set[str] = set()
    for index, row in enumerate(criterion_rows, 1):
        criterion_id = row.get("Criterion ID", "")
        if not ID_PATTERNS["criterion"].fullmatch(criterion_id):
            errors.append(f"Criteria row {index}: invalid Criterion ID '{criterion_id}'")
        elif criterion_id in criteria:
            errors.append(f"Duplicate Criterion ID: {criterion_id}")
        criteria[criterion_id] = row
        if not substantive(row.get("Scope anchor")):
            errors.append(f"Criterion {criterion_id or index}: Scope anchor is required")
        if not exact_locator(row.get("Manuscript locator")):
            errors.append(f"Criterion {criterion_id or index}: manuscript locator is missing or vague")
        else:
            locator_ok, locator_note = locator_matches_input(
                row.get("Manuscript locator", ""), input_path
            )
            if not locator_ok:
                errors.append(
                    f"Criterion {criterion_id or index}: manuscript locator does not match input: "
                    f"{locator_note}"
                )
            elif locator_note:
                warnings.append(f"Criterion {criterion_id or index}: {locator_note}")
        rule_reference = row.get("Rule ID/locator", "")
        rule_ids = set(re.findall(r"\bR\d{3,}\b", rule_reference))
        if not rule_ids or not exact_locator(rule_reference):
            errors.append(f"Criterion {criterion_id or index}: rule ID and exact locator are required")
        for rule_id in rule_ids:
            referenced_rule_ids.add(rule_id)
            if rule_id not in rules:
                errors.append(f"Criterion {criterion_id}: references unknown Rule ID {rule_id}")
            elif rule_id not in usable_rule_ids:
                errors.append(f"Criterion {criterion_id}: references unusable or superseded Rule ID {rule_id}")
        status = row.get("Status", "")
        severity = row.get("Severity", "")
        if status not in CRITERION_STATUSES:
            errors.append(f"Criterion {criterion_id or index}: invalid Status '{status}'")
        if severity not in SEVERITIES:
            errors.append(f"Criterion {criterion_id or index}: invalid Severity '{severity}'")
        if status == "NOT_APPLICABLE" and severity != "NOTE":
            errors.append(f"Criterion {criterion_id}: NOT_APPLICABLE must use severity NOTE")
        if status == "PASS" and severity != "NOTE":
            errors.append(f"Criterion {criterion_id}: PASS must use severity NOTE")
        if status in {"PARTIAL", "FAIL"} and severity == "NOTE":
            errors.append(f"Criterion {criterion_id}: {status} cannot use severity NOTE")
        for key in ("Finding/evidence", "Limitation/conflict", "Verification condition"):
            if not substantive(row.get(key), allow_dash=key == "Limitation/conflict"):
                errors.append(f"Criterion {criterion_id or index}: missing {key}")
        if status in {"PARTIAL", "FAIL"}:
            actionable_criteria.add(criterion_id)
            if not substantive(row.get("Author action")):
                errors.append(f"Criterion {criterion_id}: {status} requires an Author action")

    numeric_mode = report_meta.get("numeric_scores", "")
    if numeric_mode not in {"NONE", "OFFICIAL_ONLY"}:
        errors.append("assessment-report.md: numeric_scores must be NONE or OFFICIAL_ONLY")
    if re.search(r"readiness\s*(?:score|percentage)|เปอร์เซ็นต์ความพร้อม", texts["assessment-report.md"], re.I):
        errors.append("Assessment report must not contain a readiness score or percentage")
    if score_rows and numeric_mode != "OFFICIAL_ONLY":
        errors.append("Official numeric score rows require numeric_scores OFFICIAL_ONLY")
    if not score_rows and numeric_mode == "OFFICIAL_ONLY":
        warnings.append("numeric_scores is OFFICIAL_ONLY but the score table is empty")
    for index, row in enumerate(score_rows, 1):
        rule_reference = row.get("Rule ID/locator", "")
        rule_ids = set(re.findall(r"\bR\d{3,}\b", rule_reference))
        if not rule_ids or not exact_locator(rule_reference):
            errors.append(f"Official numeric score row {index}: verified rule ID and locator are required")
        for rule_id in rule_ids:
            if rule_id not in usable_rule_ids:
                errors.append(f"Official numeric score row {index}: unusable Rule ID {rule_id}")
        for key in ("Metric", "Score/result", "Evidence basis", "Status"):
            if not substantive(row.get(key)):
                errors.append(f"Official numeric score row {index}: missing {key}")

    if plan_meta.get("approval_status") != APPROVAL_STATUS:
        errors.append(f"author-revision-plan.md: approval_status must be {APPROVAL_STATUS}")
    revisions: dict[str, dict[str, str]] = {}
    covered_criteria: set[str] = set()
    for index, row in enumerate(revision_rows, 1):
        revision_id = row.get("Revision ID", "")
        criterion_id = row.get("Criterion ID", "")
        if not ID_PATTERNS["revision"].fullmatch(revision_id):
            errors.append(f"Revision row {index}: invalid Revision ID '{revision_id}'")
        elif revision_id in revisions:
            errors.append(f"Duplicate Revision ID: {revision_id}")
        revisions[revision_id] = row
        if criterion_id not in criteria:
            errors.append(f"Revision {revision_id or index}: unknown Criterion ID '{criterion_id}'")
        covered_criteria.add(criterion_id)
        if row.get("Priority", "") not in SEVERITIES:
            errors.append(f"Revision {revision_id or index}: invalid Priority '{row.get('Priority', '')}'")
        elif criterion_id in criteria and row.get("Priority") != criteria[criterion_id].get("Severity"):
            errors.append(
                f"Revision {revision_id or index}: Priority must match criterion severity "
                f"'{criteria[criterion_id].get('Severity', '')}'"
            )
        if not exact_locator(row.get("Affected locator")):
            errors.append(f"Revision {revision_id or index}: affected locator is missing or vague")
        for key in ("Dependency", "Proposed action", "Acceptance check"):
            if not substantive(row.get(key), allow_dash=key == "Dependency"):
                errors.append(f"Revision {revision_id or index}: missing {key}")
    missing_actions = sorted(actionable_criteria - covered_criteria)
    if missing_actions:
        errors.append("PARTIAL/FAIL criteria missing from revision plan: " + ", ".join(missing_actions))

    if project_profile is not None:
        profile = parse_profile(project_profile)
        comparisons = {
            "institution": ("institution",),
            "target_rank": ("target rank", "target_rank", "academic rank"),
            "field": ("field", "official field", "discipline"),
            "submission_route": ("submission route", "route", "method"),
            "document_type": ("document type", "document_type"),
            "intended_filing_date": ("intended filing date", "filing date"),
        }
        for metadata_key, profile_keys in comparisons.items():
            profile_value = next((profile[key] for key in profile_keys if key in profile), None)
            metadata_value = rule_meta.get(metadata_key)
            if profile_value and substantive(metadata_value) and normalize(profile_value) != normalize(metadata_value):
                errors.append(
                    f"Project profile mismatch for {metadata_key}: '{profile_value}' != '{metadata_value}'"
                )

    return {
        "valid": not errors,
        "package": str(package),
        "assessment_id": rule_meta.get("assessment_id"),
        "task": task,
        "mode": mode,
        "document_type": doc_type,
        "rules_status": rules_status,
        "package_status": package_status,
        "input_sha256": actual_hash,
        "counts": {
            "queries": len(search_rows),
            "rules": len(rule_rows),
            "criteria": len(criterion_rows),
            "revisions": len(revision_rows),
            "official_scores": len(score_rows),
        },
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path, help="Assessment package directory")
    parser.add_argument("--input", required=True, type=Path, dest="input_path")
    parser.add_argument("--project-profile", type=Path)
    parser.add_argument("--json-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate(args.package, args.input_path, args.project_profile)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())

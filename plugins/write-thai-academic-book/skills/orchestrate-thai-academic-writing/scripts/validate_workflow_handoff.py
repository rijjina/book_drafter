#!/usr/bin/env python3
"""Validate cross-skill handoffs in the Thai academic writing workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


STAGES = ("matrix-build", "matrix-revise", "draft-chapter", "teaching-material-revision")
MATRIX_HEADERS = ["ลำดับ", "หัวข้อ", "ผู้อ่านต้องทำได้", "Claim", "หลักฐาน", "ตัวอย่าง/กิจกรรม"]
CLAIM_HEADERS = [
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
]
REVISION_HEADERS = [
    "Revision ID",
    "Criterion ID",
    "Priority",
    "Dependency",
    "Affected locator",
    "Proposed action",
    "Acceptance check",
]
ASSESSMENT_FILES = ("rule-register.md", "assessment-report.md", "author-revision-plan.md")


def metadata_blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    for body in re.findall(r"```yaml\s*\r?\n(.*?)\r?\n```", text, re.S | re.I):
        fields: dict[str, str] = {}
        for raw_line in body.splitlines():
            item = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*?)\s*", raw_line)
            if not item:
                continue
            key, value = item.groups()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            fields[key] = value
        blocks.append(fields)
    return blocks


def combined_metadata(blocks: list[dict[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for block in blocks:
        result.update(block)
    return result


def split_row(line: str) -> list[str]:
    value = line.strip().strip("|")
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", value)]


def separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def tables(text: str) -> list[tuple[list[str], list[dict[str, str]]]]:
    lines = text.splitlines()
    found: list[tuple[list[str], list[dict[str, str]]]] = []
    index = 0
    while index + 1 < len(lines):
        if not lines[index].lstrip().startswith("|"):
            index += 1
            continue
        headers = split_row(lines[index])
        divider = split_row(lines[index + 1]) if lines[index + 1].lstrip().startswith("|") else []
        if not separator(divider) or len(divider) != len(headers):
            index += 1
            continue
        rows: list[dict[str, str]] = []
        index += 2
        while index < len(lines) and lines[index].lstrip().startswith("|"):
            cells = split_row(lines[index])
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
            index += 1
        found.append((headers, rows))
    return found


def table_with_headers(text: str, expected: list[str]) -> list[dict[str, str]] | None:
    for headers, rows in tables(text):
        if headers == expected:
            return rows
    return None


def fingerprint(claim: str) -> str:
    normalized = re.sub(r"\s+", " ", claim.strip()).lower()
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def input_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    ignored = {"assessments", "rendered", "__pycache__", ".pytest_cache"}
    files = sorted(
        item
        for item in path.rglob("*")
        if item.is_file() and not any(part in ignored for part in item.relative_to(path).parts)
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


def candidate_paths(recorded: str, artifact: Path) -> list[Path]:
    value = Path(recorded)
    if value.is_absolute():
        return [value.resolve()]
    bases = [Path.cwd(), artifact.parent, *artifact.parents]
    result: list[Path] = []
    for base in bases:
        candidate = (base / value).resolve()
        if candidate not in result:
            result.append(candidate)
    return result


def path_matches(recorded: str, actual: Path, artifact: Path) -> bool:
    if not recorded:
        return False
    actual = actual.resolve()
    return any(candidate == actual for candidate in candidate_paths(recorded, artifact))


def existing_recorded_path(recorded: str, artifact: Path) -> Path | None:
    for candidate in candidate_paths(recorded, artifact):
        if candidate.exists():
            return candidate
    return None


def validate_matrix(
    path: Path, errors: list[str], *, require_ready: bool
) -> tuple[dict[str, str], dict[str, str]]:
    if not path.is_file():
        errors.append(f"Matrix does not exist: {path}")
        return {}, {}
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    blocks = metadata_blocks(text)
    if not blocks:
        errors.append("Matrix is missing fenced YAML metadata")
        return {}, {}
    first = blocks[0]
    all_meta = combined_metadata(blocks)
    if require_ready:
        if first.get("status") != "READY_TO_DRAFT":
            errors.append("Matrix metadata status must be READY_TO_DRAFT")
        if all_meta.get("validator_status") != "READY_TO_DRAFT":
            errors.append("Matrix validator_status must be READY_TO_DRAFT")
    else:
        allowed = {"READY_TO_DRAFT", "NEEDS_EVIDENCE", "NEEDS_REVISION"}
        if first.get("status") not in allowed:
            errors.append("Current Matrix has an invalid status for handoff revision")
        if all_meta.get("validator_status") not in allowed:
            errors.append("Current Matrix validator_status is invalid for handoff revision")
    rows = table_with_headers(text, MATRIX_HEADERS)
    if rows is None:
        errors.append("Matrix must preserve the exact six semantic columns")
        return first, {}
    if not rows:
        errors.append("Matrix must contain at least one row")
    if require_ready and "[ต้องค้นหลักฐาน:" in text:
        errors.append("Matrix contains unresolved [ต้องค้นหลักฐาน: ...] gaps")
    claims: dict[str, str] = {}
    for index, row in enumerate(rows, 1):
        anchor = f"OM-R{index:02d}"
        claim = row.get("Claim", "").strip()
        if not claim:
            errors.append(f"Matrix row {index} has no Claim")
        claims[anchor] = claim
    return first, claims


def validate_evidence(
    path: Path,
    outline: Path,
    errors: list[str],
    expected_modes: set[str],
    matrix: Path | None = None,
    matrix_claims: dict[str, str] | None = None,
) -> dict[str, str]:
    if not path.is_file():
        errors.append(f"Evidence Package does not exist: {path}")
        return {}
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    blocks = metadata_blocks(text)
    if not blocks:
        errors.append("Evidence Package is missing fenced YAML metadata")
        return {}
    first = blocks[0]
    all_meta = combined_metadata(blocks)
    mode = first.get("mode", "")
    status = first.get("status", "")
    if mode not in expected_modes:
        errors.append(f"Evidence mode {mode or '<missing>'} is not valid for this stage")
    required_status = "READY_FOR_MATRIX" if mode == "SCOPING" else "READY_FOR_HANDOFF"
    if status != required_status:
        errors.append(f"Evidence status must be {required_status} for {mode or 'the selected mode'}")
    if all_meta.get("validator_status") != required_status:
        errors.append(f"Evidence validator_status must be {required_status}")
    if not path_matches(first.get("source_outline", ""), outline, path):
        errors.append("Evidence source_outline does not match the current outline")
    if mode == "SCOPING" and first.get("source_matrix") not in {"-", "—", ""}:
        errors.append("SCOPING Evidence Package must not identify a source Matrix")
    if mode == "GAP_FILL":
        if matrix is None or not path_matches(first.get("source_matrix", ""), matrix, path):
            errors.append("GAP_FILL source_matrix does not match the current Matrix")
        claim_rows = table_with_headers(text, CLAIM_HEADERS)
        if claim_rows is None:
            errors.append("GAP_FILL package is missing the claim-evidence map")
        elif matrix_claims is not None:
            mapped: dict[str, str] = {}
            for row in claim_rows:
                anchor = row.get("Matrix anchor", "")
                if anchor in mapped:
                    errors.append(f"Duplicate claim mapping for {anchor}")
                mapped[anchor] = row.get("Fingerprint", "")
            for anchor, claim in matrix_claims.items():
                expected = fingerprint(claim)
                if anchor not in mapped:
                    errors.append(f"Matrix row {anchor} is missing from the claim-evidence map")
                elif mapped[anchor] != expected:
                    errors.append(f"Stale claim fingerprint for {anchor}: expected {expected}")
    return first


def validate_teaching_handoff(package: Path, approval: Path, errors: list[str]) -> dict[str, str]:
    if not package.is_dir():
        errors.append(f"Assessment package directory does not exist: {package}")
        return {}
    paths = {name: package / name for name in ASSESSMENT_FILES}
    for name, path in paths.items():
        if not path.is_file():
            errors.append(f"Missing assessment artifact: {name}")
    if errors:
        return {}
    metas = {
        name: (metadata_blocks(path.read_text(encoding="utf-8-sig", errors="replace")) or [{}])[0]
        for name, path in paths.items()
    }
    rule = metas["rule-register.md"]
    report = metas["assessment-report.md"]
    plan = metas["author-revision-plan.md"]
    for key in ("package_id", "assessment_id", "input_path", "input_sha256"):
        values = {meta.get(key, "") for meta in metas.values()}
        if "" in values or len(values) != 1:
            errors.append(f"Assessment artifacts disagree on {key}")
    if rule.get("document_type") != "TEACHING_HANDOUT":
        errors.append("Teaching-material revision requires document_type TEACHING_HANDOUT")
    if rule.get("task") not in {"ASSESS_CHAPTER", "ASSESS_MANUSCRIPT"}:
        errors.append("Teaching-material revision requires ASSESS_CHAPTER or ASSESS_MANUSCRIPT")
    if rule.get("package_status") == "BLOCKED_INPUT":
        errors.append("BLOCKED_INPUT assessment cannot authorize teaching-material revision")
    if plan.get("approval_status") != "PENDING_AUTHOR_APPROVAL":
        errors.append("Assessment plan must remain PENDING_AUTHOR_APPROVAL")
    source = existing_recorded_path(rule.get("input_path", ""), paths["rule-register.md"])
    digest = rule.get("input_sha256", "").lower()
    if source is None or not (source.is_file() or source.is_dir()):
        errors.append("Assessment input_path cannot be resolved")
    elif not re.fullmatch(r"[0-9a-f]{64}", digest):
        errors.append("Assessment input_sha256 is missing or malformed")
    elif input_sha256(source) != digest:
        errors.append("Assessment input fingerprint is stale")

    if not approval.is_file():
        errors.append(f"Teaching approval does not exist: {approval}")
        return rule
    approval_blocks = metadata_blocks(approval.read_text(encoding="utf-8-sig", errors="replace"))
    if not approval_blocks:
        errors.append("Teaching approval is missing fenced YAML metadata")
        return rule
    approved = approval_blocks[0]
    if approved.get("task") != "teaching-material-revision":
        errors.append("Teaching approval task must be teaching-material-revision")
    if approved.get("status") != "CHANGES_REQUESTED":
        errors.append("Teaching approval status must be CHANGES_REQUESTED")
    if approved.get("assessment_id") != rule.get("assessment_id"):
        errors.append("Teaching approval assessment_id does not match the package")
    if not path_matches(approved.get("assessment_package", ""), package, approval):
        errors.append("Teaching approval assessment_package does not match")
    if source is not None and not path_matches(approved.get("input_path", ""), source, approval):
        errors.append("Teaching approval input_path does not match assessed input")
    if approved.get("input_sha256", "").lower() != digest:
        errors.append("Teaching approval input_sha256 does not match the assessment")
    if not approved.get("approved_at") or not approved.get("approved_by"):
        errors.append("Teaching approval requires approved_at and approved_by")

    plan_text = paths["author-revision-plan.md"].read_text(encoding="utf-8-sig", errors="replace")
    revision_rows = table_with_headers(plan_text, REVISION_HEADERS)
    known_ids = {row.get("Revision ID", "") for row in (revision_rows or [])}
    approved_ids = {
        value.strip()
        for value in approved.get("approved_revision_ids", "").split(",")
        if value.strip()
    }
    if not approved_ids:
        errors.append("Teaching approval must name at least one approved RV-### ID")
    malformed = sorted(value for value in approved_ids if not re.fullmatch(r"RV-\d{3,}", value))
    if malformed:
        errors.append("Malformed approved revision IDs: " + ", ".join(malformed))
    unknown = sorted(approved_ids - known_ids)
    if unknown:
        errors.append("Unknown approved revision IDs: " + ", ".join(unknown))
    return rule


def validate(args: argparse.Namespace) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    outline = args.outline.resolve() if args.outline else None
    matrix = args.matrix.resolve() if args.matrix else None
    evidence = args.evidence_package.resolve() if args.evidence_package else None
    summary: dict[str, str] = {}

    if args.stage in {"matrix-build", "matrix-revise", "draft-chapter"}:
        if outline is None or not outline.is_file():
            errors.append("--outline must be an existing file for this stage")
        if evidence is None:
            errors.append("--evidence-package is required for this stage")
    if args.stage in {"matrix-revise", "draft-chapter"} and matrix is None:
        errors.append("--matrix is required for this stage")
    if errors:
        return {"valid": False, "stage": args.stage, "errors": errors, "warnings": warnings}

    if args.stage == "matrix-build":
        summary = validate_evidence(evidence, outline, errors, {"SCOPING"})
    elif args.stage == "matrix-revise":
        _, claims = validate_matrix(matrix, errors, require_ready=False)
        summary = validate_evidence(
            evidence, outline, errors, {"GAP_FILL"}, matrix=matrix, matrix_claims=claims
        )
    elif args.stage == "draft-chapter":
        matrix_meta, claims = validate_matrix(matrix, errors, require_ready=True)
        summary = validate_evidence(
            evidence,
            outline,
            errors,
            {"SCOPING", "GAP_FILL"},
            matrix=matrix,
            matrix_claims=claims,
        )
        if summary.get("mode") == "SCOPING":
            basis = matrix_meta.get("source_basis", "")
            package_id = summary.get("package_id", "")
            if package_id not in basis and str(evidence) not in basis:
                errors.append("Matrix source_basis must identify the SCOPING Evidence Package")
    else:
        if args.assessment_package is None or args.approval is None:
            errors.append("--assessment-package and --approval are required for teaching revision")
        else:
            summary = validate_teaching_handoff(
                args.assessment_package.resolve(), args.approval.resolve(), errors
            )

    return {
        "valid": not errors,
        "stage": args.stage,
        "mode": summary.get("mode"),
        "status": summary.get("status") or summary.get("package_status"),
        "assessment_id": summary.get("assessment_id"),
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=STAGES)
    parser.add_argument("--outline", type=Path)
    parser.add_argument("--matrix", type=Path)
    parser.add_argument("--evidence-package", type=Path, dest="evidence_package")
    parser.add_argument("--assessment-package", type=Path, dest="assessment_package")
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--json-output", type=Path)
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    result = validate(args)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload + "\n", encoding="utf-8")
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())

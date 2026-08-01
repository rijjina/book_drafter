#!/usr/bin/env python3
"""Validate one task, its document-type contract, prerequisites, and approvals."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


DOCUMENT_TYPES = ("teaching-notes", "book", "textbook")
TYPE_CONTRACT = {
    "teaching-notes": {
        "target": "A-equivalent",
        "rubric": "teaching-document-eight-criteria-plus-a-equivalent",
        "course": "yes",
    },
    "book": {"target": "A", "rubric": "book-level-a", "course": "no"},
    "textbook": {"target": "A", "rubric": "textbook-level-a", "course": "yes"},
}
TASKS = (
    "select-document-type",
    "project-setup",
    "refresh-sources",
    "draft-outline",
    "outline-qc",
    "revise-outline",
    "draft-chapter",
    "chapter-qc",
    "revise-chapter",
    "import-manuscript",
    "manuscript-qc",
    "revise-manuscript",
    "author-review",
    "final-qc",
    "produce-document",
)

ASSESSMENT_ADAPTER_TASKS = {
    "outline-qc",
    "chapter-qc",
    "manuscript-qc",
    "author-review",
    "final-qc",
}
ASSESSMENT_HANDOFF_TASKS = ASSESSMENT_ADAPTER_TASKS | {
    "revise-outline",
    "revise-chapter",
    "revise-manuscript",
}
ASSESSMENT_TASK_COMPATIBILITY = {
    "outline-qc": {"ASSESS_OUTLINE"},
    "chapter-qc": {"ASSESS_CHAPTER"},
    "manuscript-qc": {"ASSESS_MANUSCRIPT"},
    "author-review": {"ASSESS_OUTLINE", "ASSESS_CHAPTER", "ASSESS_MANUSCRIPT"},
    "final-qc": {"ASSESS_MANUSCRIPT"},
}
ASSESSMENT_PACKAGE_STATUSES = {
    "READY_FOR_AUTHOR_REVIEW",
    "NEEDS_RULE_REFRESH",
    "NEEDS_EVIDENCE",
    "BLOCKED_RULE_SELECTION",
    "BLOCKED_INPUT",
}

TASK_GROUP_REFERENCE = {
    "select-document-type": "references/workflow-project.md",
    "project-setup": "references/workflow-project.md",
    "refresh-sources": "references/workflow-project.md",
    "draft-outline": "references/workflow-project.md",
    "outline-qc": "references/workflow-project.md",
    "revise-outline": "references/workflow-project.md",
    "draft-chapter": "references/workflow-chapter.md",
    "chapter-qc": "references/workflow-chapter.md",
    "revise-chapter": "references/workflow-chapter.md",
    "import-manuscript": "references/workflow-manuscript.md",
    "manuscript-qc": "references/workflow-manuscript.md",
    "revise-manuscript": "references/workflow-manuscript.md",
    "author-review": "references/workflow-review.md",
    "final-qc": "references/workflow-final.md",
    "produce-document": "references/workflow-final.md",
}

EDITORIAL_TASKS = {
    "draft-outline",
    "revise-outline",
    "draft-chapter",
    "revise-chapter",
    "revise-manuscript",
    "final-qc",
    "produce-document",
}
STYLE_TASKS = {
    "import-manuscript",
    "revise-manuscript",
}
TYPE_QUALITY_TASKS = {
    "select-document-type",
    "project-setup",
    "draft-outline",
    "revise-outline",
    "draft-chapter",
    "revise-chapter",
    "revise-manuscript",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--task", required=True, choices=TASKS)
    parser.add_argument("--document-type", choices=DOCUMENT_TYPES)
    parser.add_argument("--input", type=Path, dest="input_path")
    parser.add_argument("--output", type=Path, dest="output_path")
    parser.add_argument(
        "--assessment-package",
        type=Path,
        dest="assessment_package",
        help="Validated assess-thai-academic-manuscript package directory",
    )
    parser.add_argument(
        "--outline-matrix",
        type=Path,
        dest="outline_matrix",
        help="Validated six-column Outline Matrix for draft-chapter",
    )
    parser.add_argument(
        "--evidence-package",
        type=Path,
        dest="evidence_package",
        help="Validated research-outline-evidence package for draft-chapter",
    )
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--chapter-count", type=int)
    parser.add_argument("--rebuild", action="store_true")
    return parser.parse_args()


def read_fields(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    fields: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw_line.strip()
        if line.startswith("-"):
            line = line[1:].strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip().lower()] = value.strip()
    return fields


def read_yaml_metadata(path: Path) -> dict[str, str]:
    """Read the first simple fenced YAML block used by assessment artifacts."""
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    match = re.search(r"```yaml\s*\r?\n(.*?)\r?\n```", text, re.S | re.I)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        item = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*?)\s*", raw_line)
        if not item:
            continue
        key, value = item.groups()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        fields[key] = value
    return fields


def read_all_yaml_metadata(path: Path) -> dict[str, str]:
    """Merge simple fenced YAML blocks in document order."""
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    fields: dict[str, str] = {}
    for body in re.findall(r"```yaml\s*\r?\n(.*?)\r?\n```", text, re.S | re.I):
        for raw_line in body.splitlines():
            item = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*?)\s*", raw_line)
            if not item:
                continue
            key, value = item.groups()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            fields[key] = value
    return fields


def recorded_path_matches(recorded: str, actual: Path, artifact: Path, root: Path) -> bool:
    if not recorded:
        return False
    value = Path(recorded)
    if value.is_absolute():
        return value.resolve() == actual.resolve()
    bases = [root, Path.cwd(), artifact.parent, *artifact.parents]
    return any((base / value).resolve() == actual.resolve() for base in bases)


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def markdown_table_rows(text: str, expected: list[str]) -> list[dict[str, str]] | None:
    lines = text.splitlines()
    for index in range(len(lines) - 1):
        if not lines[index].lstrip().startswith("|"):
            continue
        headers = split_markdown_row(lines[index])
        if headers != expected or not lines[index + 1].lstrip().startswith("|"):
            continue
        divider = split_markdown_row(lines[index + 1])
        if len(divider) != len(headers) or not all(
            re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in divider
        ):
            continue
        rows: list[dict[str, str]] = []
        cursor = index + 2
        while cursor < len(lines) and lines[cursor].lstrip().startswith("|"):
            cells = split_markdown_row(lines[cursor])
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
            cursor += 1
        return rows
    return None


def claim_fingerprint(claim: str) -> str:
    normalized = re.sub(r"\s+", " ", claim.strip()).lower()
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def require_evidence_matrix_handoff(
    blockers: list[str],
    checked: list[str],
    root: Path,
    matrix: Path | None,
    evidence: Path | None,
) -> None:
    """Enforce the research -> Matrix -> draft ownership boundary."""
    if matrix is None:
        blockers.append("--outline-matrix is required for draft-chapter.")
    if evidence is None:
        blockers.append("--evidence-package is required for draft-chapter.")
    if matrix is None or evidence is None:
        return
    matrix = matrix.resolve()
    evidence = evidence.resolve()
    outline = (root / "project" / "outline.md").resolve()
    if not matrix.is_file():
        blockers.append(f"Outline Matrix does not exist: {matrix}")
        return
    if not evidence.is_file():
        blockers.append(f"Evidence Package does not exist: {evidence}")
        return
    if not matrix.is_relative_to(root.resolve()):
        blockers.append(f"Outline Matrix must be inside the project root: {matrix}")
    research_root = (root / "research").resolve()
    if not evidence.is_relative_to(research_root):
        blockers.append(f"Evidence Package must be inside {research_root}: {evidence}")

    matrix_text = matrix.read_text(encoding="utf-8-sig", errors="replace")
    matrix_first = read_yaml_metadata(matrix)
    matrix_all = read_all_yaml_metadata(matrix)
    if matrix_first.get("status") != "READY_TO_DRAFT":
        blockers.append("Outline Matrix metadata status must be READY_TO_DRAFT.")
    if matrix_all.get("validator_status") != "READY_TO_DRAFT":
        blockers.append("Outline Matrix validator_status must be READY_TO_DRAFT.")
    expected_header = (
        "| ลำดับ | หัวข้อ | ผู้อ่านต้องทำได้ | Claim | หลักฐาน | ตัวอย่าง/กิจกรรม |"
    )
    if expected_header not in matrix_text:
        blockers.append("Outline Matrix must preserve the exact six semantic columns.")
    if "[ต้องค้นหลักฐาน:" in matrix_text:
        blockers.append("Outline Matrix contains unresolved evidence gaps.")
    matrix_headers = ["ลำดับ", "หัวข้อ", "ผู้อ่านต้องทำได้", "Claim", "หลักฐาน", "ตัวอย่าง/กิจกรรม"]
    matrix_rows = markdown_table_rows(matrix_text, matrix_headers)
    if matrix_rows is None or not matrix_rows:
        blockers.append("Outline Matrix must contain at least one valid six-column row.")
        matrix_rows = []

    evidence_first = read_yaml_metadata(evidence)
    evidence_all = read_all_yaml_metadata(evidence)
    mode = evidence_first.get("mode", "")
    expected_status = "READY_FOR_MATRIX" if mode == "SCOPING" else "READY_FOR_HANDOFF"
    if mode not in {"SCOPING", "GAP_FILL"}:
        blockers.append(f"Unsupported Evidence Package mode for drafting: {mode or '<missing>'}")
    if evidence_first.get("status") != expected_status:
        blockers.append(f"Evidence Package status must be {expected_status} for {mode or 'its mode'}.")
    if evidence_all.get("validator_status") != expected_status:
        blockers.append(f"Evidence validator_status must be {expected_status}.")
    if not recorded_path_matches(
        evidence_first.get("source_outline", ""), outline, evidence, root
    ):
        blockers.append("Evidence source_outline does not match the current project outline.")
    if mode == "GAP_FILL" and not recorded_path_matches(
        evidence_first.get("source_matrix", ""), matrix, evidence, root
    ):
        blockers.append("GAP_FILL source_matrix does not match --outline-matrix.")
    if mode == "GAP_FILL":
        claim_headers = [
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
        claim_rows = markdown_table_rows(
            evidence.read_text(encoding="utf-8-sig", errors="replace"), claim_headers
        )
        if claim_rows is None:
            blockers.append("GAP_FILL package is missing the claim-evidence map.")
        else:
            mapped = {row.get("Matrix anchor", ""): row.get("Fingerprint", "") for row in claim_rows}
            for index, row in enumerate(matrix_rows, 1):
                anchor = f"OM-R{index:02d}"
                expected = claim_fingerprint(row.get("Claim", ""))
                if anchor not in mapped:
                    blockers.append(f"GAP_FILL package is missing Matrix row {anchor}.")
                elif mapped[anchor] != expected:
                    blockers.append(f"GAP_FILL claim fingerprint is stale for {anchor}.")
    if mode == "SCOPING":
        basis = matrix_first.get("source_basis", "")
        package_id = evidence_first.get("package_id", "")
        if package_id not in basis and str(evidence) not in basis:
            blockers.append("Matrix source_basis must identify the SCOPING Evidence Package.")

    checked.append(f"draft-ready Outline Matrix contract: {matrix}")
    checked.append(f"verified Evidence Package contract: {evidence}")
    checked.append(
        "run research and Matrix validators plus orchestrate-thai-academic-writing/"
        "scripts/validate_workflow_handoff.py --stage draft-chapter before drafting"
    )


def input_sha256(path: Path) -> str:
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


def require_assessment_package(
    blockers: list[str],
    checked: list[str],
    root: Path,
    task: str,
    package: Path | None,
    expected_input: Path | None = None,
) -> None:
    """Check the cross-skill package contract without redoing academic judgment."""
    if package is None:
        blockers.append(f"--assessment-package is required for {task}.")
        return
    package = package.resolve()
    assessments_root = (root / "assessments").resolve()
    if not package.is_dir():
        blockers.append(f"Assessment package directory does not exist: {package}")
        return
    if not package.is_relative_to(assessments_root):
        blockers.append(f"Assessment package must be inside {assessments_root}: {package}")
    paths = {
        name: package / name
        for name in ("rule-register.md", "assessment-report.md", "author-revision-plan.md")
    }
    for name, path in paths.items():
        add_missing(blockers, path, f"assessment package artifact {name}")
    if any(not path.is_file() for path in paths.values()):
        return

    rule = read_yaml_metadata(paths["rule-register.md"])
    report = read_yaml_metadata(paths["assessment-report.md"])
    plan = read_yaml_metadata(paths["author-revision-plan.md"])
    for key in ("package_id", "assessment_id", "input_path", "input_sha256"):
        values = {rule.get(key, ""), report.get(key, ""), plan.get(key, "")}
        if "" in values or len(values) != 1:
            blockers.append(f"Assessment package artifacts disagree on metadata '{key}'.")
    for key in ("task", "mode", "rules_status", "package_status"):
        if not rule.get(key) or rule.get(key) != report.get(key):
            blockers.append(f"Assessment rule/report metadata disagree on '{key}'.")

    assessment_task = rule.get("task", "")
    if assessment_task not in ASSESSMENT_TASK_COMPATIBILITY.get(task, set()):
        allowed = ", ".join(sorted(ASSESSMENT_TASK_COMPATIBILITY.get(task, set())))
        blockers.append(
            f"Assessment task {assessment_task or '<missing>'} is incompatible with {task}; expected {allowed}."
        )
    package_status = rule.get("package_status", "")
    if package_status not in ASSESSMENT_PACKAGE_STATUSES:
        blockers.append(f"Unknown assessment package status: {package_status or '<missing>'}")
    elif package_status == "BLOCKED_INPUT":
        blockers.append("Assessment package is BLOCKED_INPUT and cannot be handed to the writer.")
    if plan.get("approval_status") != "PENDING_AUTHOR_APPROVAL":
        blockers.append("Assessment package must remain PENDING_AUTHOR_APPROVAL before writer handoff.")

    digest = rule.get("input_sha256", "").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        blockers.append("Assessment package input_sha256 is missing or malformed.")
    recorded_input = Path(rule.get("input_path", ""))
    if recorded_input and not recorded_input.is_absolute():
        recorded_input = (root / recorded_input).resolve()
    elif recorded_input:
        recorded_input = recorded_input.resolve()
    if expected_input is not None:
        expected_input = expected_input.resolve()
        if recorded_input and recorded_input != expected_input:
            blockers.append(
                f"Assessment input does not match task input: {recorded_input} != {expected_input}"
            )
        recorded_input = expected_input
    if not recorded_input or not recorded_input.exists() or not (
        recorded_input.is_file() or recorded_input.is_dir()
    ):
        blockers.append(f"Assessment source input does not exist: {recorded_input}")
    elif digest and input_sha256(recorded_input) != digest:
        blockers.append("Assessment package input fingerprint is stale; reassess before handoff.")

    checked.append(f"assessment package contract: {package}")
    checked.append(
        "run assess-thai-academic-manuscript/scripts/validate_assessment_package.py before writing the adapter record"
    )


def clean_choice(value: str) -> str:
    return value.split("|", 1)[0].strip()


def usable(value: str) -> bool:
    value = value.strip()
    return bool(value) and not any(token in value for token in ("[ต้อง", "[เติม", "[ยืนยัน"))


def normalize_task(value: str) -> tuple[str, int | None]:
    value = re.sub(r"\s+", " ", value.strip().lower())
    match = re.fullmatch(r"([a-z-]+)(?:\s+0*(\d+))?", value)
    if not match:
        return value, None
    return match.group(1), int(match.group(2)) if match.group(2) else None


def task_matches(actual: str, expected: str, chapter: int | None = None) -> bool:
    actual_task, actual_chapter = normalize_task(actual)
    return actual_task == expected and (chapter is None or actual_chapter == chapter)


def chapter_dir(root: Path, chapter: int) -> Path:
    return root / "chapters" / f"chapter-{chapter:02d}"


def add_missing(blockers: list[str], path: Path, label: str) -> None:
    if not path.is_file():
        blockers.append(f"Missing {label}: {path}")


def prevent_overwrite(blockers: list[str], paths: tuple[Path, ...], rebuild: bool) -> None:
    if rebuild:
        return
    for path in paths:
        if path.exists():
            blockers.append(f"Artifact already exists and rebuild was not requested: {path}")


def require_approval(
    blockers: list[str],
    path: Path,
    tasks: tuple[str, ...],
    status: str,
    chapter: int | None = None,
) -> None:
    record = read_fields(path)
    if not record:
        blockers.append(f"Missing approval record: {path}")
        return
    actual_status = clean_choice(record.get("status", "")).upper()
    actual_task = record.get("task", "")
    if actual_status != status:
        blockers.append(f"Approval at {path} has status {actual_status or 'EMPTY'}; expected {status}.")
    if not any(task_matches(actual_task, task, chapter) for task in tasks):
        expected = " or ".join(
            f"{task} {chapter:02d}" if chapter is not None else task for task in tasks
        )
        blockers.append(f"Approval at {path} is for {actual_task or 'EMPTY'}; expected {expected}.")


def validate_profile(
    blockers: list[str], root: Path, requested_type: str | None
) -> tuple[str | None, dict[str, str]]:
    profile_path = root / "project" / "manuscript-profile.md"
    profile = read_fields(profile_path)
    if not profile:
        blockers.append(f"Missing manuscript profile: {profile_path}")
        return None, {}
    actual_type = clean_choice(profile.get("document type", ""))
    if actual_type not in DOCUMENT_TYPES:
        blockers.append(f"Invalid or ambiguous document type in {profile_path}: {actual_type or 'EMPTY'}")
        return None, profile
    if requested_type is None:
        blockers.append("--document-type is required and must match the approved manuscript profile.")
    elif requested_type != actual_type:
        blockers.append(
            f"Requested document type {requested_type} conflicts with approved profile type {actual_type}."
        )
    contract = TYPE_CONTRACT[actual_type]
    actual_target = clean_choice(profile.get("target quality", ""))
    actual_rubric = clean_choice(profile.get("primary rubric", ""))
    actual_course = clean_choice(profile.get("course alignment required", "")).lower()
    if actual_target != contract["target"]:
        blockers.append(
            f"Profile target is {actual_target or 'EMPTY'}; {actual_type} requires {contract['target']}."
        )
    if actual_rubric != contract["rubric"]:
        blockers.append(
            f"Profile rubric is {actual_rubric or 'EMPTY'}; expected {contract['rubric']}."
        )
    if actual_course != contract["course"]:
        blockers.append(
            f"Profile course-alignment flag is {actual_course or 'EMPTY'}; expected {contract['course']}."
        )
    return actual_type, profile


def validate_type_evidence(blockers: list[str], root: Path, doc_type: str | None) -> None:
    brief_path = root / "project" / "project-brief.md"
    if not brief_path.is_file() or doc_type is None:
        return
    fields = read_fields(brief_path)
    text = brief_path.read_text(encoding="utf-8-sig", errors="replace")
    if doc_type == "book":
        for key in ("disciplinary scope", "central scholarly problem", "author viewpoint/contribution"):
            if not usable(fields.get(key, "")):
                blockers.append(f"Book project requires `{key}` in {brief_path}.")
        if re.search(r"(?im)^#{2,4}\s+Course Alignment\b", text):
            blockers.append("Book project must not use a Course Alignment section or require มคอ.3/CLO mapping.")
    else:
        for key in ("course code/name", "author teaching responsibility"):
            if not usable(fields.get(key, "")):
                blockers.append(f"{doc_type} requires `{key}` in {brief_path}.")


def require_outline_gate(blockers: list[str], root: Path) -> None:
    add_missing(blockers, root / "project" / "outline.md", "approved outline")
    require_approval(
        blockers,
        root / "project" / "approval.md",
        ("outline-qc", "revise-outline"),
        "APPROVED",
    )


def require_completed_chapters(blockers: list[str], root: Path, chapter_count: int | None) -> None:
    if chapter_count is None or chapter_count < 1:
        blockers.append("--chapter-count is required and must be positive for a new-draft final task.")
        return
    for number in range(1, chapter_count + 1):
        folder = chapter_dir(root, number)
        if not (folder / "revised.md").is_file() and not (folder / "draft.md").is_file():
            blockers.append(f"Missing chapter content for chapter {number:02d}: {folder}")
        require_approval(
            blockers,
            folder / "approval.md",
            ("chapter-qc", "revise-chapter"),
            "APPROVED",
            number,
        )


def chapter_folders(root: Path) -> list[Path]:
    chapters = root / "chapters"
    if not chapters.is_dir():
        return []
    return sorted(
        (
            path
            for path in chapters.iterdir()
            if path.is_dir() and re.fullmatch(r"chapter-\d+", path.name)
        ),
        key=lambda path: path.name,
    )


def require_imported_markdown(
    blockers: list[str], root: Path, require_revision: bool
) -> None:
    folders = chapter_folders(root)
    if not folders:
        blockers.append(f"Imported manuscript has no Markdown chapters: {root / 'chapters'}")
        return
    revised_count = 0
    for folder in folders:
        revised = folder / "revised.md"
        draft = folder / "draft.md"
        if revised.is_file():
            revised_count += 1
        elif not draft.is_file():
            blockers.append(f"Missing Markdown source candidate in {folder}")
    if require_revision and revised_count == 0:
        blockers.append(
            "Approved revise-manuscript route requires at least one chapter revised.md."
        )


def require_no_intermediate_binaries(
    blockers: list[str], root: Path, allow_final_docx: bool = False
) -> None:
    disallowed: list[Path] = []
    for directory in (root / "chapters", root / "final"):
        if not directory.is_dir():
            continue
        for pattern in ("*.docx", "*.pdf"):
            for path in directory.rglob(pattern):
                if allow_final_docx and path == root / "final" / "manuscript.docx":
                    continue
                disallowed.append(path)
    if disallowed:
        blockers.append(
            "Intermediate/final PDF or non-final DOCX artifacts are not permitted: "
            + ", ".join(str(path) for path in sorted(disallowed))
        )


def require_docx_confirmation(blockers: list[str], approval_path: Path) -> None:
    fields = read_fields(approval_path)
    deliverable = clean_choice(fields.get("deliverable", "")).upper()
    if deliverable != "DOCX":
        blockers.append(
            f"Approval at {approval_path} must record Deliverable: DOCX; "
            f"found {deliverable or 'EMPTY'}."
        )


def require_qc_target_declaration(
    blockers: list[str], qc_path: Path, doc_type: str, require_met: bool
) -> None:
    fields = read_fields(qc_path)
    if not fields:
        blockers.append(f"Missing or unreadable QC report: {qc_path}")
        return
    contract = TYPE_CONTRACT[doc_type]
    target = clean_choice(fields.get("target quality", ""))
    if target != contract["target"]:
        blockers.append(f"QC target is {target or 'EMPTY'}; expected {contract['target']} in {qc_path}.")
    if not require_met:
        return
    decision = clean_choice(fields.get("target decision", "")).upper()
    blocker_count = clean_choice(fields.get("blocker count", ""))
    if decision != "MEETS_TARGET":
        blockers.append(f"QC target decision must be MEETS_TARGET in {qc_path}.")
    if blocker_count != "0":
        blockers.append(f"QC blocker count must be 0 in {qc_path}; found {blocker_count or 'EMPTY'}.")
    if doc_type in {"book", "textbook"}:
        if clean_choice(fields.get("level a evidence", "")).upper() != "COMPLETE":
            blockers.append(f"Level A evidence must be COMPLETE in {qc_path}.")
    else:
        try:
            mean = float(clean_choice(fields.get("teaching criteria mean", "")))
            minimum = int(clean_choice(fields.get("teaching minimum criterion", "")))
        except ValueError:
            blockers.append(f"Teaching A-equivalent scores are missing or invalid in {qc_path}.")
        else:
            if not 3.26 <= mean <= 4.00:
                blockers.append(f"Teaching criteria mean {mean:.2f} is below A-equivalent 3.26.")
            if minimum < 3:
                blockers.append(f"Teaching minimum criterion {minimum} is below A-equivalent minimum 3.")
        if clean_choice(fields.get("a-equivalent evidence", "")).upper() != "COMPLETE":
            blockers.append(f"A-equivalent evidence must be COMPLETE in {qc_path}.")


def is_imported_route(root: Path) -> bool:
    return (root / "source" / "original-manuscript.docx").is_file()


def quality_reference(document_type: str | None) -> str | None:
    if document_type == "teaching-notes":
        return "references/teaching-document-criteria.md"
    if document_type in {"book", "textbook"}:
        return "references/document-types-and-quality.md"
    return None


def task_reference_route(
    task: str,
    document_type: str | None,
    root: Path,
    chapter: int | None,
    input_path: Path | None,
) -> tuple[list[str], list[str]]:
    """Return the minimal deterministic contract plus genuinely conditional reads."""
    required: list[str] = []
    if task not in {"author-review", "select-document-type"}:
        required.append("references/core-production-contract.md")
    required.append(TASK_GROUP_REFERENCE[task])

    type_reference = quality_reference(document_type)
    if type_reference and task in TYPE_QUALITY_TASKS:
        required.append(type_reference)
    if task in EDITORIAL_TASKS:
        required.append("references/editorial-standards.md")
    if task in ASSESSMENT_HANDOFF_TASKS:
        required.append("references/assessment-integration.md")
    if task == "draft-chapter":
        required.append("references/evidence-matrix-integration.md")

    style_relevant = task in STYLE_TASKS or (
        task == "draft-chapter" and input_path is not None
    )
    if task in {"chapter-qc", "revise-chapter"} and chapter:
        style_relevant = style_relevant or (
            chapter_dir(root, chapter) / "draft-audit.md"
        ).is_file()
    if task == "author-review":
        style_relevant = (
            (root / "source" / "style-profile.md").is_file()
            or any(root.glob("chapters/chapter-*/style-profile.md"))
        )
    if style_relevant:
        required.append("references/style-preservation.md")

    if task in {"project-setup", "refresh-sources"}:
        required.append("references/source-map.md")
    if task == "refresh-sources":
        required.append("references/source-manifest.json")

    conditional = [
        "references/reference-index.md — only when the routed contract does not resolve a quality/source question",
    ]
    if "references/source-map.md" not in required:
        conditional.append(
            "references/source-map.md — only for authority conflicts, disputed rules, or exact-page verification"
        )
    if "references/source-manifest.json" not in required:
        conditional.append(
            "references/source-manifest.json — only the relevant source record/page segment during source verification"
        )
    return list(dict.fromkeys(required)), conditional


def task_artifact_contract(
    task: str,
    root: Path,
    chapter: int | None,
    input_path: Path | None,
    output_path: Path | None,
    assessment_package: Path | None,
    outline_matrix: Path | None,
    evidence_package: Path | None,
) -> tuple[list[str], list[str]]:
    """Describe task inputs and owned outputs without mutating the project."""
    project = root / "project"
    source = root / "source"
    final = root / "final"
    approval = project / "approval.md"
    inputs: dict[str, list[Path]] = {
        "select-document-type": [],
        "project-setup": [project / "manuscript-profile.md", project / "type-approval.md"],
        "refresh-sources": [project / "governing-standard.md", project / "type-approval.md"],
        "draft-outline": [project / "project-brief.md", project / "governing-standard.md", approval],
        "outline-qc": [project / "outline.md", project / "governing-standard.md", approval, assessment_package],
        "revise-outline": [project / "outline.md", project / "outline-qc.md", approval],
        "import-manuscript": [project / "type-approval.md"] + ([input_path] if input_path else []),
        "manuscript-qc": [source / "original-manuscript.docx", source / "import-report.md", source / "approval.md", assessment_package],
        "revise-manuscript": [source / "original-manuscript.docx", final / "manuscript-qc.md", final / "approval.md"],
        "author-review": [project / "type-approval.md", assessment_package] + ([input_path] if input_path else []),
        "final-qc": [project / "manuscript-profile.md", assessment_package],
        "produce-document": [final / "preflight-report.md", final / "final-qc.md", final / "approval.md"],
    }
    outputs: dict[str, list[Path]] = {
        "select-document-type": [project / "manuscript-profile.md", project / "type-approval.md"],
        "project-setup": [project / "project-brief.md", project / "governing-standard.md", approval],
        "refresh-sources": [project / "governing-standard.md", approval],
        "draft-outline": [project / "outline.md", approval],
        "outline-qc": [project / "outline-qc.md", approval],
        "revise-outline": [project / "outline.md", approval],
        "import-manuscript": [source / "original-manuscript.docx", source / "import-report.md", source / "style-profile.md", source / "approval.md"],
        "manuscript-qc": [final / "manuscript-preflight-report.md", final / "manuscript-qc.md", final / "approval.md"],
        "revise-manuscript": [root / "chapters" / "chapter-*" / "revised.md", root / "chapters" / "chapter-*" / "revision.md", final / "revision-log.md", final / "approval.md"],
        "author-review": [output_path] if output_path else [],
        "final-qc": [final / "preflight-report.md", final / "final-qc.md", final / "approval.md"],
        "produce-document": [final / "manuscript.docx"],
    }

    if task in {"draft-chapter", "chapter-qc", "revise-chapter"}:
        if chapter is None:
            return [], []
        folder = chapter_dir(root, chapter)
        inputs[task] = [project / "outline.md", project / "approval.md"]
        if task == "chapter-qc":
            inputs[task] += [folder / "draft.md", folder / "sources-and-rights.md", folder / "approval.md", assessment_package]
            outputs[task] = [folder / "chapter-qc.md", folder / "approval.md"]
        elif task == "revise-chapter":
            inputs[task] += [folder / "draft.md", folder / "chapter-qc.md", folder / "sources-and-rights.md", folder / "approval.md"]
            outputs[task] = [folder / "revised.md", folder / "revision.md", folder / "sources-and-rights.md", folder / "approval.md"]
        else:
            inputs[task] += [outline_matrix, evidence_package]
            if input_path is not None:
                inputs[task].append(input_path)
                outputs[task] = [
                    folder / "style-profile.md",
                    folder / "draft-audit.md",
                    folder / "draft.md",
                    folder / "sources-and-rights.md",
                    folder / "approval.md",
                ]
            else:
                outputs[task] = [folder / "draft.md", folder / "sources-and-rights.md", folder / "approval.md"]

    return (
        [str(path) for path in inputs.get(task, []) if path is not None],
        [str(path) for path in outputs.get(task, []) if path is not None],
    )


def require_import_style_profile(blockers: list[str], checked: list[str], source: Path) -> None:
    """Require profiles promised by v1.1 imports while allowing pre-profile projects."""
    profile = source / "style-profile.md"
    report = source / "import-report.md"
    if profile.is_file():
        fields = read_fields(profile)
        if clean_choice(fields.get("extraction status", "")).upper() not in {"COMPLETE", "SPARSE"}:
            blockers.append(f"Style profile is unreadable or incomplete: {profile}")
        else:
            checked.append("imported manuscript style profile")
        return
    report_text = report.read_text(encoding="utf-8-sig", errors="replace") if report.is_file() else ""
    if re.search(r"(?im)^-\s*Style profile\s*:", report_text):
        blockers.append(f"Import report declares a style profile but the artifact is missing: {profile}")
    else:
        checked.append("legacy imported project without style profile; preserve style directly from original manuscript")


def require_chapter_style_profile(
    blockers: list[str], checked: list[str], folder: Path
) -> None:
    """Validate a user-draft profile while allowing pre-1.1 chapter artifacts."""
    audit = folder / "draft-audit.md"
    if not audit.is_file():
        return
    profile = folder / "style-profile.md"
    if profile.is_file():
        fields = read_fields(profile)
        if clean_choice(fields.get("extraction status", "")).upper() not in {
            "COMPLETE",
            "SPARSE",
        }:
            blockers.append(f"Style profile is unreadable or incomplete: {profile}")
        else:
            checked.append("user-draft chapter style profile")
        return
    audit_text = audit.read_text(encoding="utf-8-sig", errors="replace")
    if re.search(r"(?im)^-\s*Style profile\s*:", audit_text):
        blockers.append(f"Draft audit declares a style profile but the artifact is missing: {profile}")
    else:
        checked.append(
            "legacy user-draft chapter without style profile; derive baseline from source recorded in draft audit"
        )


def check_gate(args: argparse.Namespace) -> dict[str, object]:
    root = args.project_root.resolve()
    project = root / "project"
    source = root / "source"
    final = root / "final"
    blockers: list[str] = []
    checked: list[str] = []
    doc_type: str | None = None

    if args.task == "select-document-type":
        if args.document_type is None:
            blockers.append("--document-type is required for select-document-type.")
        prevent_overwrite(
            blockers,
            (project / "manuscript-profile.md", project / "type-approval.md"),
            args.rebuild,
        )
        checked.append("document type selection and profile ownership")
    else:
        doc_type, _ = validate_profile(blockers, root, args.document_type)
        require_approval(
            blockers,
            project / "type-approval.md",
            ("select-document-type",),
            "APPROVED",
        )
        validate_type_evidence(blockers, root, doc_type)
        checked.append("approved document-type and fixed-quality contract")

    chapter_tasks = {"draft-chapter", "chapter-qc", "revise-chapter"}
    if args.task in chapter_tasks and (args.chapter is None or args.chapter < 1):
        blockers.append("--chapter is required and must be positive for chapter tasks.")

    if args.task == "project-setup":
        prevent_overwrite(
            blockers,
            (project / "project-brief.md", project / "governing-standard.md"),
            args.rebuild,
        )

    elif args.task == "refresh-sources":
        checked.append("explicit refresh task selection")

    elif args.task == "draft-outline":
        add_missing(blockers, project / "project-brief.md", "project brief")
        add_missing(blockers, project / "governing-standard.md", "governing standard")
        require_approval(
            blockers, project / "approval.md", ("project-setup", "refresh-sources"), "APPROVED"
        )
        prevent_overwrite(blockers, (project / "outline.md",), args.rebuild)

    elif args.task == "outline-qc":
        add_missing(blockers, project / "governing-standard.md", "governing standard")
        add_missing(blockers, project / "outline.md", "outline")
        require_approval(
            blockers, project / "approval.md", ("draft-outline", "revise-outline"), "APPROVED"
        )
        require_assessment_package(
            blockers,
            checked,
            root,
            args.task,
            args.assessment_package,
            project / "outline.md",
        )
        prevent_overwrite(blockers, (project / "outline-qc.md",), args.rebuild)

    elif args.task == "revise-outline":
        add_missing(blockers, project / "outline.md", "outline")
        add_missing(blockers, project / "outline-qc.md", "outline QC")
        require_approval(blockers, project / "approval.md", ("outline-qc",), "CHANGES_REQUESTED")

    elif args.task == "draft-chapter" and args.chapter is not None:
        require_outline_gate(blockers, root)
        require_evidence_matrix_handoff(
            blockers,
            checked,
            root,
            args.outline_matrix,
            args.evidence_package,
        )
        if args.chapter > 1:
            previous = args.chapter - 1
            require_approval(
                blockers,
                chapter_dir(root, previous) / "approval.md",
                ("chapter-qc", "revise-chapter"),
                "APPROVED",
                previous,
            )
        folder = chapter_dir(root, args.chapter)
        user_draft = args.input_path
        if user_draft is not None:
            user_draft = user_draft.resolve()
            if not user_draft.is_file():
                blockers.append(f"User draft input does not exist: {user_draft}")
            elif user_draft.suffix.lower() not in {".docx", ".md", ".txt", ".pdf"}:
                blockers.append(f"Unsupported user draft format: {user_draft}")
            chapters_root = (root / "chapters").resolve()
            final_root = (root / "final").resolve()
            if user_draft.is_relative_to(chapters_root) or user_draft.is_relative_to(final_root):
                blockers.append(
                    f"Generated output cannot be declared as a user draft: {user_draft}"
                )
            checked.append("user-supplied draft identified; diagnostic audit and targeted refinement allowed")
            checked.append(
                f"create {folder / 'style-profile.md'} from the user source before editing"
            )
            if (folder / "chapter-qc.md").exists() or (folder / "revision.md").exists():
                blockers.append(
                    f"Chapter {args.chapter:02d} already entered formal QC/revision; use revise-chapter instead of draft-chapter."
                )
        else:
            prevent_overwrite(
                blockers,
                (folder / "draft.md", folder / "sources-and-rights.md", folder / "draft-audit.md"),
                args.rebuild,
            )

    elif args.task == "chapter-qc" and args.chapter is not None:
        folder = chapter_dir(root, args.chapter)
        add_missing(blockers, folder / "draft.md", "chapter draft")
        add_missing(blockers, folder / "sources-and-rights.md", "source and rights ledger")
        require_approval(
            blockers, folder / "approval.md", ("draft-chapter",), "APPROVED", args.chapter
        )
        require_chapter_style_profile(blockers, checked, folder)
        require_assessment_package(
            blockers,
            checked,
            root,
            args.task,
            args.assessment_package,
            folder / "draft.md",
        )
        prevent_overwrite(blockers, (folder / "chapter-qc.md",), args.rebuild)

    elif args.task == "revise-chapter" and args.chapter is not None:
        folder = chapter_dir(root, args.chapter)
        add_missing(blockers, folder / "draft.md", "chapter draft")
        add_missing(blockers, folder / "chapter-qc.md", "chapter QC")
        add_missing(blockers, folder / "sources-and-rights.md", "source and rights ledger")
        require_approval(
            blockers, folder / "approval.md", ("chapter-qc",), "CHANGES_REQUESTED", args.chapter
        )
        require_chapter_style_profile(blockers, checked, folder)
        prevent_overwrite(
            blockers,
            (folder / "revised.md", folder / "revision.md"),
            args.rebuild,
        )

    elif args.task == "import-manuscript":
        if args.input_path is None:
            blockers.append("--input is required for import-manuscript.")
        elif not args.input_path.is_file() or args.input_path.suffix.lower() != ".docx":
            blockers.append(f"Import input must be an existing DOCX file: {args.input_path}")
        prevent_overwrite(
            blockers,
            (
                source / "original-manuscript.docx",
                source / "import-report.md",
                source / "style-profile.md",
            ),
            args.rebuild,
        )

    elif args.task == "manuscript-qc":
        add_missing(blockers, source / "original-manuscript.docx", "original manuscript")
        add_missing(blockers, source / "import-report.md", "import report")
        require_approval(blockers, source / "approval.md", ("import-manuscript",), "APPROVED")
        require_import_style_profile(blockers, checked, source)
        require_assessment_package(
            blockers,
            checked,
            root,
            args.task,
            args.assessment_package,
            source / "original-manuscript.docx",
        )
        prevent_overwrite(
            blockers,
            (final / "manuscript-preflight-report.md", final / "manuscript-qc.md"),
            args.rebuild,
        )

    elif args.task == "revise-manuscript":
        add_missing(blockers, source / "original-manuscript.docx", "original manuscript")
        add_missing(blockers, final / "manuscript-qc.md", "manuscript QC")
        require_approval(blockers, final / "approval.md", ("manuscript-qc",), "CHANGES_REQUESTED")
        require_import_style_profile(blockers, checked, source)
        if doc_type:
            require_qc_target_declaration(blockers, final / "manuscript-qc.md", doc_type, False)
        existing_revision_outputs = [final / "revision-log.md"]
        for folder in chapter_folders(root):
            existing_revision_outputs.extend((folder / "revised.md", folder / "revision.md"))
        prevent_overwrite(blockers, tuple(existing_revision_outputs), args.rebuild)

    elif args.task == "author-review":
        if args.chapter is not None and args.chapter < 1:
            blockers.append("--chapter must be positive when supplied for author-review.")
        if args.input_path is None:
            blockers.append("--input is required for author-review.")
        else:
            review_input = args.input_path.resolve()
            if not review_input.is_file():
                blockers.append(f"Review input does not exist: {review_input}")
            elif review_input.suffix.lower() not in {".docx", ".md", ".txt", ".pdf"}:
                blockers.append(f"Unsupported author-review format: {review_input}")
            else:
                checked.append("author manuscript is read-only")
                require_assessment_package(
                    blockers,
                    checked,
                    root,
                    args.task,
                    args.assessment_package,
                    review_input,
                )
                if args.output_path is None:
                    checked.append(
                        "response-only assessment handoff; no legacy pointer or approval artifact will be written"
                    )
                else:
                    review_output = args.output_path.resolve()
                    reviews_root = (root / "reviews").resolve()
                    if review_output.suffix.lower() != ".md":
                        blockers.append(f"Author-review output must be Markdown: {review_output}")
                    if not review_output.is_relative_to(reviews_root):
                        blockers.append(
                            f"Author-review output must be inside {reviews_root}: {review_output}"
                        )
                    prevent_overwrite(blockers, (review_output,), args.rebuild)
                    checked.append(
                        "approval-free assessment pointer; may be written without creating or changing approval artifacts"
                    )

    elif args.task == "final-qc":
        if is_imported_route(root):
            add_missing(blockers, source / "original-manuscript.docx", "original manuscript")
            require_import_style_profile(blockers, checked, source)
            record = read_fields(final / "approval.md")
            approval_task = normalize_task(record.get("task", ""))[0]
            if approval_task == "revise-manuscript":
                require_approval(blockers, final / "approval.md", ("revise-manuscript",), "APPROVED")
                add_missing(blockers, final / "revision-log.md", "manuscript revision log")
                require_imported_markdown(blockers, root, require_revision=True)
            elif approval_task == "manuscript-qc":
                require_approval(blockers, final / "approval.md", ("manuscript-qc",), "APPROVED")
                require_imported_markdown(blockers, root, require_revision=False)
                if doc_type:
                    require_qc_target_declaration(
                        blockers, final / "manuscript-qc.md", doc_type, True
                    )
            else:
                blockers.append(
                    "Imported manuscript final QC requires approved manuscript-qc or revise-manuscript."
                )
        else:
            require_outline_gate(blockers, root)
            require_completed_chapters(blockers, root, args.chapter_count)
        require_assessment_package(
            blockers,
            checked,
            root,
            args.task,
            args.assessment_package,
            None,
        )
        prevent_overwrite(
            blockers, (final / "preflight-report.md", final / "final-qc.md"), args.rebuild
        )
        require_no_intermediate_binaries(blockers, root)

    elif args.task == "produce-document":
        if is_imported_route(root):
            require_import_style_profile(blockers, checked, source)
            add_missing(blockers, source / "original-manuscript.docx", "manuscript source")
            require_imported_markdown(blockers, root, require_revision=False)
        else:
            require_outline_gate(blockers, root)
            require_completed_chapters(blockers, root, args.chapter_count)
        add_missing(blockers, final / "preflight-report.md", "preflight report")
        add_missing(blockers, final / "final-qc.md", "final QC")
        require_approval(blockers, final / "approval.md", ("final-qc",), "APPROVED")
        require_docx_confirmation(blockers, final / "approval.md")
        if doc_type:
            require_qc_target_declaration(blockers, final / "final-qc.md", doc_type, True)
        require_no_intermediate_binaries(blockers, root, allow_final_docx=True)
        prevent_overwrite(blockers, (final / "manuscript.docx",), args.rebuild)

    required_references, conditional_references = task_reference_route(
        args.task,
        doc_type or args.document_type,
        root,
        args.chapter,
        args.input_path,
    )
    inputs, owned_outputs = task_artifact_contract(
        args.task,
        root,
        args.chapter,
        args.input_path,
        args.output_path,
        args.assessment_package,
        args.outline_matrix,
        args.evidence_package,
    )

    return {
        "allowed": not blockers,
        "task": args.task,
        "document_type": args.document_type,
        "chapter": args.chapter,
        "assessment_package": str(args.assessment_package.resolve()) if args.assessment_package else None,
        "outline_matrix": str(args.outline_matrix.resolve()) if args.outline_matrix else None,
        "evidence_package": str(args.evidence_package.resolve()) if args.evidence_package else None,
        "project_root": str(root),
        "required_references": required_references,
        "conditional_references": conditional_references,
        "inputs": inputs,
        "owned_outputs": owned_outputs,
        "checked": checked,
        "blockers": blockers,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    result = check_gate(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["allowed"] else 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate one task, its document-type contract, prerequisites, and approvals."""

from __future__ import annotations

import argparse
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
    "final-qc",
    "produce-document",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--task", required=True, choices=TASKS)
    parser.add_argument("--document-type", choices=DOCUMENT_TYPES)
    parser.add_argument("--input", type=Path, dest="input_path")
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
        if not (folder / "revision.md").is_file() and not (folder / "draft.md").is_file():
            blockers.append(f"Missing chapter content for chapter {number:02d}: {folder}")
        require_approval(
            blockers,
            folder / "approval.md",
            ("chapter-qc", "revise-chapter"),
            "APPROVED",
            number,
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
        prevent_overwrite(blockers, (project / "outline-qc.md",), args.rebuild)

    elif args.task == "revise-outline":
        add_missing(blockers, project / "outline.md", "outline")
        add_missing(blockers, project / "outline-qc.md", "outline QC")
        require_approval(blockers, project / "approval.md", ("outline-qc",), "CHANGES_REQUESTED")

    elif args.task == "draft-chapter" and args.chapter is not None:
        require_outline_gate(blockers, root)
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
        prevent_overwrite(blockers, (folder / "chapter-qc.md",), args.rebuild)

    elif args.task == "revise-chapter" and args.chapter is not None:
        folder = chapter_dir(root, args.chapter)
        add_missing(blockers, folder / "draft.md", "chapter draft")
        add_missing(blockers, folder / "chapter-qc.md", "chapter QC")
        add_missing(blockers, folder / "sources-and-rights.md", "source and rights ledger")
        require_approval(
            blockers, folder / "approval.md", ("chapter-qc",), "CHANGES_REQUESTED", args.chapter
        )

    elif args.task == "import-manuscript":
        if args.input_path is None:
            blockers.append("--input is required for import-manuscript.")
        elif not args.input_path.is_file() or args.input_path.suffix.lower() != ".docx":
            blockers.append(f"Import input must be an existing DOCX file: {args.input_path}")
        prevent_overwrite(
            blockers,
            (source / "original-manuscript.docx", source / "import-report.md"),
            args.rebuild,
        )

    elif args.task == "manuscript-qc":
        add_missing(blockers, source / "original-manuscript.docx", "original manuscript")
        add_missing(blockers, source / "import-report.md", "import report")
        require_approval(blockers, source / "approval.md", ("import-manuscript",), "APPROVED")
        prevent_overwrite(
            blockers,
            (final / "manuscript-preflight-report.md", final / "manuscript-qc.md"),
            args.rebuild,
        )

    elif args.task == "revise-manuscript":
        add_missing(blockers, source / "original-manuscript.docx", "original manuscript")
        add_missing(blockers, final / "manuscript-qc.md", "manuscript QC")
        require_approval(blockers, final / "approval.md", ("manuscript-qc",), "CHANGES_REQUESTED")
        if doc_type:
            require_qc_target_declaration(blockers, final / "manuscript-qc.md", doc_type, False)

    elif args.task == "final-qc":
        if is_imported_route(root):
            add_missing(blockers, source / "original-manuscript.docx", "original manuscript")
            record = read_fields(final / "approval.md")
            approval_task = normalize_task(record.get("task", ""))[0]
            if approval_task == "revise-manuscript":
                require_approval(blockers, final / "approval.md", ("revise-manuscript",), "APPROVED")
                add_missing(blockers, final / "revised-manuscript.docx", "revised manuscript")
            elif approval_task == "manuscript-qc":
                require_approval(blockers, final / "approval.md", ("manuscript-qc",), "APPROVED")
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
        prevent_overwrite(
            blockers, (final / "preflight-report.md", final / "final-qc.md"), args.rebuild
        )

    elif args.task == "produce-document":
        if is_imported_route(root):
            if not (final / "revised-manuscript.docx").is_file():
                add_missing(blockers, source / "original-manuscript.docx", "manuscript source")
        else:
            require_outline_gate(blockers, root)
            require_completed_chapters(blockers, root, args.chapter_count)
        add_missing(blockers, final / "preflight-report.md", "preflight report")
        add_missing(blockers, final / "final-qc.md", "final QC")
        require_approval(blockers, final / "approval.md", ("final-qc",), "APPROVED")
        if doc_type:
            require_qc_target_declaration(blockers, final / "final-qc.md", doc_type, True)
        prevent_overwrite(
            blockers, (final / "manuscript.docx", final / "manuscript.pdf"), args.rebuild
        )

    return {
        "allowed": not blockers,
        "task": args.task,
        "document_type": args.document_type,
        "chapter": args.chapter,
        "project_root": str(root),
        "checked": checked,
        "blockers": blockers,
    }


def main() -> int:
    args = parse_args()
    result = check_gate(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["allowed"] else 2


if __name__ == "__main__":
    sys.exit(main())

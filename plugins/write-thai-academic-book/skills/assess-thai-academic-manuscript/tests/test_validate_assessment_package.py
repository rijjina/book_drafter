from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from validate_assessment_package import input_sha256, validate  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_package(
    folder: Path,
    source: Path,
    *,
    task: str = "ASSESS_MANUSCRIPT",
    mode: str = "REFERENCE_ONLY",
    document_type: str = "BOOK",
    package_status: str | None = None,
    rules_status: str | None = None,
    institution: str = "-",
    target_rank: str = "-",
    field: str = "-",
    route: str = "-",
    filing_date: str = "-",
    verification: str | None = None,
    disposition: str | None = None,
    exact_locator: str = "PDF p. 3, clause 2",
    rule_location: str = "../reference for skill/ตำราหนังสือ.pdf",
    criterion_status: str = "PARTIAL",
    criterion_severity: str = "MAJOR",
    include_revision: bool = True,
    approval_status: str = "PENDING_AUTHOR_APPROVAL",
    numeric_scores: str = "NONE",
    extra_report_text: str = "",
    recorded_hash: str | None = None,
) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    digest = recorded_hash or sha256(source)
    package_status = package_status or (
        "NEEDS_RULE_REFRESH" if mode == "REFERENCE_ONLY" else "READY_FOR_AUTHOR_REVIEW"
    )
    rules_status = rules_status or ("REFERENCE_ONLY" if mode == "REFERENCE_ONLY" else "CURRENT")
    verification = verification or (
        "VERIFIED_LOCAL_SOURCE" if mode == "REFERENCE_ONLY" else "VERIFIED_OFFICIAL_TEXT"
    )
    disposition = disposition or ("ADVISORY" if mode == "REFERENCE_ONLY" else "IN_FORCE")
    if mode == "CURRENT_RULES":
        search_row = (
            "| Q001 | official institutional web | institution academic rank regulation | "
            "2026-08-01 | 4 | Opened current regulation and amendment chain |"
        )
    else:
        search_row = ""

    rule_text = f"""# Rule Register

```yaml
schema_version: "1.0"
package_id: "demo-assessment"
project_id: "demo"
assessment_id: "demo-assessment"
task: "{task}"
mode: "{mode}"
document_type: "{document_type}"
institution: "{institution}"
target_rank: "{target_rank}"
field: "{field}"
submission_route: "{route}"
intended_filing_date: "{filing_date}"
assessment_cutoff: "2026-08-01"
rules_status: "{rules_status}"
package_status: "{package_status}"
input_path: "{source}"
input_sha256: "{digest}"
```

## Search log

| Query ID | Channel | Query | Searched on | Results screened | Decision/notes |
| --- | --- | --- | --- | ---: | --- |
{search_row}

## Rule ledger

| Rule ID | Issuing authority | Title | Rank/route | Effective/superseded | URL/path | Exact locator | Verification | Rights/use | Status/disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R001 | Example University | Academic work regulation | all declared ranks and routes | effective 2026-01-01 | {rule_location} | {exact_locator} | {verification} | quote minimally; local assessment use | {disposition} |

## Authority conflicts and transition notes

- None found in the assessed source set.

## Currentness conclusion

The recorded status is limited to the sources and cutoff above.
"""
    author_action = "Add the missing synthesis and cite verified evidence" if criterion_status in {"PARTIAL", "FAIL"} else "-"
    report_text = f"""# Assessment Report

```yaml
schema_version: "1.0"
package_id: "demo-assessment"
assessment_id: "demo-assessment"
task: "{task}"
scope_id: "manuscript"
input_path: "{source}"
input_sha256: "{digest}"
mode: "{mode}"
rules_status: "{rules_status}"
package_status: "{package_status}"
numeric_scores: "{numeric_scores}"
```

## Context and retained strengths

- Scope: whole work
- Strengths to retain: the central concept is visible at Heading 1, paragraph 1.
- Limits of this assessment: route currentness follows the declared rule status.

## Criteria assessment

| Criterion ID | Scope anchor | Manuscript locator | Rule ID/locator | Status | Severity | Finding/evidence | Limitation/conflict | Author action | Verification condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CR-001 | whole-work synthesis | Heading 1, paragraph 2 | R001 @ {exact_locator} | {criterion_status} | {criterion_severity} | The paragraph states a central claim but provides only one source. | Evidence breadth remains limited. | {author_action} | Recheck the revised paragraph and cited full text. |

## Official numeric scores

| Metric | Score/result | Rule ID/locator | Evidence basis | Status |
| --- | --- | --- | --- | --- |

## Overall synthesis

The work is assessable, with the rule limitations recorded above.

{extra_report_text}
"""
    revision_row = (
        f"| RV-001 | CR-001 | {criterion_severity} | none | Heading 1, paragraph 2 | "
        "Add bounded synthesis from verified sources. | Paragraph distinguishes evidence, interpretation, and limitation. |"
        if include_revision
        else ""
    )
    plan_text = f"""# Author Revision Plan

```yaml
schema_version: "1.0"
package_id: "demo-assessment"
assessment_id: "demo-assessment"
input_path: "{source}"
input_sha256: "{digest}"
approval_status: "{approval_status}"
```

## Revision sequence

| Revision ID | Criterion ID | Priority | Dependency | Affected locator | Proposed action | Acceptance check |
| --- | --- | --- | --- | --- | --- | --- |
{revision_row}

## Decisions required from the author

- Confirm whether the proposed scope is acceptable.

## Handoff

- Package ID: demo-assessment
- Approved revision IDs: PENDING
- Writing skill may revise: no
"""
    (folder / "rule-register.md").write_text(rule_text, encoding="utf-8")
    (folder / "assessment-report.md").write_text(report_text, encoding="utf-8")
    (folder / "author-revision-plan.md").write_text(plan_text, encoding="utf-8")
    return folder


class AssessmentPackageValidationTests(unittest.TestCase):
    def make_source(self, temp_dir: str) -> Path:
        source = Path(temp_dir) / "manuscript.md"
        source.write_text("# Main heading\n\nA central claim requiring synthesis.\n", encoding="utf-8")
        return source

    def test_reference_only_package_is_valid_and_provisional(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(Path(temp_dir) / "package", source)
            result = validate(package, source)
            self.assertTrue(result["valid"], result)
            self.assertEqual(result["package_status"], "NEEDS_RULE_REFRESH")
            self.assertEqual(result["counts"]["queries"], 0)

    def test_current_route_package_requires_and_accepts_complete_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(
                Path(temp_dir) / "package",
                source,
                task="ASSESS_ROUTE_READINESS",
                mode="CURRENT_RULES",
                institution="Example University",
                target_rank="ASSOCIATE_PROFESSOR",
                field="Microbiology",
                route="normal method",
                filing_date="2026-12-01",
                rule_location="https://example.ac.th/official/rule-2026.pdf",
            )
            result = validate(package, source)
            self.assertTrue(result["valid"], result)
            self.assertEqual(result["rules_status"], "CURRENT")

    def test_missing_route_requires_blocked_rule_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(
                Path(temp_dir) / "package",
                source,
                task="ASSESS_ROUTE_READINESS",
                mode="CURRENT_RULES",
                package_status="READY_FOR_AUTHOR_REVIEW",
                rule_location="https://example.ac.th/official/rule.pdf",
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("BLOCKED_RULE_SELECTION" in item for item in result["errors"]))

    def test_reference_only_route_may_report_blocked_rule_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(
                Path(temp_dir) / "package",
                source,
                task="ASSESS_ROUTE_READINESS",
                package_status="BLOCKED_RULE_SELECTION",
            )
            result = validate(package, source)
            self.assertTrue(result["valid"], result)

    def test_metadata_only_cannot_support_current_rule(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(
                Path(temp_dir) / "package",
                source,
                mode="CURRENT_RULES",
                institution="Example University",
                target_rank="ASSISTANT_PROFESSOR",
                field="Education",
                route="normal method",
                filing_date="2026-12-01",
                verification="METADATA_ONLY",
                rule_location="https://example.ac.th/rule",
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("metadata-only" in item for item in result["errors"]))

    def test_superseded_rule_cannot_support_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(
                Path(temp_dir) / "package", source, disposition="SUPERSEDED"
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("superseded Rule ID" in item for item in result["errors"]))

    def test_duplicate_rule_location_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(Path(temp_dir) / "package", source)
            register = package / "rule-register.md"
            text = register.read_text(encoding="utf-8")
            duplicate = (
                "| R002 | Example University | Duplicate record | all routes | effective 2026-01-01 | "
                "../reference for skill/ตำราหนังสือ.pdf | PDF p. 4, clause 3 | "
                "VERIFIED_LOCAL_SOURCE | local assessment use | ADVISORY |"
            )
            register.write_text(
                text.replace("\n\n## Authority conflicts", f"\n{duplicate}\n\n## Authority conflicts"),
                encoding="utf-8",
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("Duplicate rule URL/path" in item for item in result["errors"]))

    def test_vague_exact_locator_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(Path(temp_dir) / "package", source, exact_locator="-")
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("exact locator is missing or vague" in item for item in result["errors"]))

    def test_stale_fingerprint_is_rejected_without_modifying_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            before = source.read_bytes()
            package = write_package(
                Path(temp_dir) / "package", source, recorded_hash="0" * 64
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("fingerprint is stale" in item for item in result["errors"]))
            self.assertEqual(source.read_bytes(), before)

    def test_outline_matrix_is_not_modified_by_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            matrix = Path(temp_dir) / "outline-matrix.md"
            matrix.write_text("| ลำดับ | Claim | หลักฐาน |\n|---:|---|---|\n| 1 | claim | pending |\n", encoding="utf-8")
            matrix_before = matrix.read_bytes()
            package = write_package(Path(temp_dir) / "package", source)
            result = validate(package, source)
            self.assertTrue(result["valid"], result)
            self.assertEqual(matrix.read_bytes(), matrix_before)

    def test_multi_file_manuscript_directory_has_stable_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manuscript = Path(temp_dir) / "chapters"
            (manuscript / "chapter-01").mkdir(parents=True)
            (manuscript / "chapter-02").mkdir(parents=True)
            first = manuscript / "chapter-01" / "draft.md"
            second = manuscript / "chapter-02" / "revised.md"
            first.write_text("# Chapter 1\n\nContent one.\n", encoding="utf-8")
            second.write_text("# Chapter 2\n\nContent two.\n", encoding="utf-8")
            digest = input_sha256(manuscript)
            package = write_package(
                Path(temp_dir) / "package", manuscript, recorded_hash=digest
            )
            result = validate(package, manuscript)
            self.assertTrue(result["valid"], result)
            second.write_text("# Chapter 2\n\nChanged content.\n", encoding="utf-8")
            stale = validate(package, manuscript)
            self.assertFalse(stale["valid"])
            self.assertTrue(any("fingerprint is stale" in item for item in stale["errors"]))

    def test_partial_or_fail_requires_revision_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(Path(temp_dir) / "package", source, include_revision=False)
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("missing from revision plan" in item for item in result["errors"]))

    def test_readiness_score_language_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(
                Path(temp_dir) / "package",
                source,
                extra_report_text="Readiness score: 82%",
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("readiness score" in item for item in result["errors"]))

    def test_thai_readiness_percentage_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(
                Path(temp_dir) / "package",
                source,
                extra_report_text="เปอร์เซ็นต์ความพร้อม: 82%",
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("readiness score" in item for item in result["errors"]))

    def test_package_rejects_extra_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(Path(temp_dir) / "package", source)
            (package / "notes.md").write_text("not part of the contract", encoding="utf-8")
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("unexpected files" in item for item in result["errors"]))

    def test_recorded_input_path_must_match_cli_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(Path(temp_dir) / "package", source)
            for artifact in package.glob("*.md"):
                text = artifact.read_text(encoding="utf-8")
                artifact.write_text(
                    text.replace(str(source), str(Path(temp_dir) / "different.md")),
                    encoding="utf-8",
                )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("input_path does not match" in item for item in result["errors"]))

    def test_reference_only_rejects_search_log_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(Path(temp_dir) / "package", source)
            register = package / "rule-register.md"
            text = register.read_text(encoding="utf-8")
            row = (
                "| Q001 | web | simulated current search | 2026-08-01 | 1 | included |\n"
            )
            register.write_text(
                text.replace("\n\n## Rule ledger", f"\n{row}\n## Rule ledger"),
                encoding="utf-8",
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("must not contain Search log" in item for item in result["errors"]))

    def test_quoted_markdown_locator_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(Path(temp_dir) / "package", source)
            report = package / "assessment-report.md"
            report.write_text(
                report.read_text(encoding="utf-8").replace(
                    "Heading 1, paragraph 2", "heading `Does not exist`"
                ),
                encoding="utf-8",
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("quoted anchor not found" in item for item in result["errors"]))

    def test_revision_priority_must_match_criterion_severity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(Path(temp_dir) / "package", source)
            plan = package / "author-revision-plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "| RV-001 | CR-001 | MAJOR |", "| RV-001 | CR-001 | MINOR |"
                ),
                encoding="utf-8",
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("Priority must match" in item for item in result["errors"]))

    def test_author_approval_must_remain_pending(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(
                Path(temp_dir) / "package", source, approval_status="APPROVED"
            )
            result = validate(package, source)
            self.assertFalse(result["valid"])
            self.assertTrue(any("PENDING_AUTHOR_APPROVAL" in item for item in result["errors"]))

    def test_project_profile_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(
                Path(temp_dir) / "package",
                source,
                mode="CURRENT_RULES",
                institution="Example University",
                target_rank="PROFESSOR",
                field="Education",
                route="normal method",
                filing_date="2026-12-01",
                rule_location="https://example.ac.th/official/rule.pdf",
            )
            profile = Path(temp_dir) / "profile.md"
            profile.write_text("- Institution: Different University\n", encoding="utf-8")
            result = validate(package, source, profile)
            self.assertFalse(result["valid"])
            self.assertTrue(any("Project profile mismatch" in item for item in result["errors"]))

    def test_cli_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            package = write_package(Path(temp_dir) / "package", source)
            report = Path(temp_dir) / "validation" / "report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "validate_assessment_package.py"),
                    "--package",
                    str(package),
                    "--input",
                    str(source),
                    "--json-output",
                    str(report),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])

    def test_all_supported_document_types_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = self.make_source(temp_dir)
            for document_type in ("BOOK", "TEXTBOOK", "TEACHING_HANDOUT", "TEACHING_NOTES"):
                with self.subTest(document_type=document_type):
                    package = write_package(
                        Path(temp_dir) / document_type.lower(), source, document_type=document_type
                    )
                    result = validate(package, source)
                    self.assertTrue(result["valid"], result)


if __name__ == "__main__":
    unittest.main()

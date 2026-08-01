from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "validate_workflow_handoff.py"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from validate_workflow_handoff import fingerprint, validate  # noqa: E402


def options(stage: str, **values: object) -> argparse.Namespace:
    defaults = {
        "stage": stage,
        "outline": None,
        "matrix": None,
        "evidence_package": None,
        "assessment_package": None,
        "approval": None,
        "json_output": None,
    }
    defaults.update(values)
    return argparse.Namespace(**defaults)


def write_outline(root: Path) -> Path:
    path = root / "project" / "outline.md"
    path.parent.mkdir(parents=True)
    path.write_text("# Outline\n\n## Chapter 1\n", encoding="utf-8")
    return path


def write_scoping(root: Path, outline: Path) -> Path:
    path = root / "research" / "book" / "evidence-package.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        f"""# Evidence Package

```yaml
package_id: "demo-book"
mode: "SCOPING"
project_id: "demo"
scope_id: "book"
source_outline: "{outline}"
source_matrix: "-"
status: "READY_FOR_MATRIX"
```

## Validation

```yaml
validator_status: "READY_FOR_MATRIX"
```
""",
        encoding="utf-8",
    )
    return path


def write_matrix(root: Path, evidence: Path, claim: str = "หลักฐานที่ดีจำกัดข้อสรุปให้เหมาะสม") -> Path:
    path = root / "project" / "outline-matrix.md"
    path.write_text(
        f"""# Outline Matrix

```yaml
title: "Demo"
level: "CHAPTER"
main_question: "เหตุใดหลักฐานจึงสำคัญ"
intended_reader: "นักศึกษา"
scope: "บทที่ 1"
exclusions: "นอกสาขา"
source_basis: "{evidence}"
status: "READY_TO_DRAFT"
```

| ลำดับ | หัวข้อ | ผู้อ่านต้องทำได้ | Claim | หลักฐาน | ตัวอย่าง/กิจกรรม |
|---:|---|---|---|---|---|
| 1 | หลักฐาน | ประเมินหลักฐานได้ | {claim} | S001 @ p. 2 | วิจารณ์กรณีศึกษา |

## Validation

```yaml
validator_status: "READY_TO_DRAFT"
human_subject_review: "PENDING"
```
""",
        encoding="utf-8",
    )
    return path


def write_gap_fill(root: Path, outline: Path, matrix: Path, claim: str) -> Path:
    path = root / "research" / "chapter-01" / "evidence-package.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        f"""# Evidence Package

```yaml
package_id: "demo-chapter-01"
mode: "GAP_FILL"
project_id: "demo"
scope_id: "chapter-01"
source_outline: "{outline}"
source_matrix: "{matrix}"
status: "READY_FOR_HANDOFF"
```

## Claim-evidence map

| Claim ID | Outline anchor | Matrix anchor | Claim | Fingerprint | Evidence | Relation | Synthesis/limits | Sufficiency | Gap/action |
|---|---|---|---|---|---|---|---|---|---|
| C001 | OUT-CH01 | OM-R01 | {claim} | {fingerprint(claim)} | S001 @ p. 2 | S001=SUPPORTS | จำกัดข้อสรุปแล้ว | ADEQUATE | - |

## Validation

```yaml
validator_status: "READY_FOR_HANDOFF"
```
""",
        encoding="utf-8",
    )
    return path


def write_teaching_assessment(root: Path) -> tuple[Path, Path, str]:
    source = root / "teaching-handout.md"
    source.write_text("# เอกสารประกอบการสอน\n\nเนื้อหา\n", encoding="utf-8")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    package = root / "assessments" / "handout-01"
    package.mkdir(parents=True)
    common = f'''schema_version: "1.0"
package_id: "handout-01"
assessment_id: "handout-01"
input_path: "{source}"
input_sha256: "{digest}"'''
    (package / "rule-register.md").write_text(
        f'''# Rule Register

```yaml
{common}
task: "ASSESS_MANUSCRIPT"
document_type: "TEACHING_HANDOUT"
package_status: "NEEDS_RULE_REFRESH"
```
''',
        encoding="utf-8",
    )
    (package / "assessment-report.md").write_text(
        f'''# Assessment Report

```yaml
{common}
task: "ASSESS_MANUSCRIPT"
package_status: "NEEDS_RULE_REFRESH"
```
''',
        encoding="utf-8",
    )
    (package / "author-revision-plan.md").write_text(
        f'''# Author Revision Plan

```yaml
{common}
approval_status: "PENDING_AUTHOR_APPROVAL"
```

## Revision sequence

| Revision ID | Criterion ID | Priority | Dependency | Affected locator | Proposed action | Acceptance check |
|---|---|---|---|---|---|---|
| RV-001 | CR-001 | MAJOR | none | heading 1 | เพิ่มหลักฐาน | ตรวจแหล่งได้ |
''',
        encoding="utf-8",
    )
    return package, source, digest


def write_teaching_approval(root: Path, package: Path, source: Path, digest: str, ids: str = "RV-001") -> Path:
    path = root / "teaching-approval.md"
    path.write_text(
        f'''# Approval

```yaml
schema_version: "1.0"
task: "teaching-material-revision"
status: "CHANGES_REQUESTED"
assessment_id: "handout-01"
assessment_package: "{package}"
input_path: "{source}"
input_sha256: "{digest}"
approved_revision_ids: "{ids}"
approved_at: "2026-08-02"
approved_by: "Author"
```
''',
        encoding="utf-8",
    )
    return path


class WorkflowHandoffTests(unittest.TestCase):
    def test_scoping_package_allows_matrix_build(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outline = write_outline(root)
            evidence = write_scoping(root, outline)
            result = validate(options("matrix-build", outline=outline, evidence_package=evidence))
            self.assertTrue(result["valid"], result)

    def test_ready_matrix_and_scoping_package_allow_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outline = write_outline(root)
            evidence = write_scoping(root, outline)
            matrix = write_matrix(root, evidence)
            result = validate(
                options(
                    "draft-chapter",
                    outline=outline,
                    matrix=matrix,
                    evidence_package=evidence,
                )
            )
            self.assertTrue(result["valid"], result)

    def test_draft_rejects_non_ready_matrix_and_evidence_gap(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outline = write_outline(root)
            evidence = write_scoping(root, outline)
            matrix = write_matrix(root, evidence)
            text = matrix.read_text(encoding="utf-8")
            matrix.write_text(
                text.replace('status: "READY_TO_DRAFT"', 'status: "NEEDS_EVIDENCE"', 1).replace(
                    "S001 @ p. 2", "[ต้องค้นหลักฐาน: งานวิจัยปฐมภูมิ]"
                ),
                encoding="utf-8",
            )
            result = validate(
                options("draft-chapter", outline=outline, matrix=matrix, evidence_package=evidence)
            )
            self.assertFalse(result["valid"])
            self.assertTrue(any("READY_TO_DRAFT" in item for item in result["errors"]))
            self.assertTrue(any("ต้องค้นหลักฐาน" in item for item in result["errors"]))

    def test_gap_fill_handoff_accepts_current_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outline = write_outline(root)
            seed = write_scoping(root, outline)
            claim = "หลักฐานที่ดีจำกัดข้อสรุปให้เหมาะสม"
            matrix = write_matrix(root, seed, claim)
            matrix.write_text(
                matrix.read_text(encoding="utf-8")
                .replace("READY_TO_DRAFT", "NEEDS_EVIDENCE")
                .replace("S001 @ p. 2", "[ต้องค้นหลักฐาน: งานวิจัยปฐมภูมิ]"),
                encoding="utf-8",
            )
            evidence = write_gap_fill(root, outline, matrix, claim)
            result = validate(
                options("matrix-revise", outline=outline, matrix=matrix, evidence_package=evidence)
            )
            self.assertTrue(result["valid"], result)

    def test_gap_fill_rejects_stale_claim_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outline = write_outline(root)
            seed = write_scoping(root, outline)
            original = "หลักฐานที่ดีจำกัดข้อสรุปให้เหมาะสม"
            matrix = write_matrix(root, seed, "Claim ที่เปลี่ยนภายหลัง")
            evidence = write_gap_fill(root, outline, matrix, original)
            result = validate(
                options("matrix-revise", outline=outline, matrix=matrix, evidence_package=evidence)
            )
            self.assertFalse(result["valid"])
            self.assertTrue(any("Stale claim fingerprint" in item for item in result["errors"]))

    def test_teaching_revision_requires_matching_approved_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package, source, digest = write_teaching_assessment(root)
            approval = write_teaching_approval(root, package, source, digest)
            result = validate(
                options(
                    "teaching-material-revision",
                    assessment_package=package,
                    approval=approval,
                )
            )
            self.assertTrue(result["valid"], result)

    def test_teaching_revision_rejects_unknown_id_and_stale_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package, source, digest = write_teaching_assessment(root)
            approval = write_teaching_approval(root, package, source, digest, "RV-999")
            source.write_text("changed", encoding="utf-8")
            result = validate(
                options(
                    "teaching-material-revision",
                    assessment_package=package,
                    approval=approval,
                )
            )
            self.assertFalse(result["valid"])
            self.assertTrue(any("fingerprint is stale" in item for item in result["errors"]))
            self.assertTrue(any("Unknown approved revision" in item for item in result["errors"]))

    def test_cli_writes_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outline = write_outline(root)
            evidence = write_scoping(root, outline)
            report = root / "validation" / "report.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--stage",
                    "matrix-build",
                    "--outline",
                    str(outline),
                    "--evidence-package",
                    str(evidence),
                    "--json-output",
                    str(report),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["valid"])


if __name__ == "__main__":
    unittest.main()

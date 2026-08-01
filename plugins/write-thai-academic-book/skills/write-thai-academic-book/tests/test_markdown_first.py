from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
GATE = SKILL_ROOT / "scripts" / "check_task_gate.py"


def run_gate(root: Path, task: str, *extra: str) -> tuple[int, dict]:
    result = subprocess.run(
        [
            sys.executable,
            str(GATE),
            "--project-root",
            str(root),
            "--task",
            task,
            "--document-type",
            "book",
            *extra,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.returncode, json.loads(result.stdout)


def write_profile(root: Path) -> None:
    project = root / "project"
    project.mkdir(parents=True)
    (project / "manuscript-profile.md").write_text(
        "\n".join(
            (
                "- Document type: book",
                "- Target quality: A",
                "- Primary rubric: book-level-a",
                "- Course alignment required: no",
            )
        ),
        encoding="utf-8",
    )
    (project / "type-approval.md").write_text(
        "- Task: select-document-type\n- Status: APPROVED\n", encoding="utf-8"
    )


def write_draft_handoff(root: Path) -> tuple[Path, Path]:
    outline = root / "project" / "outline.md"
    evidence = root / "research" / "book" / "evidence-package.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(
        f'''# Evidence Package

```yaml
package_id: "demo-book"
mode: "SCOPING"
source_outline: "{outline}"
source_matrix: "-"
status: "READY_FOR_MATRIX"
```

```yaml
validator_status: "READY_FOR_MATRIX"
```
''',
        encoding="utf-8",
    )
    matrix = root / "project" / "outline-matrix.md"
    matrix.write_text(
        f'''# Outline Matrix

```yaml
title: "Demo"
level: "CHAPTER"
main_question: "คำถามหลัก"
intended_reader: "ผู้อ่าน"
scope: "บทที่ 1"
exclusions: "นอกขอบเขต"
source_basis: "{evidence}"
status: "READY_TO_DRAFT"
```

| ลำดับ | หัวข้อ | ผู้อ่านต้องทำได้ | Claim | หลักฐาน | ตัวอย่าง/กิจกรรม |
|---:|---|---|---|---|---|
| 1 | แนวคิด | อธิบายได้ | หลักฐานจำกัดข้อสรุป | S001 @ p. 2 | วิจารณ์กรณีศึกษา |

```yaml
validator_status: "READY_TO_DRAFT"
```
''',
        encoding="utf-8",
    )
    return matrix, evidence


def write_gap_fill_handoff(root: Path, claim: str) -> tuple[Path, Path]:
    seed_matrix, _ = write_draft_handoff(root)
    digest = hashlib.sha256(claim.lower().encode("utf-8")).hexdigest()[:12]
    outline = root / "project" / "outline.md"
    evidence = root / "research" / "chapter-01" / "evidence-package.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(
        f'''# Evidence Package

```yaml
package_id: "demo-chapter"
mode: "GAP_FILL"
source_outline: "{outline}"
source_matrix: "{seed_matrix}"
status: "READY_FOR_HANDOFF"
```

| Claim ID | Outline anchor | Matrix anchor | Claim | Fingerprint | Evidence | Relation | Synthesis/limits | Sufficiency | Gap/action |
|---|---|---|---|---|---|---|---|---|---|
| C001 | OUT-CH01 | OM-R01 | {claim} | sha256:{digest} | S001 @ p. 2 | S001=SUPPORTS | จำกัดข้อสรุป | ADEQUATE | - |

```yaml
validator_status: "READY_FOR_HANDOFF"
```
''',
        encoding="utf-8",
    )
    seed_matrix.write_text(
        seed_matrix.read_text(encoding="utf-8").replace(
            "หลักฐานจำกัดข้อสรุป", claim
        ),
        encoding="utf-8",
    )
    return seed_matrix, evidence


def write_final_ready_project(root: Path, deliverable: str | None) -> None:
    write_profile(root)
    project = root / "project"
    (project / "outline.md").write_text("# Outline\n", encoding="utf-8")
    (project / "approval.md").write_text(
        "- Task: outline-qc\n- Status: APPROVED\n", encoding="utf-8"
    )
    chapter = root / "chapters" / "chapter-01"
    chapter.mkdir(parents=True)
    (chapter / "draft.md").write_text("# บทที่ 1\n\nเนื้อหา\n", encoding="utf-8")
    (chapter / "approval.md").write_text(
        "- Task: chapter-qc 01\n- Status: APPROVED\n", encoding="utf-8"
    )
    final = root / "final"
    final.mkdir()
    (final / "preflight-report.md").write_text("# Preflight\n", encoding="utf-8")
    (final / "final-qc.md").write_text(
        "\n".join(
            (
                "- Target quality: A",
                "- Target decision: MEETS_TARGET",
                "- Blocker count: 0",
                "- Level A evidence: COMPLETE",
            )
        ),
        encoding="utf-8",
    )
    approval = "- Task: final-qc\n- Status: APPROVED\n"
    if deliverable is not None:
        approval += f"- Deliverable: {deliverable}\n"
    (final / "approval.md").write_text(approval, encoding="utf-8")


class MarkdownFirstGateTests(unittest.TestCase):
    def test_gate_returns_minimal_reference_and_artifact_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            code, payload = run_gate(root, "select-document-type")
            self.assertEqual(code, 0, payload)
            self.assertEqual(
                payload["required_references"],
                [
                    "references/workflow-project.md",
                    "references/document-types-and-quality.md",
                ],
            )
            self.assertNotIn(
                "references/workflow-contract.md", payload["required_references"]
            )
            self.assertTrue(
                any(path.endswith("project\\manuscript-profile.md") or path.endswith("project/manuscript-profile.md") for path in payload["owned_outputs"])
            )

    def test_user_draft_route_adds_style_contract_and_owned_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_profile(root)
            project = root / "project"
            (project / "outline.md").write_text("# Outline\n", encoding="utf-8")
            (project / "approval.md").write_text(
                "- Task: outline-qc\n- Status: APPROVED\n", encoding="utf-8"
            )
            source = root / "author-chapter.md"
            source.write_text("# บทที่ 1\n\nต้นฉบับผู้เขียน\n", encoding="utf-8")
            matrix, evidence = write_draft_handoff(root)
            code, payload = run_gate(
                root,
                "draft-chapter",
                "--chapter",
                "1",
                "--input",
                str(source),
                "--outline-matrix",
                str(matrix),
                "--evidence-package",
                str(evidence),
            )
            self.assertEqual(code, 0, payload)
            self.assertIn(
                "references/style-preservation.md", payload["required_references"]
            )
            self.assertTrue(
                any(path.endswith("style-profile.md") for path in payload["owned_outputs"])
            )
            self.assertTrue(
                any(path.endswith("draft-audit.md") for path in payload["owned_outputs"])
            )
            self.assertIn(str(matrix), payload["inputs"])
            self.assertIn(str(evidence), payload["inputs"])

    def test_draft_chapter_requires_ready_matrix_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_profile(root)
            project = root / "project"
            (project / "outline.md").write_text("# Outline\n", encoding="utf-8")
            (project / "approval.md").write_text(
                "- Task: outline-qc\n- Status: APPROVED\n", encoding="utf-8"
            )
            code, payload = run_gate(root, "draft-chapter", "--chapter", "1")
            self.assertEqual(code, 2)
            self.assertTrue(any("--outline-matrix is required" in item for item in payload["blockers"]))
            self.assertTrue(any("--evidence-package is required" in item for item in payload["blockers"]))

            matrix, evidence = write_draft_handoff(root)
            matrix.write_text(
                matrix.read_text(encoding="utf-8").replace(
                    'status: "READY_TO_DRAFT"', 'status: "NEEDS_EVIDENCE"', 1
                ),
                encoding="utf-8",
            )
            code, payload = run_gate(
                root,
                "draft-chapter",
                "--chapter",
                "1",
                "--outline-matrix",
                str(matrix),
                "--evidence-package",
                str(evidence),
            )
            self.assertEqual(code, 2)
            self.assertTrue(any("metadata status must be READY_TO_DRAFT" in item for item in payload["blockers"]))

    def test_draft_chapter_rejects_stale_gap_fill_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_profile(root)
            project = root / "project"
            (project / "outline.md").write_text("# Outline\n", encoding="utf-8")
            (project / "approval.md").write_text(
                "- Task: outline-qc\n- Status: APPROVED\n", encoding="utf-8"
            )
            matrix, evidence = write_gap_fill_handoff(root, "Claim เดิมที่มีหลักฐาน")
            matrix.write_text(
                matrix.read_text(encoding="utf-8").replace(
                    "Claim เดิมที่มีหลักฐาน", "Claim ใหม่หลังเปลี่ยน Matrix"
                ),
                encoding="utf-8",
            )
            code, payload = run_gate(
                root,
                "draft-chapter",
                "--chapter",
                "1",
                "--outline-matrix",
                str(matrix),
                "--evidence-package",
                str(evidence),
            )
            self.assertEqual(code, 2)
            self.assertTrue(any("fingerprint is stale" in item for item in payload["blockers"]))

    def test_revise_chapter_owns_revised_markdown_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_profile(root)
            chapter = root / "chapters" / "chapter-01"
            chapter.mkdir(parents=True)
            (chapter / "draft.md").write_text("ร่างเดิม", encoding="utf-8")
            (chapter / "chapter-qc.md").write_text("# QC\n", encoding="utf-8")
            (chapter / "sources-and-rights.md").write_text("# Sources\n", encoding="utf-8")
            (chapter / "approval.md").write_text(
                "- Task: chapter-qc 01\n- Status: CHANGES_REQUESTED\n",
                encoding="utf-8",
            )

            code, payload = run_gate(root, "revise-chapter", "--chapter", "1")
            self.assertEqual(code, 0, payload)
            (chapter / "revised.md").write_text("ฉบับแก้", encoding="utf-8")
            (chapter / "revision.md").write_text("# Audit\n", encoding="utf-8")
            code, payload = run_gate(root, "revise-chapter", "--chapter", "1")
            self.assertEqual(code, 2)
            self.assertTrue(
                any("revised.md" in blocker for blocker in payload["blockers"])
            )

    def test_production_requires_explicit_docx_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_final_ready_project(root, deliverable=None)
            code, payload = run_gate(
                root, "produce-document", "--chapter-count", "1"
            )
            self.assertEqual(code, 2)
            self.assertTrue(
                any("Deliverable: DOCX" in blocker for blocker in payload["blockers"])
            )

            (root / "final" / "approval.md").write_text(
                "- Task: final-qc\n- Status: APPROVED\n- Deliverable: DOCX\n",
                encoding="utf-8",
            )
            code, payload = run_gate(
                root, "produce-document", "--chapter-count", "1"
            )
            self.assertEqual(code, 0, payload)

    def test_intermediate_pdf_blocks_final_production(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_final_ready_project(root, deliverable="DOCX")
            (root / "final" / "manuscript.pdf").write_bytes(b"%PDF-1.4")
            code, payload = run_gate(
                root, "produce-document", "--chapter-count", "1"
            )
            self.assertEqual(code, 2)
            self.assertTrue(
                any("not permitted" in blocker for blocker in payload["blockers"])
            )


if __name__ == "__main__":
    unittest.main()

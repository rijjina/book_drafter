from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
GATE = SKILL_ROOT / "scripts" / "check_task_gate.py"


def write_profile(root: Path) -> None:
    project = root / "project"
    project.mkdir(parents=True, exist_ok=True)
    (project / "manuscript-profile.md").write_text(
        "- Document type: book\n- Target quality: A\n- Primary rubric: book-level-a\n- Course alignment required: no\n",
        encoding="utf-8",
    )
    (project / "type-approval.md").write_text(
        "- Task: select-document-type\n- Status: APPROVED\n", encoding="utf-8"
    )


def write_package(
    root: Path,
    source: Path,
    assessment_task: str = "ASSESS_OUTLINE",
    package_status: str = "NEEDS_RULE_REFRESH",
    digest: str | None = None,
) -> Path:
    package = root / "assessments" / "adapter-test"
    package.mkdir(parents=True, exist_ok=True)
    if digest is None:
        hasher = hashlib.sha256()
        if source.is_file():
            hasher.update(source.read_bytes())
        else:
            for item in sorted(path for path in source.rglob("*") if path.is_file()):
                relative = item.relative_to(source).as_posix().encode("utf-8")
                hasher.update(len(relative).to_bytes(4, "big"))
                hasher.update(relative)
                hasher.update(item.stat().st_size.to_bytes(8, "big"))
                hasher.update(item.read_bytes())
        digest = hasher.hexdigest()
    common = f'''schema_version: "1.0"
package_id: "adapter-test"
assessment_id: "adapter-test"
input_path: "{source.resolve()}"
input_sha256: "{digest}"'''
    for filename, extra in (
        (
            "rule-register.md",
            f'''task: "{assessment_task}"
mode: "REFERENCE_ONLY"
rules_status: "REFERENCE_ONLY"
package_status: "{package_status}"''',
        ),
        (
            "assessment-report.md",
            f'''task: "{assessment_task}"
mode: "REFERENCE_ONLY"
rules_status: "REFERENCE_ONLY"
package_status: "{package_status}"''',
        ),
        ("author-revision-plan.md", 'approval_status: "PENDING_AUTHOR_APPROVAL"'),
    ):
        (package / filename).write_text(
            f"# Adapter fixture\n\n```yaml\n{common}\n{extra}\n```\n", encoding="utf-8"
        )
    return package


def run_gate(root: Path, *args: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(GATE), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.returncode, json.loads(result.stdout)


class AssessmentAdapterTests(unittest.TestCase):
    def ready_outline(self, temp_dir: str) -> tuple[Path, Path]:
        root = Path(temp_dir) / "project"
        write_profile(root)
        project = root / "project"
        outline = project / "outline.md"
        outline.write_text("# Outline\n\n- Chapter 1\n", encoding="utf-8")
        (project / "governing-standard.md").write_text("# Standard\n", encoding="utf-8")
        (project / "approval.md").write_text(
            "- Task: draft-outline\n- Status: APPROVED\n", encoding="utf-8"
        )
        return root, outline

    def test_outline_qc_requires_assessment_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root, _ = self.ready_outline(temp_dir)
            code, payload = run_gate(
                root, "--task", "outline-qc", "--document-type", "book"
            )
            self.assertEqual(code, 2)
            self.assertTrue(any("--assessment-package is required" in item for item in payload["blockers"]))

    def test_outline_qc_consumes_package_without_reloading_qc_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root, outline = self.ready_outline(temp_dir)
            package = write_package(root, outline)
            before = outline.read_bytes()
            code, payload = run_gate(
                root,
                "--task",
                "outline-qc",
                "--document-type",
                "book",
                "--assessment-package",
                str(package),
            )
            self.assertEqual(code, 0, payload)
            self.assertIn("references/assessment-integration.md", payload["required_references"])
            self.assertNotIn("references/qc-rubric.md", payload["required_references"])
            self.assertIn(str(package.resolve()), payload["inputs"])
            self.assertEqual(outline.read_bytes(), before)

    def test_wrong_assessment_task_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root, outline = self.ready_outline(temp_dir)
            package = write_package(root, outline, assessment_task="ASSESS_CHAPTER")
            code, payload = run_gate(
                root,
                "--task",
                "outline-qc",
                "--document-type",
                "book",
                "--assessment-package",
                str(package),
            )
            self.assertEqual(code, 2)
            self.assertTrue(any("incompatible" in item for item in payload["blockers"]))

    def test_stale_fingerprint_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root, outline = self.ready_outline(temp_dir)
            package = write_package(root, outline, digest="0" * 64)
            code, payload = run_gate(
                root,
                "--task",
                "outline-qc",
                "--document-type",
                "book",
                "--assessment-package",
                str(package),
            )
            self.assertEqual(code, 2)
            self.assertTrue(any("fingerprint is stale" in item for item in payload["blockers"]))

    def test_blocked_input_package_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root, outline = self.ready_outline(temp_dir)
            package = write_package(root, outline, package_status="BLOCKED_INPUT")
            code, payload = run_gate(
                root,
                "--task",
                "outline-qc",
                "--document-type",
                "book",
                "--assessment-package",
                str(package),
            )
            self.assertEqual(code, 2)
            self.assertTrue(any("BLOCKED_INPUT" in item for item in payload["blockers"]))

    def test_final_qc_accepts_multi_file_manuscript_assessment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root, _ = self.ready_outline(temp_dir)
            project = root / "project"
            (project / "approval.md").write_text(
                "- Task: outline-qc\n- Status: APPROVED\n", encoding="utf-8"
            )
            chapter = root / "chapters" / "chapter-01"
            chapter.mkdir(parents=True)
            (chapter / "draft.md").write_text("# Chapter 1\n\nContent.\n", encoding="utf-8")
            (chapter / "approval.md").write_text(
                "- Task: chapter-qc 01\n- Status: APPROVED\n", encoding="utf-8"
            )
            package = write_package(
                root, root / "chapters", assessment_task="ASSESS_MANUSCRIPT"
            )
            code, payload = run_gate(
                root,
                "--task",
                "final-qc",
                "--document-type",
                "book",
                "--chapter-count",
                "1",
                "--assessment-package",
                str(package),
            )
            self.assertEqual(code, 0, payload)
            self.assertTrue(any(path.endswith("final-qc.md") for path in payload["owned_outputs"]))


if __name__ == "__main__":
    unittest.main()

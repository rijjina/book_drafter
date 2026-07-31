from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR = SKILL_ROOT / "scripts" / "extract_style_profile.py"
IMPORTER = SKILL_ROOT / "scripts" / "import_manuscript.py"
GATE = SKILL_ROOT / "scripts" / "check_task_gate.py"
SKILL_MD = SKILL_ROOT / "SKILL.md"


def write_minimal_docx(path: Path) -> None:
    document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>บทที่ 1 บทนำ</w:t></w:r></w:p>
    <w:p><w:r><w:t>อย่างไรก็ตาม การวิเคราะห์หลักฐานช่วยให้เห็นข้อจำกัด (Somchai, 2024).</w:t></w:r></w:p>
    <w:p><w:pPr><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr><w:r><w:t>ประเด็นสำคัญ</w:t></w:r></w:p>
    <w:tbl><w:tr><w:tc><w:p><w:r><w:t>หัวตาราง</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
    <w:sectPr/>
  </w:body>
</w:document>"""
    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/></w:style>
</w:styles>"""
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
</Types>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("word/document.xml", document)
        archive.writestr("word/styles.xml", styles)


def write_unstyled_docx_with_references(path: Path) -> None:
    document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>บทที่ ๑</w:t></w:r></w:p>
    <w:p><w:r><w:t>บทนำจุลชีววิทยาสิ่งแวดล้อม</w:t></w:r></w:p>
    <w:p><w:r><w:t>เนื้อหาเปิดบทที่มีรายละเอียดเพียงพอสำหรับใช้ตรวจจังหวะภาษาและน้ำเสียงของผู้เขียนในต้นฉบับเดิม</w:t></w:r></w:p>
    <w:p><w:r><w:t>1.1 ความหมายและขอบเขต</w:t></w:r></w:p>
    <w:p><w:r><w:t>ดังนั้น การวิเคราะห์หลักฐานต้องเชื่อมโยงข้อจำกัดกับบริบทการนำไปใช้โดยไม่ขยายข้อสรุปเกินข้อมูลที่ปรากฏ</w:t></w:r></w:p>
    <w:p><w:r><w:t>บรรณานุกรม</w:t></w:r></w:p>
    <w:p><w:r><w:t>Example, A. (2024). Reference title. Journal, 1(1), 1-10.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Example, B. (2025). Another reference. Publisher.</w:t></w:r></w:p>
    <w:sectPr/>
  </w:body>
</w:document>"""
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
</Types>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("word/document.xml", document)


def write_project_profile(root: Path) -> None:
    project = root / "project"
    project.mkdir(parents=True, exist_ok=True)
    (project / "manuscript-profile.md").write_text(
        """# Manuscript Profile

- Document type: book
- Target quality: A
- Primary rubric: book-level-a
- Course alignment required: no
""",
        encoding="utf-8",
    )
    (project / "type-approval.md").write_text(
        """# Approval Record

- Task: select-document-type
- Status: APPROVED
""",
        encoding="utf-8",
    )


class StyleExtractorTests(unittest.TestCase):
    def test_deterministic_for_docx_markdown_and_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources = [root / "sample.docx", root / "sample.md", root / "sample.txt"]
            write_minimal_docx(sources[0])
            sources[1].write_text(
                "# บทนำ\n\nอย่างไรก็ตาม การวิเคราะห์หลักฐานมีข้อจำกัด (Somchai, 2024).\n\n- ประเด็นสำคัญ\n",
                encoding="utf-8",
            )
            sources[2].write_text(
                "บทนำ\nอย่างไรก็ตาม การวิเคราะห์หลักฐานมีข้อจำกัด (Somchai, 2024).\n",
                encoding="utf-8",
            )
            for source in sources:
                first = root / f"{source.suffix[1:]}-first.md"
                second = root / f"{source.suffix[1:]}-second.md"
                for output in (first, second):
                    result = subprocess.run(
                        [sys.executable, str(EXTRACTOR), "--input", str(source), "--output", str(output)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(first.read_bytes(), second.read_bytes())
                profile = first.read_text(encoding="utf-8")
                self.assertIn("- Profile version: 1", profile)
                self.assertIn(hashlib.sha256(source.read_bytes()).hexdigest(), profile)
                self.assertIn("## Representative Passages", profile)
                self.assertNotIn("{{", profile)

    def test_empty_input_fails_and_short_input_is_sparse(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            empty = root / "empty.txt"
            empty.write_text("\n", encoding="utf-8")
            empty_output = root / "empty-profile.md"
            failed = subprocess.run(
                [sys.executable, str(EXTRACTOR), "--input", str(empty), "--output", str(empty_output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(failed.returncode, 2)
            self.assertIn("No readable prose paragraphs", failed.stderr)
            self.assertFalse(empty_output.exists())

            short = root / "short.txt"
            short.write_text("ข้อความสั้นสำหรับตรวจรูปแบบ", encoding="utf-8")
            short_output = root / "short-profile.md"
            completed = subprocess.run(
                [sys.executable, str(EXTRACTOR), "--input", str(short), "--output", str(short_output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("- Extraction status: SPARSE", short_output.read_text(encoding="utf-8"))

    def test_unstyled_thai_headings_and_references_are_classified(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "unstyled.docx"
            output = root / "style-profile.md"
            write_unstyled_docx_with_references(source)
            result = subprocess.run(
                [sys.executable, str(EXTRACTOR), "--input", str(source), "--output", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            profile = output.read_text(encoding="utf-8")
            self.assertIn("- Headings: 4", profile)
            self.assertIn("- Reference paragraphs excluded from prose metrics: 2", profile)
            self.assertNotIn("Example, B.", profile)
            self.assertIn("- Closing prose: ดังนั้น", profile)


class ImportAndGateTests(unittest.TestCase):
    def test_author_review_gate_supports_approval_free_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "project"
            write_project_profile(root)
            review_input = Path(temp_dir) / "draft.md"
            review_input.write_text(
                "# บทนำ\n\nเนื้อหาสำหรับให้ผู้เขียนรับข้อเสนอแนะแล้วนำไปแก้ไขด้วยตนเอง\n",
                encoding="utf-8",
            )

            before = {
                path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in root.rglob("*")
                if path.is_file()
            }
            result = subprocess.run(
                [
                    sys.executable,
                    str(GATE),
                    "--project-root",
                    str(root),
                    "--task",
                    "author-review",
                    "--chapter",
                    "1",
                    "--document-type",
                    "book",
                    "--input",
                    str(review_input),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["allowed"])
            self.assertTrue(any("author manuscript is read-only" in item for item in payload["checked"]))
            self.assertTrue(any("response-only author review" in item for item in payload["checked"]))
            after = {
                path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after)

            report = root / "reviews" / "chapter-01-review.md"
            file_result = subprocess.run(
                [
                    sys.executable,
                    str(GATE),
                    "--project-root",
                    str(root),
                    "--task",
                    "author-review",
                    "--chapter",
                    "1",
                    "--document-type",
                    "book",
                    "--input",
                    str(review_input),
                    "--output",
                    str(report),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(file_result.returncode, 0, file_result.stdout + file_result.stderr)
            file_payload = json.loads(file_result.stdout)
            self.assertTrue(file_payload["allowed"])
            self.assertTrue(
                any("approval-free review report" in item for item in file_payload["checked"])
            )
            self.assertFalse(report.exists())

            outside_report = Path(temp_dir) / "chapter-01-review.md"
            outside_result = subprocess.run(
                [
                    sys.executable,
                    str(GATE),
                    "--project-root",
                    str(root),
                    "--task",
                    "author-review",
                    "--document-type",
                    "book",
                    "--input",
                    str(review_input),
                    "--output",
                    str(outside_report),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(outside_result.returncode, 2)
            self.assertTrue(
                any(
                    "Author-review output must be inside" in item
                    for item in json.loads(outside_result.stdout)["blockers"]
                )
            )

            unsupported = Path(temp_dir) / "draft.xlsx"
            unsupported.write_bytes(b"not a review document")
            rejected = subprocess.run(
                [
                    sys.executable,
                    str(GATE),
                    "--project-root",
                    str(root),
                    "--task",
                    "author-review",
                    "--document-type",
                    "book",
                    "--input",
                    str(unsupported),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(rejected.returncode, 2)
            self.assertTrue(
                any("Unsupported author-review format" in item for item in json.loads(rejected.stdout)["blockers"])
            )

    def test_import_creates_style_profile_and_declares_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "project"
            write_project_profile(root)
            manuscript = Path(temp_dir) / "manuscript.docx"
            write_minimal_docx(manuscript)
            result = subprocess.run(
                [
                    sys.executable,
                    str(IMPORTER),
                    "--input",
                    str(manuscript),
                    "--project-root",
                    str(root),
                    "--document-type",
                    "book",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "source" / "style-profile.md").is_file())
            report = (root / "source" / "import-report.md").read_text(encoding="utf-8")
            self.assertIn("- Style profile: `source/style-profile.md`", report)

    def test_gate_allows_legacy_fallback_but_blocks_missing_declared_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "project"
            write_project_profile(root)
            source = root / "source"
            source.mkdir(parents=True)
            write_minimal_docx(source / "original-manuscript.docx")
            (source / "approval.md").write_text(
                "- Task: import-manuscript\n- Status: APPROVED\n", encoding="utf-8"
            )
            (source / "import-report.md").write_text(
                "# Manuscript Import Report\n\n- Import status: READY_FOR_REVIEW\n", encoding="utf-8"
            )

            legacy = subprocess.run(
                [
                    sys.executable,
                    str(GATE),
                    "--project-root",
                    str(root),
                    "--task",
                    "manuscript-qc",
                    "--document-type",
                    "book",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(legacy.returncode, 0, legacy.stdout + legacy.stderr)
            legacy_result = json.loads(legacy.stdout)
            self.assertTrue(any("legacy imported project" in item for item in legacy_result["checked"]))

            (source / "import-report.md").write_text(
                "# Manuscript Import Report\n\n- Style profile: `source/style-profile.md`\n",
                encoding="utf-8",
            )
            declared = subprocess.run(
                [
                    sys.executable,
                    str(GATE),
                    "--project-root",
                    str(root),
                    "--task",
                    "manuscript-qc",
                    "--document-type",
                    "book",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(declared.returncode, 2)
            declared_result = json.loads(declared.stdout)
            self.assertTrue(any("declares a style profile" in item for item in declared_result["blockers"]))

    def test_chapter_gate_supports_legacy_and_declared_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "project"
            write_project_profile(root)
            chapter = root / "chapters" / "chapter-01"
            chapter.mkdir(parents=True)
            (chapter / "draft.md").write_text("เนื้อหาร่าง", encoding="utf-8")
            (chapter / "sources-and-rights.md").write_text("# Sources\n", encoding="utf-8")
            (chapter / "draft-audit.md").write_text(
                "# Audit\n\n- User source: `source.docx`\n", encoding="utf-8"
            )
            (chapter / "approval.md").write_text(
                "- Task: draft-chapter 01\n- Status: APPROVED\n", encoding="utf-8"
            )

            command = [
                sys.executable,
                str(GATE),
                "--project-root",
                str(root),
                "--task",
                "chapter-qc",
                "--chapter",
                "1",
                "--document-type",
                "book",
            ]
            legacy = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(legacy.returncode, 0, legacy.stdout + legacy.stderr)
            self.assertTrue(
                any("legacy user-draft chapter" in item for item in json.loads(legacy.stdout)["checked"])
            )

            (chapter / "draft-audit.md").write_text(
                "# Audit\n\n- User source: `source.docx`\n- Style profile: `style-profile.md`\n",
                encoding="utf-8",
            )
            missing = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(missing.returncode, 2)
            self.assertTrue(
                any("declares a style profile" in item for item in json.loads(missing.stdout)["blockers"])
            )

            source = Path(temp_dir) / "source.txt"
            source.write_text("ข้อความต้นฉบับที่ใช้เป็นหลักฐานด้านสำนวน", encoding="utf-8")
            created = subprocess.run(
                [
                    sys.executable,
                    str(EXTRACTOR),
                    "--input",
                    str(source),
                    "--output",
                    str(chapter / "style-profile.md"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            declared = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(declared.returncode, 0, declared.stdout + declared.stderr)

    def test_portable_role_contract_is_explicit(self) -> None:
        skill = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("without assuming a particular model or reasoning label", skill)
        for role in ("Planner", "Worker", "Advisor", "Debugger"):
            self.assertIn(f"**{role}**", skill)
        self.assertNotIn("(`xhigh`)", skill)


if __name__ == "__main__":
    unittest.main()

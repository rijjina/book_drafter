from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
COMPILER_PATH = SKILL_ROOT / "scripts" / "compile_references.py"
PACKAGE_SCRIPT = SKILL_ROOT / "scripts" / "package_skill.py"
SKILL_MD = SKILL_ROOT / "SKILL.md"


def load_compiler():
    spec = importlib.util.spec_from_file_location("compile_references", COMPILER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReferenceCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compiler = load_compiler()

    def test_sanitization_rejects_corruption_and_invisible_instructions(self) -> None:
        sanitized, findings = self.compiler.analyze_text(
            "บทที่ ๑\u200b ข้อความ \ufffd uni0E01"
        )
        self.assertNotIn("\u200b", sanitized)
        self.assertEqual(
            set(findings["flags"]),
            {
                "REPLACEMENT_GLYPH",
                "UNI0E_ARTIFACT",
                "SUSPICIOUS_INVISIBLE_TEXT",
            },
        )

    def test_thai_and_arabic_chapter_numbers_are_detected(self) -> None:
        structure = self.compiler.detect_structure(
            "บทที่ ๑ บทนำ\nเนื้อหา\nบทที่ 2 วิธีการ\nเนื้อหา"
        )
        self.assertEqual(structure["chapters_detected"], 2)

    def test_all_local_sources_and_page_provenance_are_recorded(self) -> None:
        manifest = json.loads(
            (SKILL_ROOT / "references" / "source-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["source_count"], 5)
        self.assertEqual(manifest["total_pages"], 173)
        self.assertEqual(
            manifest["upstream"]["commit"],
            "e087255f187c4fd3a5cdbb1cf1a11e09cdb84b46",
        )
        for source in manifest["sources"]:
            self.assertEqual(len(source["page_map"]), source["page_count"])
            self.assertEqual(
                [page["page"] for page in source["page_map"]],
                list(range(1, source["page_count"] + 1)),
            )
            self.assertFalse(source["curated_replacement_allowed"])
        scanned = next(
            item
            for item in manifest["sources"]
            if item["filename"] == "ประกาศประเมินการสอน.pdf"
        )
        self.assertIn("OCR_REQUIRED", scanned["flags"])
        self.assertEqual(scanned["verification_status"], "VISUAL_REVIEW_REQUIRED")

    def test_completeness_inventory_remains_represented(self) -> None:
        inventory = json.loads(
            (SKILL_ROOT / "references" / "completeness-inventory.json").read_text(
                encoding="utf-8"
            )
        )
        for filename, required in inventory["files"].items():
            text = (SKILL_ROOT / "references" / filename).read_text(encoding="utf-8")
            for phrase in required:
                self.assertIn(phrase, text, f"{phrase!r} missing from {filename}")


class ProgressiveDisclosureTests(unittest.TestCase):
    def test_frontmatter_is_portable_across_skill_hosts(self) -> None:
        skill = SKILL_MD.read_text(encoding="utf-8")
        frontmatter = skill.split("---", 2)[1]
        fields = {}
        for line in frontmatter.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
        self.assertEqual(fields["name"], "write-thai-academic-book")
        self.assertLessEqual(len(fields["description"]), 200)
        self.assertNotIn("reasoning_effort", skill)
        self.assertTrue((SKILL_ROOT / "requirements.txt").is_file())

    def test_skill_is_a_compact_direct_router(self) -> None:
        skill = SKILL_MD.read_text(encoding="utf-8")
        self.assertLessEqual(len(skill.split()), 800)
        routed = (
            "core-production-contract.md",
            "workflow-project.md",
            "workflow-chapter.md",
            "workflow-manuscript.md",
            "workflow-review.md",
            "workflow-final.md",
            "style-preservation.md",
        )
        for filename in routed:
            self.assertIn(f"references/{filename}", skill)
            self.assertTrue((SKILL_ROOT / "references" / filename).is_file())

    def test_legacy_monolith_is_only_a_small_pointer(self) -> None:
        pointer = (SKILL_ROOT / "references" / "workflow-contract.md").read_text(
            encoding="utf-8"
        )
        self.assertLessEqual(len(pointer.split()), 150)
        self.assertIn("compatibility", pointer.lower())
        self.assertNotIn("## Task Catalog", pointer)


class DistributionTests(unittest.TestCase):
    def test_public_export_and_zip_match_canonical_skill(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(PACKAGE_SCRIPT), "--check"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(payload["status"], "MATCH")
        self.assertTrue(payload["excluded_source_pdfs"])
        self.assertTrue(payload["excluded_caches"])


if __name__ == "__main__":
    unittest.main()

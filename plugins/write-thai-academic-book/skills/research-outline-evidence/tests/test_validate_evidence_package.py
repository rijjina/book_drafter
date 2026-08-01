from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from validate_evidence_package import claim_fingerprint, validate  # noqa: E402


def source_row(
    source_id: str = "S001",
    citation: str = "Example Author (2025). Verified study.",
    source_type: str = "PRIMARY_RESEARCH",
    locator: str = "https://doi.org/10.1000/example",
    exact: str = "p. 10",
    verification: str = "VERIFIED_FULL_TEXT",
    currency: str = "PUBLISHED: 2025",
    disposition: str = "INCLUDED",
) -> str:
    return (
        f"| {source_id} | {citation} | {source_type} | {locator} | {exact} | "
        f"{verification} | {currency} | Cite and paraphrase only | Q001 | {disposition} |"
    )


def matrix_text(claims: list[str]) -> str:
    rows = []
    for index, claim in enumerate(claims, 1):
        rows.append(
            f"| {index} | หัวข้อ {index} | อธิบายประเด็นที่ {index} | {claim} | "
            f"[ต้องค้นหลักฐาน: งานวิจัยที่ตรงกับ Claim] | กิจกรรม {index} |"
        )
    return """# Outline Matrix

```yaml
title: "ตัวอย่าง"
level: "CHAPTER"
main_question: "หลักฐานตอบคำถามนี้อย่างไร"
intended_reader: "นักศึกษาที่มีพื้นฐานเบื้องต้น"
scope: "หัวข้อทดสอบ"
exclusions: "หัวข้อนอกขอบเขต"
source_basis: "outline.md"
status: "DRAFT"
```

| ลำดับ | หัวข้อ | ผู้อ่านต้องทำได้ | Claim | หลักฐาน | ตัวอย่าง/กิจกรรม |
|---:|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


def package_text(
    *,
    mode: str,
    status: str,
    scope_type: str = "CHAPTER",
    claims: list[str] | None = None,
    source_rows: list[str] | None = None,
    sufficiency: str = "ADEQUATE",
    gap_action: str = "-",
    handoff_status: str = "READY",
    handoff_gap: bool = False,
    relation_overrides: dict[int, str] | None = None,
    evidence_overrides: dict[int, str] | None = None,
    fingerprint_claims: list[str] | None = None,
) -> str:
    claims = claims or ["หลักฐานเฉพาะช่วยจำกัดขอบเขตของข้ออ้างได้"]
    source_rows = source_rows or [source_row()]
    relation_overrides = relation_overrides or {}
    evidence_overrides = evidence_overrides or {}
    fingerprint_claims = fingerprint_claims or claims

    claim_rows: list[str] = []
    handoff_rows: list[str] = []
    for index, claim in enumerate(claims, 1):
        claim_id = f"C{index:03d}"
        if mode == "SCOPING":
            anchor = "-"
            fingerprint = "-"
        else:
            anchor = f"OM-R{index:02d}"
            fingerprint = claim_fingerprint(fingerprint_claims[index - 1])
        evidence = evidence_overrides.get(index, "S001 @ p. 10")
        relation = relation_overrides.get(index, "S001=SUPPORTS")
        synthesis = "หลักฐานสนับสนุนข้ออ้างในบริบทที่กำหนดและระบุข้อจำกัดแล้ว"
        claim_rows.append(
            f"| {claim_id} | OUT-CH01-S{index:02d} | {anchor} | {claim} | {fingerprint} | "
            f"{evidence} | {relation} | {synthesis} | {sufficiency} | {gap_action} |"
        )
        if mode == "GAP_FILL":
            evidence_cell = (
                "[ต้องค้นหลักฐาน: full-text primary research ที่รองรับ Claim โดยตรง]"
                if handoff_gap
                else "Example Author (2025), p. 10"
            )
            handoff_rows.append(
                f"| {anchor} | {claim_id} | {fingerprint} | {evidence_cell} | KEEP | {handoff_status} |"
            )

    source_matrix = "-" if mode == "SCOPING" else "outline-matrix.md"
    return f"""# Evidence Package

```yaml
package_id: "demo-chapter-01"
mode: "{mode}"
project_id: "demo"
scope_id: "chapter-01"
scope_type: "{scope_type}"
title: "ตัวอย่างการค้นหลักฐาน"
main_question: "หลักฐานใดสนับสนุนข้ออ้างของบทนี้"
intended_reader: "นักศึกษาที่มีพื้นฐานเบื้องต้น"
scope: "ข้ออ้างภายในบทตัวอย่าง"
exclusions: "ประเด็นนอกบท"
source_outline: "outline.md"
source_matrix: "{source_matrix}"
research_cutoff: "2026-08-01"
status: "{status}"
human_subject_review: "PENDING"
```

## Research protocol

- Inclusion criteria: แหล่งที่รองรับข้ออ้างโดยตรงและตรวจฉบับเต็มได้
- Exclusion criteria: แหล่งนอกขอบเขตหรือระบุตำแหน่งไม่ได้
- Languages: ไทยและอังกฤษ
- Date coverage: งานปัจจุบันและงานพื้นฐานที่จำเป็น
- Source hierarchy exceptions: ไม่มี

## Search log

| Query ID | Channel | Query | Searched on | Results screened | Decision/notes |
|---|---|---|---|---:|---|
| Q001 | local and scholarly search | exact claim AND systematic evidence | 2026-08-01 | 2 | ตรวจทั้งแหล่งที่สนับสนุนและคัดค้าน |

## Source ledger

| Source ID | Citation/title | Type | DOI/URL/path | Exact locator | Verification | Currency/currentness | Rights/use | Query ID | Disposition/reason |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(source_rows)}

## Claim-evidence map

| Claim ID | Outline anchor | Matrix anchor | Claim | Fingerprint | Evidence | Relation | Synthesis/limits | Sufficiency | Gap/action |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(claim_rows)}

## Matrix handoff

| Matrix anchor | Claim ID | Fingerprint | Proposed evidence cell | Proposed claim adjustment | Handoff status |
|---|---|---|---|---|---|
{chr(10).join(handoff_rows)}

## Conflicts, gaps, and author decisions

- ไม่มีข้อขัดแย้งที่ยังไม่ได้บันทึก

## Validation

```yaml
validator_status: "{status}"
validated_at: "2026-08-01"
human_checks: "รอผู้เชี่ยวชาญตรวจความถูกต้องเชิงสาขา"
```
"""


class EvidencePackageValidationTests(unittest.TestCase):
    def write_inputs(self, folder: Path, package: str, matrix: str | None = None):
        package_path = folder / "evidence-package.md"
        outline_path = folder / "outline.md"
        package_path.write_text(package, encoding="utf-8")
        outline_path.write_text("# Outline\n\n- Main question and bounded scope\n", encoding="utf-8")
        matrix_path = None
        if matrix is not None:
            matrix_path = folder / "outline-matrix.md"
            matrix_path.write_text(matrix, encoding="utf-8")
        return package_path, outline_path, matrix_path

    def test_scoping_book_is_ready_for_matrix(self):
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            paths = self.write_inputs(
                folder,
                package_text(mode="SCOPING", status="READY_FOR_MATRIX", scope_type="BOOK"),
            )
            result = validate(paths[0], paths[1])
            self.assertEqual(result["validator_status"], "READY_FOR_MATRIX")
            self.assertEqual(result["exit_code"], 0)

    def test_scoping_chapter_is_ready_for_matrix(self):
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            paths = self.write_inputs(
                folder,
                package_text(mode="SCOPING", status="READY_FOR_MATRIX", scope_type="CHAPTER"),
            )
            result = validate(paths[0], paths[1])
            self.assertEqual(result["errors"], [])

    def test_gap_fill_ready_and_does_not_modify_matrix(self):
        claims = ["การตรวจฉบับเต็มช่วยยืนยันความสัมพันธ์ของหลักฐาน", "การระบุตำแหน่งทำให้ตรวจสอบย้อนกลับได้"]
        matrix = matrix_text(claims)
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            paths = self.write_inputs(
                folder,
                package_text(mode="GAP_FILL", status="READY_FOR_HANDOFF", claims=claims),
                matrix,
            )
            before = hashlib.sha256(paths[2].read_bytes()).hexdigest()
            result = validate(paths[0], paths[1], paths[2])
            after = hashlib.sha256(paths[2].read_bytes()).hexdigest()
            self.assertEqual(result["validator_status"], "READY_FOR_HANDOFF")
            self.assertEqual(before, after)

    def test_metadata_only_source_remains_needs_evidence(self):
        claims = ["ข้อมูลระเบียนเพียงอย่างเดียวยังไม่ยืนยัน Claim รายละเอียด"]
        provisional = source_row(
            verification="METADATA_ONLY",
            exact="metadata record",
            disposition="PROVISIONAL: full text not inspected",
        )
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            paths = self.write_inputs(
                folder,
                package_text(
                    mode="GAP_FILL",
                    status="NEEDS_EVIDENCE",
                    claims=claims,
                    source_rows=[provisional],
                    sufficiency="PARTIAL",
                    gap_action="ตรวจฉบับเต็มและระบุตำแหน่ง",
                    handoff_status="HOLD",
                    handoff_gap=True,
                    evidence_overrides={1: "S001 @ metadata record"},
                ),
                matrix_text(claims),
            )
            result = validate(paths[0], paths[1], paths[2])
            self.assertEqual(result["validator_status"], "NEEDS_EVIDENCE")
            self.assertEqual(result["errors"], [])

    def test_inaccessible_source_is_provisional(self):
        claims = ["แหล่งที่เข้าไม่ถึงต้องไม่ถูกยกระดับเป็นหลักฐานยืนยัน"]
        inaccessible = source_row(
            verification="INACCESSIBLE",
            exact="publisher landing page",
            disposition="PROVISIONAL: full text inaccessible",
        )
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            paths = self.write_inputs(
                folder,
                package_text(
                    mode="GAP_FILL",
                    status="NEEDS_EVIDENCE",
                    claims=claims,
                    source_rows=[inaccessible],
                    sufficiency="NONE",
                    gap_action="หาแหล่งฉบับเต็มที่ตรวจสอบได้",
                    handoff_status="HOLD",
                    handoff_gap=True,
                    evidence_overrides={1: "S001 @ publisher landing page"},
                    relation_overrides={1: "S001=CONTEXT_ONLY"},
                ),
                matrix_text(claims),
            )
            result = validate(paths[0], paths[1], paths[2])
            self.assertEqual(result["validator_status"], "NEEDS_EVIDENCE")

    def test_conflicting_evidence_can_be_ready_when_synthesized(self):
        claims = ["ผลของมาตรการขึ้นกับบริบทและวิธีการศึกษา"]
        sources = [
            source_row(),
            source_row(
                source_id="S002",
                citation="Second Author (2024). Contrary study.",
                locator="https://doi.org/10.1000/contrary",
                exact="p. 22",
            ),
        ]
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            paths = self.write_inputs(
                folder,
                package_text(
                    mode="GAP_FILL",
                    status="READY_FOR_HANDOFF",
                    claims=claims,
                    source_rows=sources,
                    evidence_overrides={1: "S001 @ p. 10; S002 @ p. 22"},
                    relation_overrides={1: "S001=SUPPORTS; S002=CONTRADICTS"},
                ),
                matrix_text(claims),
            )
            result = validate(paths[0], paths[1], paths[2])
            self.assertEqual(result["validator_status"], "READY_FOR_HANDOFF")

    def test_changed_matrix_claim_blocks_stale_fingerprint(self):
        original = ["ข้ออ้างเดิมมีขอบเขตจำกัด"]
        changed = ["ข้ออ้างที่แก้ไขแล้วมีความหมายกว้างกว่าเดิม"]
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            paths = self.write_inputs(
                folder,
                package_text(mode="GAP_FILL", status="READY_FOR_HANDOFF", claims=original),
                matrix_text(changed),
            )
            result = validate(paths[0], paths[1], paths[2])
            self.assertEqual(result["validator_status"], "BLOCKED")
            self.assertTrue(any("stale claim Fingerprint" in item for item in result["errors"]))

    def test_duplicate_doi_is_blocked(self):
        claims = ["แหล่งซ้ำไม่ควรถูกนับเป็นหลักฐานอิสระ"]
        sources = [source_row(), source_row(source_id="S002", citation="Duplicate version")]
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            paths = self.write_inputs(
                folder,
                package_text(mode="GAP_FILL", status="READY_FOR_HANDOFF", claims=claims, source_rows=sources),
                matrix_text(claims),
            )
            result = validate(paths[0], paths[1], paths[2])
            self.assertTrue(any("duplicate DOI/URL/path" in item for item in result["errors"]))

    def test_metadata_only_cannot_be_included(self):
        claims = ["Metadata ไม่เพียงพอต่อข้ออ้างเชิงรายละเอียด"]
        invalid = source_row(verification="METADATA_ONLY", exact="metadata record", disposition="INCLUDED")
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            paths = self.write_inputs(
                folder,
                package_text(mode="GAP_FILL", status="READY_FOR_HANDOFF", claims=claims, source_rows=[invalid]),
                matrix_text(claims),
            )
            result = validate(paths[0], paths[1], paths[2])
            self.assertTrue(any("INCLUDED source must" in item for item in result["errors"]))

    def test_old_guideline_requires_currentness_check(self):
        claims = ["แนวทางปัจจุบันต้องอ้างแหล่งทางการที่ตรวจความเป็นปัจจุบันแล้ว"]
        old_guideline = source_row(
            source_type="GUIDELINE_STANDARD",
            verification="VERIFIED_OFFICIAL_TEXT",
            currency="PUBLISHED: 2018",
            locator="https://example.gov/guideline",
            exact="section 4",
        )
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            paths = self.write_inputs(
                folder,
                package_text(mode="GAP_FILL", status="READY_FOR_HANDOFF", claims=claims, source_rows=[old_guideline]),
                matrix_text(claims),
            )
            result = validate(paths[0], paths[1], paths[2])
            self.assertTrue(any("requires CURRENT_AS_OF" in item for item in result["errors"]))

    def test_adequate_claim_warns_when_coverage_is_still_incomplete(self):
        claims = ["กรณีเฉพาะหนึ่งกรณีอธิบายหลักการทั่วไปได้ครบถ้วน"]
        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            package = package_text(mode="GAP_FILL", status="READY_FOR_HANDOFF", claims=claims)
            package = package.replace(
                "หลักฐานสนับสนุนข้ออ้างในบริบทที่กำหนดและระบุข้อจำกัดแล้ว",
                "หลักฐานเป็นกรณีเฉพาะและยังไม่ครอบคลุมหลักการทั่วไป ต้องเพิ่มหนังสือพื้นฐาน",
            )
            paths = self.write_inputs(folder, package, matrix_text(claims))
            result = validate(paths[0], paths[1], paths[2])
            self.assertEqual(result["validator_status"], "NEEDS_REVISION")
            self.assertTrue(any("incomplete claim coverage" in item for item in result["warnings"]))

    def test_matrix_contract_matches_build_outline_validator(self):
        validator_path = (
            Path.home()
            / ".codex"
            / "skills"
            / "build-outline-matrix"
            / "scripts"
            / "validate_outline_matrix.py"
        )
        if not validator_path.is_file():
            self.skipTest("build-outline-matrix validator is not installed")
        spec = importlib.util.spec_from_file_location("outline_matrix_validator", validator_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        claims = [f"ข้ออ้างที่ {index} ตรวจสอบได้ด้วยหลักฐานเฉพาะ" for index in range(1, 6)]
        with tempfile.TemporaryDirectory() as raw:
            matrix_path = Path(raw) / "outline-matrix.md"
            matrix_path.write_text(matrix_text(claims), encoding="utf-8")
            result = module.validate(matrix_path)
            self.assertEqual(result["status"], "NEEDS_EVIDENCE")
            self.assertEqual(result["errors"], [])
            self.assertEqual(result["warnings"], [])


if __name__ == "__main__":
    unittest.main()

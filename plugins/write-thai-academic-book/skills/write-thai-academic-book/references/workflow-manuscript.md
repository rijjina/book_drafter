# Imported Manuscript Workflow

Read with `core-production-contract.md` and `style-preservation.md`. Load
`editorial-standards.md`, `qc-rubric.md`, and the quality reference for the
approved type when performing manuscript QC or revision.

## `import-manuscript`

Require approved type selection and an existing DOCX input. Run
`scripts/import_manuscript.py`. The task owns only:

- a byte-for-byte copy at `source/original-manuscript.docx`;
- `source/import-report.md` with SHA-256, selected type, chapter detection, and
  blockers;
- deterministic `source/style-profile.md` from the preserved original;
- detected chapters as `chapters/chapter-NN/draft.md`;
- `source/approval.md` with task `import-manuscript` and status `PENDING`.

Split by Heading 1 or `บทที่ N`. If numbering is missing, duplicated, or
non-sequential, preserve the original, still create the style profile, report a
blocker, and do not guess. Do not run QC, revise prose, or create export files.

## `manuscript-qc`

Require approved import. Read the style profile first, run preflight with the
approved type, then audit the whole manuscript and every detected chapter. The
task owns only:

- `final/manuscript-preflight-report.md`;
- `final/manuscript-qc.md` from `assets/manuscript-qc-template.md`;
- each chapter's `chapter-qc.md` and `sources-and-rights.md`;
- `final/approval.md` with task `manuscript-qc` and status `PENDING`.

Do not edit the manuscript. For `book`, course evidence is not a criterion. For
`teaching-notes`, record all eight scores, mean, minimum, blockers, and
A-equivalent evidence. Record confirmed style traits, accidental
inconsistencies, mandatory overrides, and style drift by chapter. For a legacy
import without a profile, compare directly with the preserved original and
record `LEGACY_FALLBACK`.

## `revise-manuscript`

Require manuscript QC and final approval status `CHANGES_REQUESTED`. Preserve
the imported original and checksum. For every affected chapter:

- preserve `draft.md`;
- write the complete approved revision to `revised.md`;
- write `revision.md` from `assets/revision-template.md`;
- update `sources-and-rights.md` when affected.

Create `final/revision-log.md` from `assets/revision-log-template.md` and set
final approval to `PENDING`. Apply only approved QC items. Use the style profile
as the default editorial baseline; map each material style departure to an
approved QC item or mandatory rule and verify representative passages against
the original/profile. Do not generate DOCX/PDF or run final QC.

## Gate Examples

```powershell
python scripts/check_task_gate.py --project-root <project> --task import-manuscript --document-type book --input <draft.docx>
python scripts/check_task_gate.py --project-root <project> --task manuscript-qc --document-type book
python scripts/check_task_gate.py --project-root <project> --task revise-manuscript --document-type book
```

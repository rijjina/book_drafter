# Final QC and DOCX Workflow

Read with `core-production-contract.md`. Load `qc-rubric.md`, the approved
document-type quality reference, and `source-map.md` for unresolved high-risk
evidence during final QC. Load `editorial-standards.md` when checking packaging,
figures, tables, captions, citations, or rights.

## `final-qc`

For a new draft, require approved outline and approved completion of every
declared chapter. For an imported manuscript, require approved
`revise-manuscript`, or approved `manuscript-qc` when no revision is required.
Read `revised.md` when present, otherwise `draft.md`.

Run preflight and expert review. Create only:

- `final/preflight-report.md`;
- `final/final-qc.md` from `assets/qc-report-template.md`;
- `final/approval.md` with task `final-qc` and status `PENDING`.

The report must use machine-readable target, decision, blocker, and type-specific
evidence fields. Do not generate DOCX or PDF. A human may unlock export only by
approving a `MEETS_TARGET` report and recording both `Status: APPROVED` and
`Deliverable: DOCX`.

## `produce-document`

Require final QC `MEETS_TARGET`, blocker count 0, complete type-specific quality
evidence, explicit `Status: APPROVED`, and `Deliverable: DOCX`. This is the only
task permitted to create DOCX. It creates exactly `final/manuscript.docx`.

1. Use document-manifest v2. Each chapter lists source candidates in order:
   `revised.md`, then `draft.md`.
2. Run:

   ```powershell
   python scripts/build_docx.py --manifest <project>/document.yml --final-only
   ```

3. Run structural preflight:

   ```powershell
   python scripts/docx_preflight.py <project>/final/manuscript.docx --output <temporary-dir>/docx-audit.json
   ```

4. Render the complete DOCX in a temporary directory and inspect every page,
   even if structural preflight reports `PASS`.
5. Correct packaging/layout defects and repeat validation. Do not silently
   revise approved academic content.
6. Delete temporary PDF/images. Confirm `final/manuscript.docx` is the only
   generated binary deliverable.

Do not create a final PDF, chapter DOCX files, a persisted render directory, or
any second binary deliverable. The byte-preserved imported original is source
evidence, not a generated export.

## Manifest and Preflight Semantics

Use `assets/document-manifest.example.yml`. Manifest v2 assembles directly from
Markdown and never persists chapter DOCX fragments. A missing source candidate
does not authorize an empty chapter. Legacy v1 manifests remain readable only
for existing projects.

`docx_preflight.py` reports:

- `PASS`: no structural issue or detected layout-sensitive feature;
- `WARN`: structural review required;
- `RENDER_REQUIRED`: tables, images, sections, page breaks, footnotes, text
  boxes, or TOC/REF/SEQ fields require visual verification.

Rendering every final page remains mandatory for all three statuses.

```powershell
python scripts/check_task_gate.py --project-root <project> --task final-qc --chapter-count 9 --document-type textbook
python scripts/check_task_gate.py --project-root <project> --task produce-document --chapter-count 9 --document-type textbook
```

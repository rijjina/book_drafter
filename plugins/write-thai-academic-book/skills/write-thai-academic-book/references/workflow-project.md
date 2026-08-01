# Project Workflow

Read with `core-production-contract.md`. For classification and quality evidence,
load `document-types-and-quality.md` or `teaching-document-criteria.md` according
to the selected type. Add `editorial-standards.md` for outline work and
`source-map.md` only for governing-source questions.

## `select-document-type`

Require `--document-type teaching-notes|book|textbook`. Create only:

- `project/manuscript-profile.md` from `assets/manuscript-profile-template.md`;
- `project/type-approval.md` with task `select-document-type` and status
  `PENDING`.

Set target, primary rubric, and course-alignment flag from the type contract. A
type change requires an explicit change/rebuild request and new approval. Do not
create a brief or inspect manuscript content.

## `project-setup`

Require approved type selection. Create only:

- `project/project-brief.md` from `assets/project-brief-template.md`;
- `project/governing-standard.md` from
  `assets/governing-standard-template.md`;
- pending `project/approval.md`.

For `book`, omit course alignment and complete disciplinary scope, central
scholarly problem, intended readers, and author viewpoint/contribution. For
`textbook` and `teaching-notes`, record course identity, assigned scope, and the
evidence required by the governing institution. Select one primary standard in
this order: current institution/publisher rule, applicable official criteria,
bundled quality criteria, bundled editorial manuals, then declared house style.
Do not draft an outline.

## `refresh-sources`

An explicit source refresh is required. Update only
`project/governing-standard.md`; record the new source, exact pages, changed
rules, conflicts, decisions, and downstream impacts. Set project approval to
`PENDING`. Do not change type, target, outline, or manuscript content. Use
`scripts/compile_references.py` only when local source PDFs changed or a full
audit was explicitly requested.

## `draft-outline`

Require approved project setup or refresh. Create only `project/outline.md`
from `assets/outline-template.md` and pending project approval. Plan the reader
journey, logical sequence, chapter purpose, evidence, synthesis, author
contribution, and Level A/A-equivalent evidence. For course-linked types, add
learning alignment only to the degree required by the approved governing
standard. Do not run outline QC.

## `outline-qc`

Require approved outline draft/revision. Create only
`project/outline-qc.md` from `assets/assessment-adapter-template.md` and pending
project approval. Do not edit or reassess the outline. Require a validated
`ASSESS_OUTLINE` package through `--assessment-package` and preserve its input
hash, package/rule status, criterion IDs, and revision IDs. Load
`assessment-integration.md`; do not load `qc-rubric.md` to recompute findings.

## `revise-outline`

Require outline QC and project approval status `CHANGES_REQUESTED`. Revise only
`project/outline.md` for approved findings, preserve defensible content, and set
project approval to `PENDING`. Do not rerun QC or begin chapter drafting.

## Gate Examples

```powershell
python scripts/check_task_gate.py --project-root <project> --task select-document-type --document-type book
python scripts/check_task_gate.py --project-root <project> --task project-setup --document-type book
python scripts/check_task_gate.py --project-root <project> --task draft-outline --document-type textbook
python scripts/check_task_gate.py --project-root <project> --task outline-qc --document-type teaching-notes --assessment-package <project>/assessments/<assessment-id>
```

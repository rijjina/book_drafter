# Cross-Skill Workflow Contract

## Routes And Gates

### New project

1. Writer: `select-document-type` -> approved type.
2. Writer: `project-setup` -> approved brief and governing standard.
3. Writer: `draft-outline` -> approved outline.
4. Assessment: `assess-outline` -> author review; writer `outline-qc` only
   records the package pointer.
5. If changes are requested, the writer applies only approved IDs through
   `revise-outline`; reassess material changes before treating the outline as
   stable.
6. Research `SCOPING` -> `READY_FOR_MATRIX`.
7. Matrix owner creates the six-column Matrix.
8. If any evidence cell remains open, research `GAP_FILL` ->
   `READY_FOR_HANDOFF`, then the Matrix owner applies the handoff.
9. Begin `draft-chapter` only when the Matrix is `READY_TO_DRAFT` and the
   evidence handoff validates.
10. Repeat draft -> assessment -> writer QC adapter -> author-approved revision
    for each chapter.
11. Assess the stable whole manuscript, revise approved IDs, reassess the
    changed manuscript, run final QC, obtain explicit DOCX approval, then
    produce the final document.

### Imported manuscript

Run writer `select-document-type` -> `import-manuscript` ->
`ASSESS_MANUSCRIPT` -> `manuscript-qc` -> author-approved
`revise-manuscript` -> fresh assessment -> `final-qc` -> explicit DOCX approval
-> `produce-document`. Research and Matrix are optional diagnostics here unless
the author requests structural redevelopment; they are not prerequisites for
import.

The import task's owned outputs are only the byte-preserved
`source/original-manuscript.docx`, `source/import-report.md`,
`source/style-profile.md`, detected `chapters/chapter-NN/draft.md` files, and
pending `source/approval.md`. Do not invent an import ID, rights ledger, or
approval-free import route. Existing owned outputs block import unless the
writer gate accepts an explicitly authorized rebuild.

### Teaching handout

Use `$thai-academic-teaching-material` to map and draft from transcript, slide,
course, and institutional sources. Assess as `TEACHING_HANDOUT`. Record explicit
approved revision IDs in the orchestrator approval artifact before asking the
teaching-material skill to revise. Use `documents` for DOCX generation and
rendered QA. Never route this type through the book writer.

## Handoff Invariants

- `matrix-build` requires a `SCOPING` Evidence Package with
  `READY_FOR_MATRIX` and the exact current outline path.
- `matrix-revise` requires a `GAP_FILL` package with `READY_FOR_HANDOFF`, the
  exact outline and Matrix paths, and current `OM-R##` claim fingerprints.
- `draft-chapter` requires the exact six columns, Matrix metadata and validation
  status `READY_TO_DRAFT`, no `[ต้องค้นหลักฐาน: ...]`, and either:
  - the validated `SCOPING/READY_FOR_MATRIX` package named in Matrix
    `source_basis`, when no gap-fill pass was needed; or
  - the validated `GAP_FILL/READY_FOR_HANDOFF` package mapped to the current
    Matrix.
- Assessment findings never authorize edits. Writer revisions require scoped
  `CHANGES_REQUESTED` plus accepted IDs. Teaching-handout revisions require the
  orchestrator approval artifact with the same semantics.
- An assessment package must match the current input path and SHA-256. A
  changed input requires a fresh package before the next assessment-dependent
  gate.
- Final DOCX requires a current whole-manuscript assessment, successful
  mechanical preflight, `MEETS_TARGET`, `Status: APPROVED`, and
  `Deliverable: DOCX`.

## Canonical Artifacts

- Outline: `<project>/project/outline.md`
- Evidence: `<project>/research/<scope-id>/evidence-package.md`
- Matrix: caller-selected Markdown path, passed explicitly at every gate
- Assessment: `<project>/assessments/<assessment-id>/` with exactly three
  assessment artifacts
- Teaching approval: caller-selected Markdown copied from the bundled template
- Book/textbook final: `<project>/final/manuscript.docx`

Use absolute paths in cross-skill prompts and validation commands. Status is a
machine finding; approval is a separate human decision.

Use public child-task names in prompts: `assess-outline`, `assess-chapter`, and
`assess-manuscript`. Reserve `ASSESS_OUTLINE`, `ASSESS_CHAPTER`, and
`ASSESS_MANUSCRIPT` for package metadata and adapter compatibility checks.
Before returning a prompt, verify every required input path. Report expected
outputs exactly as declared by the child contract; output destinations need not
exist yet, but their parent/project ownership must be unambiguous.

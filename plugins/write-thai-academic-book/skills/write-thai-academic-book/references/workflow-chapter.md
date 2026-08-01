# Chapter Workflow

Read with `core-production-contract.md`. Load `editorial-standards.md` for
drafting and approved revision. Load `assessment-integration.md` for
`chapter-qc` and revision from approved assessment IDs. When a user draft or
style evidence is involved, also read `style-preservation.md`.
For `draft-chapter`, also read `evidence-matrix-integration.md`.

## `draft-chapter <NN>`

Require approved outline QC/revision and, from chapter 02 onward, approved
completion of the previous chapter. First determine whether the user supplied
or identified a substantial source draft. Pass it to the gate with
`--input <user-draft>`. Never infer user-draft status from generated
`chapters/chapter-NN/draft.md`.

Require `--outline-matrix` and `--evidence-package`. Both companion validators
and the cross-skill handoff validator must pass; the Matrix must be
`READY_TO_DRAFT` with no unresolved evidence cell. These artifacts are
read-only inputs and never become writer-owned outputs.

### No user draft

Create only:

- `chapters/chapter-NN/draft.md` from `assets/chapter-template.md`;
- `chapters/chapter-NN/sources-and-rights.md` from
  `assets/sources-and-rights-template.md`;
- pending chapter approval.

Use verified evidence and include type-appropriate Level A/A-equivalent
analysis. Do not create `draft-audit.md`, style profile, formal chapter QC,
DOCX, or PDF.

### User draft supplied

Preserve the source file byte-for-byte; never edit it in place. Before editing:

1. create `style-profile.md` from the source using
   `scripts/extract_style_profile.py` and `assets/style-profile-template.md`;
2. read the approved outline, governing standard, existing rights ledger,
   relevant author sources, and `style-preservation.md`;
3. perform a diagnostic audit—not the later formal `chapter-qc`;
4. create/update `draft-audit.md` from `assets/draft-audit-template.md` with
   source path, SHA-256, style profile, traits to retain, justified departures,
   representative before/after checks, and section decisions `retain`, `revise`,
   `add`, or `remove`;
5. write the improved complete chapter to generated `draft.md`, update
   `sources-and-rights.md`, and set pending approval.

Retain sound structure, arguments, examples, citations, tables, synthesis, and
author stance. Do not rewrite for style alone. Correct factual, logical,
citation, scope, terminology, accessibility, and overclaim problems; fill
necessary gaps and transitions. Mark unsupported material as a blocker or
narrow/remove it—never invent replacement evidence. Record major removals,
changed claims, and material style departures. If a user source exists, do not
use an older generated draft as the baseline. Never create `chapter-qc.md` in
this task.

## `chapter-qc <NN>`

Require approved chapter draft. Create only:

- `chapter-qc.md` from `assets/assessment-adapter-template.md`;
- pending chapter approval.

Do not edit or reassess the draft. Require a validated `ASSESS_CHAPTER` package
whose input hash matches `draft.md`. Preserve package findings and limitations;
the adapter records only their IDs, statuses, counts, and paths. A style profile
may be used during later approved revision but does not authorize a second QC
judgment here.

## `revise-chapter <NN>`

Require chapter QC and scoped approval status `CHANGES_REQUESTED`. Preserve
`draft.md`; create only:

- the complete revised chapter as `revised.md`;
- `revision.md` from `assets/revision-template.md`;
- updated `sources-and-rights.md`;
- pending chapter approval.

Apply only approved QC items. Never invent evidence or silently expand scope.
For a user-draft chapter, read the style profile before editing and map every
material voice, terminology, rhythm, heading, or citation-presentation change
to an approved QC item or mandatory rule. For a legacy chapter, derive the
baseline from the recorded source and mark `LEGACY_FALLBACK` in `revision.md`.
Do not overwrite `draft.md`, create an intermediate DOCX/PDF, rerun QC, or begin
the next chapter.

## Gate Examples

```powershell
python scripts/check_task_gate.py --project-root <project> --task draft-chapter --chapter 2 --document-type textbook --outline-matrix <matrix.md> --evidence-package <research/.../evidence-package.md>
python scripts/check_task_gate.py --project-root <project> --task draft-chapter --chapter 1 --document-type book --input <user-chapter.docx> --outline-matrix <matrix.md> --evidence-package <research/.../evidence-package.md>
python scripts/check_task_gate.py --project-root <project> --task chapter-qc --chapter 1 --document-type book --assessment-package <project>/assessments/<assessment-id>
python scripts/check_task_gate.py --project-root <project> --task revise-chapter --chapter 1 --document-type book
```

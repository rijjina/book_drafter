# Chapter Workflow

Read with `core-production-contract.md`. Load `editorial-standards.md` for every
chapter task; load `qc-rubric.md` for `chapter-qc` and `revise-chapter`; load the
document-type quality reference for the approved type. When a user draft or
style evidence is involved, also read `style-preservation.md`.

## `draft-chapter <NN>`

Require approved outline QC/revision and, from chapter 02 onward, approved
completion of the previous chapter. First determine whether the user supplied
or identified a substantial source draft. Pass it to the gate with
`--input <user-draft>`. Never infer user-draft status from generated
`chapters/chapter-NN/draft.md`.

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

- `chapter-qc.md` from `assets/chapter-qc-template.md`;
- pending chapter approval.

Do not edit the draft. Identify every gap to the fixed target using
`qc-rubric.md` and the applicable type reference. Verify claims, citations,
rights, logic, synthesis, author contribution, accessibility, and scope.

When `draft-audit.md` identifies a user draft, read `style-profile.md` and
report style preservation as `PASS`, `REVIEW`, or `FAIL`. If a legacy chapter
predates style profiles, use the source path/checksum in `draft-audit.md`, record
`LEGACY_FALLBACK`, and do not block solely because a profile is absent.

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
python scripts/check_task_gate.py --project-root <project> --task draft-chapter --chapter 2 --document-type textbook
python scripts/check_task_gate.py --project-root <project> --task draft-chapter --chapter 1 --document-type book --input <user-chapter.docx>
python scripts/check_task_gate.py --project-root <project> --task chapter-qc --chapter 1 --document-type book
python scripts/check_task_gate.py --project-root <project> --task revise-chapter --chapter 1 --document-type book
```

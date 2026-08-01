# Author-Edit Assessment Adapter

`author-review` is a manuscript-read-only, approval-free compatibility route.
The academic review is produced by `$assess-thai-academic-manuscript`; this
route validates and presents that package without recreating its findings. Do
not load the production contract or unlock a production gate.

## Inputs and Gate

Require an approved document type and `--input <docx|md|txt|pdf>`.
`--chapter <NN>` is optional. `--output
<project-root>/reviews/<name>.md` is optional and may contain only a compatibility
pointer. Require `--assessment-package
<project-root>/assessments/<assessment-id>`. Run the gate separately for every
input/package/output tuple.

Load `assessment-integration.md`. Run the companion validator with the exact
input before presenting or writing a pointer.

## Read-Only Contract

1. Do not modify, copy, convert, or overwrite the input manuscript. Disposable
   extraction used only to read a file is allowed.
2. Without `--output`, return links, status, strengths, prioritized findings,
   and the revision sequence from the validated package; change no files. With
   `--output`, create only an adapter record under `<project-root>/reviews/`
   using `assets/assessment-adapter-template.md`.
3. Do not create or change project, source, chapter, final, style-profile, or
   approval artifacts. Do not wait for approval.
4. Do not provide a fully rewritten chapter or replacement manuscript and do
   not reinterpret the package's findings.
5. Preserve package status, rule status, limitations, conflicts, criterion IDs,
   and revision IDs exactly.
6. Review every supplied author file in the same invocation, with one gate run
   and one separate report per input. Merge findings only if the user explicitly
   asks for an additional overview.
7. Deterministic report names are `reviews/chapter-NN-review.md` when a chapter
   is supplied, otherwise `reviews/<source-stem>-review.md`. Replacing an
   existing report requires explicit `--rebuild` or user authorization.

## Response Order

Present each review in this order:

1. context: input, document type, fixed target, chapter/scope;
2. package ID, validator result, package status, and rule status;
3. strengths and material to retain from the assessment;
4. prioritized `BLOCKER`, `MAJOR`, then `MINOR` findings with criterion IDs;
5. revision sequence with revision IDs;
6. unresolved questions, evidence, or route decisions;
7. reminder that revision requires explicit author approval.

End with `Review mode: AUTHOR_EDITS`, `Approval required: yes before revision`,
and the source path. For response-only review add `Files changed: none`; for
file output list only the adapter record. Assessment itself remains
approval-free, but no writing task starts until the author approves selected
criterion/revision IDs.

```powershell
python scripts/check_task_gate.py --project-root <project> --task author-review --document-type book --input <draft.docx> --assessment-package <project>/assessments/<assessment-id>
python scripts/check_task_gate.py --project-root <project> --task author-review --chapter 3 --document-type textbook --input <chapter-03.docx> --assessment-package <project>/assessments/<assessment-id> --output <project>/reviews/chapter-03-review.md
```

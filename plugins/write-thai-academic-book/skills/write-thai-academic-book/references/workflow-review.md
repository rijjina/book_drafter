# Author-Edit Review Workflow

`author-review` is a manuscript-read-only, approval-free route for authors who
want recommendations and will edit the manuscript themselves. Do not load the
production contract, create prerequisites, or unlock any production gate.

## Inputs and Gate

Require an approved document type and `--input <docx|md|txt|pdf>`.
`--chapter <NN>` is optional. `--output
<project-root>/reviews/<name>.md` is optional. Run the gate separately for every
input/output pair. Read only the identified input plus existing project/style
artifacts needed to interpret it.

Load:

- `qc-rubric.md` and the applicable document-type quality reference;
- `editorial-standards.md` for academic/editorial findings;
- `style-preservation.md` when an author baseline exists;
- `source-map.md` only when authority, provenance, or exact-source verification
  is in dispute.

## Read-Only Contract

1. Do not modify, copy, convert, or overwrite the input manuscript. Disposable
   extraction used only to read a file is allowed.
2. Without `--output`, return the review in the response and change no files.
   With `--output`, create only the requested Markdown report under
   `<project-root>/reviews/` using `assets/author-review-template.md`.
3. Do not create or change project, source, chapter, final, style-profile, or
   approval artifacts. Do not wait for approval.
4. Do not provide a fully rewritten chapter or replacement manuscript. Use
   short phrase-level examples only to clarify recommendations.
5. Separate academic defects, mandatory corrections, optional editorial
   preferences, and style drift. Preserve sound author style.
6. Review every supplied author file in the same invocation, with one gate run
   and one separate report per input. Merge findings only if the user explicitly
   asks for an additional overview.
7. Deterministic report names are `reviews/chapter-NN-review.md` when a chapter
   is supplied, otherwise `reviews/<source-stem>-review.md`. Replacing an
   existing report requires explicit `--rebuild` or user authorization.

## Report Order

Present each review in this order:

1. context: input, document type, fixed target, chapter/scope;
2. strengths and material to retain;
3. prioritized `BLOCKER`, `MAJOR`, then `MINOR` findings, each with location,
   evidence, reason, and concrete author action;
4. style traits to retain, drift to avoid, and mandatory overrides;
5. citation, evidence, rights, and unsupported-claim issues;
6. author self-edit sequence;
7. unresolved questions or evidence the author must supply.

End with `Review mode: AUTHOR_EDITS`, `Approval required: no`, and the source
path. For response-only review add `Files changed: none`; for file output list
only the report files created. The author may rerun this route after editing.

```powershell
python scripts/check_task_gate.py --project-root <project> --task author-review --document-type book --input <draft.docx>
python scripts/check_task_gate.py --project-root <project> --task author-review --chapter 3 --document-type textbook --input <chapter-03.docx> --output <project>/reviews/chapter-03-review.md
```

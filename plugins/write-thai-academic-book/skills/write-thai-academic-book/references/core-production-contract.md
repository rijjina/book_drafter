# Core Production Contract

Read this contract for every gate-bearing production task after document-type
selection. Then read exactly one task-group workflow selected by `SKILL.md`.
The classification-only `select-document-type` task and read-only
`author-review` route use their own contracts and do not load this file.

## First Gate and Fixed Targets

Before production, the user must approve exactly one type:

- `teaching-notes` = เอกสารคำสอน;
- `book` = หนังสือ;
- `textbook` = ตำรา.

If the type is not explicit, run only `select-document-type` and stop for
approval. Do not offer เอกสารประกอบการสอน. Every later task must match
`project/manuscript-profile.md` and `project/type-approval.md`.

Targets are fixed: `book` and `textbook` target Level A;
`teaching-notes` targets internal A-equivalent—official-style mean 3.26–4.00,
every criterion at least 3, zero blockers, and evidence of currency, depth,
research, author experience, and synthesis comparable to Level A. Never present
A-equivalent as an official institutional grade.

## Execution Rules

1. Perform one gate-bearing production task per invocation. If several are
   requested, run only the first whose gate is open, list the queue, and stop.
2. Inventory `output/<project-id>/` before reading source PDFs or writing.
   Existing artifacts are the default source of truth.
3. Run `scripts/check_task_gate.py` with the selected task and approved type.
   For `draft-chapter`, also pass the validated Matrix and Evidence Package.
   Stop on any blocker. Do not manufacture missing prerequisites.
4. Write only the selected task's owned artifacts. Never combine drafting,
   formal QC, revision, another chapter, final QC, or export in one invocation.
5. Do not overwrite unless the selected workflow permits it, the user explicitly
   requests a change/rebuild, or the gate was run with `--rebuild`.
6. Set the scoped approval record to `PENDING` after producing gate-bearing
   artifacts. Report type, target, artifacts, blockers, and exact next task; then
   wait for explicit human approval.
7. `PASS`, `CONDITIONAL PASS`, and `MEETS_TARGET` are findings only. Record an
   explicit `อนุมัติ`, `ผ่าน`, `โอเค`, `ไปต่อ`, or equivalent before the next
   gate. Record `แก้ตาม QC` or equivalent as `CHANGES_REQUESTED` before revision.
8. Never invent citations, permissions, research or professional experience,
   course evidence, or Level A/A-equivalent evidence. Narrow or flag unsupported
   claims.
9. Keep generated content in Markdown. Only `produce-document` may create a
   generated DOCX, exactly `final/manuscript.docx`; no task creates a final PDF.
10. Use indexed references, SHA-256 extraction cache, and incremental builds to
    reduce repeated work. Never omit a relevant rule to reduce tokens.

## Artifact Ownership

```text
output/<project-id>/
├── project/
│   ├── manuscript-profile.md   type-approval.md
│   ├── project-brief.md        governing-standard.md
│   ├── outline.md              outline-qc.md
│   └── approval.md
├── source/
│   ├── original-manuscript.docx  import-report.md
│   ├── style-profile.md           approval.md
├── chapters/chapter-NN/
│   ├── draft.md       draft-audit.md    style-profile.md
│   ├── chapter-qc.md  revised.md        revision.md
│   ├── sources-and-rights.md              approval.md
├── reviews/
│   └── chapter-NN-review.md or <source-stem>-review.md
└── final/
    ├── manuscript-preflight-report.md  manuscript-qc.md
    ├── revision-log.md                 preflight-report.md
    ├── final-qc.md                     approval.md
    └── manuscript.docx
```

Normalize chapter folders as `chapter-01`, `chapter-02`, and so on. Never mix
project, source, chapter, review, or final artifacts. Preserve
`source/original-manuscript.docx` byte-for-byte. Review reports are advisory and
never approval records.

Approval ownership is fixed:

- type selection: `project/type-approval.md`;
- other project tasks: `project/approval.md`;
- import: `source/approval.md`;
- chapter tasks: `chapters/chapter-NN/approval.md`;
- manuscript-wide and final tasks: `final/approval.md`.

Approval for one task or chapter never approves another. Final export approval
must include both `Status: APPROVED` and `Deliverable: DOCX`.

Companion artifacts under `research/`, `assessments/`, and the explicitly
passed Outline Matrix are read-only writer inputs. They remain owned by their
research, assessment, or Matrix skill and are not copied into writer outputs.

## Existing Artifacts First

Read the manuscript profile first, then reuse the existing brief, governing
standard, outline, QC, and chapter artifacts. A user draft is an original file
supplied or identified by the user, normally outside the generated project, or
the byte-preserved imported original. Files under `chapters/` or `final/` are
generated artifacts, not user drafts. Do not reopen bundled PDFs when the
governing-standard record already contains sufficient source, page, conflict,
and decision evidence. Run `refresh-sources` only on explicit request or when a
new governing source is supplied.

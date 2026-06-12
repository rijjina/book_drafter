---
name: write-thai-academic-book
description: Draft, audit, revise, and quality-check Thai teaching notes, books, and textbooks at Level A/A-equivalent, one approved task at a time with reusable artifacts and human gates.
---

# Write Thai Academic Book

Perform exactly one task per invocation. Reuse existing artifacts and stop for explicit human approval before the next task.

## Mandatory First Gate

Before any project task, the user must select exactly one type:

- `teaching-notes` = เอกสารคำสอน;
- `book` = หนังสือ;
- `textbook` = ตำรา.

If the type is not explicit, ask the user to choose and stop. Do not offer เอกสารประกอบการสอน. Run `select-document-type` to create `project/manuscript-profile.md` and `project/approval.md`. Every later task must use the approved profile and must not infer or change the type.

Quality targets are fixed:

- `book` and `textbook`: Level `A`;
- `teaching-notes`: internal `A-equivalent`, meaning official-style mean `3.26-4.00`, every criterion at least `3`, zero blockers, and evidence of currency, depth, research, author experience, and synthesis comparable to Level A.

Never state that `A-equivalent` is an official institutional grade. It is an internal production target.

## Core Rules

1. Identify one task from the catalog. If a request combines tasks, perform only the first task whose gate is open, list the remaining queue, and stop.
2. Inventory `output/<project-id>/` before reading source PDFs or writing files. Existing artifacts are the default source of truth.
3. Run `scripts/check_task_gate.py` before the selected task. If blocked, report the missing input or approval and stop. Never create prerequisites automatically.
4. Write only task-owned artifacts. Do not run formal `chapter-qc`, revision, the next chapter, final QC, or production in the same invocation. The user-draft branch of `draft-chapter` must perform a diagnostic audit before targeted editing, but this audit does not replace the later formal `chapter-qc` task.
5. Finish each task by setting its scoped `approval.md` to `PENDING`, reporting artifacts and blockers, requesting human review, and stopping.
6. `PASS`, `CONDITIONAL PASS`, and `MEETS_TARGET` are machine findings, not human approval. Only an explicit user message such as `อนุมัติ`, `ผ่าน`, `โอเค`, `ไปต่อ`, or `แก้ตาม QC` changes approval status.
7. Record approval or change requests in the relevant approval file before any later task.
8. Never invent citations, permissions, author experience, research findings, course evidence, or Level A evidence. Use visible blockers.

## Academic Voice For Analysis And Synthesis

Use an impersonal academic voice in the manuscript by default. Demonstrate scholarly contribution through the selection and evaluation of evidence, comparison of explanations, explicit limitations, conceptual integration, and defensible conclusions.

- Do not use headings such as `ข้อสังเคราะห์ของผู้เขียน` or `มุมมองของผู้เขียน` merely to signal Level A contribution.
- Do not introduce analysis with self-announcing phrases such as `ผู้เขียนเสนอว่า`, `จากมุมมองของผู้เขียน`, `ผลงานของผู้เขียนแสดงให้เห็น`, or `กรอบของผู้เขียน` when the same point can be stated directly and supported academically.
- Prefer neutral headings such as `ข้อสังเคราะห์เชิงหลักการ`, `การสังเคราะห์เชิงระบบ`, `นัยต่อการประยุกต์ใช้`, or a topic-specific analytical heading.
- Introduce research by its question, method, evidence level, or finding, followed by an author-year citation. Do not foreground ownership of the research. Example: write `การทดลองภายใต้ห้องควบคุมช่วยอธิบาย... (Pumas, 2024)` rather than `ผลงานของผู้เขียนพบว่า...`.
- Separate direct findings, interpretation, and proposed application. State study-design limits before extending a finding to another scale or context.
- Retain first-person or explicit author-position language only when the user requests it, the publisher requires an author note, or the passage describes a genuinely personal professional experience that cannot be represented as general evidence. Record that exception in the audit.
- Treat `author contribution`, `author viewpoint`, and `author experience` as evaluation/evidence fields in project and QC artifacts. They do not require self-referential labels in the published chapter prose.

## Output Contract

```text
output/<project-id>/
├── project/
│   ├── manuscript-profile.md
│   ├── type-approval.md
│   ├── project-brief.md
│   ├── governing-standard.md
│   ├── outline.md
│   ├── outline-qc.md
│   └── approval.md
├── source/
│   ├── original-manuscript.docx
│   ├── import-report.md
│   └── approval.md
├── chapters/
│   └── chapter-NN/
│       ├── draft.md
│       ├── draft-audit.md
│       ├── chapter-qc.md
│       ├── revision.md
│       ├── sources-and-rights.md
│       └── approval.md
└── final/
    ├── manuscript-qc.md
    ├── revised-manuscript.docx
    ├── revision-log.md
    ├── manuscript.docx
    ├── manuscript.pdf
    ├── manuscript-preflight-report.md
    ├── preflight-report.md
    ├── final-qc.md
    ├── rendered/
    └── approval.md
```

Normalize chapter folders as `chapter-01`, `chapter-02`, and so on. Never mix project, source, chapter, or final artifacts. Preserve `source/original-manuscript.docx` byte-for-byte.

Do not overwrite an artifact unless the task is `refresh-sources`, `revise-outline`, `revise-chapter`, or `revise-manuscript`, the user-draft branch of `draft-chapter` applies, or the user explicitly requests `rebuild`. User-draft refinement must preserve the original argument, usable prose, citations, tables, and author voice; change only material supported by the audit. Never edit the user's source file in place.

## Type-Specific Contract

### `book`

Do not request or evaluate มคอ.3, course code, credits, CLO/PLO, contact hours, teaching assignment, or classroom-use evidence. Replace course alignment with disciplinary scope, intended readers, central concept, author viewpoint, academic contribution, currency/depth, national or international usability, and publication/dissemination evidence.

### `textbook`

Require a course or defined part of a course, course code/name, author teaching scope, content coverage, and learning alignment. CLO/PLO/OBE/TQF evidence is required only when the governing institution requires it.

### `teaching-notes`

Require course identity, assigned teaching scope, coverage, teaching/learning structure, and evidence of use required by the governing institution. Evaluate the eight teaching-document criteria and the additional A-equivalent evidence.

## Existing Artifacts First

1. Read `project/manuscript-profile.md` first and verify type, target, rubric, and course-alignment flag.
2. Use the existing brief, governing standard, outline, QC, and chapter artifacts instead of reconstructing them.
3. Before `draft-chapter`, search the files supplied by the user for a substantial chapter manuscript. A user draft is an original file supplied or identified by the user, normally outside `output/<project-id>/`, or the byte-preserved `source/original-manuscript.docx`. Generated files under `chapters/` or `final/` are artifacts, not user drafts.
4. Do not reopen bundled source PDFs when the governing-standard record contains sufficient source, page, conflict, and decision evidence.
5. Load only references needed by the selected task.
6. Use `refresh-sources` only when explicitly requested or when the user supplies a new governing source.

## Task Catalog

### `select-document-type`

Require `--document-type teaching-notes|book|textbook`. Create only:

- `project/manuscript-profile.md` from `assets/manuscript-profile-template.md`;
- `project/type-approval.md` with task `select-document-type` and status `PENDING`.

Set target and course alignment automatically. A type change requires an explicit rebuild/change request and new approval. Do not create a brief or inspect manuscript content.

### `project-setup`

Require approved type selection. Create only `project/project-brief.md`, `project/governing-standard.md`, and a pending project approval. For `book`, omit course alignment and complete disciplinary scope/contribution. For `textbook` and `teaching-notes`, record required course evidence. Do not draft an outline.

### `refresh-sources`

Explicit request required. Update only `project/governing-standard.md`, record changed rules and impacts, and set project approval to `PENDING`. Do not change the selected type or target.

### `draft-outline`

Require approved project setup/refresh. Create only `project/outline.md` and pending approval. Plan Level A/A-equivalent evidence in every chapter. Do not run QC.

### `outline-qc`

Require approved outline draft/revision. Create only `project/outline-qc.md` and pending approval. Check type-specific scope and Level A/A-equivalent plan. Do not edit the outline.

### `revise-outline`

Require outline QC and `CHANGES_REQUESTED`. Revise only the outline and set pending approval. Do not rerun QC.

### `draft-chapter <NN>`

Require approved outline QC/revision and, from chapter 02 onward, approved completion of the previous chapter.

First determine whether the user supplied or identified a substantial source draft. Pass that file to the gate with `--input <user-draft>`. Do not infer user-draft status from `chapters/chapter-NN/draft.md`; that path is generated output.

- **No user draft:** create only `draft.md`, `sources-and-rights.md`, and pending approval. Include type-appropriate Level A/A-equivalent evidence. Do not create `draft-audit.md` merely to document an empty baseline.
- **User draft supplied:** preserve the source file byte-for-byte and use it as the baseline. Read the approved outline, governing standard, existing rights ledger, and relevant author sources; then perform a diagnostic QC before editing. Create/update generated `draft-audit.md` with the source path, SHA-256, and a concise section-by-section record of `retain`, `revise`, `add`, `remove`, evidence/citation gaps, rights issues, and scope or duplication risks. Write the improved version to generated `draft.md`, update `sources-and-rights.md`, and set pending approval.

In user-draft mode:

1. Do not rewrite the whole chapter for style alone.
2. Retain sound structure, arguments, examples, citations, tables, and distinctive scholarly synthesis, while recasting unnecessary self-referential phrasing into neutral academic prose.
3. Fill missing sections and transitions; correct factual, logical, citation, scope, terminology, and overclaim problems.
4. Mark unsupported material as a blocker or remove/narrow it; never invent replacement evidence.
5. Record major removals or changed claims in `draft-audit.md` so the author can review them.
6. Do not treat a prior generated `draft.md` as the baseline when a user source file exists; regenerate or revise the output from the user source and document the comparison.
7. Do not create `chapter-qc.md`; the later `chapter-qc <NN>` remains the independent formal quality gate.

### `chapter-qc <NN>`

Require approved chapter draft. Create only `chapter-qc.md` and pending approval. Use `assets/chapter-qc-template.md`; identify every gap to the fixed quality target. Do not edit the draft.

### `revise-chapter <NN>`

Require chapter QC and `CHANGES_REQUESTED`. Preserve `draft.md`; create/update only `revision.md` and `sources-and-rights.md`, then set pending approval. Do not rerun QC or start the next chapter.

### `import-manuscript`

Require approved type selection and a DOCX input. Run `scripts/import_manuscript.py`. It must:

- copy the input byte-for-byte to `source/original-manuscript.docx`;
- record SHA-256, type, chapter detection, and blockers in `source/import-report.md`;
- split chapters by Heading 1 or `บทที่ N` into `chapters/chapter-NN/draft.md`;
- create `source/approval.md` with task `import-manuscript` and status `PENDING`.

If chapter numbering is missing, duplicated, or non-sequential, retain the original, report a blocker, and do not guess. Do not run QC.

### `manuscript-qc`

Require approved import. Run preflight with the selected type, then audit the whole manuscript and each detected chapter. Create only:

- `final/manuscript-preflight-report.md`;
- `final/manuscript-qc.md` from `assets/manuscript-qc-template.md`;
- each chapter's `chapter-qc.md` and `sources-and-rights.md`;
- `final/approval.md` with task `manuscript-qc` and status `PENDING`.

For `book`, course evidence is not a criterion. Record every gap to A. For `teaching-notes`, record all eight scores, mean, minimum score, blockers, and A-equivalent evidence. Do not edit the manuscript.

### `revise-manuscript`

Require manuscript QC and `CHANGES_REQUESTED`. Use the platform's available document-editing capability; if a dedicated document skill is installed, invoke it. Preserve the original and its checksum. Create each affected chapter's `revision.md`, `final/revised-manuscript.docx`, `final/revision-log.md`, and pending final approval. Apply only approved QC items. Do not run final QC.

### `final-qc`

For a new draft, require approved outline and approved completion of every declared chapter. For an imported manuscript, require approved `revise-manuscript`, or approved `manuscript-qc` when no revision is required. Run preflight and expert review. Create only `final/preflight-report.md`, `final/final-qc.md`, and pending final approval.

The final QC report must use the machine-readable quality fields in `assets/qc-report-template.md`. Do not produce DOCX/PDF.

### `produce-document`

Require approved final QC and a machine-readable `MEETS_TARGET` result. Use the platform's available DOCX/PDF tools and visually inspect rendered pages. Create final delivery files and `rendered/`, then set final approval to `PENDING`. Do not silently revise academic content.

## Approval Protocol

- Type selection uses the persistent `project/type-approval.md`.
- Other project tasks use `project/approval.md`.
- Import uses `source/approval.md`.
- Chapter tasks use `chapters/chapter-NN/approval.md`.
- Manuscript-wide and final tasks use `final/approval.md`.

Before revision, record the user's `แก้ตาม QC` or equivalent as `CHANGES_REQUESTED` for the pending QC task. Approval for one task or chapter never approves another.

After every task report selected type, fixed quality target, produced artifacts, blockers, gate status `PENDING`, and the exact next task unlocked by approval. Then stop.

## Governing And Quality Rules

Select exactly one primary governing standard in this precedence: current institution/publisher rule, applicable official criteria, bundled quality criteria, bundled editorial manuals, then a declared house style.

Use `references/document-types-and-quality.md` for `book`/`textbook`, `references/teaching-document-criteria.md` for `teaching-notes`, `references/editorial-standards.md` for drafting, and `references/qc-rubric.md` for QC.

Level A requires Level B plus current knowledge/methods, original ideas and relevant author experience/research, high detail/depth, and potential for broad national or international use and citation. Missing author evidence must remain a blocker, not generated prose.

## Commands

```powershell
python scripts/check_task_gate.py --project-root <output/project-id> --task select-document-type --document-type book
python scripts/check_task_gate.py --project-root <output/project-id> --task import-manuscript --document-type book --input <draft.docx>
python scripts/check_task_gate.py --project-root <output/project-id> --task manuscript-qc --document-type book
python scripts/check_task_gate.py --project-root <output/project-id> --task draft-chapter --chapter 2 --document-type textbook
python scripts/check_task_gate.py --project-root <output/project-id> --task draft-chapter --chapter 1 --document-type book --input <user-chapter.docx>
python scripts/check_task_gate.py --project-root <output/project-id> --task final-qc --chapter-count 9 --document-type textbook
```

Run preflight only in `manuscript-qc` or `final-qc`:

```powershell
python scripts/preflight.py --type book --input <input> --output <project-root>/final/preflight-report.md
```

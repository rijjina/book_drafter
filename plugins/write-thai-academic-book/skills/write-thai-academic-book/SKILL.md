---
name: write-thai-academic-book
description: Draft, revise, and produce Thai teaching notes, books, and textbooks at Level A/A-equivalent. Use for Markdown-first writing, assessment-package handoff, human-approved revision, or final DOCX.
---

# Write Thai Academic Book

Create Thai academic manuscripts with Markdown as the editable source of truth.
Keep academic decisions human-approved, preserve verified evidence and author
voice, and generate DOCX only through the final production gate.

## Route Before Reading

1. Identify exactly one task below. A request with several production tasks runs
   only the first open gate; queue the rest. Multiple independent
   `author-review` inputs are the only multi-task exception.
2. Read only the task-group contract linked in the table. For a gate-bearing
   production task other than `select-document-type`, also read
   [core-production-contract.md](references/core-production-contract.md).
3. For author review or academic QC, require a validated package from
   `$assess-thai-academic-manuscript`; do not repeat its judgment. For drafting
   and revision, load only the references named by the routed contract.
4. Inventory the project, then run `scripts/check_task_gate.py` before any write.
   Treat its `required_references`, `inputs`, `owned_outputs`, and `blockers` as
   the execution checklist.
5. Write only task-owned artifacts, set the scoped approval to `PENDING`, report
   blockers and the next gate, then stop.

| Task | Read this task contract |
| --- | --- |
| `select-document-type`, `project-setup`, `refresh-sources`, `draft-outline`, `outline-qc`, `revise-outline` | [workflow-project.md](references/workflow-project.md) |
| `draft-chapter`, `chapter-qc`, `revise-chapter` | [workflow-chapter.md](references/workflow-chapter.md) |
| `import-manuscript`, `manuscript-qc`, `revise-manuscript` | [workflow-manuscript.md](references/workflow-manuscript.md) |
| `author-review` | [workflow-review.md](references/workflow-review.md) — read-only and approval-free; do not load the production contract |
| `final-qc`, `produce-document` | [workflow-final.md](references/workflow-final.md) |

[workflow-contract.md](references/workflow-contract.md) is only a compatibility
pointer for older callers. It is not a contract to preload.

## Conditional References

Load a file only when the selected task or an actual finding requires it:

- [style-preservation.md](references/style-preservation.md): any supplied or
  imported author draft, style extraction, style QC, or approved revision.
- [document-types-and-quality.md](references/document-types-and-quality.md):
  `book`/`textbook` classification and B/A/A+ evidence.
- [teaching-document-criteria.md](references/teaching-document-criteria.md):
  `teaching-notes` classification, eight criteria, and A-equivalent evidence.
- [editorial-standards.md](references/editorial-standards.md): outline, prose,
  citations, figures, tables, rights, or document structure.
- [qc-rubric.md](references/qc-rubric.md): any formal QC, readiness decision, or
  legacy compatibility only; new academic findings come from the assessment
  package.
- [assessment-integration.md](references/assessment-integration.md): every
  `author-review`, `outline-qc`, `chapter-qc`, `manuscript-qc`, `final-qc`, or
  approved revision consuming assessment IDs.
- [evidence-matrix-integration.md](references/evidence-matrix-integration.md):
  every `draft-chapter`; require a validated Evidence Package and a six-column
  Matrix at `READY_TO_DRAFT`.
- [source-map.md](references/source-map.md): authority conflicts, exact source
  pages, provenance, or a disputed rule.
- [reference-index.md](references/reference-index.md): topic/QC routing and
  source-cache policy when the task contract does not resolve the question.

`references/source-manifest.json` is data, not default context. Read only the
record and cached page segment needed for a source-verification task. Run
`scripts/compile_references.py` only for changed PDFs or an explicit source
refresh. Never replace verified curated Markdown with unverified extraction.

## Non-Negotiable Rules

- Require one approved type: `teaching-notes` (เอกสารคำสอน), `book` (หนังสือ),
  or `textbook` (ตำรา). Do not infer, silently change, or offer
  เอกสารประกอบการสอน.
- Fixed targets are Level A for `book`/`textbook` and internal A-equivalent for
  `teaching-notes`. Do not describe A-equivalent as an official grade.
- Existing project artifacts are the source of truth. Never auto-create a
  missing prerequisite or overwrite an artifact without the task contract,
  explicit change request, or `--rebuild` authorization.
- Never invent citations, permissions, author experience, research findings,
  course evidence, or quality evidence. Preserve missing evidence as blockers.
- Academic assessment is owned by `$assess-thai-academic-manuscript`. The
  compatibility QC tasks create pointer/gate records and mechanical preflight
  only; they never recompute or silently replace assessment findings.
- Draft and revise in Markdown. Preserve an imported
  `source/original-manuscript.docx` byte-for-byte. No draft, revision, review, or
  QC task creates a generated DOCX or PDF.
- `PASS`, `CONDITIONAL PASS`, `READY_FOR_AUTHOR_REVIEW`, and `MEETS_TARGET` are
  machine findings, not human approval. Approval for one task or chapter never
  approves another. Apply only author-approved criterion/revision IDs.
## Portable Work Roles

Use behavioral roles without assuming a particular model or reasoning label:
**Planner** for cross-chapter ownership, **Worker** for routine production,
**Advisor** for integrity/rights/style judgment, and **Debugger** after a
deterministic failure. Roles never bypass gates or expand ownership.

## Host Portability

- Resolve `scripts/`, `references/`, and `assets/` relative to this skill folder;
  never assume a host-specific installation path.
- Resolve all bundled helpers relative to this skill.
- Do not require named models, provider-specific reasoning labels, subagents, or
  host-only tools. Use the behavioral roles above with the capabilities present.
- If Python or DOCX rendering is unavailable, continue planning or read-only
  review when safe, report the missing capability, and keep production blocked.
- Respect the host's sandbox, permission prompts, and human approval controls;
  never reinterpret host permission as academic approval.

## Final Export Invariant

`produce-document` is the only DOCX-producing task. It requires final QC
`MEETS_TARGET`, explicit `Status: APPROVED`, and explicit
`Deliverable: DOCX`. It writes exactly `final/manuscript.docx`, validates and
renders it in a temporary directory, inspects every page, and removes temporary
PDF/images. It never creates a final PDF or persisted chapter DOCX files.

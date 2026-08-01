---
name: orchestrate-thai-academic-writing
description: Coordinate gated Thai academic-writing workflows by selecting the next safe task and enforcing evidence, Outline Matrix, assessment, approval, revision, and production handoffs.
---

# Orchestrate Thai Academic Writing

Route one open gate at a time. Inspect existing artifacts before proposing or
executing a child-skill task. Never substitute orchestration status for author
approval, disciplinary review, or a child skill's validator.

## Select The Route

- Use `NEW_PROJECT` for `teaching-notes`, `book`, or `textbook` created through
  `$write-thai-academic-book`.
- Use `IMPORTED_MANUSCRIPT` for an existing DOCX preserved and split through
  `$write-thai-academic-book import-manuscript`.
- Use `TEACHING_HANDOUT` for transcript/slide/course-source work drafted with
  `$thai-academic-teaching-material` and produced with `documents`.

Do not route `TEACHING_HANDOUT` into `$write-thai-academic-book`; that writer
does not own this type.

## Follow The Contract

Read [workflow-contract.md](references/workflow-contract.md) before choosing the
next gate. Read [prompt-flow.md](references/prompt-flow.md) only when presenting
a copy-ready prompt sequence or the next prompt. Read
[teaching-material-integration.md](references/teaching-material-integration.md)
for the teaching-handout route.

Before naming a child task, read that child skill and its routed contract. Use
the public task spelling from its skill (for example `assess-outline`), not an
artifact enum such as `ASSESS_OUTLINE`. Report only child-contract inputs and
owned outputs; do not invent a receipt, ID, ledger, approval behavior, or
fallback location. Resolve and verify every required input path before emitting
the prompt. A nonexistent input is a blocker, not a path suggestion.

Preserve these owners:

- the writer owns project setup, Markdown drafts, approved revisions, writer
  approvals, mechanical preflight, and final book/textbook DOCX;
- research owns Evidence Packages but never edits outline or Matrix;
- the Matrix skill alone creates or revises the six-column Matrix;
- assessment owns findings and revision plans but never edits the source;
- the author alone approves revision IDs and final production;
- the teaching-material and documents skills own teaching-handout prose and
  rendered DOCX after an explicit approval record.

## Validate Cross-Skill Handoffs

Run the bundled validator before these transitions:

```powershell
python scripts/validate_workflow_handoff.py --stage matrix-build --outline <outline.md> --evidence-package <evidence-package.md>
python scripts/validate_workflow_handoff.py --stage matrix-revise --outline <outline.md> --matrix <matrix.md> --evidence-package <evidence-package.md>
python scripts/validate_workflow_handoff.py --stage draft-chapter --outline <outline.md> --matrix <matrix.md> --evidence-package <evidence-package.md>
python scripts/validate_workflow_handoff.py --stage teaching-material-revision --assessment-package <assessment-directory> --approval <approval.md>
```

Stop on structural errors, stale claim fingerprints, stale assessment input,
unapproved revision IDs, `NEEDS_EVIDENCE`, or a Matrix that is not
`READY_TO_DRAFT`. The validator checks handoff integrity, not academic truth.

## Route The Next Prompt

Return the current route, completed gate, blocker or approval needed, next child
skill and task, required inputs, expected owned outputs, and exactly one next
prompt. Do not issue several production prompts at once. After any source,
Claim, Matrix, evidence, rule, or manuscript change, revalidate the affected
handoff instead of reusing a stale status.

If an owned output already exists, preserve it and report the collision. Use a
new root or `--rebuild` only when the child contract and explicit user
authorization permit it; never improvise an alternate output convention.

For a teaching-handout revision, copy
`assets/teaching-material-approval-template.md`, record only the author's
explicitly approved `RV-###` IDs, validate it, then invoke the teaching-material
skill. Validation success never creates approval automatically.

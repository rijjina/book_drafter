# Assessment Package Integration

Academic assessment belongs to `$assess-thai-academic-manuscript`. This writing
skill owns approval records, approved revision, mechanical preflight, and final
DOCX production. Do not recompute or copy the assessment findings.

## Required Handoff

For `author-review`, `outline-qc`, `chapter-qc`, `manuscript-qc`, and `final-qc`,
require:

```powershell
--assessment-package <project-root>/assessments/<assessment-id>
```

Before creating a compatibility record:

1. Run the assessment package validator with the exact assessed input.
2. Require `rule-register.md`, `assessment-report.md`, and
   `author-revision-plan.md` with matching package ID, assessment ID, input
   path, and SHA-256.
3. Require the assessment task that matches the adapter:
   - `outline-qc` -> `ASSESS_OUTLINE`;
   - `chapter-qc` -> `ASSESS_CHAPTER`;
   - `manuscript-qc` and `final-qc` -> `ASSESS_MANUSCRIPT`;
   - `author-review` -> outline, chapter, or manuscript assessment.
4. Reject `BLOCKED_INPUT`, a stale input hash, missing package artifact, or an
   assessment plan whose approval is not `PENDING_AUTHOR_APPROVAL`.
5. Preserve `NEEDS_RULE_REFRESH`, `NEEDS_EVIDENCE`, and
   `BLOCKED_RULE_SELECTION` as visible limitations. Never convert them into
   `MEETS_TARGET`.

## Compatibility Record

Use `assets/assessment-adapter-template.md`. Record only package identity,
source fingerprint, validator result, package/rule status, counts, and the IDs
the author later approves. Link to the assessment artifacts instead of
duplicating findings.

- `author-review` returns the package in the response. If `--output` is supplied,
  write only a compatibility pointer under `reviews/`; it remains approval-free.
- `outline-qc` writes the pointer to `project/outline-qc.md` and sets project
  approval to `PENDING`.
- `chapter-qc` writes the pointer to `chapters/chapter-NN/chapter-qc.md` and sets
  chapter approval to `PENDING`.
- `manuscript-qc` runs mechanical preflight, writes the pointer to
  `final/manuscript-qc.md`, and sets final approval to `PENDING`. It does not
  regenerate chapter assessments or rights ledgers.
- `final-qc` runs final mechanical preflight and writes the pointer plus the
  mechanical target decision to `final/final-qc.md` with pending approval.

## Approval And Revision

Assessment completion is not approval. Before `revise-outline`,
`revise-chapter`, or `revise-manuscript`, require the scoped writer approval to
record `CHANGES_REQUESTED` and the accepted criterion/revision IDs. Apply only
those IDs. If the input hash, rule mode, or governing rule set changes, create a
new assessment package before further revision.

`final-qc` may declare `MEETS_TARGET` only when the validated manuscript
assessment has no unresolved blocker, the relevant rule limitations are
acceptable for the declared production target, and mechanical preflight passes.
This remains a machine finding; `produce-document` still requires explicit
human approval and `Deliverable: DOCX`.


---
name: assess-thai-academic-manuscript
description: Assess Thai academic outlines, chapters, manuscripts, and route readiness against references or refreshed official rules, then prepare evidence-linked author revision plans without rewriting.
---

# Assess Thai Academic Manuscript

Produce a traceable, author-facing assessment before revision. Keep the source
manuscript read-only, separate verified rules from advisory guidance, and wait
for explicit author approval before handing findings to a writing workflow.

## Select One Task

| Task | Purpose |
| --- | --- |
| `assess-outline` | Evaluate planned scope, sequence, evidence, contribution, and route-relevant coverage. |
| `assess-chapter` | Evaluate one chapter or teaching-document unit with exact manuscript locators. |
| `assess-manuscript` | Evaluate the complete work and cross-chapter consistency. |
| `assess-route-readiness` | Compare the work and supplied route facts with the selected institution's criteria. |
| `refresh-governing-rules` | Search and verify current official rules when the user explicitly requests a refresh. |

Run one task per invocation. A refresh may prepare `rule-register.md`; run an
assessment task afterward to complete the three-part package.

## Choose The Rule Mode

- Use `REFERENCE_ONLY` unless the user explicitly asks to search, refresh,
  verify current criteria, or check the latest rules. Do not browse implicitly.
  Keep the Search log table empty in this mode.
  Set `rules_status: REFERENCE_ONLY` and `package_status:
  NEEDS_RULE_REFRESH`; provide provisional manuscript findings but no route
  readiness conclusion.
- Use `CURRENT_RULES` only after the explicit request. Follow
  [rule-research-protocol.md](references/rule-research-protocol.md), record the
  search log and cutoff, verify exact official text, and retain superseded or
  conflicting rules in the register. If verification fails, use `STALE` or
  `UNRESOLVED`; never call the route current.

## Gather Inputs

Require an outline file, manuscript file, or stable multi-file manuscript
directory and an explicit document type: `BOOK`, `TEXTBOOK`,
`TEACHING_HANDOUT`, or `TEACHING_NOTES`. Preserve every input byte-for-byte and
record the deterministic SHA-256 in all three artifacts.

For `assess-route-readiness` or any `CURRENT_RULES` assessment, also require:

- institution;
- target rank;
- official field or discipline;
- document type;
- submission method or route;
- intended filing date.

If route facts are incomplete, continue a useful manuscript assessment when
possible but set the route result to `BLOCKED_RULE_SELECTION`. Never infer a
university, route, or filing date.

## Build The Package

Write only:

```text
output/<project-id>/assessments/<assessment-id>/
|- rule-register.md
|- assessment-report.md
`- author-revision-plan.md
```

Copy the three templates from `assets/`. Follow
[integration-contract.md](references/integration-contract.md) exactly and use
[assessment-protocol.md](references/assessment-protocol.md) for finding and
severity decisions. Load [criterion-catalog.md](references/criterion-catalog.md)
only for the selected document type and scope. Use
[reference-index.md](references/reference-index.md) when local workspace
references are in scope; do not copy or redistribute the indexed PDFs.
Keep the package directory limited to these three Markdown files; write an
optional validator JSON report outside it.

Use these package statuses only: `READY_FOR_AUTHOR_REVIEW`,
`NEEDS_RULE_REFRESH`, `NEEDS_EVIDENCE`, `BLOCKED_RULE_SELECTION`, or
`BLOCKED_INPUT`. Use `PASS`, `PARTIAL`, `FAIL`, or `NOT_APPLICABLE` per
criterion and `BLOCKER`, `MAJOR`, `MINOR`, or `NOTE` for severity.

Record a rule locator and a manuscript locator for every finding. Preserve
contradictory evidence and limitations. Do not calculate a readiness
percentage. Record numeric scores only when a verified governing rule defines
the score and cite its exact locator.

## Validate And Stop

Run:

```powershell
python scripts/validate_assessment_package.py --package <assessment-directory> --input <outline-or-manuscript> [--project-profile <profile.md>] [--json-output <report.json>]
```

Fix structural errors without changing academic conclusions. The validator
checks traceability and consistency; it does not replace subject-matter review.

End with `Approval status: PENDING_AUTHOR_APPROVAL`. Present the prioritized
plan to the author and stop. Do not edit the manuscript, update an Outline
Matrix, create an approval record, or invoke a revision task. After explicit
approval, hand the validated package ID and only the approved findings to the
writing skill described in the integration contract.

For `TEACHING_HANDOUT`, use the teaching-material handoff in the integration
contract instead of the book writer. Require an explicit approval record naming
the accepted `RV-###` IDs before any teaching-material revision.

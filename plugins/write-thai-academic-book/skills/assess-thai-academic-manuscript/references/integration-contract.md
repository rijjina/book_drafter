# Assessment Package And Writer Handoff Contract

## Package Location

Use `output/<project-id>/assessments/<assessment-id>/`. Keep assessment IDs
lowercase and stable. Never overwrite a prior package; create a new assessment
ID after the input or governing rules change.

The package contains exactly these author-facing Markdown artifacts:

- `rule-register.md`;
- `assessment-report.md`;
- `author-revision-plan.md`.

Do not place notes, copied references, full text, or validator JSON in the
package directory. When `--json-output` is used, write the report beside the
package or in a separate validation directory.

All three YAML blocks must repeat `schema_version`, `package_id`,
`assessment_id`, `input_path`, and the full `input_sha256`. Rule and report
metadata must also agree on task, status, and rule mode.
The recorded `input_path` must resolve to the same file or directory supplied
to the validator, not merely to another file with identical bytes.

`input_path` may be one manuscript file or a directory containing a multi-file
manuscript. Directory fingerprints hash sorted relative paths, file sizes, and
bytes while excluding `assessments`, `rendered`, `__pycache__`, and
`.pytest_cache`. Prefer the narrowest stable manuscript directory, normally
`chapters/`, rather than the whole project root.

## Controlled Values

- Tasks: `ASSESS_OUTLINE`, `ASSESS_CHAPTER`, `ASSESS_MANUSCRIPT`,
  `ASSESS_ROUTE_READINESS`.
- Modes: `REFERENCE_ONLY`, `CURRENT_RULES`.
- Document types: `BOOK`, `TEXTBOOK`, `TEACHING_HANDOUT`, `TEACHING_NOTES`.
- Package statuses: `READY_FOR_AUTHOR_REVIEW`, `NEEDS_RULE_REFRESH`,
  `NEEDS_EVIDENCE`, `BLOCKED_RULE_SELECTION`, `BLOCKED_INPUT`.
- Rule statuses: `REFERENCE_ONLY`, `CURRENT`, `STALE`, `UNRESOLVED`.
- Criterion statuses: `PASS`, `PARTIAL`, `FAIL`, `NOT_APPLICABLE`.
- Severities and revision priorities: `BLOCKER`, `MAJOR`, `MINOR`, `NOTE`.
- Approval status: `PENDING_AUTHOR_APPROVAL` only.

`REFERENCE_ONLY` always produces `rules_status: REFERENCE_ONLY` and normally
`package_status: NEEDS_RULE_REFRESH`. It may still contain actionable
manuscript findings. A missing route field takes precedence and requires
`BLOCKED_RULE_SELECTION` for a route assessment unless the package is already
blocked by missing input.

## IDs And Links

- Rule IDs: `R001`, `R002`, ...
- Query IDs: `Q001`, `Q002`, ...
- Criterion IDs: `CR-001`, `CR-002`, ...
- Revision IDs: `RV-001`, `RV-002`, ...

Every criterion row cites one or more rule IDs with exact locators. Every
`PARTIAL` or `FAIL` criterion appears in the revision plan. Every revision row
links back to a criterion ID and contains an affected locator, proposed action,
and acceptance check. Use `NOTE` for `PASS` and `NOT_APPLICABLE`; actionable
`PARTIAL` or `FAIL` rows cannot use `NOTE`. A revision row's priority repeats
the linked criterion severity; order the rows separately by blocker,
dependency, then impact.

## Writer Compatibility Adapter

`write-thai-academic-book` owns approvals, revision, preflight, and production;
this skill owns academic assessment. Its compatibility tasks `author-review`,
`outline-qc`, `chapter-qc`, `manuscript-qc`, and the academic portion of
`final-qc` consume a validated package through `--assessment-package`.

The writer may create a small legacy-path adapter record containing package ID,
path, input hash, validator result, package status, and approved criterion IDs.
It must not copy or recompute the academic findings. Mechanical preflight may
remain in writer-owned QC artifacts.

Before revision, require explicit author approval. Record that decision only in
the writer's scoped approval file. Approval must list the accepted criterion or
revision IDs; silence, validator success, `PASS`, or
`READY_FOR_AUTHOR_REVIEW` is not approval.

If the input hash changes, the rule mode changes, a governing rule is refreshed,
or a cited package artifact is missing, reject the handoff and reassess. Never
edit the source manuscript or an Outline Matrix from this package.

## Teaching Handout Handoff

For `document_type: TEACHING_HANDOUT`, do not route revision or production to
`write-thai-academic-book`. Keep the three-part assessment package read-only.
After the author explicitly names accepted `RV-###` IDs, record a separate
teaching-material approval containing assessment ID, package path, assessed
input path and SHA-256, approved IDs, date, and approver. Validate that every ID
exists in the revision plan and that the current input hash still matches.

Only then may `$thai-academic-teaching-material` revise the approved items.
Use `documents` for DOCX generation and rendered visual QA. Material content,
evidence, rights, alignment, or route changes require a fresh assessment before
the next approval-dependent step.

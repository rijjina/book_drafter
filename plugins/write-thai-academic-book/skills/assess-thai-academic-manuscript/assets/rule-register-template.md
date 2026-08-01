# Rule Register

```yaml
schema_version: "1.0"
package_id: "{{package_id}}"
project_id: "{{project_id}}"
assessment_id: "{{assessment_id}}"
task: "{{ASSESS_OUTLINE|ASSESS_CHAPTER|ASSESS_MANUSCRIPT|ASSESS_ROUTE_READINESS}}"
mode: "{{REFERENCE_ONLY|CURRENT_RULES}}"
document_type: "{{BOOK|TEXTBOOK|TEACHING_HANDOUT|TEACHING_NOTES}}"
institution: "{{institution-or-dash}}"
target_rank: "{{target-rank-or-dash}}"
field: "{{official-field-or-dash}}"
submission_route: "{{route-or-dash}}"
intended_filing_date: "{{YYYY-MM-DD-or-dash}}"
assessment_cutoff: "{{YYYY-MM-DD}}"
rules_status: "{{REFERENCE_ONLY|CURRENT|STALE|UNRESOLVED}}"
package_status: "{{READY_FOR_AUTHOR_REVIEW|NEEDS_RULE_REFRESH|NEEDS_EVIDENCE|BLOCKED_RULE_SELECTION|BLOCKED_INPUT}}"
input_path: "{{source-path}}"
input_sha256: "{{full-sha256}}"
```

## Search log

| Query ID | Channel | Query | Searched on | Results screened | Decision/notes |
| --- | --- | --- | --- | ---: | --- |

Leave the table empty in `REFERENCE_ONLY`. Do not create a simulated search.

## Rule ledger

| Rule ID | Issuing authority | Title | Rank/route | Effective/superseded | URL/path | Exact locator | Verification | Rights/use | Status/disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R001 | {{authority}} | {{title}} | {{rank-and-route}} | {{effective-or-superseded-detail}} | {{URL-or-local-path}} | {{page-clause-heading}} | {{VERIFIED_OFFICIAL_TEXT|VERIFIED_LOCAL_SOURCE|ADVISORY_ONLY|METADATA_ONLY|INACCESSIBLE}} | {{rights-note}} | {{IN_FORCE|SUPERSEDED|AMENDS|ADVISORY|EXCLUDED}} |

## Authority conflicts and transition notes

- {{conflict-or-none-with-reason}}

## Currentness conclusion

{{State exactly what was and was not verified. Do not predict committee approval.}}


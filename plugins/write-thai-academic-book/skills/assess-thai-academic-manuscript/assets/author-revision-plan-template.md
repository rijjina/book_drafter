# Author Revision Plan

```yaml
schema_version: "1.0"
package_id: "{{package_id}}"
assessment_id: "{{assessment_id}}"
input_path: "{{source-path}}"
input_sha256: "{{full-sha256}}"
approval_status: "PENDING_AUTHOR_APPROVAL"
```

## Revision sequence

| Revision ID | Criterion ID | Priority | Dependency | Affected locator | Proposed action | Acceptance check |
| --- | --- | --- | --- | --- | --- | --- |
| RV-001 | CR-001 | {{BLOCKER|MAJOR|MINOR|NOTE}} | {{dependency-or-none}} | {{exact-input-locator}} | {{bounded-author-action}} | {{observable-check}} |

## Decisions required from the author

- {{decision-or-evidence-needed}}

## Handoff

- Package ID: {{package_id}}
- Approved revision IDs: PENDING
- Writing skill may revise: no
- Next action: review this plan with the author and wait for explicit approval.


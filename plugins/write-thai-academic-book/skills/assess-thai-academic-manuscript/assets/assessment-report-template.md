# Assessment Report

```yaml
schema_version: "1.0"
package_id: "{{package_id}}"
assessment_id: "{{assessment_id}}"
task: "{{ASSESS_OUTLINE|ASSESS_CHAPTER|ASSESS_MANUSCRIPT|ASSESS_ROUTE_READINESS}}"
scope_id: "{{scope-id}}"
input_path: "{{source-path}}"
input_sha256: "{{full-sha256}}"
mode: "{{REFERENCE_ONLY|CURRENT_RULES}}"
rules_status: "{{REFERENCE_ONLY|CURRENT|STALE|UNRESOLVED}}"
package_status: "{{READY_FOR_AUTHOR_REVIEW|NEEDS_RULE_REFRESH|NEEDS_EVIDENCE|BLOCKED_RULE_SELECTION|BLOCKED_INPUT}}"
numeric_scores: "{{NONE|OFFICIAL_ONLY}}"
```

## Context and retained strengths

- Scope: {{scope}}
- Strengths to retain: {{specific-evidence-with-locators}}
- Limits of this assessment: {{limits}}

## Criteria assessment

| Criterion ID | Scope anchor | Manuscript locator | Rule ID/locator | Status | Severity | Finding/evidence | Limitation/conflict | Author action | Verification condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CR-001 | {{scope-anchor}} | {{exact-input-locator}} | R001 @ {{exact-rule-locator}} | {{PASS|PARTIAL|FAIL|NOT_APPLICABLE}} | {{BLOCKER|MAJOR|MINOR|NOTE}} | {{visible-evidence}} | {{limitation-or-none}} | {{action-or-dash}} | {{recheck-condition}} |

## Official numeric scores

Use only when a verified rule defines the score. Never add readiness percentages.

| Metric | Score/result | Rule ID/locator | Evidence basis | Status |
| --- | --- | --- | --- | --- |

## Overall synthesis

{{Synthesize strengths, material risks, unresolved evidence, and route limits without claiming approval.}}


# Evidence Package

```yaml
package_id: "{{PROJECT_ID}}-{{SCOPE_ID}}"
mode: "{{SCOPING_OR_GAP_FILL}}"
project_id: "{{PROJECT_ID}}"
scope_id: "{{SCOPE_ID}}"
scope_type: "{{BOOK_CHAPTER_SECTION_ARTICLE_COURSE_OTHER}}"
title: "{{WORKING_TITLE}}"
main_question: "{{QUESTION_THE_SCOPE_MUST_ANSWER}}"
intended_reader: "{{READER_AND_PREREQUISITES}}"
scope: "{{IN_SCOPE}}"
exclusions: "{{OUT_OF_SCOPE}}"
source_outline: "{{PATH_TO_OUTLINE}}"
source_matrix: "{{PATH_TO_MATRIX_OR_DASH}}"
research_cutoff: "{{YYYY-MM-DD}}"
status: "{{MODE_APPROPRIATE_STATUS}}"
human_subject_review: "PENDING"
```

## Research protocol

- Inclusion criteria: {{RELEVANCE_SOURCE_TYPE_CONTEXT_LANGUAGE_DATE_ACCESS}}
- Exclusion criteria: {{OUT_OF_SCOPE_UNVERIFIABLE_OR_UNSUITABLE_MATERIAL}}
- Languages: {{THAI_ENGLISH_OR_OTHER}}
- Date coverage: {{JUSTIFIED_RANGE_AND_FOUNDATIONAL_EXCEPTION}}
- Source hierarchy exceptions: {{NONE_OR_JUSTIFICATION}}

## Search log

| Query ID | Channel | Query | Searched on | Results screened | Decision/notes |
|---|---|---|---|---:|---|
| Q001 | {{LOCAL_OR_SEARCH_CHANNEL}} | {{EXACT_QUERY_OR_LOCAL_INVENTORY_RULE}} | {{YYYY-MM-DD}} | {{COUNT}} | {{SCREENING_RESULT_OR_ZERO_RESULT_NOTE}} |

## Source ledger

| Source ID | Citation/title | Type | DOI/URL/path | Exact locator | Verification | Currency/currentness | Rights/use | Query ID | Disposition/reason |
|---|---|---|---|---|---|---|---|---|---|
| S001 | {{FULL_CITATION_OR_UNAMBIGUOUS_TITLE}} | {{CONTROLLED_SOURCE_TYPE}} | {{DOI_URL_OR_LOCAL_PATH}} | {{PAGE_SECTION_TABLE_FIGURE_PARAGRAPH_OR_TIMESTAMP}} | {{CONTROLLED_VERIFICATION_STATE}} | {{CURRENT_AS_OF_PUBLISHED_FOUNDATIONAL_HISTORICAL_OR_NOT_CHECKED}} | {{CITATION_REUSE_OR_PERMISSION_NOTE}} | Q001 | {{INCLUDED_PROVISIONAL_OR_EXCLUDED_WITH_REASON}} |

## Claim-evidence map

| Claim ID | Outline anchor | Matrix anchor | Claim | Fingerprint | Evidence | Relation | Synthesis/limits | Sufficiency | Gap/action |
|---|---|---|---|---|---|---|---|---|---|
| C001 | {{OUTLINE_ANCHOR}} | {{OM_ROW_OR_DASH}} | {{BOUNDED_EVIDENCE_CHECKABLE_CLAIM}} | {{SHA256_FINGERPRINT_OR_DASH}} | {{SOURCE_ID_AT_EXACT_LOCATOR_OR_DASH}} | {{SOURCE_ID_EQUALS_RELATION_OR_DASH}} | {{PARAPHRASED_FINDING_AND_LIMITS}} | {{ADEQUATE_PARTIAL_OR_NONE}} | {{DASH_OR_PRECISE_NEXT_ACTION}} |

## Matrix handoff

| Matrix anchor | Claim ID | Fingerprint | Proposed evidence cell | Proposed claim adjustment | Handoff status |
|---|---|---|---|---|---|
| {{OM_ROW_OR_DASH}} | C001 | {{SHA256_FINGERPRINT_OR_DASH}} | {{VERIFIED_LOCATORS_OR_PRECISE_EVIDENCE_REQUIREMENT}} | {{KEEP_OR_NARROWER_CLAIM}} | {{READY_HOLD_OR_AUTHOR_DECISION}} |

## Conflicts, gaps, and author decisions

- {{CONFLICT_GAP_DECISION_OR_NONE}}

## Validation

```yaml
validator_status: "{{READY_FOR_MATRIX_READY_FOR_HANDOFF_NEEDS_EVIDENCE_NEEDS_REVISION_OR_BLOCKED}}"
validated_at: "{{YYYY-MM-DD}}"
human_checks: "Evidence supports each exact claim; disciplinary accuracy; current official sources; material contrary findings; reuse rights"
```

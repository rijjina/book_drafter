# Assessment Protocol

## Purpose And Boundaries

Evaluate what the submitted artifact demonstrates, what remains unsupported,
and what the author should inspect before revision. Do not rewrite prose,
invent evidence, act as a committee, or state that a submission will pass.

Treat three questions separately:

1. Is the outline or manuscript academically sound and usable for its declared
   document type?
2. Does visible evidence satisfy each cited criterion?
3. When current rules were explicitly refreshed, does the supplied route appear
   complete enough for an author readiness review?

## Assessment Sequence

1. Preserve the input and calculate SHA-256.
2. Confirm task, scope, document type, and rule mode.
3. Load only applicable local references and project artifacts.
4. For `CURRENT_RULES`, finish the rule register before judging route criteria.
5. Create criterion rows with exact outline/manuscript and rule locators.
6. Separate strengths to retain from defects, missing evidence, optional
   preferences, and unresolved authority conflicts.
7. Map every `PARTIAL` or `FAIL` row to at least one revision-plan action.
8. Validate the package and stop for author approval.

## Criterion Status

- `PASS`: visible evidence meets the cited criterion for this scope.
- `PARTIAL`: some evidence is visible, but a material element or verification
  condition remains.
- `FAIL`: a mandatory or central requirement is not met, contradicted, or
  unsupported.
- `NOT_APPLICABLE`: the criterion does not apply to the declared type, scope,
  rank, or route; explain why.

## Severity

- `BLOCKER`: prevents a defensible readiness conclusion or creates material
  integrity, rights, factual, classification, route, or eligibility risk.
- `MAJOR`: materially weakens correctness, coverage, synthesis, contribution,
  teaching usability, or route evidence.
- `MINOR`: bounded correction that does not change the central argument or
  route selection.
- `NOTE`: strength, optional improvement, or documented limitation that does
  not require revision.

Automatic blocker examples include invented or unverifiable citations,
plagiarism or unclear reuse, unlicensed central figures/tables, material factual
errors, unsupported central claims, wrong document classification, missing
required course scope, missing route identity, and a current-rules conclusion
based only on metadata or search snippets.

## Evidence And Locator Rules

- Use a stable manuscript locator: heading plus paragraph, page plus section,
  table/figure number, or outline anchor. `whole document` is not exact.
- In Markdown, quote the source's exact heading or anchor text in backticks; do
  not substitute a conceptual alias. In DOCX without stable pages, count Word
  document paragraphs in XML order as `P0001`, `P0002`, and so on, and add the
  visible heading or table/figure number. The validator checks quoted Markdown
  anchors and DOCX `P####` bounds when it can.
- Use a rule ID plus exact page, clause, section, annex, form field, or official
  HTML heading. A title or URL alone is not an exact locator.
- Distinguish absence of evidence from evidence of absence.
- Retain qualifying and contradictory material; narrow conclusions when the
  record does not support a stronger one.
- Treat an abstract, metadata record, index entry, or search snippet as a lead,
  not as evidence for a detailed criterion.

When page rendering is unavailable, continue a content assessment with stable
structural locators and state that visual findings remain unverified. Visual QA
is not a package-wide blocker unless the selected criterion depends on layout,
legibility, pagination, or rendered media; production preflight remains owned
by the writing skill.

In `REFERENCE_ONLY`, record the local criterion catalog and other assessment
references in the Rule ledger as `ADVISORY_ONLY` / `ADVISORY`. This is a
comprehensive source register, not a claim that those references are governing
law. Keep the Search log empty because no current-rule search occurred.

The validator confirms that the current input matches the recorded fingerprint
and path. It cannot prove the state of a file before the fingerprint was first
captured; use an intake manifest or trusted receipt hash when chain-of-custody
evidence is required.

## Numeric Scores

Do not create a readiness percentage, composite probability, or unofficial
quality score. If a verified governing rule defines a score, reproduce only the
applicable calculation, cite the exact rule locator, expose the evidence for
each component, and label the result `OFFICIAL_ONLY`. Keep qualitative findings
and blockers visible even when arithmetic meets a threshold.

## Scope-Specific Checks

- `assess-outline`: judge planned coverage, order, evidence, rights needs,
  contribution, reader journey, and route-critical missing sections. Do not
  treat a plan as proof that the final manuscript satisfies a criterion.
- `assess-chapter`: judge local correctness, depth, evidence, synthesis,
  terminology, examples, teaching use, citations, rights, and alignment.
- `assess-manuscript`: add cross-chapter unity, duplication, progression,
  front/back matter, terminology, reference integrity, contribution, and
  publication/dissemination evidence.
- `assess-route-readiness`: judge only the route facts and artifacts visible in
  the package against verified current rules. Report missing portfolio evidence
  without expanding into assessment of unrelated academic-work categories.

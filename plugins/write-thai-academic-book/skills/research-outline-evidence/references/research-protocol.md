# Research protocol

## Frame the search

Convert the main question and each outline topic or Matrix claim into a search
block. Record concepts, Thai/English synonyms, narrower and broader terms,
exclusions, population/context, mechanism or outcome, source type, and date
limits. Use date limits only when the question justifies them; retain
foundational sources alongside current work.

Search to test the claim, not merely to find text that agrees with it. Include
queries for limitations, competing explanations, adverse findings, and
replication when the claim is disputed or consequential.

## Search order

Use this order unless the discipline requires a documented exception:

1. User-supplied local files, existing source ledgers, and verified author work.
2. Primary research and systematic or high-quality review literature.
3. Current guidelines, standards, regulations, and official reports.
4. Authoritative books or monographs for stable foundations.
5. Institutional web pages for bounded contextual facts.

Do not use generic web pages to support specialist, causal, legal, regulatory,
or quantitative claims when a primary or official source exists. Preserve the
search channel and exact query in the Search log. Record zero-result searches
and access failures because they explain remaining gaps.

## Screen and appraise

Apply two-stage screening when volume requires it:

1. Screen title, abstract, summary, and metadata for scope and likely relevance.
2. Inspect full text or exact official text before including evidence.

Assess each source on:

- direct relevance to the exact claim;
- authority and source type;
- study design or traceability of the reported information;
- currency and applicability to the intended context;
- exact locator availability;
- access and reuse or adaptation rights;
- conflicts of interest, limitations, and contradictory findings.

Use these verification states:

- `VERIFIED_FULL_TEXT`: relevant full text inspected;
- `VERIFIED_OFFICIAL_TEXT`: current official text and locator inspected;
- `VERIFIED_LOCAL_SOURCE`: user-supplied source inspected and identified;
- `ABSTRACT_ONLY`: abstract inspected but full support not verified;
- `METADATA_ONLY`: title/citation record only;
- `INACCESSIBLE`: potentially relevant record cannot be inspected.

Only the first three states may be `INCLUDED`. Mark the other states
`PROVISIONAL` or `EXCLUDED` with a reason.

## Judge evidence sufficiency

Set a claim to `ADEQUATE` only when at least one included source directly
supports or appropriately qualifies the exact claim and has an exact locator.
Use multiple sources when needed for breadth, triangulation, or risk. Require a
current authoritative source for laws, standards, guidelines, official figures,
and other time-sensitive claims.

Set `PARTIAL` when evidence supports only part of the claim, is context-limited,
or still needs corroboration. Set `NONE` when no included evidence directly
addresses the claim. Never upgrade sufficiency because many metadata records
were found.

Keep the Claim, synthesis, sufficiency, and gap action internally consistent.
If the synthesis says the inspected evidence is only a case, does not cover the
whole Claim, or still needs another scholarly source, use `PARTIAL` even when
the available case itself is well verified. Use `ADEQUATE` only for the exact
bounded Claim as written.

When evidence conflicts, retain every material side, map the relation, explain
differences in population, method, context, or date, and propose narrower claim
wording or an author decision.

## Extract and cite safely

Record page, section, table, figure, paragraph, timestamp, or stable fragment.
Use paraphrase by default. Quote only when exact wording is necessary, keep it
short, and preserve the locator. Do not copy source figures or tables into the
package. Record rights separately from scholarly relevance; citation does not
grant reuse rights.

Deduplicate by DOI first, then stable URL, normalized citation/title, or local
path/hash. Keep the best verified record and link alternate versions in its
notes rather than presenting them as independent evidence.

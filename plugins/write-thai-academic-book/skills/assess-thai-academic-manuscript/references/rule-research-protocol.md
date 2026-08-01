# Official Rule Research Protocol

Use this protocol only after the user explicitly requests a current-rule search
or refresh. Search in Thai and English where useful.

## Authority Order

1. Local files and references supplied for the project.
2. The submitting institution's official regulation, announcement, academic
   personnel page, forms, and transition notices.
3. Official ก.พ.อ./สป.อว. criteria and incorporated amendments, starting from
   the official collection at
   `https://www.ops.go.th/th/content_page/item/13735-2025-12-01-09-01-19`.
4. Royal Gazette records at `https://ratchakitcha.soc.go.th/` when applicable.
5. Official institutional manuals or explanatory pages as advisory sources.

Never make one institution the default. The institution named by the author is
the route authority that must be researched. Use the Chiang Mai University
academic-rank index at `https://hr.oop.cmu.ac.th/academic/01` only as a test
fixture when CMU is the selected institution.

## Search Design

Construct queries from institution, rank, field, employment track when
relevant, route/method, document type, filing date, and terms for amendment,
repeal, transition, effective date, forms, dissemination, teaching evaluation,
and ethics. Record every material query and screening decision.

Search both the main regulation and linked materials. A current landing page
does not prove every linked PDF is current. Trace amendment chains and record:

- issuing authority and exact title;
- publication, effective, transition, and repeal dates;
- rank, field, track, method, and document types covered;
- source URL or local path;
- exact clause/page/annex/form locator;
- verification status and access date;
- documents amended, incorporated, or superseded;
- rights/use status.

## Verification

Use `VERIFIED_OFFICIAL_TEXT` only after opening the official text and checking
the exact relevant passage. Use `VERIFIED_LOCAL_SOURCE` for a readable local
copy whose provenance is recorded. Mark manuals `ADVISORY_ONLY`. Keep
`METADATA_ONLY` and `INACCESSIBLE` leads in the register but never use them as
included evidence for a current route decision.

When sources conflict, do not silently choose one. Record both, identify the
authority and effective-date issue, narrow the conclusion, and use
`UNRESOLVED` until the conflict is resolved. Mark an older rule `SUPERSEDED`
rather than deleting it.

## Freshness And Failure

Currentness is run-specific. Record the search date and assessment cutoff. Do
not reuse a prior `CURRENT` label without an explicit new refresh request.

If the official source cannot be reached, the amendment chain is incomplete,
or the filing date falls in an unresolved transition period, retain useful
provisional manuscript findings but set `rules_status: STALE` or `UNRESOLVED`
and `package_status: NEEDS_RULE_REFRESH` or `NEEDS_EVIDENCE`. Do not infer route
readiness.


# Evidence Package integration contract

## Canonical artifact

Use one Markdown source of truth:

```text
output/<project-id>/research/<scope-id>/evidence-package.md
```

Do not create a second editable JSON ledger. The validator may emit JSON as a
derived report. Do not edit an outline or Outline Matrix while producing the
package.

## Metadata

Start with a fenced `yaml` block containing exactly the template keys. Use:

- `mode`: `SCOPING` or `GAP_FILL`;
- `scope_type`: `BOOK`, `CHAPTER`, `SECTION`, `ARTICLE`, `COURSE`, or `OTHER`;
- `status` in `SCOPING`: `READY_FOR_MATRIX`, `NEEDS_REVISION`, or `BLOCKED`;
- `status` in `GAP_FILL`: `READY_FOR_HANDOFF`, `NEEDS_EVIDENCE`,
  `NEEDS_REVISION`, or `BLOCKED`;
- `human_subject_review`: `PENDING` or `PASS`.

Use ISO `YYYY-MM-DD` for `research_cutoff`. Use `-` only for `source_matrix` in
`SCOPING`; every other required metadata value must be substantive.

## Identifiers and anchors

- Search queries: `Q001`, `Q002`, ...
- Sources: `S001`, `S002`, ...
- Claims: `C001`, `C002`, ...
- Outline anchors: use a visible structural locator such as `OUT-CH03` or
  `OUT-CH03-S02`; do not depend on heading wording alone.
- Matrix anchors: `OM-R01`, `OM-R02`, ... matching the Matrix row order.

Identifiers remain stable when a record is updated. Do not renumber existing
records merely because a record is rejected or a row moves.

## Claim fingerprint

For each `GAP_FILL` claim:

1. trim the exact Matrix Claim cell;
2. collapse consecutive whitespace to one space;
3. lowercase Unicode text;
4. calculate SHA-256 over UTF-8;
5. store the first 12 hexadecimal characters as `sha256:<12-hex>`.

The validator repeats this calculation. A mismatch means the Matrix claim
changed after the package was mapped; use `NEEDS_REVISION`, inspect the new
claim, and remap evidence rather than silently reusing the old mapping.

## Controlled table values

Use these source types:

`LOCAL_USER_SOURCE`, `PRIMARY_RESEARCH`, `SYSTEMATIC_REVIEW`,
`GUIDELINE_STANDARD`, `OFFICIAL_REPORT`, `AUTHORITATIVE_BOOK`,
`INSTITUTIONAL_WEB`, or `OTHER`.

Use these source dispositions:

- `INCLUDED` for verified evidence used by a claim;
- `PROVISIONAL: <reason>` for promising but unverified material;
- `EXCLUDED: <reason>` for screened-out material.

Record currency as one of `CURRENT_AS_OF: YYYY-MM-DD`, `PUBLISHED: YYYY`,
`FOUNDATIONAL`, `HISTORICAL`, or `NOT_CHECKED`. An included current guideline,
standard, regulation, or institutional web claim must use `CURRENT_AS_OF`.
`HISTORICAL` may be included only for an explicitly historical claim.

Use `SUPPORTS`, `QUALIFIES`, `CONTRADICTS`, or `CONTEXT_ONLY` in the Relation
column. When a claim uses several sources, map relations as
`S001=SUPPORTS; S002=QUALIFIES`.

Use `ADEQUATE`, `PARTIAL`, or `NONE` for claim sufficiency. The Evidence cell
must pair each source ID with an exact locator, for example
`S001 @ p. 14; S002 @ section 3.2`.
Do not use `ADEQUATE` when the synthesis or gap action says the sources do not
cover the whole Claim or that another evidence source is still required.

Use `READY`, `HOLD`, or `AUTHOR_DECISION` for handoff status. A
`READY_FOR_HANDOFF` package requires `READY` for every Matrix row and cannot
contain unresolved material gaps.

## Matrix handoff

Preserve the Matrix's six semantic columns:

1. `ลำดับ`
2. `หัวข้อ`
3. `ผู้อ่านต้องทำได้`
4. `Claim`
5. `หลักฐาน`
6. `ตัวอย่าง/กิจกรรม`

The handoff table does not reproduce or replace the Matrix. Give the Matrix
owner only:

- Matrix anchor and current claim fingerprint;
- proposed content for the `หลักฐาน` cell using verified source locators;
- `KEEP` or proposed narrower Claim wording;
- `READY`, `HOLD`, or `AUTHOR_DECISION`.

If evidence is missing, write a precise
`[ต้องค้นหลักฐาน: <ชนิด/ประเด็น>]` requirement and use `HOLD`. Only
`build-outline-matrix` may apply the handoff and decide `READY_TO_DRAFT`.

## Status invariants

- `READY_FOR_MATRIX` requires a valid search log, at least one screened source,
  and claim-level evidence needs; named gaps are allowed.
- `READY_FOR_HANDOFF` requires every Matrix row to have a matching claim map,
  current fingerprint, included verified evidence, `ADEQUATE` sufficiency, and
  a `READY` handoff.
- `NEEDS_EVIDENCE` requires at least one `PARTIAL`/`NONE` mapping or `HOLD`.
- `NEEDS_REVISION` covers stale fingerprints, broken anchors, malformed
  mappings, or scope drift.
- `BLOCKED` covers missing main question, intended reader, bounded scope, or an
  unusable source basis.

No package status is human approval or permission to draft prose.

## Draft Handoff

The writing workflow may consume this package only alongside a six-column
Matrix at `READY_TO_DRAFT`. If the Matrix required no gap-fill pass, its
`source_basis` must identify the `SCOPING/READY_FOR_MATRIX` package. Otherwise
the current `GAP_FILL/READY_FOR_HANDOFF` package must name the exact Matrix and
carry current Claim fingerprints. Re-run both companion validators and the
cross-skill workflow validator after any outline, Claim, Matrix, or evidence
change.

---
name: research-outline-evidence
description: Research and verify evidence for outlines, claims, and six-column Outline Matrices through reproducible local-first searches, exact locators, claim-evidence maps, and Matrix-ready handoffs.
---

# Research Outline Evidence

Create a traceable Evidence Package between outline planning and claim-led
drafting. Search local materials first, then scholarly and official sources.
Never invent a citation, source passage, author contribution, or verification
status.

## Select one mode

- Use `SCOPING` when an outline exists but no Outline Matrix exists. Map the
  evidence landscape, queries, usable sources, planned claims, and explicit
  gaps. A valid result may become `READY_FOR_MATRIX` even when named evidence
  gaps remain.
- Use `GAP_FILL` when an Outline Matrix exists or the user identifies Matrix
  claims that need evidence. Verify every in-scope Matrix claim and prepare a
  handoff. Use `READY_FOR_HANDOFF` only when every material claim has adequate
  verified evidence.

Do not combine the modes in one fresh package. Complete `SCOPING`, let the
Outline Matrix owner create or revise the Matrix, then update the package in a
separate `GAP_FILL` pass.

## Establish inputs and output

Inspect supplied files and existing project artifacts before searching. For a
Book Drafter project, read the approved project brief and `project/outline.md`.
In `GAP_FILL`, also read the current Outline Matrix. Establish:

- project and scope identifiers;
- main question, intended reader, scope, and exclusions;
- current outline and Matrix paths;
- available local sources and author works;
- discipline, languages, currency needs, and high-risk claim types.

Return `BLOCKED` when the main question, intended reader, or bounded source
scope cannot be established. Do not manufacture missing context.

Copy `assets/evidence-package-template.md` to:

```text
output/<project-id>/research/<scope-id>/evidence-package.md
```

For non-Book-Drafter work, use the user-selected output root while preserving
the `research/<scope-id>/evidence-package.md` suffix. Never edit the source
outline or Matrix.

## Research systematically

Read `references/research-protocol.md` before searching. Then:

1. Inventory local files and existing ledgers before external search.
2. Convert each bounded outline topic or Matrix claim into Thai and English
   concepts, synonyms, exclusions, and source-type filters.
3. Search in the source hierarchy defined by the protocol. Record every
   material query, including zero-result and unsuccessful searches.
4. Screen by relevance, authority, method, currency, exact support, access, and
   rights. Record exclusions and do not hide contrary evidence.
5. Verify included evidence in full text or exact official text. Treat
   abstract-only, metadata-only, and inaccessible records as provisional, not
   evidence for a detailed claim.
6. Extract only the minimum needed synthesis with exact page, section, table,
   figure, paragraph, timestamp, or stable fragment locator.
7. Map each source as `SUPPORTS`, `QUALIFIES`, `CONTRADICTS`, or
   `CONTEXT_ONLY`. Narrow an overbroad claim instead of forcing support.

Do not use a fixed citation count as a proxy for sufficiency. Require
corroboration when a claim is causal, quantitative, disputed, fast-changing,
legal, regulatory, safety-related, or otherwise high risk.

## Build the Evidence Package

Read `references/integration-contract.md` and preserve its controlled values.
Use stable `Q###`, `S###`, and `C###` identifiers. In `GAP_FILL`, use
`OM-R##` Matrix anchors and the documented claim fingerprint so later Matrix
drift is detectable.

Fill all sections of the template:

- metadata and research protocol;
- reproducible search log;
- included, provisional, and excluded source ledger;
- claim-evidence map with exact locators and limitations;
- Matrix handoff with proposed evidence-cell text and any proposed claim
  adjustment;
- conflicts, unresolved gaps, and author decisions.

Write the package in Thai by default. Preserve original source titles,
technical terms, identifiers, citation metadata, and exact search queries in
their source language.

The handoff is advisory. Do not insert it into the Matrix. Do not set
`human_subject_review: "PASS"` without explicit subject-expert or author
confirmation.

## Validate and hand off

Run:

```powershell
python scripts/validate_evidence_package.py --input <evidence-package.md> --outline <outline.md>
```

For `GAP_FILL`, add the current Matrix:

```powershell
python scripts/validate_evidence_package.py --input <evidence-package.md> --outline <outline.md> --matrix <outline-matrix.md>
```

Use `--json-output <report.json>` only when a machine-readable report is
needed. The validator checks structure and traceability, not disciplinary truth.

Report the package path, mode, status, verified-source count, unresolved gaps,
human-review state, and next action:

- `READY_FOR_MATRIX`: give the package to `build-outline-matrix` as source
  basis.
- `READY_FOR_HANDOFF`: give the handoff to `build-outline-matrix`; only that
  skill may revise the Matrix and decide `READY_TO_DRAFT`.
- `NEEDS_EVIDENCE`: report missing or provisional evidence and keep the Matrix
  evidence-ready decision blocked.
- `NEEDS_REVISION`: report stale anchors, claim drift, or malformed mappings.
- `BLOCKED`: report the missing essential input or unusable source scope.

Evidence Package status is an agent finding, not human approval and not
authorization to draft prose.

With `$orchestrate-thai-academic-writing`, run its handoff validator before
Matrix work and `draft-chapter`; keep the package at its canonical project path.

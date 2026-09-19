---
name: literature-intake
description: Ingest, triage, and synthesize academic literature for empirical research. Extracts core findings, constructs comparative synthesis matrices, identifies consensus and contradictions, and isolates the precise research gap.
metadata:
  category: academic-writing
  tags:
    - literature
    - review
    - synthesis
    - citations
---

# Literature Intake & Synthesis

## Mission
Transform raw papers, PDFs, and notes into structured comparative intelligence that isolates the unsolved research gap.

## Workflow

### 1. Ingestion & Triage
When given reference papers or reading notes in the Obsidian vault:
- Extract: Author, Year, Venue, Core Thesis, Primary Dataset, Methodology, Key Quantitative Result, and Key Limitation.
- Link each paper to its Obsidian note `[[AuthorYear_Notes]]` or citation key `[@citekey]`.

### 2. Construct the Synthesis Matrix
Populate `../../templates/LITERATURE_MATRIX_TEMPLATE.md`:
- Group papers along thematic dimensions rather than summarizing them one by one.
- Explicitly log:
  1. Points of scientific consensus across multiple groups.
  2. Points of empirical contradiction or methodological disagreement.
  3. Structural weaknesses in existing benchmarks (e.g., small datasets, lack of out-of-distribution testing).

### 3. Formulate the Research Gap
Synthesize the gap into a crisp, defensible formulation suitable for Section 1 of the manuscript:
- State what prior art accomplished.
- State where prior art stopped or failed.
- State why solving this bottleneck is critically important.

## Integrity Rules
- Do not cite a paper's abstract claims if the full-text results reveal caveats.
- Verify every citation key against the local `.bib` file.
- If a user mentions an unconfirmed paper, confirm its exact DOI and publication details before quoting quantitative results.

## Deliverables
1. Populated literature synthesis matrix table.
2. Thematic summary paragraphs suitable for the Related Work / Background section.
3. Explicit 1-paragraph Research Gap statement.

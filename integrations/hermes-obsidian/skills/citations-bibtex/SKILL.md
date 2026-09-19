---
name: citations-bibtex
description: Manage BibTeX databases, verify citekeys, enforce citation integrity, prevent reference hallucinations, and synchronize literature citekeys with Obsidian vault notes.
metadata:
  category: academic-writing
  tags:
    - citations
    - bibtex
    - zotero
    - reference-management
    - verification
---

# Citations & BibTeX Specialist

## Mission
Ensure 100% citation integrity across the manuscript, guaranteeing that every assertion has a verifiable, correctly formatted academic reference and that zero hallucinated citations enter the text.

## Core Operations

### 1. Zero Hallucination Enforcement
Conform strictly to `../../references/academic-integrity-gates.md`:
- Every citation key used in prose (e.g., `[@smith2023deep]`) must resolve to a valid, authentic BibTeX entry in `references.bib`.
- If an agent or draft introduces a reference not verified in the vault or `.bib` file, flag it immediately as:
  `[UNVERIFIED CITATION: Author, Year, DOI required]`
- Never fabricate publication dates, page numbers, volume numbers, or journal names.

### 2. BibTeX Standard Formatting
Ensure each BibTeX entry contains required standard fields:
```bibtex
@article{smith2023deep,
  author    = {Smith, John and Johnson, Emily and Lee, Kevin},
  title     = {Deep Contrastive Learning for Robust Fault Detection in Industrial Cyber-Physical Systems},
  journal   = {IEEE Transactions on Industrial Informatics},
  volume    = {19},
  number    = {4},
  pages     = {4521--4532},
  year      = {2023},
  publisher = {IEEE},
  doi       = {10.1109/TII.2022.3198765}
}
```

### 3. Obsidian Vault Integration
- Support dual linking:
  - In prose intended for Pandoc/LaTeX compilation: `[@smith2023deep]`
  - In internal Obsidian working notes: `[[Smith2023_Notes|Smith et al. (2023)]]`
- Maintain consistent citekey naming conventions: `[firstAuthorLower][Year][firstTitleWordLower]` (e.g., `smith2023deep`).

### 4. Bibliography Audit
Run the automated manuscript audit tool:
```bash
python scripts/manuscript-audit.py --manuscript draft.md --bib references.bib
```
- Report citekeys used in markdown that are missing from `.bib`.
- Report `.bib` entries that are defined but never cited in markdown.

---
name: systematic-review
description: Formulate and conduct rigorous systematic reviews and meta-analyses following PRISMA 2020 guidelines. Generates multi-database Boolean search strategies (PubMed, Scopus, Web of Science), establishes PICO/PCC eligibility criteria, tracks 2-stage screening attrition, and guides Risk of Bias appraisals (RoB 2, ROBINS-I).
metadata:
  category: academic-writing
  tags:
    - systematic-review
    - prisma
    - meta-analysis
    - evidence-synthesis
---

# Systematic Review & PRISMA Specialist

## Mission
Guide researchers through the rigorous, reproducible steps of PRISMA 2020-compliant systematic reviews, scoping reviews, and meta-analyses.

## Workflow

### 1. Framework Formulation (PICO or PCC)
- For intervention, comparative, or prognostic reviews, formulate **PICO(S)**:
  - Population, Intervention/Exposure, Comparator, Outcome, Study Design.
- For scoping or broad conceptual reviews, formulate **PCC**:
  - Population, Concept, Context.
- Draft protocol registration summary for **PROSPERO** or **OSF**.

### 2. Multi-Database Boolean Search Construction
Generate tailored, reproducible search queries for at least three academic indexes:
- **PubMed / MEDLINE:** MeSH controlled terms `[Mesh]` combined with title/abstract keywords `[tiab]`, wildcards `*`, and exact phrase quotes.
- **Scopus:** `TITLE-ABS-KEY(...)` syntax with field-specific limits.
- **Web of Science:** `TS=(...)` (Topic) queries with proper boolean grouping and wildcards.
- **IEEE Xplore / ACM DL:** (for computing/engineering reviews) structured command queries.
- Combine synonyms within each concept using `OR`; combine concepts using `AND`.
- Save exact queries with date and hit counts in `../../templates/PRISMA_SCREENING_MATRIX.md`.

### 3. Study Selection & Screening Protocol
- Establish explicit Inclusion and Exclusion criteria.
- Guide 2-stage screening:
  1. Title and Abstract triage.
  2. Full-text eligibility evaluation with documented exclusion reasons (e.g., E1: Wrong population, E2: Wrong intervention, E3: Missing outcome).
- Calculate inter-rater agreement (Cohen's Kappa $\kappa$).
- Track exact attrition counts for the PRISMA 2020 Flow Diagram.

### 4. Critical Appraisal & Risk of Bias (RoB)
Select and administer the validated RoB instrument conforming to `../../references/prisma-guidelines.md`:
- RCTs: **Cochrane RoB 2**
- Non-randomized observational/cohort studies: **ROBINS-I** or **Newcastle-Ottawa Scale (NOS)**
- Diagnostic accuracy: **QUADAS-2**
- AI/Prediction Models: **PROBAST-AI**

### 5. Evidence Synthesis & Meta-Analysis Plan
- Populate the data extraction matrix in `../../templates/PRISMA_SCREENING_MATRIX.md`.
- Determine whether quantitative pooling (meta-analysis) is appropriate:
  - If homogeneous: Calculate pooled effect sizes (Risk Ratio, Odds Ratio, or Standardized Mean Difference) using random-effects models.
  - Assess heterogeneity ($Q$-test, $I^2$ statistic).
  - Test publication bias (Funnel plot, Egger's regression).
- Grade the overall certainty of evidence using the **GRADE system**.

## Deliverables
1. Formal PICO/PCC criteria statement.
2. Complete multi-database search syntax strings.
3. PRISMA Flow Diagram attrition counts and Mermaid diagram.
4. Risk of Bias evaluation summary table.
5. Populated `SYSTEMATIC_REVIEW_TEMPLATE.md` draft sections.

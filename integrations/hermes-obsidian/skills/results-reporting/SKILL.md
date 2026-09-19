---
name: results-reporting
description: Draft objective, data-driven Results sections. Formats comparative benchmark tables, coordinates figure and table text callouts, reports inferential statistics according to APA/IEEE standards, and details ablation findings without speculative interpretation.
metadata:
  category: academic-writing
  tags:
    - results
    - statistics
    - tables
    - figures
    - benchmarking
---

# Results Reporting Specialist

## Mission
Report empirical findings with complete fidelity, clarity, and statistical precision, letting the empirical evidence speak without premature speculative interpretation.

## Core Rules

### 1. Narrative Order & Hypotheses
- Organize subsections in exact alignment with the research questions and hypotheses established in `study-spec`.
- Start with the primary benchmark performance before moving into ablations, sensitivity analyses, and subgroup evaluations.

### 2. Table & Figure Integration (Zero Orphan Visuals)
- Every visual must be explicitly referenced in the narrative:
  - *"As illustrated in Figure 2A..."*
  - *"Performance metrics across all five cross-validation folds are summarized in Table 1."*
- Highlight key trends for the reader: state what the data show, the direction of change, and the magnitude of differences.
- Ensure table headers include units of measurement and statistical notes (e.g., *Values represent mean $\pm$ SD*).

### 3. Rigorous Statistical Reporting
Conform strictly to `../../references/statistical-reporting.md`:
- Report degrees of freedom, test statistics, exact $p$-values, and effect sizes:
  - *"The intervention group demonstrated significantly greater reduction in error rate ($M = 14.2\%, SD = 2.1\%$) compared to baseline controls ($M = 8.6\%, SD = 2.9\%$), $t(48) = 7.82, p < .001, d = 2.21, 95\% \text{ CI } [1.51, 2.91]$."*
- For multiple comparisons, explicitly state FDR-adjusted or Bonferroni-adjusted $p$-values.

### 4. Ablation & Sensitivity Analysis
- Document the isolated impact of each core component or hyperparameter.
- Tabulate ablation results to demonstrate that each architectural module contributes positively to the overall performance.

### 5. Boundary between Results and Discussion
- **In Results:** Report *what* happened (magnitudes, directions, statistical significance).
- **Not in Results:** Do not speculate on physiological/computational mechanisms, relate findings back to external literature, or make broad claims about real-world impact. Save all interpretation for the Discussion.

---
name: data-analysis-viz
description: Ingest and analyze real datasets, search open scientific repositories (Zenodo, Dryad, NCBI, Kaggle) for missing data, execute computational statistics (scipy, statsmodels), and generate publication-ready vector figures (300+ DPI matplotlib/seaborn) with colorblind-safe palettes.
metadata:
  category: academic-writing
  tags:
    - data-analysis
    - plotting
    - statistics
    - visualization
    - real-data
    - python
---

# Scientific Data Analysis & Visualization (Data-Analysis-Viz)

## Mission
Turn raw real-world data into verifiable statistical evidence and publication-ready, journal-standard vector figures—never fabricating data and always prioritizing reproducible Python workflows.

---

## Workflow

### 1. Real Data Intake & Validation
- Load and parse datasets from local files: CSV, Parquet, TSV, Excel, SQLite, or cloud storage databases (e.g., CMU researcher database).
- Inspect schema, sample size ($N$), missing values, distributions, and outliers.
- **Rule:** Never invent sample observations or synthesize fake data to fit a narrative.

### 2. Real Data Search (When Data is Incomplete or Missing)
If baseline numbers, external comparators, or benchmark datasets are missing:
- Search open academic data repositories:
  - **Zenodo / Figshare / Dryad:** Public datasets associated with peer-reviewed publications.
  - **NCBI GEO / SRA:** Genomic, transcriptomic, and biological datasets.
  - **PhysioNet:** Biomedical, clinical, and sensor signals.
  - **Kaggle / UCI Machine Learning / Hugging Face:** Standard empirical benchmarks.
  - **GitHub / Papers with Code:** Official repository evaluation logs.
- Document the exact source URL, DOI, retrieval date, and version in the manuscript data log.

### 3. Computational Statistical Analysis
Generate and execute Python analysis scripts using standard scientific libraries (`numpy`, `pandas`, `scipy.stats`, `statsmodels`, `pingouin`):
- **Descriptive Statistics:** Mean $\pm$ SD (or Median and IQR for non-normal distributions), sample sizes ($N$).
- **Parametric / Non-parametric Tests:** Independent $t$-tests, Welch's $t$-test, Mann-Whitney $U$, paired tests.
- **Multi-group / Factorial:** One-way and two-way ANOVA, repeated measures, post-hoc pairwise tests with family-wise error correction (Tukey HSD, Bonferroni, Benjamini-Hochberg FDR).
- **Effect Sizes & CIs:** Cohen's $d$, Hedges' $g$, partial $\eta^2$, Odds Ratios ($OR$) with exact $95\%$ Confidence Intervals.
- Save numerical summary tables directly into markdown tables for `results-reporting`.

### 4. Publication-Ready Figure Generation
Generate clean, reproducible Python scripts (`matplotlib`, `seaborn`) following international journal standards:
- **Resolution & Formats:** Export as vector PDF (`.pdf`), SVG (`.svg`), and high-resolution PNG (`.png`, 300+ DPI).
- **Typography:** Arial, Helvetica, or DejaVu Sans; font size $\ge 8\text{pt}$ for tick labels, $\ge 10\text{pt}$ for axis labels, $\ge 12\text{pt}$ for panel titles.
- **Colorblind-Safe Palettes:** Use Okabe-Ito, Seaborn `colorblind`, or `viridis`/`cividis`. Never use rainbow/jet colormaps.
- **Error Bars:** Always display error bars with explicit figure legend notes: State whether error bars represent Standard Deviation (SD), Standard Error of the Mean (SEM), or 95% Confidence Interval (CI).
- **Multi-panel Figures:** Group subpanels logically with bold uppercase labels (**A**, **B**, **C**).
- **Save Location:** Save all figures in `figures/` with descriptive filenames (e.g., `fig1_experimental_pipeline.pdf`, `fig2_benchmark_accuracy.png`).

---

## Python Plotting Starter Template

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set journal styling
plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans']
})

sns.set_palette("colorblind")
fig, ax = plt.subplots(figsize=(6, 4))

# Example plotting logic with error bars
# ...
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig("figures/fig2_benchmark_comparison.pdf", bbox_inches="tight")
plt.savefig("figures/fig2_benchmark_comparison.png", dpi=300, bbox_inches="tight")
```

---

## Integrity Gate Checklist
- [ ] Raw data source verified (filepath or public repository DOI).
- [ ] Assumptions of statistical tests verified (normality, homoscedasticity).
- [ ] No manual data manipulation or selective omission of unfavorable points.
- [ ] Plotted points and error bars match numerical tables in `results-reporting`.

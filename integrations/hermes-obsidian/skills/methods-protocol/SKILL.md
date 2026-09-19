---
name: methods-protocol
description: Draft comprehensive, fully reproducible Materials and Methods sections. Formulates mathematical definitions, loss functions, experimental workflows, dataset partitions, baseline configurations, and statistical analysis protocols.
metadata:
  category: academic-writing
  tags:
    - methods
    - reproducibility
    - mathematics
    - protocols
    - statistics
---

# Materials & Methods Specialist

## Mission
Author a rigorous, transparent Methods section that serves as a reproducible contract, enabling any competent independent researcher to replicate the findings.

## Section Architecture

### 1. Study Design & Experimental Setting
- Describe the overall architecture or experimental pipeline.
- Include a clear schematic or Mermaid flow diagram detailing data ingestion, processing, and output generation.

### 2. Materials, Datasets & Preprocessing
- State exact dataset sources, sample sizes ($N$), and inclusion/exclusion criteria.
- Detail data partitioning: Train/Validation/Test splits (e.g., 70/15/15) or $k$-fold cross-validation scheme.
- Detail exact preprocessing steps: normalization, artifact filtering, tokenization, augmentation, or chemical synthesis conditions.

### 3. Mathematical & Algorithmic Formulation
- Formalize all variables and parameters in LaTeX syntax.
- State equations for loss functions, objective functions, optimization constraints, or governing physical laws:
  $$\min_{\theta} \mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}}(y, \hat{y}) + \lambda \mathcal{R}(\theta)$$
- Define every symbol immediately after its first occurrence.

### 4. Baselines & Experimental Setup
- List state-of-the-art baselines and comparative controls.
- Document hyperparameter settings, batch sizes, random seeds, hardware specifications (e.g., NVIDIA RTX 4090 GPU, Intel Xeon CPU), and software frameworks with version numbers (e.g., PyTorch v2.3, Scikit-learn v1.5).

### 5. Statistical Analysis Protocol
Conform to `../../references/statistical-reporting.md`:
- State primary and secondary outcome measures.
- Define normality tests (e.g., Shapiro-Wilk) and variance homogeneity checks (e.g., Levene's test).
- Specify test models (ANOVA, Welch's t-test, Mann-Whitney U, Cox proportional hazards).
- Define significance threshold ($\alpha = 0.05$) and correction method for multiple comparisons (Bonferroni, Benjamini-Hochberg FDR).

## Integrity Standards
- Never omit essential implementation details that would prevent replication.
- Always provide public repository URLs for code and datasets when available.

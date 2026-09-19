# IMRaD Standard Guide (Introduction, Methods, Results, and Discussion)

The **IMRaD** format is the standard architecture for empirical scientific manuscripts across medicine, natural sciences, engineering, and empirical social sciences.

---

## Word Count & Proportional Budget

For a standard full research paper of 5,000 to 8,000 words (excluding references):

| Section | Recommended Proportion | Word Count Target (6,000-word paper) | Key Focus |
| :--- | :---: | :---: | :--- |
| **Title & Abstract** | ~5% | ~250–300 words | Hook, gap, core finding, significance |
| **Introduction** | ~15–20% | ~800–1,200 words | Context, problem, gap, contributions |
| **Methods** | ~25–30% | ~1,500–2,000 words | Replicability, design, data, analysis |
| **Results** | ~25–30% | ~1,500–2,000 words | Empirical findings, statistics, figures |
| **Discussion** | ~20–25% | ~1,200–1,800 words | Interpretation, literature, limitations |
| **Conclusion** | ~5% | ~200–400 words | Final synthesis, future trajectory |

---

## 1. Introduction: The Funnel Pattern
The Introduction moves from broad background to narrow, specific contribution:
1. **The Broad Domain & Significance:** Why does this problem matter to the field or society?
2. **Current State of the Art:** What do we already know? (Cite key recent papers).
3. **The Problem / Gap:** What critical limitation, contradiction, or unanswered question remains? (Use explicit contrast words: "However, existing methods fail to...", "Despite these advances, the mechanism governing X remains unresolved...").
4. **The Proposed Study & Objectives:** What did this study specifically do to address the gap?
5. **Key Contributions / Value Add:** Bullet points detailing primary novel contributions.
6. **Paper Roadmap (optional in short papers, standard in CS/Engineering):** Outline of subsequent sections.

---

## 2. Methods: The Reproducibility Contract
The Methods section must provide sufficient operational detail for an independent researcher to replicate the entire study:
- **Study Design & Setting:** Empirical paradigm, longitudinal/cross-sectional, control vs. treatment.
- **Participants / Samples / Datasets:** Source, inclusion/exclusion criteria, demographics, sample size justification / power calculation.
- **Apparatus / Materials / Reagents:** Model numbers, suppliers, concentrations, environmental conditions.
- **Procedures / Experimental Protocol:** Step-by-step sequential workflow.
- **Algorithmic Formulation / Mathematical Models:** Formal variable definitions, loss functions, optimization techniques.
- **Statistical Analysis Plan:** Hypotheses, primary outcome metrics, normality tests, models (ANOVA, GLM, Mixed Models), significance threshold ($\alpha = 0.05$), software packages with versions.

---

## 3. Results: Objective Findings Narrative
The Results section reports findings without speculative interpretation:
- **Logical Sequencing:** Group by sub-questions or hypotheses, matching the order introduced in Methods.
- **Data Integration:** Every table and figure must be explicitly cited in the text (e.g., "(Figure 3A)", "as detailed in Table 2").
- **No Orphan Visuals:** Do not present a figure without text explaining what the reader should notice in the trends or distributions.
- **Report Exact Statistics:** Always include degrees of freedom, test statistics, exact p-values, and effect sizes (e.g., $F(2, 45) = 4.82, p = .013, \eta_p^2 = .18$).

---

## 4. Discussion: The Inverted Funnel
The Discussion mirrors the Introduction in reverse, expanding from the study's specific findings outward to the broader discipline:
1. **Summary of Key Findings:** Brief recap of the most important empirical results (1 paragraph, no duplicate statistical printouts).
2. **Contextualization with Prior Literature:**
   - Where do our results agree with previous work?
   - Where do they diverge, and what methodological or biological differences explain the divergence?
3. **Underlying Mechanisms / Theoretical Interpretation:** Why did the results occur this way?
4. **Practical / Clinical / Engineering Implications:** How can practitioners or researchers use these findings?
5. **Limitations:** Honest self-appraisal of potential biases, confounding variables, sample size limits, and measurement precision.
6. **Future Research:** 2–3 concrete, actionable directions for subsequent investigation.

---

## 5. Conclusion
A succinct concluding section stating the primary takeaway message and broader perspective, avoiding simple repetition of the Abstract.

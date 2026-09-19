# Statistical Reporting Standards (APA & IEEE Standards)

Precision in quantitative statistical reporting is vital to withstand reviewer scrutiny. This guide outlines standard reporting formats for descriptive and inferential statistics.

---

## 1. General Principles
- **Report Exact p-Values:** Never report "p < .05" or "p = NS" unless p is below the machine/table limit, in which case report `$p < .001$`.
- **Preceding Zero Rule:**
  - If a statistic can exceed 1 (e.g., $F$, $t$, $\chi^2$, $z$, $d$, $M$, $SD$), write the leading zero: `$F(1, 84) = 4.25$`.
  - If a statistic cannot exceed 1 (e.g., $p$, $r$, $R^2$, $\alpha$, $\beta$), omit the leading zero: `$p = .023$`, `$r = .48$`.
- **Effect Sizes are Mandatory:** A p-value without an effect size only indicates sample size sensitivity. Always report effect size with confidence intervals.

---

## 2. Common Inferential Tests

### Independent Samples t-Test
- **Formula Format:** `$t(\text{df}) = \text{value}, p = \text{value}, d = \text{value}, 95\% \text{ CI } [\text{LL}, \text{UL}]$`
- *Example:* "An independent-samples t-test revealed that the fine-tuned model achieved significantly higher precision ($M = 88.4\%, SD = 3.2\%$) than the baseline model ($M = 81.1\%, SD = 4.5\%$), $t(58) = 7.23, p < .001, d = 1.87, 95\% \text{ CI } [1.28, 2.45]$."

### Analysis of Variance (ANOVA)
- **Formula Format:** `$F(\text{df}_{\text{between}}, \text{df}_{\text{within}}) = \text{value}, p = \text{value}, \eta_p^2 = \text{value}$`
- *Example:* "A one-way ANOVA demonstrated a significant main effect of learning rate on validation loss, $F(2, 42) = 14.89, p < .001, \eta_p^2 = .415$. Post-hoc Tukey HSD tests indicated that $\eta = 10^{-4}$ outperformed both $10^{-3}$ ($p = .002$) and $10^{-5}$ ($p < .001$)."

### Chi-Square Test of Independence
- **Formula Format:** `$\chi^2(\text{df}, N = \text{sample}) = \text{value}, p = \text{value}, V = \text{value}$`
- *Example:* "A chi-square test of independence showed a significant association between intervention exposure and clinical remission, $\chi^2(1, N = 240) = 8.64, p = .003, \phi = .19$."

### Multiple Linear / Logistic Regression
- Report unstandardized coefficients ($B$) with standard errors ($SE$), standardized coefficients ($\beta$), test statistic ($t$ or $z$), $p$-value, and confidence intervals.
- For Logistic Regression, report Odds Ratio ($OR = \exp(B)$) with $95\%$ CI.
- *Example:* "In the multivariable logistic model, baseline ferritin level was independently associated with disease progression ($OR = 1.64, 95\% \text{ CI } [1.22, 2.21], p = .001$)."

---

## 3. Machine Learning & Computational Benchmarking
- **Never report single-point evaluations without variance:** Always report cross-validation mean and standard deviation:
  - *Preferred:* "Accuracy = $94.3 \pm 0.8\%$ across 10-fold cross-validation."
  - *Unacceptable:* "Accuracy = $94.3\%$."
- **Multiple Metrics:** Report precision, recall, macro-F1, AUROC, and latency (ms/sample) alongside parameter count.
- **Statistical Significance of Model Comparisons:** When comparing two architectures on benchmark datasets, conduct Wilcoxon signed-rank test or paired t-test across benchmark folds/tasks.

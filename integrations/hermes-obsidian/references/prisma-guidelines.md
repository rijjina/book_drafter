# PRISMA 2020 Guidelines & Systematic Review Standard

This reference document outlines the methodology, reporting standards, and workflow for conducting and reporting high-impact Systematic Reviews and Meta-Analyses conforming to the **PRISMA 2020 Statement** (Preferred Reporting Items for Systematic Reviews and Meta-Analyses).

---

## 1. Study Formulation Frameworks

Before executing a search, establish structured eligibility criteria using an internationally accepted framework:

### PICO / PICOS (Intervention & Clinical Studies)
- **P (Population / Participants):** Detailed demographic, condition, or sample characteristics.
- **I (Intervention / Exposure):** Specific technique, drug, treatment, algorithmic method, or experimental condition.
- **C (Comparator / Control):** Placebo, standard of care, baseline model, or alternative method.
- **O (Outcomes):** Primary and secondary endpoints (e.g., mortality, accuracy, latency, toxicity, cost).
- **S (Study Design):** RCTs, cohort studies, observational studies, or experimental benchmarks.

### PCC (Scoping & Exploratory Reviews)
- **P (Population):** Relevant subjects or entities.
- **C (Concept):** The overarching phenomenon, paradigm, algorithm, or concept examined.
- **C (Context):** Geographic, clinical, educational, or computational environment.

---

## 2. Protocol Registration & Reporting Checklist

- **Protocol Registration:** Register prior to screening in **PROSPERO** (health/biomedical), **OSF (Open Science Framework)**, or **Inplasy**. Record registration number.
- **PRISMA 2020 27-Item Checklist:** All 27 checklist items must be addressed in the final manuscript.
  - Title: Identify the report as a systematic review (or meta-analysis).
  - Abstract: Structured (Background, Methods, Results, Discussion, Registration).
  - Methods: Databases searched, date range, full search strategy, screening process, data extraction items, RoB tools, synthesis methods.
  - Results: Study selection (PRISMA flow), study characteristics, RoB appraisals, synthesis of results, certainty of evidence.
  - Discussion: Limitations of evidence, limitations of review processes, implications.

---

## 3. Comprehensive Multi-Database Search Strategy

Systematic reviews require querying at least **three major academic databases**:
- **Biomedical & Life Sciences:** PubMed / MEDLINE, Embase, Cochrane Library.
- **Multidisciplinary & STEM:** Scopus, Web of Science Core Collection, Dimensions.
- **Computing & Engineering:** IEEE Xplore, ACM Digital Library, arXiv.

### Boolean Query Engineering Rules
1. **Combine within concepts using `OR`:** `(conceptA1 OR conceptA2 OR conceptA3)`
2. **Combine between concepts using `AND`:** `(Concept A terms) AND (Concept B terms) AND (Concept C terms)`
3. **Use controlled vocabulary and free text:**
   - Controlled vocabulary: MeSH terms (e.g., `"Artificial Intelligence"[Mesh]`)
   - Free-text synonyms with wildcards/truncation: `("machine learning"[tiab] OR "deep learning"[tiab] OR neural network*[tiab])`
4. **Reproducibility:** Save exact query strings with date executed, platform, and total hits retrieved.

---

## 4. Screening Workflow & PRISMA Flow Diagram

Systematic reviews must document study attrition through four mandatory phases:

```text
[ Identification ]
  ├── Total records identified through database searching (n = X)
  ├── Total records from registers, websites, citation chasing (n = Y)
  └── Duplicates removed (automated + manual) (n = Z)
[ Screening ]
  ├── Records screened by Title & Abstract (n = A)
  └── Records excluded based on predefined criteria (n = B)
[ Eligibility ]
  ├── Full-text articles retrieved & assessed for eligibility (n = C)
  └── Full-text articles excluded, with specific reasons documented (n = D):
       ├── Reason 1: Wrong population (n = d1)
       ├── Reason 2: Wrong intervention/comparator (n = d2)
       ├── Reason 3: Insufficient outcome data (n = d3)
       └── Reason 4: Non-peer reviewed / abstract only (n = d4)
[ Included ]
  ├── Total studies included in qualitative synthesis (n = E)
  └── Studies included in quantitative synthesis / meta-analysis (if applicable) (n = F)
```

- **Dual Independent Screening:** Minimum 2 reviewers screening independently; discrepancies resolved by consensus or a third senior reviewer. Report Cohen's Kappa ($\kappa$) or percentage agreement.

---

## 5. Critical Appraisal & Risk of Bias (RoB) Tools

Select the appropriate validated appraisal instrument based on study design:

| Study Design | Recommended Assessment Instrument | Focus Domains |
| :--- | :--- | :--- |
| **Randomized Controlled Trials** | **Cochrane RoB 2** | Randomization, deviations from intervention, missing outcome data, outcome measurement, selective reporting. |
| **Non-Randomized Interventions** | **ROBINS-I** | Confounding, participant selection, intervention classification, missing data. |
| **Observational Studies (Cohort/Case-Control)** | **Newcastle-Ottawa Scale (NOS)** | Selection of cohorts, comparability of cohorts, assessment of outcome. |
| **Diagnostic Accuracy Studies** | **QUADAS-2** | Patient selection, index test, reference standard, flow and timing. |
| **Qualitative Studies** | **CASP Checklist** | Research design appropriateness, recruitment, reflexivity, ethical issues. |
| **Machine Learning / AI Clinical Models** | **PROBAST-AI / TRIPOD+AI** | Participants, predictors, outcome, sample size, model performance optimism. |

---

## 6. Synthesis & Meta-Analysis Standards

- **Qualitative Synthesis:** Construct a comparative synthesis matrix grouping studies by intervention type, population, or methodology.
- **Quantitative Meta-Analysis (if applicable):**
  - **Effect Size Metric:** Odds Ratio (OR), Relative Risk (RR), Standardized Mean Difference (Hedges' $g$ or Cohen's $d$).
  - **Heterogeneity Evaluation:** Cochran's $Q$ test and Higgins $I^2$ statistic ($I^2 > 50\%$ indicates moderate heterogeneity; $I^2 > 75\%$ indicates substantial heterogeneity).
  - **Model Selection:** Prefer random-effects model (DerSimonian-Laird or REML) when clinical/methodological heterogeneity exists across studies.
  - **Publication Bias:** Funnel plot visualization and Egger's regression test ($p < .05$ suggests funnel asymmetry).
- **Certainty of Evidence:** Use the **GRADE framework** (Grading of Recommendations Assessment, Development and Evaluation) rating evidence as High, Moderate, Low, or Very Low.

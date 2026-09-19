# PRISMA Screening & Data Extraction Matrix

Use this tabular matrix to log study screening decisions, exclusion reasons, and data extraction fields for systematic reviews.

---

## 1. Study Identification & Deduplication Log

| Database | Date Searched | Hits Retrieved | Notes / Query File |
| :--- | :--- | :---: | :--- |
| PubMed / MEDLINE | 2026-09-01 | 1,240 | Saved as `queries/pubmed_20260901.txt` |
| Scopus | 2026-09-01 | 890 | Scopus export `.ris` |
| Web of Science | 2026-09-01 | 630 | WoS export `.ciw` |
| IEEE Xplore | 2026-09-01 | 320 | IEEE export `.bib` |
| **Total Retrieved** | | **3,080** | |
| **Duplicates Removed** | | **-780** | Deduplicated in Zotero / Rayyan |
| **Net Records for Screening** | | **2,300** | |

---

## 2. Title & Abstract Screening Log

| Study ID / Citekey | Authors & Year | Title | Decision (Include/Exclude) | Exclusion Reason (if Excluded) | Screened By |
| :--- | :--- | :--- | :---: | :--- | :---: |
| `[@doe2023ai]` | Doe et al. (2023) | Deep learning in clinical triage | Include | — | Rev1 & Rev2 |
| `[@lee2022rev]` | Lee & Park (2022) | Narrative review of healthcare AI | Exclude | E1: Narrative review / not empirical | Rev1 |
| `[@wang2024ped]` | Wang et al. (2024) | Pediatric diagnostic validation | Exclude | E2: Wrong population (pediatric < 18) | Rev2 |

*Exclusion Codes: E1 = Not empirical / editorial; E2 = Wrong population; E3 = Wrong intervention/comparator; E4 = Missing primary outcome; E5 = Foreign language without translation.*

---

## 3. Full-Text Eligibility & Extraction Matrix (Included Studies)

| Study ID | Design | Country | Total N | Intervention / Exposure | Control / Comparator | Primary Outcome Metric | Effect Size (95% CI) | RoB Assessment (Low/Unclear/High) |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| `[@smith2023deep]` | RCT | USA | 250 | ResNet-50 AI Pipeline | Physician Standard Care | Sensitivity (%) | $94.2\%$ vs $81.5\%$ ($p < .001$) | Low Risk |
| `[@zhang2024trans]` | Cohort | China | 1,120 | Vision Transformer | Expert Radiologists | AUROC | $0.932 \text{ [0.91, 0.95]}$ | Some Concerns |

---

## 4. PRISMA 2020 Attrition Counts (For Flow Diagram)

- **Total identified from databases:**
- **Total from citation chaining/registers:**
- **Duplicates removed:**
- **Records screened (Title/Abstract):**
- **Records excluded at Title/Abstract:**
- **Full-text reports assessed for eligibility:**
- **Full-text excluded (by reason):**
  - Reason A (Population):
  - Reason B (Intervention):
  - Reason C (Outcomes missing):
  - Reason D (Design/Review):
- **Final included studies (Qualitative):**
- **Final included studies (Meta-Analysis):**

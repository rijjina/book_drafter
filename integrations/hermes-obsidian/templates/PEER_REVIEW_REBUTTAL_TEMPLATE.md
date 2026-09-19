# Point-by-Point Author Response to Reviewers (Rebuttal Document)

Use this document to prepare a structured, diplomatic, and rigorous response to editor and peer reviewer comments during paper revision.

---

## Cover Note to the Editor

```text
[Date]

Dear Editor [Editor Name],

Thank you for providing the opportunity to revise our manuscript entitled "[Manuscript Title]" (Manuscript ID: [ID-XXXX]). We deeply appreciate the constructive feedback and insightful comments from both reviewers. 

We have addressed every comment in detail, performed additional experimental benchmarks, and substantially revised the manuscript accordingly. In the text below, reviewer comments are shown in bold italic font, followed by our point-by-point responses and exact excerpts of the modifications made to the manuscript. A marked copy highlighting all revisions in blue has also been provided.

We believe these substantial revisions have significantly strengthened the rigor and clarity of the paper.

Sincerely,

[The Authors]
```

---

## Response to Reviewer #1

### Summary of Reviewer #1's Assessment
> *"The authors present an interesting study on... However, several clarifications regarding sample baseline choice and statistical power are required."*

**Author Response:**
We sincerely thank Reviewer 1 for their thoughtful evaluation and positive appraisal of our contribution. Below we address each specific critique.

---

### Comment 1.1 (Baseline Comparators)
> ***Reviewer Comment 1.1:***
> *"The authors benchmarked against method A and B, but failed to include method C (Doe et al., 2023), which is currently considered state-of-the-art in this domain."*

**Author Response:**
We thank the reviewer for this crucial suggestion. We agree that evaluating against method C (Doe et al., 2023) is essential to demonstrate general superiority. We have now acquired the official source code for Doe et al., calibrated the hyperparameters under identical conditions on our benchmark dataset, and added the results to Table 2 and Section 3.2.

As shown in revised Table 2, our proposed architecture maintains a 3.4% higher macro-F1 score than Doe et al. while achieving a 2.1x lower inference latency.

**Manuscript Revision (Section 3.2, Page 8, Lines 142–151):**
> *"To ensure rigorous comparison against modern state-of-the-art architectures, we also benchmarked against the contrastive model proposed by Doe et al. [@doe2023contrastive]. As summarized in Table 2, our proposed model significantly surpassed Doe et al. in macro-F1 ($91.4\%$ vs $88.0\%, p = .003$), demonstrating superior stability under noise."*

---

### Comment 1.2 (Statistical Clarification)
> ***Reviewer Comment 1.2:***
> *"In Section 3.3, what correction was applied for multiple comparisons across the 12 sub-features?"*

**Author Response:**
We appreciate this astute observation. In the original draft, uncorrected p-values were reported. In the revised manuscript, we have applied the Benjamini-Hochberg False Discovery Rate (FDR) correction at $q = 0.05$. All significant effects reported in Section 3.3 survived this FDR correction. We have explicitly clarified this in Section 2.5 and updated Table 3 accordingly.

**Manuscript Revision (Section 2.5, Page 5, Lines 95–97):**
> *"To control for the inflation of Type I error rate across multiple subgroup contrasts, p-values were adjusted using the Benjamini-Hochberg False Discovery Rate (FDR) procedure with a threshold of $q < .05$."*

---

## Response to Reviewer #2

### Comment 2.1 (Limitations & Scope)
> ***Reviewer Comment 2.1:***
> *"The authors claim that their method works in all sensor environments. This seems overclaimed given that only indoor laboratory conditions were tested."*

**Author Response:**
We fully agree with the reviewer that our initial phrasing overgeneralized the findings beyond the evaluated experimental conditions. We have tempered our claims throughout the Introduction, Results, and Discussion sections. Specifically, we have rewritten Section 4.4 (Limitations) to explicitly acknowledge that outdoor ambient conditions and extreme temperature gradients were not evaluated and represent a key direction for future work.

**Manuscript Revision (Section 4.4, Page 12, Lines 230–236):**
> *"While our system demonstrated robust performance across controlled laboratory temperature ranges ($20^\circ\text{C}$ to $28^\circ\text{C}$), outdoor deployment scenarios characterized by severe thermal gradients and precipitation were outside the scope of this study and warrant further field testing."*

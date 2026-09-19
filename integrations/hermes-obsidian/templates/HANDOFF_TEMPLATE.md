# Agent Task Handoff Contract

Use this contract when handing off work between **QUANTA**, **NOVA**, and **AEGIS**.

---

## Handoff Metadata
- **From Agent:** [QUANTA / NOVA / AEGIS]
- **To Agent:** [QUANTA / NOVA / AEGIS]
- **Date & Timestamp:** 2026-09-04 14:00
- **Manuscript ID / Working Title:** [Working Title]
- **Target Section / Asset:** (e.g., Section 3 Results, Figure 2 Benchmark Plot, PRISMA Search Strategy)

---

## 1. Goal & Context
Briefly state what was requested and what this handoff completes.

## 2. Artifacts Produced / Modified
- File 1: `[[figures/fig2_benchmark.pdf]]`
- File 2: `[[drafts/section3_results.md]]`
- Script: `scripts/analyze_benchmarks.py`

## 3. Key Scientific Decisions & Methods
- Statistical tests performed: (e.g., Welch's t-test with FDR correction)
- Effect sizes obtained: (e.g., Cohen's $d = 1.45, 95\% \text{ CI } [0.92, 1.98]$)
- Software/library versions: (e.g., Python 3.13, scipy v1.14)

## 4. Known Limitations & Remaining Assumptions
- Assumptions made: (e.g., Missing baseline C was omitted due to unavailable code; noted in limitations)
- Unverified items: (None, or flag `[UNVERIFIED]`)

## 5. Explicit Request to Next Agent
- **If to NOVA:** "Please integrate Figure 2 and Table 1 into the Results narrative adhering to APA formatting."
- **If to AEGIS:** "Please perform independent review on Section 3. Verify that degrees of freedom match sample size and check for overclaims."
- **If to QUANTA:** "Please generate an ablation plot evaluating learning rates from $10^{-5}$ to $10^{-3}$."

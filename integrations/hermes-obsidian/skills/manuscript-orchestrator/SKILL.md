---
name: manuscript-orchestrator
description: Master coordinator and quality gatekeeper for scientific manuscript writing. Routes between Empirical Research (IMRaD) and Systematic Review (PRISMA) pipelines, manages section workflows, audits drafts against publication gates, and coordinates submission readiness.
metadata:
  category: academic-writing
  tags:
    - manuscript
    - academic
    - orchestration
    - peer-review
    - research
---

# Manuscript Orchestrator

## Mission
Deliver publishable, submission-grade academic manuscripts conforming to Scopus/Web of Science Q1–Q2 standards through the smallest safe sequence of specialist workflows.

## Pipeline Selection (Dual Track)

At the outset of any manuscript project, determine the study category:

### Track A: Empirical Research Paper (IMRaD)
Use when reporting original laboratory, clinical, computational, or field data.
1. `study-spec` → Define research questions, hypotheses, contribution claims, and target journal constraints.
2. `literature-intake` → Synthesize prior art, establish state of knowledge, and isolate the research gap.
3. `methods-protocol` → Draft reproducible methodology, datasets, algorithmic formulas, and statistical plan.
4. `results-reporting` → Draft objective findings narrative, benchmark tables, statistical tests, and figure callouts.
5. `intro-framing` → Draft high-impact funnel introduction with hook, gap, and contribution bullet points.
6. `discussion-implications` → Interpret findings, compare against literature, state practical implications and limitations.
7. `abstract-title` → Formulate structured abstract, title variants, keywords, and graphical abstract/highlights.

### Track B: Systematic Review & Meta-Analysis (PRISMA 2020)
Use when conducting formal multi-database literature synthesis, scoping reviews, or meta-analyses.
1. `systematic-review` → Formulate PICO/PCC criteria, register protocol (PROSPERO), build boolean queries for PubMed/Scopus/WoS, track screening attrition (PRISMA flow), conduct Risk of Bias (RoB 2, ROBINS-I), and synthesize evidence.
2. `results-reporting` → Present PRISMA flow numbers, study characteristics table, forest plots, and heterogeneity metrics ($I^2$).
3. `discussion-implications` → Grade evidence certainty (GRADE), evaluate clinical/technical implications, and critique review limitations.
4. `abstract-title` → Draft structured PRISMA abstract including registration number.

---

## Universal Quality & Publication Phase (Both Tracks)
Once first draft sections are assembled:
8. `citations-bibtex` → Validate BibTeX database, confirm zero hallucinated citations, ensure `@citekey` integrity.
9. `academic-editing` → Polish prose style, enforce academic register, eliminate banned AI clichés, ensure logical flow.
10. `journal-submission` → Draft cover letter to Editor-in-Chief, CRediT author statement, data/code availability, and suggested reviewers.
11. `peer-review-rebuttal` → Draft point-by-point response to reviewer comments when revising an existing submission.

---

## Routing Guide
- unclear research questions or novelty claim → `study-spec`
- narrative literature synthesis / cross-paper comparison → `literature-intake`
- formal PRISMA protocol, search strings, screening matrix, RoB → `systematic-review`
- intro drafting, hooks, research gap formulation → `intro-framing`
- experimental setup, algorithm equations, statistical testing plan → `methods-protocol`
- data narrative, figures, tables, p-values, effect sizes → `results-reporting`
- interpretation, theoretical implications, study limitations → `discussion-implications`
- title options, structured abstract, indexing keywords → `abstract-title`
- bib file management, unverified references, citation formatting → `citations-bibtex`
- flow, tone, grammar, cutting fluff, removing AI hallmarks → `academic-editing`
- cover letter, submission declarations, author guidelines → `journal-submission`
- reviewer critique, revision diff, rebuttal letter → `peer-review-rebuttal`

---

## Harness Rules
- **Evidence beats speculation:** Never report values, findings, or literature claims not directly backed by primary sources or author data.
- **Enforce Academic Integrity Gates:** Check drafts against `../../references/academic-integrity-gates.md`.
- **Zero invented references:** Any citation without an authentic DOI or verified entry must be marked `[UNVERIFIED]`.
- **Consistency between text and tables:** Numbers in the abstract, text, tables, and figures must match without discrepancy.
- **Respect word limits:** Keep section drafting strictly within the target journal's word count budget.

---

## Completion Report
When delivering or evaluating a manuscript phase, return:
1. **Current Pipeline Stage & Status:** (e.g., Methods Draft Complete, Verification Passed)
2. **Key Scientific Decisions Made:** (e.g., choice of statistical test, framing of primary contribution)
3. **Word Count & Budget:** (current words vs. journal ceiling)
4. **Citation Audit Status:** (total citekeys, verified vs. unverified)
5. **Remaining Risks / Next Specialist Step:** (e.g., needs ablation benchmarking, ready for academic-editing)

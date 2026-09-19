# Academic Integrity & Publication Verification Gates

Before any section or complete manuscript is marked **Submission Ready**, it must satisfy these non-negotiable integrity gates.

---

## Gate 1: Source Truth & Non-Hallucination
- **Zero Hallucinated Citations:** Every cited paper must exist with a valid DOI, PMID, or publisher URL. Never invent author names, journal titles, publication years, or volume/page numbers.
- **Direct Evidence Attribution:** Specific claims, benchmarks, and statistical findings cited from external literature must accurately reflect the cited paper's original conclusions. Do not extrapolate or misrepresent findings.
- **Verification Rule:** If a citekey cannot be verified in the local `.bib` database or a verified literature matrix, flag it immediately as `[UNVERIFIED: author, year]` rather than generating plausibly sounding text.

---

## Gate 2: Data Consistency & Experimental Reality
- **Internal Numerical Alignment:** Values reported in the Abstract, Introduction, Results text, Tables, and Figures must match exactly. Discrepancies between text and tables are a primary cause of reviewer rejection.
- **Sample Sizes & Attrition:** Reported $N$ values must be mathematically consistent across subgroups, dropouts, exclusions, and baseline demographics.
- **No Fabricated Data:** The AI assistant must never fabricate raw numbers, p-values, standard deviations, or measurement units. Only summarize, calculate, and format data explicitly provided by the author.

---

## Gate 3: Claim Calibration & Overclaim Prevention
- **Defensible Language:** Do not use hyperbolic or ungrounded claims (e.g., "revolutionizes", "proves conclusively", "flawless", "unprecedented") unless supported by decisive empirical benchmark evidence.
- **Appropriate Hedging:** Distinguish between correlation and causation. Frame findings using appropriate scientific epistemic modality: "indicates", "suggests", "demonstrates under conditions X and Y".
- **Limitation Transparency:** Every manuscript must explicitly articulate its methodology boundaries, sample constraints, generalizability limits, and threats to internal/external validity.

---

## Gate 4: Plagiarism & Originality
- **Paraphrasing & Synthesis:** Do not copy contiguous sentences from source literature. Synthesize ideas conceptually and express them in fresh, original academic phrasing.
- **Direct Quotes:** Direct quotations are rare in STEM empirical papers. If exact phrasing from another author is essential, wrap in quotation marks with exact page number attribution.
- **Self-Plagiarism Avoidance:** Ensure previously published text by the author (from earlier papers or conference abstracts) is properly cited or re-articulated.

---

## Gate 5: Ethical & Regulatory Compliance
- **IRB / Ethics Committee Approval:** State committee name, approval/protocol reference number, and confirmation of informed consent for human/animal studies.
- **Declarations:** Explicit statements required for:
  1. Author Contributions (CRediT taxonomy).
  2. Competing Interests / Conflicts of Interest.
  3. Funding Sources and grant IDs.
  4. Data Availability Statement with repository DOI/URL.
  5. Code / Software Availability Statement.

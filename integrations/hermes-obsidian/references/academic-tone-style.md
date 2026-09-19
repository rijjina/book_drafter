# Academic Tone & Stylistic Guidelines

This reference defines the linguistic standards, voice conventions, and stylistic rules required for international indexed journals (Elsevier, Springer Nature, IEEE, Wiley, MDPI).

---

## 1. Scientific Voice & Register

- **Clarity over Complexity:** Write to be understood, not to impress. Avoid ornate sentence structures that obscure experimental logic.
- **Active vs. Passive Voice:**
  - Prefer **active voice** when describing author decisions and interpretations:
    - *Preferred:* "We evaluated model convergence using five-fold cross-validation."
    - *Acceptable:* "Model convergence was evaluated using five-fold cross-validation."
  - Use **passive voice** when the procedure or object of study is the focal point, not the actor:
    - *Example:* "Samples were centrifuged at 4,000 rpm for 15 minutes."
- **Person:** Use first-person plural ("We") judiciously for author choices. Avoid first-person singular ("I") unless writing an invited single-author perspective.

---

## 2. Eliminating AI Clichés and Hallmarks

Academic reviewers and editors increasingly reject manuscripts exhibiting stereotypical LLM phrasing. The following words, phrases, and structures are strictly banned or must be heavily restricted:

### Banned / Heavily Restricted Terms
| AI Cliché Term | Problem | Preferred Academic Alternative |
| :--- | :--- | :--- |
| **"delve" / "delves into"** | Overused cliché | "investigate", "examine", "analyze", "explore" |
| **"testament to"** | Fluffy hyperbole | "evidence of", "demonstrates", "reflects" |
| **"tapestry" / "rich tapestry"** | Metaphorical fluff | "complex interaction", "multifaceted landscape" |
| **"pivotal" / "crucial role"** | Overstated significance | "key factor", "significant component", "essential" |
| **"beacon of" / "fosters"** | Rhetorical embellishment | "enables", "promotes", "facilitates" |
| **"in summary, it is clear that"** | Wordy filler | "Consequently,", "These findings indicate that" |
| **"game-changer" / "revolutionary"** | Marketing hype | "substantial advancement", "novel architecture" |
| **"harnessing the power of"** | Generic filler | "applying", "utilizing", "implementing" |
| **"serves as a reminder"** | Moralizing tone | "indicates the necessity of", "underscores" |

### Structural Patterns to Avoid
- **Excessive introductory rhetorical flourishes:** Do not start paragraphs with "In today's fast-paced digital world..." or "From time immemorial...". Start directly with the domain problem.
- **Formulaic transitional triples:** Avoid repetitive sequences like "Not only... but also...", "Moreover,... Furthermore,... In conclusion,...". Vary transitional phrasing organically.
- **Symmetric bulleted summaries:** Do not end discussion sections with uniform, overly polished bullet lists that look like chatbot summaries. Write cohesive academic paragraphs.

---

## 3. Scientific Hedging & Epistemic Modality

Scientific claims must reflect the certainty warranted by empirical evidence.

| Certainty Level | Appropriate Verbs & Qualifiers | Example Phrasing |
| :--- | :--- | :--- |
| **High Certainty** (direct observation, established theory) | "demonstrates", "shows", "confirms", "establishes" | "The spectrophotometric data confirm that..." |
| **Moderate Probability** (statistically significant trends, strong inference) | "indicates", "suggests", "is consistent with", "points toward" | "These results suggest that parameter \(\alpha\) modulates..." |
| **Tentative / Speculative** (hypotheses for future study, non-significant trends) | "may indicate", "could potentially reflect", "warrants further investigation" | "This variation may stem from minor thermal fluctuations..." |

---

## 4. Paragraph Architecture (The MEAL Plan)

Every body paragraph in an academic paper should follow a structured logical progression:
- **M (Main idea):** Clear topic sentence presenting the core claim or focus of the paragraph.
- **E (Evidence):** Empirical data, experimental findings, or literature citations backing the topic sentence.
- **A (Analysis):** Explanation of what the evidence means, how it relates to the research question, or mechanism.
- **L (Lead-out / Link):** Concluding sentence that synthesizes the takeaway or transitions smoothly to the next paragraph.

---

## 5. Mathematical & Formula Formatting

- Render all equations and inline variables using LaTeX syntax:
  - Inline variables: `$x_i$`, `$\sigma^2$`, `$\mathbb{E}[X]$`
  - Display equations:
    $$\mathcal{L}(\theta) = -\frac{1}{N} \sum_{i=1}^N \log P(y_i \mid x_i; \theta)$$
- Define every symbol immediately upon its first occurrence in the text.
- Punctuate display equations as part of the surrounding grammatical sentence.

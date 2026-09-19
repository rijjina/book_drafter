# Literature Synthesis Matrix (Empirical Cross-Study Comparison)

Use this matrix to systematically compare related works, identify research gaps, and build the Introduction and Related Work sections.

---

## 1. Cross-Study Synthesis Table

| Paper / Citekey | Focus / Core Idea | Dataset / Domain | Methodology / Model | Key Metric / Performance | Major Limitation / Unresolved Gap | Obsidian Link |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `[@smith2023deep]` | Supervised CNN for defect detection | Industrial surface image dataset ($N=10k$) | ResNet-50 + Cross-entropy | $F1 = 88.2\%$ | High false alarm on reflective surfaces; requires large labeled data | `[[Smith2023_Notes]]` |
| `[@chen2024novel]` | Self-supervised contrastive learning | Multi-sensor vibration data | SimCLR adaptation | Precision $= 91.0\%$ | Extreme computational overhead; poor inference speed on edge chips | `[[Chen2024_Notes]]` |
| `[@kumar2024edge]` | Quantized transformer for real-time triage | Edge device streaming video | INT8 ViT | Latency $= 12\text{ms}$ | 7.5% drop in recall on low-contrast lighting scenarios | `[[Kumar2024_Notes]]` |

---

## 2. Synthesis by Thematic Dimension

### Theme A: Representation Learning & Generalization
- Common consensus across papers:
- Diverging results or debates:
- What remains untested:

### Theme B: Computational Efficiency & Deployment Feasibility
- Current benchmark bottlenecks:
- Why existing techniques struggle in production or real-world setups:

---

## 3. The Resulting Research Gap Statement
Synthesize the final gap paragraph for Section 1 of the manuscript:
> "While recent studies have improved detection precision using supervised deep networks `[@smith2023deep]` and self-supervised pre-training `[@chen2024novel]`, existing architectures remain prohibitively resource-intensive for edge deployment or experience catastrophic accuracy degradation under adverse sensor noise `[@kumar2024edge]`. A lightweight, noise-resilient formulation that maintains real-time throughput without sacrificing detection sensitivity has not yet been demonstrated."

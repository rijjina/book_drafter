---
name: academic-writing-vault
description: Route and resume manuscript, Thai book/textbook/teaching-notes, and เอกสารประกอบการสอน projects in a portable Hermes + Obsidian vault.
metadata:
  hermes:
    tags: [Obsidian, academic-writing, manuscript, Thai, migration]
---

# Academic Writing Vault

Use this skill as the portable entrypoint for academic-writing work stored in an
Obsidian vault.

## Resolve context

1. Resolve the concrete vault path from `OBSIDIAN_VAULT_PATH`. If unset, use the
   Hermes Obsidian skill's documented fallback and confirm that it exists.
2. Read the vault-root `AGENTS.md`, `AI-SHARED-CONTEXT.md`, and the selected project's
   `project.md` before choosing a writing workflow.
3. Treat paths recorded on another computer as historical metadata. Resolve current
   files from the vault, repository, project note, or user input; never guess a new
   absolute path.
4. Reuse the project's current status, approvals, evidence ledger, and latest handoff.
   A computer or provider change does not reset an academic approval gate.

## Route by project kind

- `journal-manuscript`, `systematic-review`, or `thai-research`: use
  `manuscript-orchestrator` and only the specialist manuscript skills needed for the
  current stage.
- `book`, `textbook`, or `teaching-notes`: use
  `orchestrate-thai-academic-writing` and `write-thai-academic-book`. Preserve their
  one-task and human-approval gates.
- `teaching-material` / `เอกสารประกอบการสอน`: use
  `thai-academic-teaching-material`. Do not route it through the book skill's
  `teaching-notes` (`เอกสารคำสอน`) type unless the user explicitly changes the
  deliverable and the governing institution supports that classification.

If the project kind is absent and source evidence cannot resolve it safely, ask the
user for the intended deliverable before production work.

## Evidence and file rules

- Read human sources from `Sources/` and durable notes from `Notes/`.
- Write generated drafts, audits, and handoffs to `Outputs/` unless the routed skill
  defines a stricter output contract.
- Do not overwrite human-authored source files.
- Label direct source support as `FACT`, interpretation as `INFERENCE` or
  `ASSUMPTION`, and absent required evidence as `MISSING DATA`.
- Never invent citations, DOI records, study results, course evidence, institutional
  rules, permissions, or author experience.
- Keep secrets, provider configuration, browser state, and authentication artifacts
  outside the vault.

## Handoff and completion

Before changing provider, agent, or computer, update the project's latest handoff with:

- project kind and current stage;
- inputs read and immutable source checksums when available;
- artifacts changed;
- approvals and unresolved blockers;
- exact next permitted task.

Finish only when the routed workflow's quality and human-approval gates are satisfied.

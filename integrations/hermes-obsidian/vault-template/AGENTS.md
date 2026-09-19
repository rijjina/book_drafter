# Academic Writing Vault Rules

## Mission

Use this vault as durable, provider-neutral memory for evidence-grounded academic
writing. Support scientific manuscripts, Thai books/textbooks/teaching notes, and Thai
teaching materials without mixing their governing standards or approval gates.

## Architecture

- `SOUL.md` defines an agent's identity and portable voice.
- This `AGENTS.md` defines shared project rules and workflow.
- `Notes/` contains durable human-curated knowledge and decisions.
- `Sources/` contains author inputs and evidence; treat them as read-only by default.
- `Projects/<project-id>/` contains project state, evidence ledgers, handoffs, and
  generated `Outputs/`.
- Hermes runtime configuration, provider state, and secrets stay outside the vault.

## Evidence rules

1. Read the relevant source or note before making a claim.
2. Classify direct support as `FACT`, reasoned interpretation as `INFERENCE` or
   `ASSUMPTION`, and absent required evidence as `MISSING DATA`.
3. Cite the source note/file and page, slide, table, or section when available.
4. Never invent citations, DOI records, data, statistics, permissions, ethics approval,
   institutional criteria, author experience, course evidence, or quality evidence.
5. Keep claim, evidence, interpretation, and proposed application distinguishable.

## Project routing

Every `Projects/<project-id>/project.md` must declare one `project_kind`:

- `journal-manuscript`, `systematic-review`, or `thai-research`;
- `book`, `textbook`, or `teaching-notes` (`เอกสารคำสอน`);
- `teaching-material` (`เอกสารประกอบการสอน`).

Do not silently change project kind. A changed deliverable requires an explicit user
decision and a new record of the governing standard and workflow impact.

## Shared workflow

1. Planner/PI establishes scope, governing standard, risks, and acceptance criteria.
2. Evidence/Data role verifies sources, data, citations, and rights.
3. Author role drafts only from approved scope and verified evidence.
4. Reviewer independently checks claims, consistency, style preservation, and the
   project-specific rubric.
5. Compiler creates final files only after the applicable content and human approvals.

Reviewer findings use `BLOCKER`, `MAJOR`, `MINOR`, and `SUGGESTION`. BLOCKER and MAJOR
findings return to the responsible role. Machine findings such as PASS or
MEETS_TARGET do not replace human approval.

## File and migration safety

- Never overwrite files in `Sources/` unless the user explicitly requests it.
- Put generated project work in the project's `Outputs/` or the stricter directory
  required by the routed skill.
- Do not store machine-specific absolute paths as the only locator for an artifact.
  Also record a vault-relative or repository-relative path and a checksum when useful.
- Before changing computer, provider, or agent, update `handoff-latest.md` with current
  state, approvals, blockers, artifacts, and the exact next permitted task.
- Do not commit `.obsidian/workspace*.json`, credentials, cookies, tokens, passwords,
  private keys, session databases, or provider configuration.


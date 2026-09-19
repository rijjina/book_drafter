# Hermes + Obsidian Academic Writing Harness

Portable harness for three related workflows:

- scientific manuscripts and systematic reviews;
- Thai books, textbooks, and teaching notes;
- Thai `เอกสารประกอบการสอน` built from lectures, slides, and course evidence.

The repository contains reusable skills, agent roles, references, and a clean Obsidian
vault template. Real manuscripts and the active Obsidian vault stay outside the Git
checkout so a pull, rebuild, or clean clone cannot overwrite author data.

## Portable layout

```text
repository/
├── plugins/write-thai-academic-book/skills/  # book/textbook/teaching-notes suite
├── integrations/hermes-obsidian/
│   ├── skills/                               # manuscript, teaching-material, vault router
│   ├── agents/                               # portable role definitions
│   ├── references/                           # manuscript standards
│   ├── templates/                            # reusable manuscript templates
│   └── vault-template/                       # safe starting vault; no author data
└── scripts/setup-hermes-obsidian.ps1
```

No tracked file should contain an API key, browser cookie, OAuth token, password,
Hermes server key, or machine-specific absolute path.

## New-computer setup (Windows)

Prerequisites: Git, Python 3.10+, Hermes Agent, and Obsidian.

```powershell
git clone https://github.com/rijjina/book_drafter.git
Set-Location book_drafter

# Create a new vault from the template and register both skill directories in Hermes.
.\scripts\setup-hermes-obsidian.ps1 `
  -VaultPath "$HOME\Documents\Academic-Writing-Vault" `
  -InitializeVault `
  -ConfigureHermes
```

If an existing vault was copied or synchronized from the old computer, omit
`-InitializeVault` and point `-VaultPath` to that folder. The script preserves existing
Hermes external skill directories and existing vault files. Use `-ForceTemplateFiles`
only when replacement of same-named template files is intentional.

Restart Hermes after configuration, then verify:

```powershell
hermes config get skills.external_dirs
hermes skills list
python scripts/validate_hermes_obsidian.py
```

Open the selected folder as a vault in Obsidian. Start at `00-HOME.md`.

## What to move from the old computer

Move separately:

1. the Git repository (prefer clone/pull rather than copying a working tree);
2. the active Obsidian vault or its sync location;
3. source DOCX/PDF/data files that are not already inside the vault;
4. a Hermes skills snapshot if other, unrelated installed skills are needed:
   `hermes skills snapshot export hermes-skills.json`.

Do not copy Hermes `.env`, authentication stores, browser profiles, cookies, session
databases, or provider secrets through Git. Re-authenticate providers on the new
computer and set secrets through Hermes or the provider's secure storage.

## Workflow routing

Use `academic-writing-vault` as the entrypoint. It reads the project note and routes:

| Project kind | Primary workflow |
| --- | --- |
| `journal-manuscript`, `systematic-review`, `thai-research` | `manuscript-orchestrator` and specialist manuscript skills |
| `book`, `textbook`, `teaching-notes` | `orchestrate-thai-academic-writing` / `write-thai-academic-book` |
| `teaching-material` (`เอกสารประกอบการสอน`) | `thai-academic-teaching-material` |

The teaching-material skill includes a content-neutral writing-style profile distilled
from legacy teaching documents. It transfers voice, paragraph rhythm, explanatory
sequence, and teaching structure only; subject facts, examples, citations, and course
identifiers are explicitly excluded.

`เอกสารประกอบการสอน` is deliberately separate from the book suite's
`teaching-notes` (`เอกสารคำสอน`) gate. Do not silently convert one type into the other.

## Runtime boundaries

- Obsidian is durable, provider-neutral project memory.
- Hermes configuration and secrets remain outside the vault.
- `SOUL.md` contains identity only; project rules belong in `AGENTS.md`.
- Human-authored sources are read-only unless the user explicitly requests an edit.
- Generated work goes under each project's `Outputs/` or its approved book-suite
  output contract.
- FACT, INFERENCE/ASSUMPTION, and MISSING DATA must remain visibly distinct.
- Human approval gates remain valid after provider or computer migration.

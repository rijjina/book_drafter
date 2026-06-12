# Write Thai Academic Book

Cross-platform Agent Skill for drafting, auditing, revising, and quality-checking Thai `เอกสารคำสอน`, `หนังสือ`, and `ตำรา` at Level A or A-equivalent.

The workflow performs one task per invocation, reuses existing project artifacts, separates chapter outputs, and requires explicit human approval before every next task.

## Install

Clone the repository:

```bash
git clone https://github.com/rijjina/book_drafter.git
cd book_drafter
```

### Codex

Ask `$skill-installer` to install this GitHub repository, or run:

```powershell
.\scripts\install.ps1 -Target codex
```

The skill is installed to `~/.agents/skills/write-thai-academic-book`.

### Claude Cowork

In **Customize > Plugins > Add marketplace > Add from a repository**, enter:

```text
https://github.com/rijjina/book_drafter
```

Install `write-thai-academic-book` from the `thai-academic-writing` marketplace. For direct skill upload, use `packages/write-thai-academic-book.zip` in **Customize > Skills**.

### Google Antigravity

```powershell
.\scripts\install.ps1 -Target antigravity
```

This installs to `~/.agents/skills/write-thai-academic-book`. For Antigravity CLI use `-Target antigravity-cli`.

### macOS or Linux

```bash
./scripts/install.sh codex
./scripts/install.sh antigravity
./scripts/install.sh antigravity-cli
./scripts/install.sh claude-code
```

## Start A Project

Ask the agent to use `write-thai-academic-book`. The first task is always `select-document-type`, choosing exactly one of:

- `teaching-notes` (`เอกสารคำสอน`)
- `book` (`หนังสือ`)
- `textbook` (`ตำรา`)

The fixed target is Level A for books and textbooks, or internal A-equivalent for teaching notes.

## Distribution Notes

Original institutional and publisher PDF manuals are intentionally excluded because redistribution rights may vary. The skill includes distilled criteria and supports `refresh-sources` when users provide current governing documents.

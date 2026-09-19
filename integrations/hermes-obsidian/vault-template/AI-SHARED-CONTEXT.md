# AI Shared Context

This Obsidian vault is the durable project memory for the academic-writing harness.
Hermes is the runtime. Models and providers may change; evidence, decisions, approval
records, and handoffs remain in the vault.

## Reading order

1. [[AGENTS]]
2. the selected project's `project.md`
3. its governing-standard and evidence notes
4. its latest handoff and approval records
5. only the source files required for the current task

## Invariants

- Preserve the declared project kind.
- Preserve human-authored sources.
- Preserve academic approval gates across agents and computers.
- Resolve paths on the current computer; do not reuse stale absolute paths blindly.
- Never store secrets in this vault.


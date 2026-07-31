# Workflow Contract Compatibility Pointer

This path is retained so older projects and prompts do not fail, but the former
monolithic contract has been split for context-efficient loading.

Start with `SKILL.md`, identify one task, and load only:

- `core-production-contract.md` plus `workflow-project.md` for project tasks;
- `core-production-contract.md` plus `workflow-chapter.md` for chapter tasks;
- `core-production-contract.md` plus `workflow-manuscript.md` for imported
  manuscript tasks;
- `workflow-review.md` for approval-free `author-review`;
- `core-production-contract.md` plus `workflow-final.md` for final QC or DOCX
  production;
- `style-preservation.md` only when author-style evidence is relevant.

Do not treat this pointer as a substitute for the routed task contract.

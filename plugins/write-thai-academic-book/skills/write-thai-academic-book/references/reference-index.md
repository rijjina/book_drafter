# Quality and Source Reference Index

Task routing is canonical in `SKILL.md` and the routed workflow files. Use this
index only when a task reveals a quality, authority, or source-verification
question that the workflow does not already resolve.

## Topic Routing

| Question | Load |
| --- | --- |
| Is the claimed document type supported? | `document-types-and-quality.md`; add `teaching-document-criteria.md` for teaching materials |
| Is Level A/A-equivalent evidence sufficient? | applicable type reference plus `qc-rubric.md` |
| Are chapter purpose, structure, prose, citations, figures, tables, or rights sound? | `editorial-standards.md`; add `qc-rubric.md` for a formal decision |
| Does author voice need preservation or justified override? | `style-preservation.md` plus the approved style profile/source |
| Which authority controls, or is a rule universal? | `source-map.md` plus exact source pages |
| Is a citation, permission, or source claim verifiable? | `editorial-standards.md`, `source-map.md`, and only the exact source segment |
| May DOCX be generated? | `workflow-final.md`: require `MEETS_TARGET`, `Status: APPROVED`, and `Deliverable: DOCX` |

## Source Provenance and Cached Extraction

`source-manifest.json` records SHA-256, page count, extraction method,
page-level findings, segment ranges, curated target, flags, and verification
status. The excluded `.reference-cache/` stores sanitized page text keyed by
source hash. Read only the manifest record and page files for the selected
segment.

Run:

```powershell
python scripts/compile_references.py
```

Only changed PDFs are rebuilt. Use `--rebuild-all` only for an explicit corpus
audit. OCR is attempted only for failed pages when the required engine is
available. Empty extraction, replacement glyphs, `uni0E` artifacts, invisible
instructions, failed OCR, or uncertain Thai require visual review and must not
replace verified references.

## Authority and Completeness

- Curated Markdown remains authoritative until a replacement is visually
  checked against exact source pages and marked verified.
- Preserve every material rule, exception, criterion, blocker, decision rule,
  and page mapping. Progressive loading never authorizes lossy summarization.
- A publisher house style is not universal policy unless declared as the
  project's governing authority.
- A newer applicable institutional source supersedes an older one only after
  the project records what changed, source pages, and why the new source
  controls.

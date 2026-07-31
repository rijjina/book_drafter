# Style Preservation

Use this reference only when a user-supplied or imported manuscript provides an
authorial baseline, or when style extraction, style QC, or revision is part of
the selected task.

## Build the Baseline

For DOCX, Markdown, or text, run:

```powershell
python scripts/extract_style_profile.py --input <source> --output <project>/source/style-profile.md
```

For a chapter-specific user draft, place the profile at
`chapters/chapter-NN/style-profile.md`. The deterministic extractor and
`assets/style-profile-template.md` record checksum, structure, paragraph
patterns, diction, script use, citations, transitions, and representative
passages without timestamps.

For a PDF-only user draft, use the PDF capability to extract readable text,
create the same profile manually, record the extraction method, and keep the PDF
authoritative. Do not claim evidence from unreadable pages.

## Decision Hierarchy

The profile describes the author's established style; it does not authorize
preserving errors. Apply this order:

1. factual accuracy and academic integrity;
2. evidence and citation integrity;
3. logic, clarity, and accessibility;
4. approved QC corrections;
5. mandatory institutional, publisher, or official rules;
6. confirmed authorial style;
7. optional house preferences.

Before editing, record which measured traits will be retained, which must be
overridden, and the governing reason. Do not rewrite sound prose merely to make
it resemble generic AI-generated academic language.

## Traits to Compare

Compare the source and revision for:

- stance, formality, and legitimate first-person use;
- sentence and paragraph rhythm;
- terminology, Thai/English balance, transliteration, and abbreviation use;
- heading patterns and section transitions;
- examples, analogies, synthesis, and presentation of author experience;
- citation placement, figure/table introductions, and caption voice;
- representative passages named in the profile.

A changed rhythm is not automatically a defect. Report style drift only when it
violates the confirmed baseline without justification or harms clarity,
consistency, scholarly function, or accessibility.

## Revision Rules

- Preserve sound arguments, usable prose, citations, tables, examples,
  distinctive synthesis, and defensible author stance.
- Recast self-reference only for a documented accuracy, integrity, evidence,
  logic, clarity/accessibility, approved-QC, or mandatory-rule reason.
- Map every material voice, terminology, rhythm, heading, or
  citation-presentation change to an approved QC item or mandatory rule.
- Log major removals, changed claims, representative before/after checks, and
  justified style departures in `draft-audit.md`, `revision.md`, or
  `final/revision-log.md` as the task contract requires.
- Never edit a user source or `source/original-manuscript.docx` in place.

## Legacy Fallback

For an imported project without `source/style-profile.md`, compare directly
with `source/original-manuscript.docx`, record `LEGACY_FALLBACK`, and continue
through the existing gates. For an older user-draft chapter, use the source path
and checksum in `draft-audit.md`. Absence of a profile alone is not a blocker
unless an import/audit explicitly declared that the profile should exist.

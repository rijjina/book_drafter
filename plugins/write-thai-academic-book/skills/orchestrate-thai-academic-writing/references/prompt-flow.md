# Copy-Ready Prompt Flow

Use only the next open prompt. Replace angle-bracket placeholders with absolute
paths and declared project facts.

## New Project

1. `Use $write-thai-academic-book with task select-document-type. Document type: <teaching-notes|book|textbook>. Working title: <title>. Target readers: <readers>. Do not draft the outline.`
2. `Use $write-thai-academic-book with task project-setup. Use the approved type. Define the brief, scope, exclusions, author contribution, quality target, and governing standard. Stop for approval.`
3. `Use $write-thai-academic-book with task draft-outline. Create project/outline.md from the approved brief. Plan reader journey, chapter sequence, evidence, synthesis, contribution, and rights-sensitive materials. Do not draft chapters.`
4. `Use $assess-thai-academic-manuscript with task assess-outline. Input: <outline>. Document type: <type>. Mode: REFERENCE_ONLY. Use supplied references; do not search current rules or edit the outline.`
5. `Review <author-revision-plan.md> with me. Explain BLOCKER, MAJOR, MINOR, and NOTE findings. Wait for explicit CR/RV approval.`
6. `Use $write-thai-academic-book with task outline-qc and assessment package <directory>. Record the package pointer. Apply no revision until approved IDs are recorded.`
7. When IDs are approved: `Record project approval as CHANGES_REQUESTED for <approved CR/RV IDs>. Use $write-thai-academic-book with task revise-outline. Apply only those IDs, preserve defensible content, and stop for approval. Reassess material changes.`
8. `Use $research-outline-evidence in SCOPING mode. Project brief: <brief>. Outline: <outline>. Local sources: <paths>. Search local-first in Thai and English. Produce READY_FOR_MATRIX; do not edit outline or Matrix.`
9. `Use $build-outline-matrix. Inputs: <outline> and <evidence-package>. Create exactly six columns and one evidence-checkable Claim per row. Mark unverified evidence precisely; do not invent citations.`
10. When gaps remain: `Use $research-outline-evidence in GAP_FILL mode. Inputs: <outline>, <matrix>, and <evidence-package>. Verify every Claim and evidence gap, preserve contrary evidence, and create a Matrix handoff without editing the Matrix.`
11. `Use $build-outline-matrix to revise <matrix> from the validated handoff in <evidence-package>. Preserve six columns and row anchors. Validate and report READY_TO_DRAFT or the blocking status.`
12. `Use $write-thai-academic-book with task draft-chapter <NN>. Outline: <outline>. Outline Matrix: <matrix>. Evidence Package: <evidence-package>. Draft Markdown from verified evidence, update sources and rights, and do not create DOCX or run QC.`
13. `Use $assess-thai-academic-manuscript with task assess-chapter. Input: <draft.md>. Document type: <type>. Mode: <mode>. Assess with exact locators; do not edit.`
14. `Review the chapter revision plan with me and wait. Approved revision IDs: <RV-...>. After approval, use $write-thai-academic-book with task revise-chapter <NN> and apply only those IDs.`
15. `Use $assess-thai-academic-manuscript with task assess-manuscript. Input: <stable manuscript directory>. Document type: <type>. Mode: CURRENT_RULES. Use the refreshed rule register for <institution/rank/route/date>. Do not edit.`
16. `Review the manuscript revision plan with me and wait. Approved revision IDs: <RV-...>. Record CHANGES_REQUESTED, then use $write-thai-academic-book with task revise-manuscript and apply only those IDs. Do not produce DOCX.`
17. `Use $assess-thai-academic-manuscript with task assess-manuscript on the revised stable manuscript. Use the same declared route and current-rule cutoff. Produce a fresh package whose input hash matches.`
18. `Use $write-thai-academic-book with task final-qc and the latest validated ASSESS_MANUSCRIPT package <directory>. Run mechanical preflight; do not recompute academic findings or create DOCX.`
19. `I approve the final QC. Status: APPROVED. Deliverable: DOCX. Use $write-thai-academic-book with task produce-document. Create only final/manuscript.docx, render every page, inspect it, and remove temporary render files.`

Insert an explicit `refresh-governing-rules` assessment prompt before a
`CURRENT_RULES` assessment. Include institution, target rank, official field,
document type, submission route, and intended filing date.

## Imported Manuscript

Start with: `Use $write-thai-academic-book with task import-manuscript. Document type: <type>. Input: <existing-DOCX>. Project root: <project-root>. Preserve the original byte-for-byte; create only source/original-manuscript.docx, source/import-report.md, source/style-profile.md, detected chapter draft.md files, and pending source/approval.md. Stop on any existing-output collision. Do not revise or assess yet.`

Then use whole-manuscript assessment, writer `manuscript-qc`, explicit revision
ID approval, writer `revise-manuscript`, a fresh assessment, final QC, and the
same explicit DOCX production prompt.

## Teaching Handout

Start with: `Use $thai-academic-teaching-material. Inputs: <transcripts>, <slides>, <course/OBE/TQF>, and <institutional template>. Map sources, rewrite as formal Thai teaching material, align CLO/PLO, and preserve source and rights notes.`

Assess the result with `$assess-thai-academic-manuscript` and
`document_type: TEACHING_HANDOUT`. After the author approves named revision IDs,
validate the teaching approval artifact, revise only those IDs with the
teaching-material skill, then use `documents` to create, render, and inspect the
DOCX.

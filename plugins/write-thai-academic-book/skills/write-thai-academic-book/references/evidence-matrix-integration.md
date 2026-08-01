# Evidence And Outline Matrix Integration

Use this contract only for `draft-chapter`. Research and Matrix preparation are
owned by their companion skills; the writer consumes validated handoffs and
does not recompute them.

Require both:

```powershell
--outline-matrix <project-owned-matrix.md>
--evidence-package <project>/research/<scope-id>/evidence-package.md
```

Before drafting:

1. Validate the Evidence Package against the current approved outline. For
   `GAP_FILL`, also validate it against the exact current Matrix.
2. Validate the Matrix with the `build-outline-matrix` validator.
3. Run the orchestrator handoff validator with `--stage draft-chapter`.
4. Require Matrix metadata and `validator_status` `READY_TO_DRAFT`, the exact
   six columns, and no unresolved `[ต้องค้นหลักฐาน: ...]` cells.
5. Accept `SCOPING/READY_FOR_MATRIX` when no Matrix gap-fill was needed and the
   Matrix `source_basis` names that package. Otherwise require
   `GAP_FILL/READY_FOR_HANDOFF` mapped to the current Matrix.

Use verified evidence and exact locators from the package. Do not copy the
Matrix wholesale into prose, invent missing support, silently broaden a Claim,
or let a package status act as author approval. If Claim fingerprints, outline,
Matrix, or evidence changed, block drafting until the companion validators pass
again.


# Choose analyses by the question

| User question | Initial analysis | Conditions for stronger inference |
|---|---|---|
| Which cells express my gene? | Expression/detection by documented cell type and donor | Confirm annotation, gene mapping, detection limits and protein evidence |
| Does treatment change expression in a cell type? | Donor expression plots followed by condition DE when appropriate | Independent donors, valid design, reviewed labels and counts |
| Does a cell population expand? | Fractions per donor, with the sampling denominator stated | Dedicated compositional model and comparable sampling; not shipped here |
| Which program might explain the change? | Donor DE, then a predeclared gene set and background | Enrichment requires an additional tool; report gene-set version and multiplicity |
| Is one state becoming another? | Examine states, time points and lineage evidence | Trajectory tools are additional; pseudotime alone does not establish lineage |
| Do these cells communicate? | Examine ligand/receptor expression and experimental context | Coexpression alone does not establish functional communication |

The bundled `research` command supports the first descriptive step. It requires
H5AD `layers['counts']` and exact gene IDs, and gives each eligible donor equal weight
within a condition. It reports mean per-cell log1p(CP10K) and the fraction of cells
with a nonzero count. Neither is a protein measurement or a differential-expression
test. A donor appearing in multiple conditions is paired; do not treat those rows
as independent groups in a subsequent test. Missing cell types are absent observations.

Use published labels with an explicit source for initial summaries. New automated
proposals are exploratory. HPA-guided human review retains its own requirements;
never claim it was completed by supplying a label-source string. Count-based DE
retains the existing reviewed-label and replication checks.

Record normalization, support thresholds, batch choices and sensitivity checks in
the run. Repeat only analyses that resolve a material uncertainty. Keep unadjusted
and alternative analyses distinguishable, and report evidence that weakens the
user's initial hypothesis as well as evidence that supports it.

# Condition DE decisions

Clarify biological question, tissue/cell type, case/control, replicate unit and
paired versus independent design before fitting. Paired mode requires the same
biological donor in both requested conditions. Unpaired mode requires distinct
donors across conditions. A technical repeat or random split of cells is not a
new donor. Cell-culture experiments need a justified independent biological
replicate unit; do not label technical wells as donors without checking design.

Sum full retained raw counts by donor × condition × reviewed cell type. Default
eligibility is 20 cells per group and 3 donors/pairs; this is not a power analysis.
Missing populations are excluded, not zero-filled. Unknown labels are excluded.
Paired model: ~ donor + condition. Unpaired: ~ condition. More complex designs,
continuous time, interactions and covariates require a separately reviewed model;
do not silently collapse them to these two supported designs.

PyDESeq2 uses an explicit case/control contrast. Log2FC > 0 means higher in case.
The output keeps NA adjusted p-values and reports the number of fitted genes
separately from the number with nonmissing padj. BH adjustment is within cell
type; repeated tests across types need an explicit study-wide strategy.

Batch effects completely aligned with treatment cannot be separated by adding
a collinear covariate. State this limitation; DE is an association, not causal
proof. Report donor counts, exclusions, count/metadata tables and effect sizes,
not just a list of significant genes. No eligible analysis means blocked.

Sources: https://pydeseq2.readthedocs.io/en/stable/auto_examples/plot_step_by_step.html
https://www.nature.com/articles/s41467-021-25960-2

---
card_id: scrna-donor-design
version: 0.1
status: draft
species: human_or_mouse
tissue: unspecified
assay: scRNA-seq
analysis_stage: condition_differential_expression
reviewer: null
reviewed_on: null
---

# Check biological replication before a condition comparison

This is an engineering-prepared authoring example. Scientific review is pending;
it is not an approved protocol or a production knowledge entry.

## Biological purpose

Determine whether expression differences between conditions can be estimated at
the level of independent biological samples for a specified cell population.
The proposed comparison concerns association; causal claims need further design
or experimental evidence.

## Required evidence

Inspect verified cell-to-sample and sample-to-donor mappings, condition labels,
paired sampling, technical repeats, cell-type review state and available count
representation. Capture or batch IDs are not automatically donor IDs. Check
whether condition is confounded with donor, processing batch or another factor.

## Proposed decision

For population-level condition DE, preserve biological replication in the model.
A donor-aware pseudobulk approach can be appropriate when supported by the assay,
design, counts and available biological replicates. Verify the local runner's
actual supported design instead of assuming it can fit any requested covariate.

If the donor mapping is unavailable, ask for it or report the limitation. A
well-labeled descriptive expression summary may still be useful, but it must not
be presented as an independently replicated condition test.

## Example and counterexample

The inspected HPA export for [GSE115469](../../datasets/studies/GSE115469.md)
contains cell IDs, clusters and UMAP coordinates but no donor field. The original
study having five donors does not recover the missing mapping in this export.

Splitting cells from one donor into several random groups does not create new
biological donors. A small p-value obtained that way cannot establish replicated
population-level evidence.

## Quantification and limitations

Record donors per group, cells per donor and cell population, exclusions, count
aggregation, supported design terms, effect estimates and multiple-testing
procedure. Exact minimums and analysis settings require the reviewed study design
and tool contract; this example does not prescribe a universal threshold.

## Sources

- Published methodological evidence: Squair et al. (2021), *Confronting false
  discoveries in single-cell differential expression*,
  [10.1038/s41467-021-25960-2](https://doi.org/10.1038/s41467-021-25960-2).
  Consult the biological-replication analyses and Methods when reviewing this card.
- Project input contract: [data contract](../../../plugins/scrna-seq-workbench/references/data-contract.md).
- Local source observation: [HPA liver provenance](../../datasets/provenance/GSE115469-hpa-v25.1.json).

## Review history

| Version | Reviewer | Date | Decision |
|---|---|---|---|
| 0.1 | Unassigned | Pending | Draft example; scientific review pending |

# Shared data contract (v1)

The plugin installation is read-only during analysis. Put inputs and fresh output
directories in the user's project, not in this package/cache.

| Stage | Numerical input | Main output | Required metadata |
|---|---|---|---|
| report | Report + verified metrics JSON | normalized_metrics.json, review.md | sample, platform/assay, species, report version |
| qc | Raw integer UMI X or counts layer | filtered.h5ad, cell_qc.csv, gene_qc.csv | sample_id or explicit single-sample label |
| integrate | H5AD with counts and explicit species; mapped cycle gene set when needed | full-gene integrated.h5ad, required scVI model, cycle diagnostics, candidate graphs/Leiden/UMAP and training history | verified batch key or None; S/G2M covariates unless explicit user override; parameter selection pending review |
| annotate | Full retained genes/counts + cluster IDs | annotated.h5ad, proposals, evidence, exploratory markers | species, tissue, reference provenance |
| de | Reviewed labels + counts | pseudobulk matrices/design, exclusions, DE tables | actual donor_id and condition |

`layers['counts']` always means finite nonnegative integer UMI counts, after any
declared cell/gene exclusions. It is never corrected expression. Integration
uses an HVG subset for fitting but outputs every retained gene. `X` and `lognorm`
after integration/annotation mean log1p(CP10K). These stages recompute them from
counts rather than trust inherited `.raw`. IDs must be unique; do not silently
merge gene symbols or rename barcodes without a mapping.

`cell_type_proposal` is unreviewed. `cell_type` plus
`uns['cell_type_reviewed']=true` is the output of an explicit review table. An
external reviewed column can be named explicitly for DE, with a review declaration.
Unknown is an allowed annotation and is excluded from condition DE by default.

Cell metadata CSV: cell_id must match the matrix index exactly. Optional columns
include sample_id, capture_id, donor_id, condition, batch. A physical capture,
technical replicate and biological donor are different entities. Do not infer
donors from names such as rep1. Pooled captures need real demultiplexing metadata.
For multiple matrices, merge with explicit barcode namespaces and gene mapping
before invoking the CLI; this release does not implement multi-matrix assembly.

Each stage uses a new/empty output directory. `report.json` records parameters,
versions, source/input/output SHA-256, warnings and complete/blocked/failed status.
It is finalized on failure as well. Exits: 0 complete, 2 error, 3 analysis blocked.
These are restartable stages, not automatic checkpoint/resume of a partial fit.
Hashing a large input is an intentional full read. Runtime/memory depend on input
size; no performance claim is made for atlas-scale data.

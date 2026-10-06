---
card_id: scrna-kb-06-representation
version: 0.1.0
status: draft
plugin_version: 0.3.0
scientific_reviewer: null
reviewed_on: null
production_rag_eligible: false
---

# Understand PCA, scVI, clustering and UMAP as different operations

Learning draft. Scientific review is pending.

## Principle

PCA summarizes directions of variation using linear combinations of features. scVI fits a probabilistic latent-variable model to counts and can include a batch covariate. Neither method guarantees removal of unwanted variation while preserving every biological signal. When batch and condition coincide, the data may not identify which differences are technical.

A neighbor graph connects cells with similar representations. Leiden partitions that graph. UMAP displays a low-dimensional layout of neighborhood structure; distances between separated islands, island sizes and axis values are not direct measurements of cell lineage or causal relatedness.

## Decision sequence

1. Decide whether a simple uncorrected baseline is sufficient. Inspect batch, donor, condition and expected populations together.
2. Choose a representation and record selected features, dimensions and seed. Use scVI only with its dependencies installed and an explicit batch interpretation.
3. Build neighbors, cluster and visualize. Compare a small set of justified alternative resolutions or neighborhood sizes in separate output directories.
4. Inspect whether results preserve expected biology across donors and whether apparent clusters track technical variables.
5. Assess stability with markers and sample composition; do not pick a parameter solely because its UMAP looks cleaner.

## Actual plugin behavior

`--backend pca` provides an explicitly uncorrected baseline. It is not scVI batch correction. scVI uses a negative-binomial model in this implementation, configured from counts; training duration matters. The two-epoch optional smoke test checks execution only. The current runner does not automatically export a comprehensive training-convergence diagnostic report.

Read `integrated.h5ad`, `umap_clusters.png` and the stage report. Verify that QC-retained genes/counts survive the representation step. A cluster number is a partition label, not a cell-type name.

## Self-check

**Question:** Two clusters are far apart on UMAP. Does that prove different lineages?

**Suggested answer:** No. Inspect marker evidence, representation stability and independent biological context. UMAP separation alone cannot establish lineage.

## Further reading

- [scVI model and assumptions](https://docs.scvi-tools.org/en/stable/user_guide/models/scvi.html).
- [UMAP original method](https://arxiv.org/abs/1802.03426).

## Implementation sources

- [plugins/scrna-seq-workbench/scripts/scrna_core/integrate.py](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/scripts/scrna_core/integrate.py)

[Learning path](../LEARNING_PATH.md) | [Review worksheet](../REVIEW_WORKSHEET.csv)

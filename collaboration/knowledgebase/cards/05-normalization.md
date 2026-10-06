---
card_id: scrna-kb-05-normalization
version: 0.1.0
status: draft
plugin_version: 0.3.0
scientific_reviewer: null
reviewed_on: null
production_rag_eligible: false
---

# Separate raw counts, normalization and feature selection

Learning draft. Scientific review is pending.

## Principle

A cell with more captured molecules tends to have more counts across many genes. Library-size normalization rescales each cell to a common total. The runner calculates `ln(1 + 10000 * x / T)`, where `x` is a gene's count and `T` is the cell total across the measured genes currently in the matrix. This is a relative expression measure, not an absolute molecule concentration or a batch correction.

For example, 10 counts among 1,000 total and 20 among 2,000 total produce the same normalized value, approximately 4.615. The result depends on the denominator; total-RNA shifts or dominant transcripts can affect relative interpretation.

## Decision sequence

1. Keep counts unchanged in their named layer. Distinguish the matrix used for visualization from the matrix used for count-based modeling.
2. Normalize from counts rather than repeatedly normalizing an already transformed matrix.
3. Select highly variable genes (HVGs) to focus representation learning. Inspect biological relevance and technical drivers; variability alone does not establish biological importance.
4. Use parameters appropriate to the data size. The exercise uses 80 HVGs out of only 100 artificial genes, which is not a recommendation for real tissue.
5. Confirm that genes omitted from representation fitting remain available in the output for targeted expression questions.

## Actual plugin behavior

Integration recomputes log-normalized values from counts. The `seurat` HVG flavor uses log-normalized values; `seurat_v3` uses counts and requires its optional dependency. Fitting uses the selected features, while the written H5AD preserves the QC-retained gene set and counts. PCA additionally scales the selected genes with clipping at 10 before decomposition. scVI receives counts rather than the log-normalized matrix.

## Self-check

**Question:** Should pseudobulk DE sum log-normalized values?

**Suggested answer:** No. This runner sums raw counts within biological groups and lets its count model handle normalization and dispersion. Summing transformed expression changes the modeled quantity.

## Implementation sources

- [plugins/scrna-seq-workbench/scripts/scrna_core/common.py](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/scripts/scrna_core/common.py)
- [plugins/scrna-seq-workbench/scripts/scrna_core/integrate.py](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/scripts/scrna_core/integrate.py)

[Learning path](../LEARNING_PATH.md) | [Review worksheet](../REVIEW_WORKSHEET.csv)

---
card_id: scrna-kb-02-data
version: 0.1.0
status: draft
plugin_version: 0.3.0
scientific_reviewer: null
reviewed_on: null
production_rag_eligible: false
---

# Understand counts, identifiers and metadata before analysis

Learning draft. Code behavior is tied to the source snapshot below; scientific review is pending.

## Principle

A cell-by-gene count matrix links molecular measurements to cell identities. UMI counts approximate captured molecules after deduplication; sequencing reads are not interchangeable with UMIs. Normalized or logarithmic expression values answer different numerical questions and must not be supplied to a raw-count model as if they were original counts.

AnnData stores cells in rows, genes in columns, cell metadata in `obs`, gene metadata in `var`, and named matrices in `layers`. A layer named `counts` is a storage convention, not proof of provenance.

## Decision sequence

1. Read the source Methods and download description. Establish assay, species, reference genome and whether the matrix represents UMI counts, reads or transformed values.
2. Check file dimensions, unique cell IDs and unique gene IDs. Confirm that metadata match the matrix by ID, not just row position.
3. Record cell-to-sample and sample-to-donor mappings, condition, technical batch and label provenance separately.
4. Inspect nonnegative, finite, near-integer values and positive totals. These checks reject many invalid inputs but cannot prove that values are raw UMIs. Never round normalized values to manufacture counts.
5. Preserve the downloaded source and its hash. Write conversions into a new directory with mapping and conversion records.

## Actual plugin contract

Inputs are H5AD, 10x H5 or 10x-compatible matrix directories. QC can accept raw values in H5AD `X` when no counts layer exists, validate them, then preserve them in `layers['counts']`. Later stages require the count layer. CSV metadata must have matching cell IDs; conflicting or incomplete mappings are rejected. Automatic gene-ID remapping is not provided by the expression-summary command.

The inspected HPA liver export for GSE115469 has cell IDs, clusters and UMAP coordinates but no donor column. Knowing that the original study had multiple donors does not recover the mapping in this particular export. Source-specific provenance remains necessary.

## Self-check

**Question:** A matrix contains only integers. Is it valid input for a UMI-based analysis?

**Suggested answer:** Not established. Check the assay and processing history. Numeric validation and provenance validation answer different questions.

## Implementation sources

- [plugins/scrna-seq-workbench/scripts/scrna_core/common.py](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/scripts/scrna_core/common.py)
- [collaboration/datasets/provenance/GSE115469-hpa-v25.1.json](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/collaboration/datasets/provenance/GSE115469-hpa-v25.1.json)

[Learning path](../LEARNING_PATH.md) | [Review worksheet](../REVIEW_WORKSHEET.csv)

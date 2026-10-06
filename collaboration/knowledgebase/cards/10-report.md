---
card_id: scrna-kb-10-report
version: 0.1.0
status: draft
plugin_version: 0.3.0
scientific_reviewer: null
reviewed_on: null
production_rag_eligible: false
---

# Build a conclusion from traceable observations

Learning draft. Scientific review is pending.

## Principle

A useful report connects a question to measured results, the analysis that produced them and the limits of the inference. Reproducibility means another person can identify the inputs and reconstruct the computation. It does not establish that the scientific interpretation is correct.

## Decision sequence

1. Restate the original question and identify which part was answerable with the available data.
2. Report concrete values and the relevant donor/cell counts. Link each figure and table to its stage and parameters.
3. Separate direct observations, statistical comparisons and biological hypotheses. State competing explanations and missing evidence.
4. Record exclusions, provisional labels and incomplete stages. A blocked DE analysis is not evidence of no differential expression.
5. Recommend an informative next experiment or data request that could distinguish alternatives.
6. Save software versions, inputs and hashes, parameters, command outcomes and generated artifacts in an isolated run directory.

## Actual plugin behavior

Stages use separate output directories and produce reports with provenance and status. Reusing a populated output directory is rejected. Successful calculations, blocked scientific prerequisites and execution errors are distinct outcomes. Errors before stage initialization may not have a complete stage report, so retain the command outcome too. A crash is not automatically a safely resumable model request or partial fit.

The original data file should remain unchanged. QC output legitimately differs because excluded cells and genes are recorded; later representation fitting should not silently replace retained raw counts with transformed values. Compare the appropriate stages rather than assuming all matrices in a workflow should be identical.

## Report outline

Question; study design; input provenance; decisions and parameters; results with values; alternative explanations; limitations; next experiment; files and reproducibility record.

## Self-check

**Question:** Does a completed run with an attractive UMAP demonstrate a valid biological discovery?

**Suggested answer:** No. Execution, data suitability and biological inference require separate checks. The report should expose all three.

## Implementation sources

- [plugins/scrna-seq-workbench/scripts/scrna_core/common.py](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/scripts/scrna_core/common.py)
- [plugins/scrna-seq-workbench/scripts/scrna.py](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/scripts/scrna.py)

[Learning path](../LEARNING_PATH.md) | [Review worksheet](../REVIEW_WORKSHEET.csv)

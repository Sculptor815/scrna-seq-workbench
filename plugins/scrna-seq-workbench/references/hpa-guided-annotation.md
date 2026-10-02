# HPA-guided annotation policy

Source: [HPA single-cell transcriptomics methods](https://www.proteinatlas.org/humanproteome/single%2Bcell/single%2Bcell%2Btype/method/transcriptomics), accessed 2026-10-02. This is an independent implementation, not an HPA product or a claim of exact replication.

## Published basis

HPA annotates clusters manually using tissue-specific markers, including publication and pathology markers. It assigns detailed and main cell types, displays marker heatmaps, refines selected clusters through subclustering, and omits ambiguous main types from atlas aggregation. Its human tissue scope does not directly validate mouse labels. The documented clustering route uses PCA, 40 components, 15 neighbors and Leiden resolution 1; scVI is a separate Workbench alternative.

## Workbench contract

Use `--annotation-policy hpa-guided` (the default). Computational marker scores propose candidates; they never establish an HPA-reviewed label. `--hpa-expression` also supplies candidate evidence only. Neither nCPM specificity nor UMAP island separation replaces marker review.

Each run creates:

- `marker_expression.csv`: cluster/gene detection fractions and mean log-normalized expression, including missing-marker indicators.
- `marker_heatmap.png`: expression evidence for the supplied panel.
- `annotation_proposals.csv` and `annotation_evidence.csv`: alternatives, score margins and panel coverage.
- `hpa_review.template.csv`: an initially pending record for every cluster.

Read the packet before proposing final labels. Record the main type in `cell_type` and the within-study detail in `cell_type_detail`. If finer resolution is unsupported, repeat the defensible main type. Use species-matched markers with traceable sources; mouse capitalization is not an orthology mapping. Assess opposing evidence, tissue plausibility, sample composition and possible doublets. Decide whether a mixed cluster requires subclustering; the script does not perform this automatically.

The review file requires `decision` (accept/unresolved/mixed), `reviewer`, `reviewer_type`, `markers_for` (semicolon-separated), `markers_against`, `evidence_source`, `qc_review`, `subcluster_review` and `rationale`. Write an explicit assessment such as "none observed in the tested panel" rather than leaving opposing evidence blank. A real reviewer must inspect the expression evidence; checking a CSV schema does not validate their judgment.

Only an actual human review can be recorded as `reviewer_type=human`. The agent may draft all evidence and suggested decisions, but must not fabricate that identity or approval. Accepted labels need at least two available supporting genes, a Workbench safeguard rather than an HPA numerical rule. Unresolved/mixed clusters retain `Unknown` at both levels and `atlas_aggregation_eligible=false`. Keep them in evaluation denominators; exclusion must not inflate annotation accuracy. This flag governs ambiguity only and does not certify the other HPA atlas inclusion criteria.

Apply a completed file in a new output directory using `--reviewed-labels`. The original clusters and raw counts remain unchanged. The historical four-column contract is available only through explicit `--annotation-policy legacy`; it is never described as HPA-guided finalization.

## What remains outside this implementation

We do not bundle the full HPA marker survey or reproduce its original manual decisions, tissue preprocessing, subclustering or atlas normalization. HPA-style review is not complete while any row is pending. Do not give final HPA annotation accuracy to the five legacy datasets until their independent review is complete. Keep the original paper labels quarantined until scoring; they are references, not annotation instructions.

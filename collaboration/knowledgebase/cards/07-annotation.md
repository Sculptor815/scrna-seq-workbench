---
card_id: scrna-kb-07-annotation
version: 0.1.0
status: draft
plugin_version: 0.3.0
scientific_reviewer: null
reviewed_on: null
production_rag_eligible: false
---

# Treat cell annotation as evidence review

Learning draft. Scientific review is pending.

## Principle

A cell identity is a biological interpretation supported by coherent positive markers, contradictory markers, tissue context and technical quality. A single transcript can reflect shared biology, ambient RNA, a doublet or a transitional state. Automated proposals organize evidence; they do not establish that a researcher has inspected it.

## Decision sequence

1. Confirm species, tissue and gene identifiers. Use a panel with a documented source and plausible competing identities.
2. Inspect marker expression and detection fractions, not only the proposed top label. Check whether the marker is available in the matrix.
3. Consider contradictory markers, QC patterns, donor distribution and mixed populations. Review subclusters when the question and evidence justify them.
4. Record accepted identities or retain Unknown/mixed/unresolved status. Do not force every cluster into a familiar type.
5. Complete the review evidence and actual reviewer identity before using reviewed labels for condition DE.

## Actual plugin behavior

The score uses marker expression standardized across clusters and aggregated into candidate scores. It is a heuristic relative to the current clusters, not a calibrated probability of identity. Default safeguards include informative marker availability, overlap and separation from a competing label. Changing the cluster set can change the score.

HPA-guided review records supporting and opposing markers, evidence source, QC/subcluster review and rationale. The program can validate submitted fields but cannot prove that a human really inspected them. The agent must never fill a human-review claim on the researcher's behalf. New proposals do not inherit an old final label automatically.

Read `marker_expression.csv`, the proposal/evidence files, `marker_heatmap.png` and `hpa_review.template.csv`. The review template starts pending. Synthetic fixture truth is only for engineering checks, not evidence of accuracy on real cells.

## Self-check

**Question:** The top annotation score is 0.9. Is the label 90% certain?

**Suggested answer:** No. Its scale is not a probability. Inspect markers, alternatives and applicable review requirements.

## Implementation sources

- [plugins/scrna-seq-workbench/scripts/scrna_core/annotate.py](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/scripts/scrna_core/annotate.py)
- [plugins/scrna-seq-workbench/scripts/scrna_core/annotation_policy.py](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/scripts/scrna_core/annotation_policy.py)

[Learning path](../LEARNING_PATH.md) | [Review worksheet](../REVIEW_WORKSHEET.csv)

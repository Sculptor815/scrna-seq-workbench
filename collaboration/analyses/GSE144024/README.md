# GSE144024 analysis records

This directory keeps the user-designated manual analysis and two future AI analyses as separate, traceable submissions. Study-specific results live here; general analysis rules remain in the [knowledge base](../../knowledgebase/README.md).

| Record | Status | Contents |
|---|---|---|
| [Manual v1](manual-v1/README.md) | Submitted; archived on 2026-10-07 | English report, original QC/marker/annotation artifacts, extracted tables and a knowledge-base supplement checklist |
| [AI analysis 1](ai-01/README.md) | Awaiting user submission | No analysis results yet |
| [AI analysis 2](ai-02/README.md) | Awaiting user submission | No analysis results yet |

## Adding the AI analyses

Preserve each run's actual outputs and record its model/agent version, inputs, prompts, parameter choices, annotation/review process, runtime and resources. Use the same report headings: grouping and inputs; QC and retained cells; representation and clustering; annotation and marker evidence; DE; limitations; artifact provenance.

State whether a run started from raw counts, QC-filtered data or existing embeddings, whether cell/gene universes match, and whether the agent saw the manual labels. Keep human edits distinguishable from original AI output. Do not populate unsubmitted runs with estimates or scores.

When comparison is requested later, align cell IDs and label granularity before calculating agreement. Different Leiden IDs are not label matches; different retained-cell sets require an explicit common-cell denominator and retention analysis. Agreement with this manual baseline is not independently established biological accuracy. No comparison or ranking has been performed here.

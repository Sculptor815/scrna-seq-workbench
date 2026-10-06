---
card_id: scrna-kb-09-expression
version: 0.1.0
status: draft
plugin_version: 0.3.0
scientific_reviewer: null
reviewed_on: null
production_rag_eligible: false
---

# Answer focused expression questions without overstating them

Learning draft. Scientific review is pending.

## Principle

A mean expression value and a detection fraction answer different questions. The former summarizes measured relative abundance; the latter is the fraction of cells with nonzero observed counts. A zero can reflect limited sampling rather than absence of the transcript. Neither summary alone establishes a mechanism or a condition effect.

Pooling all cells can let a donor with many captured cells dominate the result. This runner first summarizes within donor-condition-cell-type groups, then weights eligible donors equally when producing condition summaries. Equal weighting does not resolve confounding or create missing replication.

## Decision sequence

1. Specify the exact gene identifiers and the population of interest. Check their presence before interpreting a missing row.
2. Establish counts, donor IDs, condition and label provenance. The current command requires donor and condition columns even for its descriptive summaries.
3. Inspect donor-level mean log-normalized expression, detection fraction and group cell counts.
4. Compare donor variation with the aggregated display. Keep missing groups distinct from observed zero expression.
5. State whether labels are exploratory, externally supplied or reviewed. Follow the DE route only when its separate requirements are met.

## Plugin behavior and outputs

Normalization uses the total across all measured genes currently present, not just the requested gene list. The default eligible group minimum is 20 cells. Low-cell groups remain in detailed output but are excluded from eligible condition aggregation. The command warns about fewer than three donors and does not turn descriptive summaries into a replicated significance test. No eligible groups results in a blocked status.

Gene matching is exact. Some missing genes trigger a warning; no matching genes triggers an error. Figures show a limited subset (first 12 genes and 60 rows), so read the complete tables before concluding that an omitted item was absent. The current HPA liver export cannot satisfy this command's donor requirement without a verified additional mapping.

## Self-check

**Question:** Can an absent donor-cell-type group be filled with zeros?

**Suggested answer:** Not as an observed expression measurement. Absence of sampled cells and measured zero counts within sampled cells are different observations.

## Implementation sources

- [plugins/scrna-seq-workbench/scripts/scrna_core/research.py](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/scripts/scrna_core/research.py)

[Learning path](../LEARNING_PATH.md) | [Review worksheet](../REVIEW_WORKSHEET.csv)

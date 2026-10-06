---
card_id: scrna-kb-01-question
version: 0.1.0
status: draft
plugin_version: 0.3.0
scientific_reviewer: null
reviewed_on: null
production_rag_eligible: false
---

# Turn a biological question into an observable comparison

Learning draft. Code behavior is tied to the source snapshot below; scientific review is pending.

## Principle

A useful question identifies a population, a measurement and a comparison. An expression map answers where transcripts were detected; it does not establish that a gene causes a phenotype. A condition comparison additionally needs independent biological replication and attention to confounding. The strength of the claim must follow the study design.

## Before acting

Write down species, tissue, target population, exposure or condition, intended comparison, outcome and the unit of biological replication. Identify whether the request is descriptive, comparative or causal. Distinguish a donor from a sequencing capture: several libraries from one person are not several independent people.

## Decision sequence

1. Rewrite a broad topic into a question with an observable outcome. Example: among reviewed liver macrophages, how does gene X expression vary across donors and conditions?
2. List the minimum evidence needed: usable counts, gene identifiers, labels with provenance, and donor/condition mappings for that comparison.
3. Check whether the data contain the proposed comparison. A healthy-only atlas cannot estimate a disease effect.
4. Choose the shortest supported route. Existing documented labels may support an exploratory summary; rebuilding every cluster is not always necessary.
5. State missing information and a useful restricted analysis when the full question is unsupported. Do not invent donor assignments.

## Plugin behavior and output

`scrna-research` is a Skill that guides the host assistant. Discovery depends on that host's available search tools; the Python runner is not a standalone literature-search agent. Record the question, evidence requirements, selected dataset and intended limits before tool execution. The current runner supports focused expression summaries but does not test differential cell abundance or causal mechanisms.

## Self-check

**Question:** A disease cohort has one donor and 8,000 cells. Can those cells establish a replicated disease effect?

**Suggested answer:** No. They provide many measurements within one donor. Describe the observation and request biological replication; more cells cannot recover missing independent donors.

## Implementation sources

- [plugins/scrna-seq-workbench/skills/scrna-research/SKILL.md](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/skills/scrna-research/SKILL.md)
- [plugins/scrna-seq-workbench/references/study-selection.md](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/references/study-selection.md)

[Learning path](../LEARNING_PATH.md) | [Review worksheet](../REVIEW_WORKSHEET.csv)

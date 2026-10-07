# scRNA-seq Workbench

Version **0.4.0 — with knowledge base · research preview**.

A single-cell RNA-seq analysis plugin for **Codex**, **Claude Code** and
**DeepSeek Harness**. Workbench combines executable analysis tools with a bundled
knowledge base covering study design, quality control, scVI, cell annotation and
differential expression.

## Analysis workflow

Start with your data or a biological question. The agent checks sample relationships,
defines which datasets to analyze together, and runs the relevant stages.

| Stage | Skill | Main outputs |
|---|---|---|
| Study selection and exploration | `scrna-research` | Relevant studies, experimental context and expression summaries |
| Sequencing report review | `sequencing-report-review` | Sequencing metrics and delivery checks |
| Quality control | `scrna-qc` | QC plots, filtering records, doublet assessment when applicable and filtered counts |
| Representation and clustering | `scrna-scvi-umap` | scVI model, cell-cycle diagnostics, candidate clusters and UMAPs |
| Cell annotation | `scrna-cell-annotation` | Marker expression, candidate cell types and human review records |
| Condition comparison | `scrna-condition-de` | Donor-level pseudobulk counts and differential-expression results |

New representation workflows use **scVI with cell-cycle covariates**, with or
without technical batches. Raw counts and the full retained gene set are preserved.

Several neighbor counts and Leiden resolutions are presented for selection.
Annotation follows tissue-specific marker evidence and HPA-guided review, with
additional investigation of unresolved populations. Final labels require human
review; condition DE requires biological donor replicates and reviewed annotations.

Use `scrna-research` to plan an analysis, or enter a specific stage when suitable
intermediate results already exist.

## Bundled knowledge base

The [knowledge base](collaboration/knowledgebase/README.md) defines how the agent
groups datasets, chooses parameters, investigates uncertain annotations and reports
results. All six Skills point to the relevant sections.

It ships inside the plugin. Synchronization checks prevent outdated copies, and
each run records the policy hash with its parameters and software versions.
See [how agents use the knowledge base](docs/AGENT_KNOWLEDGE.md).

## Get started

1. [Install the plugin and dependencies](docs/INSTALLATION.md), then
   [connect it to your agent](docs/HOSTS.md).
2. Run the [400-cell example](docs/QUICKSTART.md) to check your environment.
3. Follow the [research workflow](docs/RESEARCH_WORKFLOW.md) or
   [analyze your own data](docs/USAGE.md).

Calculations run in your local or server Python environment. Install
`requirements-scvi.txt` for representation analysis; condition DE has additional
dependencies.

Example request:

> Analyze these datasets with scRNA-seq Workbench. Read the knowledge base,
> establish the analysis groups, and run QC and scVI. Show clustering options
> for my selection and marker-expression figures for annotation review.
> Save the analysis records and figures in my project directory.

## Analysis reports and validation

### GSE144024: manual and AI analyses

The [study collection](collaboration/analyses/GSE144024/README.md) covers human
fetal liver (FL), yolk sac (YS) and hESC-derived Day0/Day6 cells.

| Record | Method and grouping | Results |
|---|---|---|
| [Manual analysis](collaboration/analyses/GSE144024/manual-v1/README.md) | scVI; separate FL and YS, joint hESC Day0/Day6 | Final submitted annotations, annotated UMAPs, QC report and marker-expression PDFs |
| [AI analysis 1](collaboration/analyses/GSE144024/ai-01/README.md) | PCA; all four sources analyzed jointly | Exploratory annotations, marker evidence, composition and sensitivity results |
| [AI analysis 2](collaboration/analyses/GSE144024/ai-02/README.md) | PCA; independent FL, YS and hESC analyses | Three cohort reports, UMAPs and expanded marker assessment |

The manual record preserves the user's final submitted results. AI annotations
remain exploratory and await human review. Both AI runs predate the mandatory-scVI
update and have not been rerun with v0.4.0.

![Submitted manual FL annotation, Leiden clusters and confidence](collaboration/analyses/GSE144024/manual-v1/figures/FL_annotated_UMAP.png)

### Current software checks

Version 0.4.0 passed **42 local tests**, including CPU scVI training with and
without batches, count preservation, cell-cycle covariate registration, model
save/reload and candidate graph outputs. Package checks cover knowledge-base
synchronization, Skill entry points and standalone installation files.

These synthetic tests assess execution, not biological annotation accuracy.
See the [validation record](validation.json), [validation details](docs/VALIDATION.md)
and [CI results](https://github.com/Sculptor815/scrna-seq-workbench/actions).
Earlier [five-study analyses](docs/COMPARISONS.md) remain available as historical results.

## Development

[Development guide](docs/DEVELOPMENT.md) · [Changelog](CHANGELOG.md) ·
[Collaboration](collaboration/README.md) · [Data and publication sources](docs/THIRD_PARTY_SOURCES.md)

Code is MIT licensed.

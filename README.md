# scRNA-seq Workbench

Investigate biological questions with public or user-provided single-cell RNA-seq
data. This analysis plugin works with **Codex**, **Claude Code** and **DeepSeek Harness**.
Version **0.3.0 - research preview**.

Start with a hypothesis, tissue or disease, and what you want to learn. The
`scrna-research` entry point guides your assistant to find relevant studies, check
their design, run focused analyses and explain what the results support. You can
delegate routine settings without learning a pipeline first. Existing data are
welcome; a count matrix is not required to begin finding suitable studies.

## Get started

1. Follow the [installation tutorial](docs/INSTALLATION.md): Windows and Linux/macOS instructions, Python dependencies and common errors.
2. Enable the plugin in [your assistant](docs/HOSTS.md).
3. Run the [400-cell example](docs/QUICKSTART.md) to check your setup.
4. Follow [Start with a biological question](docs/RESEARCH_WORKFLOW.md) for research prompts, data selection and results.
5. Use [Analyze your own data](docs/USAGE.md) when you need the individual analysis stages.

Installing the plugin adds instructions and scripts. Its calculations use a
Python environment on your computer or server. scVI and differential expression
have additional dependencies described in the installation tutorial.

## What it does

| Skill | What you provide | What you receive |
|---|---|---|
| `scrna-research` | Biological question, context and any data/resource limits | Study shortlist, focused analysis and an evidence-based explanation |
| `sequencing-report-review` | Vendor report and sample details | A summary of sequencing metrics, source evidence and missing files |
| `scrna-qc` | UMI counts, species and sample metadata | QC measurements, filtering records and a filtered H5AD |
| `scrna-scvi-umap` | Filtered counts and a batch definition if needed | scVI or PCA representation, Leiden clusters and UMAP plots |
| `scrna-cell-annotation` | Clusters and a tissue-matched marker panel or HPA table | Candidate cell types, marker evidence and a review form |
| `scrna-condition-de` | Reviewed cell types, conditions and biological donor IDs | Donor-level pseudobulk counts and PyDESeq2 results |

Use `scrna-research` as the main entry point, or invoke one of the five analysis
Skills directly. The assistant chooses stages relevant to the question. It can reuse
documented counts and labels for an initial expression summary without rebuilding
every intermediate result. A sequencing report alone supports delivery review;
numerical expression analysis also needs a matrix and metadata.

## A first request

> Use scrna-research to investigate whether KRT8-associated epithelial states
> are relevant to lung injury and repair. Find public studies with suitable
> comparisons and explain which data could help. Choose routine analysis settings.
> Use my configured Python environment and save results under D:/lung-repair.
> Limit the first pass to a 2 GB download and one hour of computation.
> Show the evidence, limitations and a useful next experiment.

Change the paths and biological details to match your project. The assistant can
answer in your language. If you want it to choose parameters, state that in your
request and it should record the choices and their reasons.

## Inputs and scope

Supported inputs are human or mouse UMI counts in H5AD, 10x H5 or 10x-compatible
matrix directories. Each run records parameters, package versions and file hashes.
Original counts are preserved in `layers['counts']` after the declared QC exclusions.

Study discovery uses the assistant's available search/database tools. The bundled
runner supports QC, representations, annotation, donor-level DE and focused
gene-expression summaries. It does not include a standalone literature-search
service. FASTQ alignment, multi-matrix assembly, ambient-RNA correction, enrichment,
trajectory analysis, abundance testing and arbitrary DE covariates require additional
tools. HPA reference tables are optional and supplied by the user. See the
[input requirements](docs/USAGE.md) before using an existing H5AD.

Published labels can support exploratory summaries when their source is documented.
Human HPA review and the DE label/design checks retain their existing requirements.
The research entry point does not turn an automated label proposal into a reviewed label.

## Analysis and evaluation are separate

The installable plugin contains analysis Skills and scripts. Users invoke
`scrna-research` to investigate their question; no benchmark setup or scoring is
required. Results include scientific limitations and provenance.

The separate [benchmark branch](https://github.com/Sculptor815/scrna-seq-workbench/tree/benchmark/benchmarks/research) evaluates
data suitability, analytical relevance, evidence reasoning, usefulness and interaction
burden after a session. Its scoring program is not shipped on `main` or in the
plugin archive, and is never called by the analysis runner. Ratings require documented review; the calculator does not
judge scientific correctness itself. The new research protocol has no published
expert-scored results yet.

## Existing validation

[Five-study comparisons](docs/COMPARISONS.md) show published figures alongside our
UMAPs and annotation proposals for Kang, Haber, Paul, Zeisel and Baron. The three
panels in each of our plots share coordinates, showing reference labels, Leiden
clusters and proposed labels. Three published figures are available inline;
Paul and Zeisel have source links because the image downloads were unavailable.

![Kang reference labels, clusters and proposed cell types](docs/figures/kang-comparison.png)

These historical technical comparisons exposed loss of low-RNA populations, ambiguous labels and missed
rare types. Its scores describe the historical fixed-parameter workflow.
The current annotation step adds [HPA-guided review](docs/HPA_METHODS.md);
the five benchmark review forms are still pending.

They do not measure the new research workflow's ability to answer biological
questions. See the [research quality plan](https://github.com/Sculptor815/scrna-seq-workbench/blob/benchmark/docs/QUALITY_EVALUATION_PLAN.md) for the
separate pilot: question-driven studies, checked evidence and adjudicated conclusions,
including well-supported disagreements with the original paper.

Read [validation](docs/VALIDATION.md) for the measured results and remaining work,
or [benchmark verification](benchmarks/README.md) to check the frozen source and
published tables. [The review response](docs/REVIEW_FIXES.md) records the v0.2.1 corrections.

## Contributing

For joint study selection, start in the [collaboration workspace](collaboration/README.md).
The [GSE shortlist](collaboration/datasets/README.md) includes HPA sources, paper links,
input checks and editable study cards.

See [development and release instructions](docs/DEVELOPMENT.md),
[the changelog](CHANGELOG.md) and [GitHub Actions](https://github.com/Sculptor815/scrna-seq-workbench/actions).
Code is MIT licensed. Dataset and publication attribution is documented in
[Third-party sources](docs/THIRD_PARTY_SOURCES.md).

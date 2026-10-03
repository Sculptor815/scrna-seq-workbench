# Start with a biological question

After [installation](INSTALLATION.md) and [host setup](HOSTS.md), use the
`scrna-research` Skill. The assistant handles data selection and analytical choices;
you provide biological context and any limits on downloads or computation.

## Starting without data

> Use scrna-research to investigate whether KRT8-associated epithelial states are
> relevant to lung injury and repair. Find public studies that can address this
> question. Explain the donor design, available files and supporting experiments
> before selecting data. Choose routine analysis settings. Use my configured
> Python environment and save data and results under D:/lung-repair.
> Keep the initial download below 2 GB and computation below one hour.
> Give me an initial answer, its limitations and an experiment worth considering.

Adapt the organism, tissue, hypothesis and resource limits. You do not need to know
PCA dimensions or QC cutoffs. The assistant should ask about missing biological
facts, explain choices that change interpretation and record routine settings.
The specified folder must be writable by your host; a path in a prompt does not
grant operating-system permissions.

Discovery uses the host's search/database tools, not a bundled search service.
If those tools are unavailable, provide article links, accession records or local
files. Candidate studies remain provisional until their design and files are checked.

## Starting with data

> Use scrna-research on D:/study/annotated.h5ad. The counts layer contains original
> UMI counts. Use published_cell_type, donor_id and condition from the cell metadata.
> Labels come from the study's published metadata, which I have supplied.
> Show which cell types express my gene across donors and whether the condition
> patterns justify a more detailed comparison. Choose routine settings and save
> results under D:/study/runs/research-01.

For new counts, the assistant first inspects QC and annotation needs. For documented
processed data, a focused expression summary can use existing labels, with their
source and uncertainty stated. The original five Skills remain available individually.

## Focused expression command

This command is normally run by the assistant. It is also usable directly:

```text
python plugins/scrna-seq-workbench/scripts/scrna.py research --input D:/study/annotated.h5ad --question "Which cell types express KRT8 across conditions?" --genes KRT8 KRT18 --celltype-key published_cell_type --donor-key donor_id --condition-key condition --label-source "Study DOI and supplied metadata file" --label-status published --min-cells 20 --outdir D:/study/runs/research-01
```

Use exact gene identifiers from `var_names`. H5AD must have `layers['counts']` and
nonempty metadata columns. Twenty cells is a configurable display-support threshold,
not a universal quality cutoff. Low-support groups remain visible in the detailed
table; no expression zero is invented for an absent cell type.

| Output | How to use it |
|---|---|
| `research_report.html` | Open in a browser for donor observations, summaries and limitations |
| `donor_expression.csv` | Inspect gene expression and detection within each donor/condition/cell type |
| `condition_summary.csv` | Compare descriptive means with equal weight per eligible donor |
| `research_summary.json` | Read the question, missing genes and declared annotation source |
| `report.json` | Check actual status, parameters, input hashes and software/source versions |

The command does not perform DE, prove causality, verify publication integrity or
validate cell labels. It does not alter the input matrix. For a supported condition
test, the assistant uses the existing donor-level DE workflow after its design and
label-review checks. Enrichment, trajectories, abundance testing and communication
models currently require additional tools and an explicit method record.

## What a useful answer contains

Expect a short answer to your question, reasons for choosing the data, measured
effects with donor support, links to outputs, comparison with independent evidence,
and an actionable next step. The assistant should tell you when a dataset cannot
support the requested conclusion. Publication disagreement should lead to examining
evidence, not automatic acceptance or rejection of either result.

The plugin does not score itself. Developer benchmark ratings are maintained
separately and are not part of this workflow.

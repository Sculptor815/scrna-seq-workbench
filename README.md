# scRNA-seq Workbench

Five agent skills and a shared Python runner for guided single-cell RNA-seq analysis.
Supports **Codex and Claude Code plugin packaging**, plus **DeepSeek Harness project skills**.
Version **0.2.0 - research preview**. This is a small starting point for incremental improvement.

Give your assistant a counts matrix, sample information and an analysis goal.
It should inspect the inputs, explain important parameters, run the requested stages,
and show evidence and uncertainty before treating annotations as final.

| Skill | Purpose | Main output |
|---|---|---|
| `sequencing-report-review` | Review a vendor report and identify missing files | Verified metrics and delivery inventory |
| `scrna-qc` | Inspect per-sample quality and apply explicit filters | Filtered counts and exclusion ledgers |
| `scrna-scvi-umap` | Fit scVI or a PCA baseline, cluster and visualize | Representation, Leiden clusters and UMAP |
| `scrna-cell-annotation` | Propose marker-supported labels and record review | Proposals, evidence and reviewed labels |
| `scrna-condition-de` | Compare conditions using donor-level pseudobulk | Counts, exclusions and PyDESeq2 results |

## Five-study visual benchmark

[Original figures and plugin comparisons](docs/COMPARISONS.md) show Kang, Haber,
Paul, Zeisel and Baron. All five author-label versus plugin-label replots are
available. Three original figures are externally displayed; two originals have
explicit source-access limitations. Original t-SNE/heatmaps are never called UMAP.

![Kang reference labels and plugin proposals](docs/figures/kang-comparison.png)

Annotation now defaults to an [HPA-guided evidence and manual-review contract](plugins/scrna-seq-workbench/references/hpa-guided-annotation.md).
The old automatic scores remain a historical baseline. The five new review packets
are pending, so we do not claim completed HPA annotation or improved accuracy.
See [benchmark scope](benchmarks/README.md) and [HPA lessons](docs/HPA_METHODS.md).

## Start here

1. Clone or extract this repository to your working drive. Large data and outputs can stay on D: or a server.
2. Set up the Python environment below.
3. Follow [your host's setup instructions](docs/HOSTS.md).
4. Send the [first-analysis prompt](docs/QUICKSTART.md), or try the small synthetic example.

```text
python -m venv .venv
```

Activate `.venv` using your shell, or use its Python executable directly:
`.venv\Scripts\python.exe` on Windows; `.venv/bin/python` on Linux/macOS.

```text
python -m pip install -r plugins/scrna-seq-workbench/requirements-scvi.txt -r plugins/scrna-seq-workbench/requirements-de.txt
python scripts/validate_package.py
```

Use Python 3.12. For QC, PCA and marker annotation only, install `requirements.txt`
instead. Installing the plugin does **not** install Python dependencies. The host
needs permission to read your project and execute the chosen Python environment.
GPU use needs a compatible PyTorch/CUDA installation; CPU is supported.

## What the first version supports

- Human/mouse UMI count matrices: H5AD, 10x H5, or 10x-compatible matrix directories.
- A shared intake workflow: goals, tissue, assay, raw-count provenance and sample design.
- Per-sample QC configuration, explicit batch selection, optional doublet assessment.
- Separate annotation proposals and reviewed labels, including `Unknown`.
- Paired/unpaired donor-level condition DE, with minimum replicate checks.
- Fresh output directories and reports recording parameters, versions and file hashes.

The report command validates a transcription made by the assistant; it is not an OCR
engine. Multi-file matrix assembly, FASTQ alignment, ambient-RNA correction, arbitrary
DE covariates and universal automatic annotation are outside this release.
HPA input is optional and human-only. No datasets or reference downloads are bundled.

## Example request

> Use scRNA-seq Workbench to inspect my human PBMC counts in data/raw.h5ad.
> My sample information is in data/cells.csv. I want broad cell-type annotation.
> First check the inputs and QC distributions. Explain your proposed filters,
> PCA/scVI settings and batch definition before filtering or training.
> Save new results under runs/analysis-01 and preserve the original counts.

Documentation is in English; the assistant should answer in the user's language.
Users may explicitly delegate parameter choices rather than approve every setting.

## Reliability and development

This is an **assisted research workflow**, not a validated autonomous analyst.
Previous fixed-configuration experiments exposed low-RNA QC loss, rare-type failures
and unstable developmental-state annotation. See [validation and limitations](docs/VALIDATION.md).
Do not treat an attractive UMAP, a completed command, or a high overall agreement rate as biological validation.

```text
python scripts/sync_adapters.py --check
python -m unittest discover -s tests -v
```

- [Quickstart and intake](docs/QUICKSTART.md)
- [Host setup: Codex, Claude Code, DeepSeek Harness](docs/HOSTS.md)
- [Important parameters](plugins/scrna-seq-workbench/references/important-parameters.md)
- [Development and publishing](docs/DEVELOPMENT.md)
- [Changelog](CHANGELOG.md) / [License](LICENSE)

This repository does not configure model credentials, send messages, download public
datasets or run an analysis merely because it is installed.

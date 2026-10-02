# Your first analysis

## Tell the assistant what you know

Provide your goal, species, tissue, cell/nucleus assay, count-matrix path, any vendor
report, sample metadata and previous processing. Unknown facts can be stated as
unknown. Explain donor/condition relationships if you want condition DE.
Use the [intake template](../plugins/scrna-seq-workbench/assets/analysis-intake.template.md)
or answer in plain language. A vendor report is useful but does not replace counts.

The assistant should inspect first, then explain the proposed parameters and their
consequences. You can accept/change the plan, or explicitly delegate parameter
selection within a stated scope. Reviewed labels are a separate later decision.

## A small local example without downloading data

Run these commands from the repository root using the prepared environment.
Every output directory must be new. These 400 cells are artificial and provide
an execution example, not biological accuracy evidence.

```text
python examples/make_synthetic.py --outdir work/demo
python plugins/scrna-seq-workbench/scripts/scrna.py qc --input work/demo/raw.h5ad --config work/demo/qc.json --species human --inspect-only --outdir work/demo-inspection
```

Inspect the generated report and QC tables. For this deliberately synthetic example,
the supplied config is an explicit test choice. A real project needs its own review.

```text
python plugins/scrna-seq-workbench/scripts/scrna.py qc --input work/demo/raw.h5ad --config work/demo/qc.json --species human --outdir work/demo-qc
python plugins/scrna-seq-workbench/scripts/scrna.py integrate --input work/demo-qc/filtered.h5ad --backend pca --hvg 80 --latent 5 --outdir work/demo-pca
python plugins/scrna-seq-workbench/scripts/scrna.py annotate --input work/demo-pca/integrated.h5ad --panel work/demo/panel.json --species human --tissue blood --outdir work/demo-annotation
```

Read `annotation_proposals.csv`, `annotation_evidence.csv`, `marker_expression.csv`,
`marker_heatmap.png` and `report.json`. The generated `hpa_review.template.csv`
starts pending; follow the [HPA review contract](../plugins/scrna-seq-workbench/references/hpa-guided-annotation.md).
Do not treat proposals as reviewed labels. For an optional full engineering smoke,
including an explicitly legacy synthetic review and synthetic-truth DE, install `requirements-de.txt` and run:

```text
python scripts/smoke_test.py --backend pca --outdir work/full-smoke
```

`--backend scvi` exercises scVI with only two training epochs. Neither smoke
configuration establishes model convergence, annotation accuracy or DE false-discovery control.

## Keep large data on the chosen drive

Clone/extract the repository on your data drive, for example `D:/scRNAseq-workbench`,
and use `work/` for local experiments or absolute output paths on that drive.
Do not store outputs inside an installed plugin cache. The repository ignores work,
runs, data, model files and local environments; do not upload private input data.
The assistant must disclose any subsampling instead of silently applying a benchmark cap.

On Windows, prefer a short repository path. If Numba reports a missing cache file
with a very long path, set `NUMBA_CACHE_DIR` to a short, writable directory on the
same working drive before launching Python. This affects compiled-code caching,
not analysis parameters. Some restricted Windows execution environments also block
Python's private temporary directories; run tests in an environment with working
temporary-directory permissions and do not interpret those permission errors as
biological failures.

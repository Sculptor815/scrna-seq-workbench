# Your first analysis

This example creates 400 artificial cells and 100 genes. It checks the Python
environment and shows the files produced at each stage. It uses a small PCA model
and does not download experimental data.

Complete [Installation](INSTALLATION.md) first. Run from the repository root.
In the commands below, Windows users should replace `python` with
`.\.venv\Scripts\python.exe`; Linux/macOS users can use `.venv/bin/python`.

## 1. Create the example

```text
python examples/make_synthetic.py --outdir work/demo
```

The `work/demo` folder contains a count matrix, cell metadata, a synthetic vendor
report, a QC config and a two-type marker panel. The generator refuses to replace
an existing folder. For another run, choose a different name throughout the example.

## 2. Review the synthetic delivery

```text
python plugins/scrna-seq-workbench/scripts/scrna.py report --source work/demo/vendor.txt --metrics work/demo/metrics.json --outdir work/demo-report
```

Open `work/demo-report/review.md`. It records the 400-cell fixture and which vendor
metrics are absent. In a real project, your assistant prepares the metric
transcription from the supplied vendor report.

## 3. Inspect QC before filtering

```text
python plugins/scrna-seq-workbench/scripts/scrna.py qc --input work/demo/raw.h5ad --config work/demo/qc.json --species human --inspect-only --outdir work/demo-inspection
```

Read `report.json`, `cell_qc.csv` and `threshold_suggestions.json` in the inspection
folder, or ask your assistant to explain them. `mode` should be `inspect_only`,
and no filtered matrix is created. The config allows at least 10 detected genes
because the artificial matrix has only 100 genes. Real-data thresholds need their
own assessment. Missing hemoglobin/ribosomal symbol warnings are expected here.

## 4. Apply the example filters

```text
python plugins/scrna-seq-workbench/scripts/scrna.py qc --input work/demo/raw.h5ad --config work/demo/qc.json --species human --outdir work/demo-qc
```

This writes `filtered.h5ad`, a cell exclusion ledger, a gene exclusion ledger and
`qc_by_sample.png`. Check the retained counts in `report.json`.

## 5. Calculate PCA, clusters and UMAP

```text
python plugins/scrna-seq-workbench/scripts/scrna.py integrate --input work/demo-qc/filtered.h5ad --backend pca --hvg 80 --latent 5 --outdir work/demo-pca
```

Open `work/demo-pca/umap_clusters.png`. The runner selected 80 highly variable
genes, computed five principal components, then built the neighbor graph, Leiden
clusters and UMAP. `integrated.h5ad` keeps the QC-retained genes and raw counts.

## 6. Propose cell types

```text
python plugins/scrna-seq-workbench/scripts/scrna.py annotate --input work/demo-pca/integrated.h5ad --panel work/demo/panel.json --species human --tissue blood --outdir work/demo-annotation
```

Read the proposal/evidence CSVs and `marker_heatmap.png`. The example panel contains
T-cell and B-cell markers. `hpa_review.template.csv` starts with pending decisions.
An artificial example cannot establish performance on experimental cell types.

For your own study, the next step is marker review and, if needed, subclustering.
Follow [Analyze your own data](USAGE.md) to complete a review and run condition DE.

## Optional: check all stages automatically

After installing `requirements-de.txt`, run:

```text
python scripts/smoke_test.py --backend pca --outdir work/full-smoke
```

This engineering check includes synthetic labels and paired donor DE. It uses the
legacy review format explicitly for artificial labels; it does not supply a human
review for experimental data. With scVI installed, `--backend scvi` runs a short
two-epoch execution check. That short run is insufficient to assess convergence.

## Ask the assistant to run the example

> Use the five scRNA-seq Workbench Skills and the Python environment I supplied.
> Run the example in docs/QUICKSTART.md in fresh work/demo-* folders.
> Explain what each stage reads and writes, and show the QC plot, UMAP and marker
> evidence. Keep the annotation proposals provisional.

This tests how the assistant uses the Skills, in addition to whether Python works.
If you already ran the commands manually, give it the existing output paths for
review or choose new paths for an independent run.

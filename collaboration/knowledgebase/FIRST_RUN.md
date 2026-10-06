# Guided first run: learn from the actual files

This exercise uses 400 artificial cells and 100 genes. It requires the existing scientific Python environment, but no LLM, API key, download or scVI installation. It checks the computational route; synthetic success does not validate real biology. Read each explanation before moving to the next command.

## 0. Choose Python and an isolated output folder

The following PowerShell setup matches the owner's local sandbox. Other users should replace the Python, checkout and output-root paths after following [Installation](../../docs/INSTALLATION.md). Keep the same PowerShell window for the following steps.

```powershell
$py = 'D:\scrna-agent-sandbox\.venv\Scripts\python.exe'
$repo = 'C:\Users\alw\Documents\Codex\scrna-seq-workbench'
$cli = Join-Path $repo 'plugins\scrna-seq-workbench\scripts\scrna.py'
$run = Join-Path 'D:\scrna-agent-sandbox\runs' ('learning-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $run | Out-Null
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:NUMBA_CACHE_DIR = 'D:\scrna-agent-sandbox\cache\numba'
$env:MPLCONFIGDIR = 'D:\scrna-agent-sandbox\cache\matplotlib'
Write-Output $run
```

**Why:** an environment pins available software; a unique run folder separates attempts. Cache settings keep compilation and plotting caches in the sandbox. No original matrix is replaced. If a command fails, read its message/report before continuing; do not treat a downstream missing file as a new biological result.

## 1. Generate a small dataset

```powershell
& $py -B (Join-Path $repo 'examples\make_synthetic.py') --outdir "$run\fixture"
if ($LASTEXITCODE -ne 0) { throw 'Fixture generation failed' }
```

**Inspect:** `fixture/raw.h5ad`, the metadata, `qc.json` and `panel.json`.

**Why:** artificial data let us learn file relationships without a download or patient data. The known artificial labels can test execution, but cannot measure how well the agent annotates real tissue. Read cards 1 and 2 before using an external dataset.

## 2. Review a delivery report

```powershell
& $py -B $cli report --source "$run\fixture\vendor.txt" --metrics "$run\fixture\metrics.json" --outdir "$run\01-report"
if ($LASTEXITCODE -ne 0) { throw 'Delivery review failed' }
```

**Inspect:** `01-report/review.md`. Identify one present metric and one absent metric. Check units and source evidence.

**Why:** sequencing metrics and cell metrics are different. The prepared JSON is a checked transcription input, not evidence that every report can be parsed automatically. Read card 3.

## 3. Inspect QC without filtering

```powershell
& $py -B $cli qc --input "$run\fixture\raw.h5ad" --config "$run\fixture\qc.json" --species human --inspect-only --outdir "$run\02-inspection"
if ($LASTEXITCODE -ne 0) { throw 'QC inspection failed' }
```

**Inspect:** `cell_qc.csv`, `threshold_suggestions.json` and `report.json`. Confirm inspect-only mode and the absence of a filtered H5AD. Missing ribosomal/hemoglobin symbol warnings can occur in this small fixture.

**Why:** inspect distributions before selecting cutoffs. The fixture's minimum of 10 detected genes is meaningful only for this tiny artificial matrix, not a real-tissue recommendation. Suggestions are not applied automatically. Read card 4.

## 4. Apply the example filters

```powershell
& $py -B $cli qc --input "$run\fixture\raw.h5ad" --config "$run\fixture\qc.json" --species human --outdir "$run\03-qc"
if ($LASTEXITCODE -ne 0) { throw 'QC filtering failed' }
```

**Inspect:** retained cells/genes in `report.json`, `cell_qc.csv`, `gene_qc.csv`, `qc_by_sample.png` and `filtered.h5ad`.

**Why:** exclusions change the population being studied. Record who was removed and why. Later count-preservation checks compare against this QC-retained matrix, while the source matrix remains unchanged. Try alternative justified thresholds only in a new output directory.

## 5. Build a representation

```powershell
& $py -B $cli integrate --input "$run\03-qc\filtered.h5ad" --backend pca --hvg 80 --latent 5 --outdir "$run\04-pca"
if ($LASTEXITCODE -ne 0) { throw 'Representation step failed' }
```

**Inspect:** `umap_clusters.png`, `integrated.h5ad` and the report's parameter record.

**Why:** 80 variable genes and five principal components make the exercise small. Normalization, feature selection, PCA, graph construction, Leiden and UMAP are distinct operations. This PCA route is uncorrected; it is not scVI integration. Read cards 5 and 6. A visually separated island does not yet have a cell identity.

## 6. Propose labels and stop for evidence review

```powershell
& $py -B $cli annotate --input "$run\04-pca\integrated.h5ad" --panel "$run\fixture\panel.json" --species human --tissue blood --outdir "$run\05-proposals"
if ($LASTEXITCODE -ne 0) { throw 'Annotation proposal failed' }
```

**Inspect:** the proposal/evidence CSVs, marker heatmap and `hpa_review.template.csv`.

**Why:** the panel offers two candidate identities; it is not an exhaustive real-world reference. Compare supporting and contradictory markers, and keep pending review pending. The score is not a probability. Read card 7. Do not change a field to human-reviewed merely to make DE run.

## 7. Optional engineering check of donor-level DE

With the DE dependencies installed, use a separate output directory:

```powershell
& $py -B (Join-Path $repo 'scripts\smoke_test.py') --backend pca --outdir "$run\de-execution-check"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic DE check failed' }
```

**Inspect:** `smoke_summary.json`, `commands.log` and the DE tables under `05-de`.

**Why:** this separate engineering test uses explicit synthetic truth and the legacy fixture-review path. It neither approves the proposals above nor substitutes for human review of real labels. Read card 8 to understand paired donors, count aggregation, replication floors and adjusted p-values. Real-data DE follows [Usage](../../docs/USAGE.md) and its actual review/design requirements.

## 8. Explain the result and write one experience card

Use cards 9 and 10 to distinguish descriptive expression, replicated contrasts and mechanistic hypotheses. Write a short report containing the question, inputs, parameters, files inspected, direct observations and unresolved limitations.

Then use card 11 and the [template](templates/EXPERIENCE.md) to write one decision you would change for real data. Include a reason, source, counterexample and observable check. Record scientific feedback in [REVIEW_WORKSHEET.csv](REVIEW_WORKSHEET.csv). Card 12 explains enrichment as a future extension; it is not a runnable stage in this plugin.

## Completion checklist

- I can explain what each matrix representation means.
- I can locate the QC exclusions and distinguish source counts from retained counts.
- I know why a cluster label and a cell identity differ.
- I can explain why more cells do not create more independent donors.
- I can distinguish an execution check from a scientific validation.
- I have written one reviewable knowledge card rather than a universal parameter recipe.

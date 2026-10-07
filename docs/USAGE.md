# Analyze your own data

Use this guide after [installation](INSTALLATION.md) and the [small example](QUICKSTART.md).
You can give the requests below to your assistant. The command examples are also
available if you prefer to run the same steps yourself.

## Prepare your files

Put the experimental data in a separate study directory:

```text
my-study/
  data/
    raw.h5ad
    cells.csv
    vendor-report.html
  config/
    qc.json
    markers.json
  runs/
```

The report and marker file names are examples. Do not rename a different file
format to H5AD. The input can be:

- **H5AD:** a cells-by-genes matrix with raw UMI counts in `layers['counts']`, or
  raw counts in `X` declared through the QC step. Normalized-only H5AD files need
  their original counts restored from a documented source.
- **10x H5:** a count file such as `filtered_feature_bc_matrix.h5`.
- **10x matrix directory:** compressed `matrix.mtx.gz`, `features.tsv.gz` and
  `barcodes.tsv.gz` in one folder. For older two-column gene files or uncompressed
  deliveries, first confirm compatibility or perform an explicit conversion.

The current runner accepts one matrix per QC call. If your study has multiple
matrices, ask the assistant to prepare a separate merge step with unique cell IDs
and a gene mapping, and check it before analysis. Gene symbols and cell IDs must
be unique. Species-specific mitochondrial QC and marker panels use gene symbols.

### Cell metadata and sample design

`cells.csv` has one row per cell and a `cell_id` matching the matrix exactly:

```csv
cell_id,sample_id,capture_id,donor_id,condition,batch
S01_AAAC-1,S01,CAP01,D01,control,RUN1
S01_AAAG-1,S01,CAP01,D01,control,RUN1
S02_AAAC-1,S02,CAP02,D01,treated,RUN2
```

These are illustrative IDs; replace them with the actual matrix IDs. The runner
matches all cells, not just the rows shown here. Existing H5AD metadata must agree
with the CSV. If the needed columns are already present, omit `--metadata`.

| Field | Meaning | Needed for |
|---|---|---|
| `sample_id` | The sample whose QC thresholds should be applied | QC; alternatively use `--single-sample` for a genuine single sample |
| `capture_id` | A physical droplet capture or library preparation | Optional doublet scoring |
| `donor_id` | The biological replicate, such as an individual donor | Condition DE |
| `condition` | The experimental group | Condition DE |
| `batch` | A documented technical source of variation | Optional integration |

The [sample-design template](../plugins/scrna-seq-workbench/assets/sample-design.template.csv)
has one row per sample and is useful for planning. It is different from the
per-cell CSV consumed by the runner. A name such as `rep1` does not establish
whether a sample is a biological or technical replicate.

## Start with a short project description

> Use scRNA-seq Workbench for human PBMC data from a droplet UMI assay.
> The matrix is D:/my-study/data/raw.h5ad and metadata is D:/my-study/data/cells.csv.
> The vendor report is D:/my-study/data/vendor-report.html.
> I want broad cell types, then a treated-versus-control comparison within each type.
> The same donors were sampled in both conditions.
> Use D:/scrna-seq-workbench/.venv/Scripts/python.exe and save runs under D:/my-study/runs.
> Start by checking the inputs. Explain any missing information and the parameters
> you recommend before filtering or training.

State what is unknown. A missing vendor report need not prevent matrix inspection.
For an annotation-only project, donor and condition information may be unnecessary.
Use the [intake template](../plugins/scrna-seq-workbench/assets/analysis-intake.template.md)
if you want a written project record.

## Parameters to discuss

| Choice | How it affects the analysis |
|---|---|
| Minimum genes/counts | Higher floors remove weak libraries but may lose low-RNA populations. Compare distributions by sample. |
| Maximum genes/counts | High-count cells may be large cells or doublets; counts alone do not distinguish them. |
| Mitochondrial/hemoglobin thresholds | Choose from the assay, tissue and observed gene coverage. A missing gene set makes its percentage unavailable. |
| Doublet scoring | Use actual capture IDs and a justified expected rate. Scoring and removal are separate options. |
| HVGs | Defines which genes fit the representation; all QC-retained genes stay in the output. |
| `--latent` | scVI latent dimensions; requested PCA dimensions for explicitly selected Harmony. |
| `--batch-key` | Verified technical metadata for HVGs and scVI; omit it for no-batch scVI. |
| `--species` / `--cell-cycle-genes` | Human symbols have a bundled preset; mouse/non-symbol IDs need a sourced exact-ID gene set. |
| Neighbors and Leiden resolution | Change the graph and clustering granularity. Review markers and stability as well as the plot. |
| Annotation panel and label depth | Determine the candidate types the method can distinguish. Use the correct species and tissue. |
| DE design | Use paired analysis for the same donors in both groups, or unpaired for independent donors. |

In particular, when condition and batch are confounded, the data cannot identify
which effect is technical. Discuss that design before selecting a batch key.
See [Important parameters](../plugins/scrna-seq-workbench/references/important-parameters.md)
for the complete parameter guide. You can delegate parameter selection to the
assistant within a stated scope; it should still record its reasons.

## The five stages

Commands below run **from the repository root**. Replace `python` with your
environment's executable, and replace the example study paths with your paths.
Each `--outdir` should be new. Example values illustrate the interface; choose
real-data settings after inspection.

### 1. Review the sequencing delivery

Ask the assistant to read the report and inventory the delivered files. It can
transcribe observed metrics into the
[metric template](../plugins/scrna-seq-workbench/assets/vendor_metrics.template.json),
including source locations and missing values. Then validate the transcription:

```text
python plugins/scrna-seq-workbench/scripts/scrna.py report --source D:/my-study/data/vendor-report.html --metrics D:/my-study/config/vendor-metrics.json --outdir D:/my-study/runs/01-report
```

Read `review.md` and `normalized_metrics.json`. The assistant reads the report;
the CLI checks the supplied transcription and records its source. A screenshot
can support this step but does not contain the cell-level count matrix.

### 2. Inspect and filter cells

Copy the [example QC config](../plugins/scrna-seq-workbench/assets/qc.example.json)
to your study's `config/qc.json`, then ask for inspection:

```text
python plugins/scrna-seq-workbench/scripts/scrna.py qc --input D:/my-study/data/raw.h5ad --metadata D:/my-study/data/cells.csv --config D:/my-study/config/qc.json --species human --inspect-only --outdir D:/my-study/runs/02-inspect
```

The inspection writes all cell measurements to `cell_qc.csv`, descriptive MAD
summaries to `threshold_suggestions.json` and settings/warnings to `report.json`.
Its retained flags show what the supplied configuration would do. No filtered
matrix is written. Ask the assistant to plot these measurements by sample and
explain the expected losses before settling on thresholds.

Edit the QC config, including sample overrides if needed. Run the same command
without `--inspect-only`, with a fresh output directory such as
`D:/my-study/runs/03-qc`. Read `qc_by_sample.png`, `gene_qc.csv` and the exclusion
counts. The next stage uses `03-qc/filtered.h5ad`.

For one sample without a metadata file, replace `--metadata ...` with
`--single-sample S01`. For capture-level doublet scoring, add `--doublets` and the
correct capture key/rate. Add `--remove-doublets` only when you intend removal.

### 3. Compute a representation, clusters and UMAP

The full pipeline may take more than 1 hour. Default to scVI, including single
samples or inputs without batch metadata. Install requirements-scvi.txt. With
a compatible CUDA GPU, --device auto uses it; otherwise it runs CPU scVI, which
can require a longer wait. The backend never changes automatically:

```text
python plugins/scrna-seq-workbench/scripts/scrna.py integrate --input D:/my-study/runs/03-qc/filtered.h5ad --species human --hvg 3000 --latent 20 --neighbors 30 --resolution 1 --max-epochs 400 --device auto --seed 0 --outdir D:/my-study/runs/04-scvi
```

Add `--batch-key batch` only when the column exists and represents the technical
effect you intend to model. Omitting it still runs scVI. S/G2M scores are computed
before HVG subsetting and registered as nuisance covariates. Raw counts are preserved.
For mouse or non-symbol IDs, supply --cell-cycle-genes JSON containing species,
source, s_genes and g2m_genes with exact matrix identifiers and documented mapping.

Each scVI run writes integrated.h5ad, a reloadable model with its training data, model
gene order, training history, cycle coverage/scores, pre-scVI cycle PCA, post-scVI
cycle UMAP and latent correlations. report.json records the bundled policy hash.
Inspect diagnostics; covariate registration does not prove complete cycle removal.

The default grid compares neighbors 15/20/30/50 and resolutions 0.3/0.5/0.8/1.0.
Override the ranges with --neighbors-grid and --resolutions-grid. The specified
--neighbors/--resolution pair is also included as a display baseline, pending
review. Review parameter_candidates.csv and PNGs with markers and QC, display
them for the user and follow the [selection recipe](../plugins/scrna-seq-workbench/references/parameter-selection.md)
before final annotation. A delegated decision must still have a recorded rationale.

If you prefer the CPU alternative, explicitly choose Harmony and install
requirements-harmony.txt. This requires a verified technical batch column with
at least two categories; keep no-batch scVI when that information is absent.
Replace the example batch field and reason with your actual choice:

```text
python plugins/scrna-seq-workbench/scripts/scrna.py integrate --input D:/my-study/runs/03-qc/filtered.h5ad --species human --backend harmony --batch-key batch --device cpu --backend-reason "User chose the CPU Harmony alternative" --outdir D:/my-study/runs/04-harmony
```

Harmony uses the Python package harmonypy. It regresses cycle scores on an HVG
log-expression copy before PCA, then corrects the PCA embedding. Full-gene counts
and normalized expression remain intact. The output includes integrated.h5ad,
X_pca_harmony, cycle diagnostics, PCA loadings, feature order, objective history
and candidate graphs/UMAPs. It does not include a scVI model. --latent specifies
requested PCs; scVI epoch, layer and minibatch settings do not control Harmony.
It often takes less time, but neither runtime nor equivalent biological results
are guaranteed. Review the same markers, QC and candidate parameters for either route.

### 4. Propose and review cell types

Prepare a marker panel matched to the experiment. The bundled PBMC panel is a
small example; use it only when its candidate types fit your question. Ask the
assistant to document panel sources and missing candidate types.

```text
python plugins/scrna-seq-workbench/scripts/scrna.py annotate --input D:/my-study/runs/04-scvi/integrated.h5ad --panel D:/my-study/config/markers.json --species human --tissue blood --outdir D:/my-study/runs/05-proposals
```

Use the selected H5AD/cluster partition after parameter review. Examine:

- `annotation_proposals.csv`: the candidate assigned to each cluster.
- `annotation_evidence.csv` and `marker_expression.csv`: candidate scores and measured markers.
- `marker_heatmap.png`: expression across clusters.
- `exploratory_markers.csv`: cluster-associated genes, when enough groups/cells exist.
- `hpa_review.template.csv`: a review form with one row per cluster.

Ask the assistant to explain supporting and conflicting evidence. Copy the review
form to `config/reviewed-labels.csv` and record the actual review. Accepted labels
need main and detailed types, at least two present supporting markers, reviewer
identity, sources and QC/subcluster assessments. Use `unresolved` or `mixed` with
`Unknown` at both levels when a type cannot be resolved. The
[review field guide](../plugins/scrna-seq-workbench/references/hpa-guided-annotation.md)
explains each field. The assistant can prepare evidence and draft entries; the
default policy requires a real human review before final labels are saved.

Repeat the annotation command with `--reviewed-labels D:/my-study/config/reviewed-labels.csv`
and `--outdir D:/my-study/runs/06-reviewed`. The resulting `annotated.h5ad` contains
`cell_type`, `cell_type_detail` and the review record. The initial proposal file
has `cell_type_proposal`; it is useful for review, but is not the final label column.

### 5. Compare conditions within cell types

After installing the DE dependencies, use the reviewed H5AD:

```text
python plugins/scrna-seq-workbench/scripts/scrna.py de --input D:/my-study/runs/06-reviewed/annotated.h5ad --case treated --control control --design paired --outdir D:/my-study/runs/07-de
```

The condition names must match the metadata. This implementation requires at
least three eligible donor pairs for a paired comparison, or three eligible
donors per group for an unpaired comparison. A cell type can be excluded when
too few cells or donors remain. Check the status, exclusions, pseudobulk counts
and per-type DE tables. Review effect sizes and adjusted p-values together.
Additional covariates require a separate statistical design.

## What to keep after an analysis

Keep the input provenance, configs, marker sources, review CSV and stage output
directories. `report.json` records the status, parameters, package versions and
input/output hashes. A failed or blocked report explains what must be resolved;
use a new directory when retrying. Share a compact report and figures as needed,
while keeping private matrices and sample metadata outside the code repository.

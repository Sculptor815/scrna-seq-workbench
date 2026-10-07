# Universal scRNA-seq QC and scVI Parameter Decision Knowledge Base

Updated: 2026-10-07.

This document is the English edition of the revised analysis policy agreed with
the owner. It applies across scRNA-seq datasets, including primary tissues, cell
lines and differentiation experiments, rather than only HSC differentiation.

**Fixed project policy: always score and correct cell cycle unless the user
explicitly overrides this policy. Preserve raw counts and cell-cycle scores.**

Numerical values below are starting points that require validation, not universal
biological thresholds or necessarily software defaults. The cell-cycle rule is an
owner-selected analysis policy, not a claim that every research question benefits
from removing cell-cycle variation. This document replaces the previous learning
cards, templates and review packets. It describes intended analysis behavior;
updating this document does not implement changes in the analysis runner.

## 1. Overall decision framework

Inspect the assay, organism, tissue, cell/gene counts, QC distributions, metadata,
technical batches, biological conditions and cellular heterogeneity before choosing
parameters. Record what was observed, the decision, its reason and its validation.

```text
Verify counts and metadata
  -> Calculate QC on counts
  -> Apply justified low-quality filters; inspect high outliers
  -> Detect doublets per independent capture/library
  -> Preserve counts; normalize/log-transform a working expression matrix
  -> Score cell cycle before restricting features to HVGs
  -> Select HVGs from counts, accounting for verified technical batches
  -> Fit scVI with cell-cycle nuisance covariates
  -> Transfer latent coordinates to the full-gene object
  -> Neighbors -> UMAP -> Leiden
  -> Validate markers, QC, batches, biology, cell cycle and stability
```

Reuse documented intermediate results when their provenance and settings are known.
A filename containing `QC` does not establish which steps were completed.

## 2. Verify raw counts

Inspect `adata.X`, layers, input documentation and processing history. Check shape,
finite values, non-negativity, integer compatibility, empty cells and identifiers.
For sparse matrices, inspect stored values without densifying the full matrix.

| Observation | Interpretation |
|---|---|
| Non-negative, integer-compatible values | Consistent with counts, but provenance still needs confirmation |
| Negative values | Invalid as raw count input to the intended scVI NB model |
| Many fractional values | Investigate normalization or other processing before proceeding |
| Small fractional values | May be log-transformed; the value range alone is insufficient evidence |
| Existing counts layer | Verify its origin and contents; do not assume the name proves its meaning |

If counts cannot be established, locate the original matrix or report the missing
input. Never round normalized expression to manufacture counts. `adata.raw` is not
guaranteed to contain raw counts.

## 3. Preserve matrix representations

Keep verified raw counts in `adata.layers["counts"]`. Copy `X` into that layer only
when `X` is verified counts and the layer is absent. Never overwrite a valid count
layer with normalized values.

The working `X` may hold normalized/log expression for scoring, visualization and
suitable marker analyses. Normalization, scaling and regression must not alter the
count layer. Keep the source file unchanged and record retained cells and genes.

## 4. Required QC metrics

Calculate at least `n_genes_by_counts`, `total_counts`, `pct_counts_mt`, and doublet
scores/classifications when applicable. Interpret total counts as UMI counts only
for UMI assays. Also retain hemoglobin and ribosomal percentages for diagnostics.

Resolve the organism and identifier system first. Gene-symbol prefixes such as
`MT-`, `RPL` and `RPS` do not work directly on Ensembl identifiers. Use mapped
symbols or appropriate annotations and inspect coverage. Prefer a curated
organism-specific hemoglobin set to a broad prefix that may match unrelated genes.

Calculate metrics from counts, document the denominator and gene universe, and
inspect distributions by sample/library. Record percentage units explicitly.

## 5. Gene filtering

Start with `min_cells=3`. For a very large atlas, consider 5-10 if justified.
Check whether filtering removes rare-population markers or genes needed for the
scientific question. Save the retained gene universe.

## 6. Low-quality cell filtering

Select thresholds from sample biology and observed distributions.

| Sample context | Candidate minimum genes | Candidate minimum counts | Candidate maximum MT |
|---|---:|---:|---:|
| Primary tissue | 200-500 | 500-1,000 | 10-20% |
| Cell line | 500-1,000 | 1,000-3,000 | 10-15% |

These are calibration ranges, not mandatory cutoffs. Low-RNA immune or erythroid
cells may be genuine populations. Epithelial cells, hepatocytes and some tumor
cells can naturally have high gene/count totals. High counts alone do not prove
a doublet. Preserve before/after plots, sample retention rates and exclusion reasons.

## 7. Mitochondrial percentage

Inspect the high-MT tail together with counts, complexity, tissue and assay.
Historical starting ranges are 10-15% for immune cells or cell lines and 15-20%
for solid tissues. A higher cutoff, such as 20-25%, needs sample-specific evidence.
No MT percentage alone establishes viability or damage.

Do not transfer whole-cell thresholds unchanged to single-nucleus or other assays.

## 8. Hemoglobin filtering

Default hard filtering is **OFF**. High hemoglobin can reflect erythroid biology,
especially in fetal liver, yolk sac, bone marrow and related experiments, or ambient
contamination. Use it for annotation and contamination assessment before considering
exclusions. Do not automatically delete high-HB cells.

## 9. Ribosomal filtering

Default hard filtering is **OFF**. Retain ribosomal percentage as a QC diagnostic.
High expression may occur in proliferating, activated, stem/progenitor or cultured
cells and is not by itself a reason for exclusion.

## 10. High gene/count outliers

Never remove the highest fixed percentage of cells by genes or counts. Such a rule
deletes cells even when no abnormal high tail exists.

A candidate upper flag is median plus 4 MAD in `log1p` space; consider 5 MAD for
heterogeneous samples. MAD here is the unscaled median absolute deviation:

```text
y = log1p(x)
MAD = median(abs(y - median(y)))
upper_flag = expm1(median(y) + n_mad * MAD)
```

Calculate flags within meaningful sample/library groups where feasible. Handle
small groups, missing values and zero MAD explicitly. A flag is evidence to inspect,
not an automatic doublet diagnosis or deletion criterion. Combine flags with
doublet scores, marker combinations and expected cell-type complexity.

## 11. Doublet detection

Use Scrublet as an initial method when compatible with the assay and counts.
Prefer independent 10x captures, then independent libraries; sample or replicate
labels are suitable substitutes only when they identify the relevant captures.

Do not pool unrelated experiments merely to increase cell numbers. Record expected
doublet-rate assumptions, score distributions, thresholds, classifications and
exclusions. Inspect the quality of the classification before filtering. If grouping
metadata or adequate data are unavailable, report the limitation.

## 12. Normalization and log transformation

After preserving counts, normalize a working expression matrix to
`target_sum=1e4`, then apply `log1p`. Do not normalize or log-transform twice.
Use this representation for cell-cycle scoring and expression visualization.
scVI and `seurat_v3` HVG selection continue to read the count layer.

Document which representation each downstream expression/marker analysis uses.

## 13. Fixed cell-cycle scoring and correction policy

Always compute and retain `S_score`, `G2M_score` and `phase`. Use a documented
gene set, such as the Seurat cell-cycle sets, with appropriate species/identifier
mapping. Score on suitable normalized/log expression before taking the HVG subset.

Record gene-set source/version, matched genes and missing genes. If scores are
missing, non-finite or based on inadequate coverage, resolve or report the problem;
do not silently substitute zero scores or skip correction.

For scVI:

```python
scvi.model.SCVI.setup_anndata(
    adata_hvg,
    layer="counts",
    batch_key=batch_key,  # None if no reliable technical batch is available
    continuous_covariate_keys=["S_score", "G2M_score"],
)
```

These continuous covariates are treated as nuisance factors, with the aim of
reducing their effects on the latent representation. This is not equivalent to
linearly residualizing the expression matrix and does not guarantee that all
cell-cycle signal disappears. Do not feed regression residuals into scVI as counts.

For a conventional PCA route, regress the two scores from a separate normalized
working matrix, then scale and compute PCA. Preserve counts and account for the
memory cost of regression/scaling.

## 14. Validate cell-cycle correction

Inspect `phase`, `S_score`, `G2M_score` and cluster labels on the embedding.
Also examine associations between scores and latent dimensions, preferably within
cell types or relevant biological groups; UMAP alone cannot demonstrate removal.

The target is that cell cycle no longer dominates clustering while interpretable
lineage and condition structure remains. Preserve the original scores and report
residual effects or loss of biological structure. Correction remains enabled unless
explicitly overridden by the user.

## 15. Identify a technical batch variable

Inspect metadata columns, category counts, missing values and the study design.
Multiple categories alone do not make a field a technical batch.

| Metadata | Decision rule |
|---|---|
| Capture, library, processing batch, plate, sequencing run, lane | Consider when it represents a relevant technical effect |
| Sample, donor, patient, mouse, replicate | Determine its biological and technical meaning first |
| Cell type, cluster | Do not use as a batch variable |
| Tissue, FL/YS, developmental stage, Day0/Day6, treatment, disease, dose, genotype | Preserve as biological variables by default |

Check confounding between technical batch and the biological comparison. Do not
claim correction can separate effects that the experimental design cannot distinguish.

## 16. Donor effects and missing batches

Donor can be considered for representation integration when donors are biological
replicates and the analysis objective supports that choice. Do not automatically
remove donor effects when individual variation is the research target. Preserve
donor identities for downstream analysis regardless of representation choices.

If no reliable technical batch is available, use `batch_key=None`. Do not invent
metadata or substitute tissue, timepoint or condition merely to run integration.

## 17. Choose HVGs

Default to 3,000 HVGs, adjusting to biological complexity and stability evidence.

| Context | Candidate HVG count |
|---|---:|
| Simple cell line/population | 2,000 |
| Single tissue | 2,500-3,000 |
| General primary tissue | 3,000 |
| Highly heterogeneous tissue | 3,000-4,000 |
| Multi-tissue atlas | 4,000-5,000 |

Use `flavor="seurat_v3"` with `layer="counts"`. If a justified technical batch
exists, consider batch-aware HVG selection using that field. Record the actual
number and ordered identifiers of selected genes. Check dependencies; report
selection failures instead of silently substituting another method.

## 18. Model features and full-gene results

Train scVI on an HVG copy and retain the full QC-retained gene object for expression
visualization, markers and other suitable analyses. Verify identical cell identities
and order before assigning the latent array to `adata.obsm["X_scvi"]`.

The model covers its trained gene set only. A full-gene result object does not
provide model-derived estimates for excluded genes. Save the model gene order and
the data/registration information needed to reload it correctly.

## 19. scVI model starting configuration

```python
model = scvi.model.SCVI(
    adata_hvg,
    n_latent=20,
    n_layers=2,
    gene_likelihood="nb",
    dropout_rate=0.1,
)
```

This is a starting configuration for suitable count data, not a universal optimum.

## 20. Select latent dimensions

| Biological complexity | Candidate n_latent |
|---|---:|
| Simple cell line/population | 10 |
| Moderate complexity | 15 |
| Typical tissue | 20 |
| Complex tissue | 20-30 |
| Large heterogeneous atlas | 30 |

For fewer than 5,000 cells and low complexity, consider 10-15. Cell count alone
does not justify increasing the latent dimension.

## 21. Training parameters and hardware

Start with `max_epochs=400`, `early_stopping=True`, patience 20 and batch size
256. Consider 512 if memory and training behavior support it; reduce to 128 when
needed for memory. Record training/validation splits, seed, monitored metric,
training history, convergence and actual stopping epoch.

For a GPU run, verify CUDA availability and device selection before requesting
`accelerator="gpu", devices=1`. A CPU run is a separately recorded execution
choice. HVG selection, neighbors, UMAP and Leiden can remain CPU-bound; reduced
GPU utilization during these steps is not evidence of failed training.

Check arguments against installed Scanpy, scvi-tools, PyTorch and training framework
versions. An import error is not a model-parameter failure.

## 22. Neighbors

Compute neighbors using `use_rep="X_scvi"`, starting with 30 neighbors.

| Candidate n_neighbors | Intended emphasis |
|---|---|
| 10-15 | Very local structure and small populations |
| 20 | Subpopulation analysis |
| 30 | General starting point |
| 40-50 | Broader topology |
| Above 50 | Atlas/global structure, requiring explicit justification |

Keep the value compatible with the cell count and check that rare populations
are not lost through excessive smoothing.

## 23. Leiden and UMAP

Start Leiden resolution at 1.0. Consider 0.5, 0.8, 1.0, 1.2 and 1.5 when justified.
Resolution has no universal mapping to cell-type granularity. Inspect marker
coherence, cluster stability, merged lineages and artificial fragmentation of
continuous states. More clusters are not automatically better.

Record random seeds. UMAP is a visualization, not proof that a model or cluster
assignment is correct.

## 24. Validate technical and biological structure

Assess all of the following:

- Marker coherence and plausible populations, including rare types.
- QC distributions by cluster, especially high MT and low complexity.
- Mixing of comparable cell types across relevant technical batches.
- Preservation of interpretable tissue, condition and timepoint differences.
- Residual cell-cycle effects after the required correction.
- Stability of major populations and conclusions under modest parameter changes.

Do not force every batch to mix when cell-type composition differs. Do not select
parameters solely for an attractive UMAP or a preferred number of clusters.

## 25. Bounded sensitivity analysis

Change one main parameter at a time initially; a full grid search is not required.
Candidate comparisons:

| Parameter | Candidate values |
|---|---|
| HVGs | 2,000 / 3,000 / 4,000 |
| n_latent | 10 / 20 / 30 |
| Neighbors | 20 / 30 / 40 |
| Leiden resolution | 0.8 / 1.0 / 1.2 |

Retrain when model inputs or model parameters change. Reuse a validated latent
representation when changing only neighbors or clustering. Record all attempts
and results. If modest changes substantially alter major conclusions, revisit
counts, QC, doublets, batches, HVGs and convergence.

## 26. Default decision table

| Parameter | Starting value or policy |
|---|---|
| Gene minimum detected cells | 3 |
| Cell minimum genes | 300; calibrate to distributions |
| Cell minimum counts | 1,000; calibrate to assay/sample |
| Maximum mitochondrial percentage | 15%; calibrate to tissue/assay |
| Hemoglobin / ribosomal hard filters | OFF / OFF |
| High gene/count flag | 4 MAD in log1p space; inspect before exclusion |
| Doublet method | Scrublet per independent capture/library when applicable |
| Normalization target | 10,000 in the working matrix |
| Cell-cycle scoring | ON |
| Cell-cycle correction | ON unless explicitly overridden |
| HVG method / count | seurat_v3 on counts / 3,000 |
| Technical batch | Verified metadata only; otherwise None |
| Latent dimensions / layers | 20 / 2 |
| Likelihood / dropout | NB / 0.1 |
| Batch size / maximum epochs | 256 / 400 |
| Early stopping / patience | ON / 20 |
| Neighbors / Leiden resolution | 30 / 1.0 |

## 27. FL, YS and hESC examples

These are historical starting configurations from the analysis discussion, not
measured results or proof that input files have been validated.

| Dataset | Expected input | HVGs | n_latent | Neighbors | Leiden |
|---|---|---:|---:|---:|---:|
| FL | GSE144024_FL_QC.h5ad | 3,000 | 20 | 30 | 1.0 |
| YS | GSE144024_YS_QC.h5ad | 3,000 | 20 | 30 | 1.0 |
| hESC Day0 + Day6 | GSE144024_hESC_Day0_Day6_QC.h5ad | 3,000 | 15 | 20 | 0.8 |

The plan fits three separate models, with Day0/Day6 together in the hESC model.
No joint FL/YS/hESC integration has been established. Use no batch key until
reliable technical metadata are identified; do not use `day` as a technical batch
by default. Enable cell-cycle correction for all three analyses.

The earlier one-copy script did not compute/register cell-cycle scores and does
not yet implement the final policy. Inspect actual code and data before claiming
that this has been fixed or that a model has been trained.

## 28. Import-name conflict troubleshooting

A local script named `scvi.py` can shadow the installed package and import itself,
causing `partially initialized module 'scvi' has no attribute 'model'`.

Rename it to a distinct name such as `run_scvi_analysis.py`. If the conflict
remains, inspect local same-name files/directories and related stale caches.
Verify the import in the actual execution environment:

```bash
python -c "import scvi; print(scvi.__file__); print(scvi.__version__)"
```

The path should resolve to the intended installed package. Also avoid script names
such as `scanpy.py`, `torch.py`, `numpy.py`, `pandas.py` and `anndata.py`.
The current server-side fix remains unverified until the import check succeeds.

## 29. Required decision report and artifacts

Produce a table with **parameter, selected value, observed evidence, reason and
validation outcome**. Include:

- Biological question, organism, assay and sample/library structure.
- Input provenance/hashes and verified count source.
- Matrix representations and cell/gene numbers before and after each QC step.
- QC thresholds, exclusions, doublet settings and cell-cycle gene coverage.
- Batch definition, confounding assessment and biological variables preserved.
- HVG list/order, model/training parameters, seeds, software versions and hardware.
- Training history, latent coordinates, graphs, embedding and cluster labels.
- Marker, QC, batch, cell-cycle and robustness checks, with unresolved issues.
- Full-gene H5AD, saved model and matching feature/registration information for
  reloading, figures and a readable report in an isolated output directory.

Do not infer completion from file existence. Distinguish execution success from
biological validation and clearly label missing or unverified evidence.

## 30. Agent guardrails

1. Verify count provenance and preserve counts before transformations.
2. Never use normalized expression or regression residuals as scVI count input.
3. Score and correct cell cycle under the fixed policy, then validate the outcome.
4. Never infer technical batch from category count or invent missing metadata.
5. Do not automatically remove tissue, timepoint, treatment or target biology.
6. Do not hard-filter HB/ribosomal expression or a fixed upper percentage.
7. Investigate high-count MAD flags alongside doublet and biological evidence.
8. Detect doublets at the appropriate independent capture/library level.
9. Justify parameters with data distributions and experimental design.
10. Evaluate biological markers, technical effects and stability beyond UMAP.
11. Preserve identifiers, feature order, provenance and reproducible outputs.
12. Report missing inputs, failed checks and unverified results explicitly.

## 31. Official implementation references

The fixed cell-cycle policy and numerical starting values are project decisions.
These references describe relevant API behavior; consult the version matching
the installed environment before execution.

- [scvi-tools SCVI API](https://docs.scvi-tools.org/en/stable/api/reference/scvi.model.SCVI.html): count-layer registration, continuous nuisance covariates, model and training interfaces.
- [Scanpy HVG API](https://scanpy.scverse.org/en/stable/generated/scanpy.pp.highly_variable_genes.html): seurat_v3 count input and batch-aware selection.
- [Scanpy cell-cycle scoring](https://scanpy.scverse.org/en/stable/generated/scanpy.tl.score_genes_cell_cycle.html): scoring interface and phase labels.
- [Scanpy Scrublet API](https://scanpy.scverse.org/en/stable/api/generated/scanpy.pp.scrublet.html): doublet-detection interface.

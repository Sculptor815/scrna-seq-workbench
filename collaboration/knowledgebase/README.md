# Universal scRNA-seq Analysis and Cell Annotation Knowledge Base

Updated: 2026-10-07.

This document is the English edition of the revised analysis policy agreed with
the owner. It applies across scRNA-seq datasets, including primary tissues, cell
lines and differentiation experiments, with no dataset-specific cluster labels or preferred parameter choices.

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
Establish dataset relationships from the paper, metadata and/or user clarification
  -> Define the number of analysis groups and which inputs belong in each group
  -> Verify counts and metadata
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
  -> Follow the annotation plugin's evidence and review workflow
  -> Investigate unresolved populations with alternative candidates and markers
  -> Present reference judgments and expression evidence for human review
  -> Apply reviewed labels; save and display annotation outputs
```

Reuse documented intermediate results when their provenance and settings are known.
A filename containing `QC` does not establish which steps were completed.

### 1.1. Establish dataset relationships and analysis groups before analysis

**Do not blindly analyze every input separately or merge all inputs together.**
Before committing to an analysis plan, determine how the datasets relate to one
another and to the user's biological question.

Consult the original paper, Methods, supplementary sample tables and repository
metadata when available. Identify study/accession, organism, tissue or source,
donor, biological replicate, condition, timepoint, assay/platform, technical
capture/library and any pairing or overlap between inputs. Distinguish independent
datasets from technical partitions, subsets or duplicate exports of the same cells.

Use that evidence to specify:

- How many analysis groups are needed and the purpose of each group.
- Which datasets or samples should be combined and analyzed jointly.
- Which datasets or samples should be analyzed separately, and why.
- Which groups will be compared downstream, including any reference/query roles.
- Whether grouping differs by stage, such as capture-level QC/doublet detection
  followed by a shared representation or separate condition comparisons.

If the paper and metadata do not resolve the intended grouping, ask the user a
focused question naming the inputs and plausible groupings. Obtain the missing
answer before performing grouping-dependent merging, splitting, integration or
model training. Independent input inspection can continue while clarification
is pending.

Record a dataset-to-analysis-group map, the rationale and supporting paper
section/table, metadata field or explicit user instruction. Preserve source
dataset, sample, donor, condition and timepoint labels when combining inputs.
Joint analysis does not automatically require batch correction, and an analysis
group is not automatically a technical batch or a biological replicate.

Do not infer grouping solely from filenames, file count, a shared accession,
tissue labels or timepoints. A previous script's grouping is a historical choice
to verify, not sufficient justification to reuse it.

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
| Tissue, developmental stage, timepoint, treatment, disease, dose, genotype | Preserve as biological variables by default |

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

## 22. Choose n_neighbors

Build the graph in a validated representation: use `use_rep="X_scvi"` after
scVI, or an explicitly selected PCA representation for a conventional workflow.
Do not build the biological clustering graph from two-dimensional UMAP coordinates.

By default, run several candidate values and let the user choose after reviewing
the results. A practical initial set is 15, 20, 30 and 50, adjusted to the cell
count, biological question and available resources. The value 30 may serve as a
comparison baseline, not an automatically selected final setting. These are
practical candidates, not universal optima or HPA requirements.

| Candidate n_neighbors | Interpretation and check |
|---|---|
| 10-15 | Emphasizes local structure; inspect fragmentation and sensitivity to noise |
| 20-30 | General starting range; inspect both major lineages and small populations |
| 40-50 | Emphasizes broader connectivity; check that distinct or rare populations remain distinguishable |
| Above 50 | Use only with a specific rationale and evidence that relevant local structure is preserved |

Present a recommendation using heterogeneity, target granularity, rare-population
preservation, graph connectivity and robustness, not cell count alone. The user
makes the final choice unless they have explicitly delegated parameter selection. A smaller neighborhood
does not guarantee recovery of a rare type. Check whether apparent fragments
have reproducible marker programs or instead reflect QC, residual cell cycle,
batch effects or unstable graph connections.

Keep `n_neighbors < n_cells`; reconsider the range after subsetting. Initially
hold latent coordinates, distance metric and seed fixed while comparing graphs.
Record the graph key, representation, metric, neighbor count and software version.
A changed graph requires rerunning Leiden and any UMAP intended to represent that
graph; it does not by itself require retraining scVI.

If cells merely look too scattered because their plotted dots are tiny, adjust
point size and figure dimensions first. Point size changes display only;
`n_neighbors` changes the graph and can change the biological conclusions.

## 23. Choose Leiden resolution and interpret UMAP

Leiden partitions the neighbor graph. Higher resolution generally produces finer
partitions, but a numerical resolution has no universal mapping to cell types.
Results depend on the graph, representation, cells, backend and random seed.

For a broad initial survey, run a bounded set such as 0.3, 0.5, 0.8 and 1.0,
and present the alternatives for the user's selection. Extend to 1.2 or 1.5 when
finer structure is relevant and supported. Adjust the candidate range to the
analysis; do not select the same resolution across datasets automatically.

| Observation | Next decision |
|---|---|
| One lineage is split into many clusters with no reproducible distinguishing markers | Compare a lower resolution and inspect QC, batch and cell-cycle effects |
| Distinct, coherent lineage programs occupy different cells within one cluster | Compare a higher resolution or perform a justified local subclustering analysis |
| A small cluster has coherent markers and acceptable QC | Preserve and investigate it; small size alone does not justify merging |
| Cluster boundaries follow a continuous expression gradient | Consider a broad identity plus state labels rather than declaring every partition a distinct type |
| Major populations change substantially under modest settings or seeds | Revisit the representation, graph and technical effects before final annotation |

Recommend a resolution that supports the requested biological granularity with
coherent markers, interpretable alternatives and reasonable stability, while
leaving the final selection to the user unless explicitly delegated. Neither
the lowest resolution nor the largest number of clusters is inherently best.
Multiple clusters may legitimately share one broad cell-type label.

When comparing resolution alone, reuse the same graph and UMAP so that only
cluster labels change. Store each partition under a distinct key, for example
`leiden_res_0.5`; preserve the selected partition and its settings explicitly.
Changes to the graph, cell subset or cluster membership invalidate old
cluster-ID-to-label mappings until reviewed again. Never reuse labels merely
because the new run has the same number or names of clusters.

UMAP is a display of a high-dimensional representation. Island separation,
compactness and inter-island distance do not establish identity, lineage
relationships or differentiation direction. Changes to UMAP `min_dist`, seed,
point size or layout should not be used to manufacture biological evidence.
Changing only UMAP display settings does not require rerunning Leiden.

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

For neighbors and Leiden resolution, the default deliverable is an executed,
reviewable parameter comparison followed by the user's selection. Merely listing
possible values or silently choosing one does not satisfy this workflow. An
exhaustive grid search is not required. Candidate comparisons:

| Parameter | Candidate values |
|---|---|
| HVGs | 2,000 / 3,000 / 4,000 |
| n_latent | 10 / 20 / 30 |
| Neighbors | 15 / 20 / 30 / 50, adjusted to cell count and heterogeneity |
| Leiden resolution | 0.3 / 0.5 / 0.8 / 1.0; extend only when justified |

Retrain when model inputs or model parameters change. Reuse a validated latent
representation when changing only neighbors or clustering. Record all attempts
and results. If modest changes substantially alter major conclusions, revisit
counts, QC, doublets, batches, HVGs and convergence.


### 25.1. Run comparisons before asking the user to select

Use either a bounded joint grid or a staged comparison:

- **Bounded grid:** for example, four neighbor values crossed with four
  resolutions produce 16 partitions. Build one graph and UMAP per neighbor
  value, then run each resolution on that graph. This illustrates the interaction
  between graph construction and clustering without retraining the latent model.
- **Staged comparison:** first compare neighbor values at a shared provisional
  resolution; then compare resolutions on the user's selected or shortlisted
  graph(s). If the second stage changes the interpretation of the first, revisit
  the relevant neighbor alternatives rather than treating them as independent.

Hold the input cells, latent representation, distance metric, backend and seeds
fixed across the initial comparison. Use the same UMAP coordinates for all
resolutions of a given graph. Neighbor-specific UMAPs may differ in layout, so
do not interpret their rotation or island positions as biological changes.
Use consistent plot size, point size and labeling across panels.

Give each candidate a stable identifier and preserve its graph, UMAP and
cluster labels under distinct keys or in separate artifacts. Label every panel
with neighbor count, resolution and cluster count. Cluster IDs and their colors
are arbitrary between partitions; do not imply a one-to-one identity match.

Save and directly display a comparison gallery, such as rows for neighbor values
and columns for resolutions, alongside a concise table containing:

- Candidate ID, parameters, cluster count and cluster-size distribution.
- Major marker programs, plausible rare populations and signs of merging or
  fragmentation, with supporting marker plots for shortlisted alternatives.
- QC, batch and cell-cycle patterns that could explain the partitions.
- Stability evidence where assessed, unresolved tradeoffs, and the agent's
  recommendation with its reason. Mark unperformed checks as unassessed.

Ask the user to select a parameter pair, or separate pairs for separate analysis
groups, only after providing the concrete comparison. The user may request
additional values or explicitly delegate the decision. If they have already
chosen values or delegated selection, honor that instruction without asking again.
Do not treat a lack of response as selection; keep outputs provisional and
continue only work that does not depend on the final partition.

After selection, record the chosen pair, selected graph and cluster key, decision
source and rationale. Save the selected result while preserving alternatives.
Use that exact partition for downstream cluster annotation and marker tables;
invalidate earlier label mappings when cluster membership changes. Never claim
a parameter sweep was executed when only code or a proposed grid was delivered.

## 26. Default decision table

| Parameter | Starting value or policy |
|---|---|
| Analysis groups / joint vs. separate analysis | Determine from study relationships and the research question; clarify unresolved choices with the user |
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
| Neighbors | Run multiple valid candidates, display comparisons, and let the user select unless explicitly delegated |
| Leiden resolution | Run multiple candidates on the chosen/shortlisted graphs; provide evidence and let the user select unless explicitly delegated |
| Annotation | Follow the plugin's evidence policy, investigate alternatives, and obtain actual human review |

## 27. Transfer principles, not dataset-specific settings

Keep this knowledge base general. Store accession-specific decisions, cluster
mappings, chosen parameters and user corrections in the corresponding analysis
record, not as universal defaults here.

Reuse a previous configuration only after checking assay, species, tissue,
experimental design, data quality and the requested biological granularity.
A value that worked in one dataset is a candidate to evaluate elsewhere, not
evidence that it will work again. Different analysis groups may need different
settings; matching their cluster counts or UMAP appearance is not a goal.

Separate three kinds of statements in reports: a user-selected policy, an
empirical starting heuristic, and a conclusion supported by the current data.
Record whether each step was planned, executed, checked or human-reviewed.
Existing embeddings or filenames do not establish that all current policies,
including cell-cycle correction, were applied.

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
Do not report the conflict as resolved until this import check succeeds in the
actual execution environment.

## 29. Required decision report and artifacts

Produce a table with **parameter, selected value, observed evidence, reason and
validation outcome**. Include:

- Biological question, organism, assay and sample/library structure.
- Dataset relationships and dataset-to-analysis-group map: number of groups,
  joint/separate analysis decisions, stage-specific grouping, rationale and sources
  or explicit user clarification.
- Input provenance/hashes and verified count source.
- Matrix representations and cell/gene numbers before and after each QC step.
- QC thresholds, exclusions, doublet settings and cell-cycle gene coverage.
- Batch definition, confounding assessment and biological variables preserved.
- HVG list/order, model/training parameters, seeds, software versions and hardware.
- Training history, latent coordinates, graphs, embedding and cluster labels.
- Marker, QC, batch, cell-cycle and robustness checks, with unresolved issues.
- Candidate cell types, positive/contradictory/missing markers, reference coverage,
  specificity-screen provenance, human review decisions and annotation version.
- Both saved figures and directly displayed review figures, with the expression
  representation and cluster key stated.
- Full-gene H5AD, saved model and matching feature/registration information for
  reloading, figures and a readable report in an isolated output directory.

Do not infer completion from file existence. Distinguish execution success from
biological validation and clearly label missing or unverified evidence.

## 30. Agent guardrails

1. Establish dataset relationships and analysis groups from the paper, metadata
   or user clarification before merging, splitting or training; never group blindly.
2. Verify count provenance and preserve counts before transformations.
3. Never use normalized expression or regression residuals as scVI count input.
4. Score and correct cell cycle under the fixed policy, then validate the outcome.
5. Never infer technical batch from category count or invent missing metadata.
6. Do not automatically remove tissue, timepoint, treatment or target biology.
7. Do not hard-filter HB/ribosomal expression or a fixed upper percentage.
8. Investigate high-count MAD flags alongside doublet and biological evidence.
9. Detect doublets at the appropriate independent capture/library level.
10. Run and display multiple neighbor/resolution candidates; justify a recommendation
    and let the user select the final settings unless they have delegated selection.
11. Evaluate biological markers, technical effects and stability beyond UMAP.
12. Preserve identifiers, feature order, provenance and reproducible outputs.
13. Report missing inputs, failed checks and unverified results explicitly.
14. Investigate unresolved populations without forcing an unsupported identity.
15. Treat external specificity screens as reference evidence, not automatic labels.
16. Present an evidence-based recommendation and preserve genuine human review.
17. Keep reusable knowledge separate from dataset-specific decisions.

## 31. Start annotation with the plugin's documented workflow

Read the active [cell annotation skill](../../plugins/scrna-seq-workbench/skills/scrna-cell-annotation/SKILL.md),
[annotation decisions](../../plugins/scrna-seq-workbench/skills/scrna-cell-annotation/references/annotation.md)
and [HPA-guided review policy](../../plugins/scrna-seq-workbench/references/hpa-guided-annotation.md).
Follow their current input, evidence and review contracts before proposing labels.
This knowledge base supplements those contracts; it does not claim to implement
new runner behavior.

Confirm species, tissue, developmental or disease context, assay and desired
granularity. Select a traceable, context-appropriate marker panel. For human
data, use HPA's documented tissue-specific markers and reference expression when
appropriate, supplemented by primary literature and matched atlases. HPA is
human-only: capitalization changes do not validate cross-species marker transfer.
Adult normal references can lack developmental, malignant or induced states.

Review the plugin's proposals, marker expression, coverage, contradictory
evidence and review template. Use combinations of available, informative markers;
one familiar gene or a high heuristic score is insufficient. The plugin requires
at least two supporting genes for accepted labels; this is its safeguard, not a
universal numerical rule published by HPA. Scores are relative evidence, not
calibrated probabilities.

Distinguish cell identity from activation, proliferation, stress and maturation
state. Prefer a supported broad label when fine detail is uncertain. Do not
assume that every Leiden partition is a separate cell type.

## 32. Investigate unresolved populations actively

An unresolved label means that the evidence does not yet support a sufficiently
specific identity. It is neither a QC failure nor proof of a doublet or novel
cell type. Do not delete cells merely because annotation is difficult.

For each unresolved cluster:

1. Check marker availability, gene identifiers, expression representation, cell
   number, counts, complexity, mitochondrial fraction and doublet evidence.
   A missing gene in the input is different from a measured but undetected gene.
2. Inspect exploratory cluster markers and expression fractions, including
   comparisons with the most plausible competing populations. A top-marker list
   dominated by housekeeping, stress or cell-cycle genes may be uninformative.
3. Expand the candidate set beyond the initial panel. Consult tissue and study
   context, matched references and primary literature for alternative lineages,
   progenitors, immature states or context-specific phenotypes. Do not force an
   expected label when an appropriate reference type is absent.
4. Build a small discriminating panel for each plausible alternative, including
   supporting genes and genes that favor competing identities. Use the external
   specificity skill in Section 33 when reference specificity needs investigation.
5. Plot these genes on the existing UMAP and summarize detection fractions and
   mean expression by cluster with dot plots, heatmaps or violins. Determine
   whether competing programs occur in the same cells or different subregions;
   separate feature plots alone do not prove coexpression.
6. If distinct subpopulations are supported, consider local subclustering while
   preserving parent IDs and provenance. If signals are mixed within cells,
   assess biological states, ambient RNA and doublets with additional evidence;
   none of these explanations follows automatically from mixed markers.
7. Present the best-supported candidate, alternatives, supporting and opposing
   evidence, limitations and the next discriminating check to the human reviewer.

If evidence remains inadequate, retain an unresolved or broad provisional label.
Use the active plugin's canonical `Unknown` representation for unresolved/mixed
output; keep candidate names in evidence fields. Do not silently equate a
candidate string with an accepted label. Stop adding speculative labels when
available expression and reference evidence cannot distinguish the alternatives.

## 33. Use the gene specificity skill to evaluate candidate markers

Use [scrnaseq-gene-specificity-screen](https://github.com/Sculptor815/scrnaseq-gene-specificity-screen)
when a proposed marker panel needs reference specificity assessment or a
difficult population needs better discriminating genes. Read its `SKILL.md`
and specificity rules before execution. It evaluates a supplied candidate gene
list; it does not discover markers from an unspecified transcriptome by itself.

Candidate genes can come from official HPA panels, primary literature, matched
atlases and exploratory DE in the query. Include alternatives rather than
screening only genes that support the favored identity. Define explicit target
cell-type groups using the exact HPA column names, checking coverage and group
membership before screening. Prefer specific comparison groups to an excessively
broad lineage group that obscures the distinction of interest.

Run the documented fetch, plotting and screening steps, or reuse an appropriately
documented cache. Preserve input genes, configuration and target-group order,
repository revision, reference retrieval information, validation reports,
expression tables, selected/borderline genes and plots. Download references to
an isolated analysis directory; do not modify installed plugin/cache contents.

Interpret its output according to its actual rule: selection occurs when the
cell-type expression peak is assigned to a target group; tissue expression is
additional annotation and does not filter candidates. Review the inside/outside
peak ratio, competing peaks, absolute expression and borderline cases. Passing
this rule does not establish exclusive expression, an official HPA enrichment
category, or the identity of a query cluster.

A broad target group can select a gene whose peak belongs to a different member
of that group. A ratio close to one, tied peaks, missing reference values,
ambiguous identifiers or incomplete population coverage require explicit review.
Absence from HPA is not evidence of absence in the query; a developmental or
species-mismatched population may have no suitable HPA counterpart.

Finally, test shortlisted genes in the user's expression data. A useful
annotation marker needs appropriate query expression, coverage and discrimination
against the relevant alternatives, not just favorable external reference values.
Report a screen as unrun, failed or incomplete when appropriate; do not mark a
gene "validated by the skill" without a traceable successful result.

## 34. Human review determines the final annotation

The agent prepares evidence and reference judgments. Human review determines
whether a proposed label is accepted, revised, broad-only, mixed or unresolved.
Do not call an unreviewed proposal final or fabricate a reviewer identity.
An explicit user correction is a real review decision for the stated population;
it does not approve every other cluster or turn the decision into an independent
experimental validation.

Provide a review table with cluster ID and clustering version, cell count,
proposed broad/detailed identity, alternatives, positive and contradictory
markers, missing markers, sources, reference limitations, QC assessment,
subclustering assessment, rationale, confidence and review status. Keep evidence
confidence separate from human review status: an accepted label need not have
high evidential confidence.

Complete the plugin's actual review fields and apply reviewed labels through its
documented workflow. Preserve original cluster IDs and counts. Version the label
map and retain earlier proposals, review decisions and reasons. Never map labels
positionally or reuse a mapping after reclustering without verifying membership.
Regenerate tables, annotated plots and saved annotated data after approved edits.
Unresolved populations remain visible in reports and analysis denominators;
apply the plugin's downstream eligibility rules explicitly.

## 35. Figures must support direct review and reproducible saving

Save and directly display the important figures in the active notebook or review
interface. Saving a file alone does not satisfy a request to view it. If normal
notebook rendering fails, display the saved PNG explicitly and verify the output.

Use the same UMAP coordinates for cluster labels, annotation labels and candidate
gene expression within a review version. Include a cluster-ID map alongside
cell-type labels. Organize marker genes by proposed cell type or competing
hypothesis, and include a dot plot or heatmap with expression fractions or means.
State the matrix/layer, normalization, gene identifiers and missing markers.
Gene-wise scaled colors do not support absolute expression comparisons between
different genes.

Keep comparable labels colored consistently across related datasets. Use
readable point sizes and legends; change plotting size before changing analysis
parameters to address a visual-density complaint. Produce a separate multipage
marker-review PDF for each analysis group when requested, with cluster reference,
candidate panels and summary plots. Save annotation UMAPs as PNG and PDF with
traceable filenames and the annotation version.

PDF-only review supports provisional visual interpretation. Do not infer
per-cell coexpression, exact expression fractions or new DE statistics from a
PDF. Identify figures made from original expression data separately from
annotation legends added to an existing image.

## 36. Separate exploratory markers from condition differential expression

First specify the contrast: cluster versus rest, annotated type versus rest,
one candidate population versus another, or the same cell type across conditions.
Specify which datasets are combined and why before running the analysis.

For exploratory markers, use a documented normalized/log expression copy derived
from verified counts, with explicit `use_raw` and layer settings. Do not use scVI
latent coordinates as gene expression, and do not restrict markers to HVGs unless
that limitation is intentional. Export the complete tested-gene table as well
as filtered positive markers, effect estimates, adjusted p-values and detection
fractions inside and outside the target group. Treat thresholds as tunable
screening criteria, not biological truth. Rank-based marker tests following
clustering are exploratory and do not independently validate the same clusters.

For condition inference, establish biological replicates, pairing, confounding
and the relevant cell type. Prefer a justified replicate-aware design, such as
count pseudobulk by biological sample and cell type with a suitable count model.
Cells are not independent biological replicates. If the required replicate
structure is unavailable, label descriptive comparisons accordingly.

Registering cell-cycle covariates in scVI does not automatically correct a later
Wilcoxon test on normalized counts. State which covariates each analysis actually
models. Preserve the fixed representation-level cell-cycle policy, inspect
cell-cycle-driven marker results, and choose a suitable downstream model when
covariate-adjusted inference is required; do not claim residualization happened
implicitly or feed residuals to count models.

## 37. Implementation and reference sources

The fixed cell-cycle policy and numerical starting values are project decisions.
These references describe relevant API behavior; consult the version matching
the installed environment before execution.

- [scvi-tools SCVI API](https://docs.scvi-tools.org/en/stable/api/reference/scvi.model.SCVI.html): count-layer registration, continuous nuisance covariates, model and training interfaces.
- [Scanpy HVG API](https://scanpy.scverse.org/en/stable/generated/scanpy.pp.highly_variable_genes.html): seurat_v3 count input and batch-aware selection.
- [Scanpy cell-cycle scoring](https://scanpy.scverse.org/en/stable/generated/scanpy.tl.score_genes_cell_cycle.html): scoring interface and phase labels.
- [Scanpy Scrublet API](https://scanpy.scverse.org/en/stable/api/generated/scanpy.pp.scrublet.html): doublet-detection interface.

- [Scanpy neighbors API](https://scanpy.readthedocs.io/en/stable/api/generated/scanpy.pp.neighbors.html): representation, neighborhood size and graph storage.
- [Scanpy Leiden API](https://scanpy.readthedocs.io/en/stable/generated/scanpy.tl.leiden.html): resolution, graph selection, backend and labels.
- [Scanpy marker ranking API](https://scanpy.readthedocs.io/en/stable/generated/scanpy.tl.rank_genes_groups.html): log-expression input, contrasts and marker outputs.
- [HPA single-cell transcriptomics methods](https://www.proteinatlas.org/humanproteome/single%2Bcell/single%2Bcell%2Btype/method/transcriptomics): tissue-specific annotation and reference scope.
- [Gene specificity skill](https://github.com/Sculptor815/scrnaseq-gene-specificity-screen/blob/main/SKILL.md) and [screening rules](https://github.com/Sculptor815/scrnaseq-gene-specificity-screen/blob/main/references/specificity-rules.md): external candidate-marker assessment and its limits.

# Important analysis parameters

These are **current software defaults**, not universal recommendations. Explain
relevant choices after understanding the sample and goal. Users can ask the
assistant to recommend values. Inspect the installed CLI's --help for exact options.

## Quality control

| Setting | Meaning and current example | Evidence needed |
|---|---|---|
| min_genes / max_genes | Detected genes per cell; example minimum 200, no maximum | Per-sample distribution, assay, low-RNA populations, paper method |
| min_counts / max_counts | UMI counts; example minimum 1, no maximum | Library depth and biology; high counts alone do not prove doublets |
| max_counts_quantile | Optional per-sample upper quantile, expressed from 0 to 1 | Outlier review; ties can remove more than the nominal fraction |
| max_pct_mt / max_pct_hb | Optional percentages, expressed from 0 to 100 | Gene identifiers, tissue and target lineages; missing markers are not zero-quality evidence |
| min_cells_per_gene | Minimum cells expressing a gene; example 3 | Rare-type marker loss |
| per_sample | Overrides for individual samples | Explain differences and asymmetric condition filtering |
| doublets / remove-doublets | Separate scoring and explicit removal choices | Actual capture_id, assay and loading; expected rate defaults to 0.06 only when requested |

Lower limits are inclusive and upper limits exclusive. Check excluded counts and
reasons by sample. Review unexpected loss of low-RNA candidate populations; do not
invent cell labels during initial QC or restore every low-count cell automatically.
An absent MT gene set makes that metric unavailable. Paper thresholds and their
gene universes may differ from a processed public matrix.

## Representation and clustering

The default route is counts -> scVI -> neighbors -> Leiden/UMAP. An explicitly
selected alternative is HVG log expression -> cycle regression -> scaled PCA ->
Harmony -> neighbors -> Leiden/UMAP, using verified technical batches. scVI does not train on PCA coordinates. Cell-cycle
scores from full-gene log expression are registered before training; inspect their
coverage and post-training diagnostics. See the [policy entry point](agent-policy.md).

| Setting | Current CLI default | Decision to explain |
|---|---|---|
| backend | scvi | Explicit harmony uses harmonypy on CPU with verified technical batches; no automatic switch |
| backend-reason | Unset | Record the actual user choice or delegated rationale, not fabricated consent |
| species / cycle genes | Explicit species; human symbol preset | Mouse/non-symbol IDs need a documented exact mapping JSON |
| min-cycle-genes | 5 per phase | Execution minimum, not biological validation; inspect missing genes |
| latent / n-layers / dropout | 20 / 2 / 0.1 | scVI model parameters; for Harmony latent means requested PCA dimensions, other two are unused |
| hvg / hvg-flavor | 3000 / seurat_v3 | Raw counts by default; explicit seurat uses lognorm |
| batch-key | Unset (None) | Verified technical metadata only; scVI still runs without it |
| neighbors / resolution | 30 / 1 | Display baseline, pending review; not automatic final acceptance |
| neighbors-grid | 15 20 30 50 | Capped/deduplicated at n_cells - 1; adjust explicitly |
| resolutions-grid | 0.3 0.5 0.8 1.0 | Same graph/UMAP per neighbor setting; review candidates |
| max-epochs / batch-size | 400 / 256 | Budget and minibatch size; inspect training history |
| early stopping / patience | On / 20 | --no-early-stopping is explicit; stopping does not prove convergence |
| train-size | 0.9 | Validation uses the remaining cells; record seed and split |
| seed / device | 0 / auto | scVI selects available CUDA else CPU; Harmony is CPU only; full pipeline may exceed 1 hour |
| skip-cell-cycle | Off | Requires an actual user override and nonempty recorded reason |

Inspect condition/batch/donor relationships before correction. Missing types across
batches can be biological. The CLI uses the library defaults for UMAP min_dist
and spread. PCA variance-spectrum inspection requires a separate analysis.
Compare settings using marker support, preserved populations and stability.

## Annotation and condition DE

Annotation needs species, tissue, label granularity and a versioned reference/panel.
Defaults are min-markers=2, min-overlap=0.5, min-score=0.5 and min-margin=0.25.
Marker scores are not probabilities. Explain why stricter rules may increase Unknown
and looser ones may increase wrong assignments. Final labels require actual review.

DE needs case/control direction, true donors and paired/unpaired design. Defaults:
20 cells per donor/condition/type, 3 complete pairs or 3 independent donors per arm,
and gene pseudobulk total count >=10. These minima do not guarantee power.
Current formulas are `~ donor + condition` and `~ condition`; arbitrary additional
batch/age/sex covariates are unsupported. The summary uses a fixed per-type
reporting threshold of padj < 0.05.

Implementation: [CLI](../scripts/scrna.py), [integration](../scripts/scrna_core/integrate.py),
[QC config](../assets/qc.example.json). Algorithm background:
[scVI API](https://docs.scvi-tools.org/en/stable/api/reference/scvi.model.SCVI.html).

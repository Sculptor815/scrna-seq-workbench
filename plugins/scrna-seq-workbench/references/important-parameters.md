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

PCA -> neighbors -> Leiden/UMAP and counts -> scVI -> neighbors -> Leiden/UMAP are
different routes. The current scVI branch does not train on PCA coordinates.

| Setting | Current CLI default | Decision to explain |
|---|---|---|
| backend | scvi | scVI, explicit PCA baseline, or a planned comparison |
| latent | 10 | PCA components for pca; latent dimensions for scvi. Record separately; actual PCA dimensions may be capped |
| hvg / hvg-flavor | 2000 / seurat | Feature space; seurat uses lognorm, seurat_v3 uses counts and needs scikit-misc |
| batch-key | Unset | Meaning of a real metadata column and its relation to condition/donor. PCA does not perform scVI batch correction |
| neighbors | 15 | Local versus broader structure; actual value is capped by cell count |
| resolution | 1 | Leiden granularity; more clusters do not imply more true cell types |
| max-epochs | 200 | Training budget; early stopping enabled by this wrapper when the cap is at least 30. A cap does not prove convergence |
| seed / device | 0 / cpu | Repeatability, sensitivity checks and an actually available GPU environment |

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

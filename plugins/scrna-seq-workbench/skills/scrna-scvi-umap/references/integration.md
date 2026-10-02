# scVI and UMAP decisions

Use technical batch IDs only when their meaning is understood. If all controls
are in one batch and all cases in another, correction cannot prove that the
biological treatment effect was preserved. Keep uncorrected comparisons and
review known cell identities. One batch cannot demonstrate batch-removal quality.

The CLI defaults to seurat HVGs on log-normalized expression; seurat_v3 is an
explicit option on integer counts. No dependency-dependent HVG switch occurs.
scVI receives only raw counts; the output preserves every retained gene for
annotation and pseudobulk. scVI seed is set before model creation and training.
GPU kernels/environment changes can still change numerical results.

Cell-cycle regression/covariates are deliberately not automatic in this release.
If proliferation is part of the question, removing it can erase the desired
signal. UMAP distance/global geometry and visually mixed batches are not a
standalone biological validation. Evaluate label conservation, rare cells and
batch mixing jointly on suitable reference data.

Sources: https://docs.scvi-tools.org/en/stable/api/reference/scvi.model.SCVI.html
https://docs.scvi-tools.org/en/stable/api/reference/scvi._settings.ScviConfig.html

# Representation and UMAP decisions

Default to scVI. Explain before a full pipeline that runtime may exceed 1 hour;
cell counts, hardware, training and review affect the duration. With compatible
CUDA, use GPU scVI. Without it, users can keep slower CPU scVI or explicitly
choose Harmony (harmonypy). No automatic backend switch is allowed.

Use technical batch IDs only when their experimental meaning is understood.
Confounded batch and condition effects cannot be proven separable by integration.
Preserve biological variables and assess cell identities alongside batch mixing.
scVI can run with no batch key; Harmony requires two or more verified batches.

Default seurat_v3 HVGs use counts and require scikit-misc. An explicitly selected
seurat method uses log-normalized expression; never switch due to a missing package.
Score cell cycle on the full-gene normalized expression before subsetting HVGs.
Inspect gene coverage, residual associations and biological conservation.

- scVI receives count HVGs with S_score/G2M_score continuous covariates. Save the
  model/history and use X_scvi. GPU kernels can change numerical results.
- Harmony receives scaled PCA from an HVG log-expression copy after regression
  of S_score/G2M_score. Use harmonypy and X_pca_harmony; save PCA loadings,
  features, objective history and coordinates. No scVI model is produced.

Both routes preserve full-gene counts and normalized expression for annotation.
Cell-cycle exceptions require an explicit user override and recorded reason.
Record backend choice, actual device and elapsed time. Candidate parameter and
annotation review requirements apply equally. UMAP geometry and mixed batches
alone do not establish biological validity or equivalent results across methods.

Sources: [SCVI API](https://docs.scvi-tools.org/en/stable/api/reference/scvi.model.SCVI.html),
[Harmony via harmonypy](https://scanpy.readthedocs.io/en/stable/generated/scanpy.external.pp.harmony_integrate.html).

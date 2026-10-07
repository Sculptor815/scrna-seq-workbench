# v0.4.0 - required scVI, cell-cycle covariates and bundled agent knowledge

New representations now require scVI in every analysis group, including inputs
without technical batch metadata. Integration scores cell cycle before HVG
subsetting and registers S_score/G2M_score with the count model. It preserves the
full-gene count object, saves a reloadable model and exports cycle diagnostics,
training history and neighbor/resolution candidates for review.

The six Skills load a bundled policy entry point and the relevant knowledge-base
sections. The collaboration knowledge base remains the single maintenance source;
synchronization and archive checks prevent stale or missing plugin copies.

Breaking CLI changes: --species is required for integrate; --backend pca is rejected.
Use requirements-scvi.txt in the execution environment. Human symbols have a
bundled cycle preset; mouse or other gene identifiers require documented mapping.
Defaults now use 3,000 seurat_v3 HVGs, 20 latent dimensions, a 400-epoch budget,
early stopping with patience 20, and candidate parameter grids. These are starting
settings, not universal biological optima. Cycle exceptions require a recorded
explicit user override. Model/candidate completion does not imply convergence or
human approval.

See [agent knowledge setup](docs/AGENT_KNOWLEDGE.md), [usage](docs/USAGE.md) and
validation.json for the exact checks. Historical analysis reports and benchmark
results are not rewritten. Host loading, GPU training and biological accuracy
are not established by the package or synthetic tests.

# v0.4.0 - default scVI, explicit Harmony and runtime guidance

New representations default to scVI in every analysis group, including inputs
without technical batch metadata. Integration scores cell cycle before HVG
subsetting and registers S_score/G2M_score with the count model. It preserves the
full-gene count object, saves a reloadable model and exports cycle diagnostics,
training history and neighbor/resolution candidates for review.

This update retains version 0.4.0 as requested. Before a full pipeline, the agent
discloses that execution may exceed 1 hour. scVI remains the default; --device auto
uses available compatible CUDA or otherwise CPU. Users without a GPU can wait for
CPU scVI or explicitly choose Harmony (harmonypy) with verified technical batches.
No failure, missing dependency or slow training triggers an automatic backend switch.

The Harmony route uses cycle regression on an HVG log-expression copy, scaled PCA
and Harmony coordinates; counts/full-gene expression are preserved. It adds
requirements-harmony.txt and records backend/device/elapsed-time provenance.
Historical analysis figures retain their original methods and versions.
The knowledge base now explains scVI's NB count likelihood, variational inference
and potential advantages over direct PCA, with brief user-facing guidance in
the Skills and README and no claim of guaranteed biological superiority.

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

# Select a reviewed parameter candidate

The integration runner fits the selected scVI or Harmony backend once, then saves
candidate graphs, UMAPs and
Leiden partitions in the full-gene H5AD. Review parameter_candidates.csv and its
PNGs together with markers, QC, batch and cell-cycle diagnostics. Show the user
the figures. Record their selection or explicit delegation and your rationale.

Use the exact graph_key, embedding_key and cluster_key from the chosen CSV row.
The following is a recipe, not permission to fabricate a decision. Replace the
example paths, row number and decision text with the actual reviewed values:

```python
from pathlib import Path
import scanpy as sc
import pandas as pd

run = Path("runs/integrate-01")
output = Path("runs/selected-01.h5ad")
if output.exists():
    raise FileExistsError(output)
a = sc.read_h5ad(run / "integrated.h5ad")
row = pd.read_csv(run / "parameter_candidates.csv").iloc[0]  # actual chosen row
g = a.uns[row.graph_key]
a.obsp["distances"] = a.obsp[g["distances_key"]].copy()
a.obsp["connectivities"] = a.obsp[g["connectivities_key"]].copy()
a.uns["neighbors"] = dict(g, distances_key="distances", connectivities_key="connectivities")
a.obsm["X_umap"] = a.obsm[row.embedding_key].copy()
a.obs["leiden"] = a.obs[row.cluster_key].copy()
a.uns["leiden"] = dict(a.uns[row.cluster_key])
a.uns["scrna_parameter_selection"] = {
    "status": "selected", "graph_key": row.graph_key, "cluster_key": row.cluster_key,
    "neighbors": int(row.neighbors), "resolution": float(row.resolution),
    "decision_source": "REPLACE with the actual user choice or delegated decision",
    "rationale": "REPLACE with evidence supporting the selected granularity",
}
a.write_h5ad(output)
sc.pl.umap(a, color="leiden", show=True)
```

Save the selected UMAP as well. Finalize this choice before creating cluster-to-type
labels; changed cluster membership invalidates earlier mappings. Existing labels
must be re-reviewed rather than blindly copied onto new cluster IDs. Parameter
selection is separate from human approval of cell-type annotations.

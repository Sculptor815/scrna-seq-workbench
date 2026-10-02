import numpy as np
from .common import load_counts, lognormalize, require_columns


def run(args, report):
    import scanpy as sc
    import matplotlib.pyplot as plt
    a=load_counts(args.input)
    if min(a.shape)<3 or np.any(np.asarray(a.layers["counts"].sum(axis=1)).ravel()<=0):
        raise ValueError("Integration needs at least three cells/genes and positive counts in each cell")
    if args.batch_key:
        require_columns(a.obs,[args.batch_key])
        a.obs[args.batch_key]=a.obs[args.batch_key].astype("category")
    if (args.hvg<3 or args.latent<2 or args.neighbors<2 or args.max_epochs<1
            or not np.isfinite(args.resolution) or args.resolution<=0 or not 0<=args.seed<2**32):
        raise ValueError("Invalid integration parameters")
    np.random.seed(args.seed)
    lognormalize(a)
    sc.pp.highly_variable_genes(a,n_top_genes=min(args.hvg,a.n_vars),flavor=args.hvg_flavor,
                               layer="counts" if args.hvg_flavor=="seurat_v3" else None,
                               batch_key=args.batch_key,subset=False)
    h=a[:,a.var.highly_variable].copy()
    if min(h.shape)<3:
        raise ValueError("Too few HVGs for dimensionality reduction")
    report.update(n_cells=a.n_obs,n_genes=a.n_vars,n_hvg=h.n_vars,backend=args.backend,
                  actual_hvg_flavor=args.hvg_flavor,actual_batch_key=args.batch_key)
    if args.backend=="scvi":
        import scvi
        scvi.settings.seed=args.seed
        scvi.model.SCVI.setup_anndata(h,layer="counts",batch_key=args.batch_key)
        model=scvi.model.SCVI(h,n_latent=args.latent,n_layers=2,gene_likelihood="nb")
        model.train(max_epochs=args.max_epochs,accelerator=args.device,devices=1,
                    early_stopping=args.max_epochs>=30,batch_size=min(256,a.n_obs))
        model.save(str(args.outdir/"model"),overwrite=False)
        latent=model.get_latent_representation()
        rep="X_scvi"
    else:
        sc.pp.scale(h,max_value=10)
        ncomp=min(args.latent,h.n_vars-1,h.n_obs-1)
        sc.tl.pca(h,n_comps=ncomp,svd_solver="arpack",random_state=args.seed)
        latent=h.obsm["X_pca"]; rep="X_pca_baseline"
        report["warnings"].append("PCA baseline does not perform scVI batch integration.")
    if not np.isfinite(latent).all():
        raise ValueError("Non-finite latent coordinates")
    a.obsm[rep]=latent
    sc.pp.neighbors(a,use_rep=rep,n_neighbors=min(args.neighbors,a.n_obs-1),random_state=args.seed)
    sc.tl.leiden(a,resolution=args.resolution,random_state=args.seed,flavor="igraph",directed=False,n_iterations=2)
    sc.tl.umap(a,random_state=args.seed)
    a.write_h5ad(args.outdir/"integrated.h5ad")
    for col in ["leiden"]+([args.batch_key] if args.batch_key else []):
        sc.pl.umap(a,color=col,show=False)
        plt.gcf().savefig(args.outdir/("umap_clusters.png" if col=="leiden" else "umap_batch.png"),dpi=120,bbox_inches="tight")
        plt.close("all")
    report.update(n_clusters=int(a.obs.leiden.nunique()),cluster_sizes=a.obs.leiden.value_counts().to_dict())
    report["warnings"].append("UMAP layout and batch mixing alone do not establish biological accuracy; assess preserved cell identities.")

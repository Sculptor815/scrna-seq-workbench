"""Default scVI or explicitly selected Harmony, with cycle correction and review candidates."""
import time
import numpy as np
from .common import load_counts, lognormalize, require_columns, write_json, safe_name
from .cell_cycle import score_cell_cycle
from .runtime import announce_runtime, resolve_device


def validate_parameters(args):
    if args.backend not in ('scvi', 'harmony'):
        raise ValueError('Choose scvi or explicitly select harmony; no automatic backend substitution')
    if args.backend == 'harmony' and not args.batch_key:
        raise ValueError('Harmony requires a verified technical batch key with at least two batches; use scVI for no-batch analysis')
    positive = [args.hvg, args.latent, args.n_layers, args.neighbors, args.max_epochs,
                args.batch_size, args.early_stopping_patience]
    if (any(x < 1 for x in positive) or args.hvg < 3 or args.latent < 2 or args.neighbors < 2
            or not np.isfinite(args.resolution) or args.resolution <= 0
            or not 0 <= args.dropout < 1 or not 0 < args.train_size < 1
            or not 0 <= args.seed < 2**32):
        raise ValueError('Invalid integration parameters')
    if any(n < 2 for n in args.neighbors_grid) or any(not np.isfinite(r) or r <= 0 for r in args.resolutions_grid):
        raise ValueError('Invalid neighbor/resolution grid')


def save_umap(a, color, path, title=None):
    import scanpy as sc
    import matplotlib.pyplot as plt
    sc.pl.umap(a, color=color, show=False, title=title)
    plt.gcf().savefig(path, dpi=150, bbox_inches='tight')
    plt.close('all')


def build_candidates(a, args, report):
    import scanpy as sc
    import pandas as pd
    backend = args.backend
    representation = 'X_scvi' if backend == 'scvi' else 'X_pca_harmony'
    primary_n = min(args.neighbors, a.n_obs - 1)
    neighbors = sorted({min(n, a.n_obs - 1) for n in args.neighbors_grid + [args.neighbors]})
    resolutions = sorted(set(args.resolutions_grid + [args.resolution]))
    rows = []
    plots = args.outdir / 'parameter_candidates'
    plots.mkdir()
    for n in neighbors:
        graph = f'neighbors_{backend}_n{n}'
        sc.pp.neighbors(a, use_rep=representation, n_neighbors=n, random_state=args.seed, key_added=graph)
        sc.tl.umap(a, neighbors_key=graph, random_state=args.seed)
        embedding = f'X_umap_{backend}_n{n}'
        a.obsm[embedding] = a.obsm['X_umap'].copy()
        for resolution in resolutions:
            key = f'leiden_n{n}_r{resolution:g}'
            sc.tl.leiden(a, neighbors_key=graph, resolution=resolution, random_state=args.seed,
                         flavor='igraph', directed=False, n_iterations=2, key_added=key)
            save_umap(a, key, plots / f'{key}.png', title=f'{backend} | neighbors={n} | resolution={resolution:g}')
            rows.append({'neighbors': n, 'resolution': resolution, 'graph_key': graph,
                         'embedding_key': embedding, 'cluster_key': key,
                         'n_clusters': int(a.obs[key].nunique()),
                         'min_cluster_size': int(a.obs[key].value_counts().min()),
                         'display_baseline': n == primary_n and resolution == args.resolution})
    primary_graph = f'neighbors_{backend}_n{primary_n}'
    primary_cluster = f'leiden_n{primary_n}_r{args.resolution:g}'
    a.obsm['X_umap'] = a.obsm[f'X_umap_{backend}_n{primary_n}'].copy()
    a.obs['leiden'] = a.obs[primary_cluster].copy()
    a.obsp['distances'] = a.obsp[a.uns[primary_graph]['distances_key']].copy()
    a.obsp['connectivities'] = a.obsp[a.uns[primary_graph]['connectivities_key']].copy()
    a.uns['neighbors'] = dict(a.uns[primary_graph], distances_key='distances', connectivities_key='connectivities')
    a.uns['leiden'] = dict(a.uns[primary_cluster])
    # UMAP parameters are constant across candidates; its coordinates must match the primary graph.
    a.uns['scrna_parameter_selection'] = {'status': 'pending_review', 'graph_key': primary_graph,
                                         'cluster_key': primary_cluster, 'neighbors': primary_n,
                                         'resolution': args.resolution}
    pd.DataFrame(rows).to_csv(args.outdir / 'parameter_candidates.csv', index=False)
    report['parameter_candidates'] = rows
    report['parameter_selection'] = a.uns['scrna_parameter_selection']
    report['warnings'].append('Default leiden/X_umap are a display baseline; review candidates and record the user selection or delegated decision before final annotation.')


def fit_scvi(a, h, args, report, covariates, device):
    try:
        import scvi
    except ImportError as exc:
        raise RuntimeError('Install requirements-scvi.txt for scVI; no automatic Harmony fallback.') from exc
    import pandas as pd
    scvi.settings.seed = args.seed
    scvi.model.SCVI.setup_anndata(h, layer='counts', batch_key=args.batch_key,
                                  continuous_covariate_keys=covariates or None)
    model = scvi.model.SCVI(h, n_latent=args.latent, n_layers=args.n_layers,
                            gene_likelihood='nb', dropout_rate=args.dropout)
    model.train(max_epochs=args.max_epochs, accelerator=device, devices=1,
                early_stopping=not args.no_early_stopping,
                early_stopping_patience=args.early_stopping_patience,
                batch_size=min(args.batch_size, a.n_obs), train_size=args.train_size,
                check_val_every_n_epoch=1, default_root_dir=str(args.outdir / 'training_logs'))
    latent = model.get_latent_representation()
    if not np.array_equal(a.obs_names, h.obs_names):
        raise ValueError('Cell order changed during scVI fitting')
    if latent.shape != (a.n_obs, args.latent) or not np.isfinite(latent).all():
        raise ValueError('Invalid scVI latent coordinates')
    a.obsm['X_scvi'] = latent
    model.save(str(args.outdir / 'model'), overwrite=False, save_anndata=True)
    split = pd.Series('unassigned', index=h.obs_names, name='training_split')
    for label, indices in [('train', model.train_indices), ('validation', model.validation_indices),
                           ('test', model.test_indices)]:
        if indices is not None:
            split.iloc[np.asarray(indices, dtype=int)] = label
    split.to_csv(args.outdir / 'training_splits.csv', index_label='cell_id')
    pd.Series(h.var_names, name='gene').to_csv(args.outdir / 'model_genes.csv', index=False)
    history_dir = args.outdir / 'training_history'
    history_dir.mkdir()
    for name, values in model.history.items():
        if hasattr(values, 'to_csv'):
            values.to_csv(history_dir / f'{safe_name(name)}.csv')
    report['training'] = {'max_epochs': args.max_epochs, 'epochs_completed': int(model.trainer.current_epoch),
                          'early_stopping': not args.no_early_stopping, 'patience': args.early_stopping_patience,
                          'train_size': args.train_size, 'validation_size': 1 - args.train_size,
                          'batch_size': min(args.batch_size, a.n_obs), 'monitor': 'elbo_validation',
                          'actual_split_counts': {str(k): int(v) for k, v in split.value_counts().items()},
                          'convergence': 'Review history; a budget or stopping criterion is not proof of convergence'}
    return latent


def fit_harmony(a, h, args, report, covariates):
    import scanpy as sc
    import pandas as pd
    try:
        import harmonypy
    except ImportError as exc:
        raise RuntimeError('Install requirements-harmony.txt for the selected Harmony backend; no automatic scVI fallback.') from exc
    # Only the HVG working copy is residualized. Full-gene log expression and counts survive.
    if covariates:
        sc.pp.regress_out(h, keys=covariates, n_jobs=1)
    sc.pp.scale(h, max_value=10)
    dimensions = min(args.latent, h.n_obs - 1, h.n_vars - 1)
    sc.tl.pca(h, n_comps=dimensions, random_state=args.seed)
    result = harmonypy.run_harmony(h.obsm['X_pca'], h.obs, args.batch_key,
                                  random_state=args.seed,
                                  nclust=max(2, min(100, round(h.n_obs / 30))))
    latent = np.asarray(result.Z_corr).T
    if not np.array_equal(a.obs_names, h.obs_names):
        raise ValueError('Cell order changed during Harmony fitting')
    if latent.shape != (a.n_obs, dimensions) or not np.isfinite(latent).all():
        raise ValueError('Invalid Harmony coordinates')
    a.obsm['X_pca_before_harmony'] = h.obsm['X_pca'].copy()
    a.obsm['X_pca_harmony'] = latent
    pd.Series(h.var_names, name='gene').to_csv(args.outdir / 'representation_genes.csv', index=False)
    pd.DataFrame(h.varm['PCs'], index=h.var_names).to_csv(args.outdir / 'pca_loadings.csv', index_label='gene')
    pd.DataFrame({'objective': result.objective_harmony}).to_csv(args.outdir / 'harmony_objective.csv', index_label='iteration')
    report['harmony'] = {'implementation': 'harmonypy', 'device': 'cpu',
                         'requested_pcs': args.latent, 'actual_pcs': dimensions,
                         'max_iter_harmony': 10,
                         'iterations_completed': len(result.objective_harmony) - 1,
                         'cell_cycle_regressed_keys': covariates,
                         'input': 'scaled HVG log1p(CP10K); ' + ('cell-cycle regression before PCA' if covariates else 'cycle correction explicitly overridden'),
                         'convergence': 'Inspect objective history and biological conservation; completion is not proof of convergence'}
    report['warnings'].append('Harmony adjusts PCA coordinates, not counts. No scVI model or scVI-normalized expression was generated. --latent specifies PCA dimensions; scVI training options do not apply.')
    return latent


def run(args, report):
    started = time.monotonic()
    announce_runtime(args, report)
    validate_parameters(args)
    device = resolve_device(args, report)
    # Check the selected dependency before doing expensive preprocessing.
    if args.backend == 'scvi':
        try:
            import scvi
        except ImportError as exc:
            raise RuntimeError('Install requirements-scvi.txt; no automatic Harmony fallback.') from exc
    else:
        try:
            import harmonypy
        except ImportError as exc:
            raise RuntimeError('Install requirements-harmony.txt; no automatic scVI fallback.') from exc
    import scanpy as sc
    import pandas as pd
    import matplotlib.pyplot as plt
    a = load_counts(args.input)
    if min(a.shape) < 3 or np.any(np.asarray(a.layers['counts'].sum(axis=1)).ravel() <= 0):
        raise ValueError('Integration needs at least three cells/genes and positive counts in every cell')
    if args.batch_key:
        require_columns(a.obs, [args.batch_key])
        a.obs[args.batch_key] = a.obs[args.batch_key].astype('category')
    if args.backend == 'harmony' and a.obs[args.batch_key].nunique() < 2:
        raise ValueError('Harmony requires at least two verified technical batches; use scVI for a single batch')
    np.random.seed(args.seed)
    lognormalize(a)
    covariates = score_cell_cycle(a, args, report)
    if covariates:
        cc_genes = report['cell_cycle']['s_genes']['informative'] + report['cell_cycle']['g2m_genes']['informative']
        cc = a[:, cc_genes].copy()
        sc.pp.scale(cc, max_value=10)
        sc.tl.pca(cc, n_comps=min(10, cc.n_obs - 1, cc.n_vars - 1), random_state=args.seed)
        sc.pl.pca(cc, color='phase', show=False)
        plt.gcf().savefig(args.outdir / f'cell_cycle_pca_before_{args.backend}.png', dpi=150, bbox_inches='tight')
        plt.close('all')
    sc.pp.highly_variable_genes(a, n_top_genes=min(args.hvg, a.n_vars), flavor=args.hvg_flavor,
                               layer='counts' if args.hvg_flavor == 'seurat_v3' else None,
                               batch_key=args.batch_key, subset=False)
    h = a[:, a.var.highly_variable].copy()
    if min(h.shape) < 3:
        raise ValueError('Too few HVGs for representation analysis')
    report.update(n_cells=a.n_obs, n_genes=a.n_vars, n_hvg=h.n_vars, backend=args.backend,
                  actual_hvg_flavor=args.hvg_flavor, actual_batch_key=args.batch_key,
                  actual_device=device,
                  continuous_covariate_keys=covariates if args.backend == 'scvi' else [])
    if args.backend == 'scvi':
        latent = fit_scvi(a, h, args, report, covariates, device)
    else:
        latent = fit_harmony(a, h, args, report, covariates)
    if covariates:
        report['cell_cycle']['status'] = 'registered_and_trained' if args.backend == 'scvi' else 'regressed_before_pca'
        report['cell_cycle']['continuous_covariate_keys'] = covariates if args.backend == 'scvi' else []
        report['cell_cycle']['regressed_keys'] = covariates if args.backend == 'harmony' else []
        write_json(args.outdir / 'cell_cycle_coverage.json', report['cell_cycle'])
        latent_frame = pd.DataFrame(latent, columns=[f'latent_{i}' for i in range(latent.shape[1])])
        correlations = {key: latent_frame.corrwith(pd.Series(a.obs[key].to_numpy())) for key in covariates}
        pd.DataFrame(correlations).to_csv(args.outdir / 'cell_cycle_latent_correlations.csv', index_label='dimension')
    build_candidates(a, args, report)
    save_umap(a, 'leiden', args.outdir / 'umap_clusters.png')
    if args.batch_key:
        save_umap(a, args.batch_key, args.outdir / 'umap_batch.png')
    if covariates:
        save_umap(a, ['phase', 'S_score', 'G2M_score'], args.outdir / 'umap_cell_cycle.png')
    a.uns['scrna_integration'] = {'backend': args.backend, 'batch_key': args.batch_key or '',
                                 'continuous_covariate_keys': covariates if args.backend == 'scvi' else [],
                                 'cell_cycle_regressed_keys': covariates if args.backend == 'harmony' else [],
                                 'cell_cycle_status': report['cell_cycle']['status']}
    a.write_h5ad(args.outdir / 'integrated.h5ad')
    report.update(n_clusters=int(a.obs.leiden.nunique()), cluster_sizes=a.obs.leiden.value_counts().to_dict())
    report['warnings'].append('Cell-cycle adjustment does not guarantee removal of cell-cycle signal; inspect diagnostics within biological groups. UMAP and batch mixing alone do not establish biological accuracy.')
    report['runtime_choice']['integration_elapsed_seconds'] = time.monotonic() - started

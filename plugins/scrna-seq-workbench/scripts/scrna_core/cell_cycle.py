"""Explicit gene matching and cell-cycle scoring on full-gene log expression."""
from pathlib import Path
import numpy as np
from .common import read_json, sha256, write_json


def score_cell_cycle(a, args, report):
    if args.skip_cell_cycle:
        if not args.cell_cycle_override_reason or not args.cell_cycle_override_reason.strip():
            raise ValueError("Skipping cell cycle requires an explicit user override reason")
        report['cell_cycle'] = {'status': 'user_override', 'reason': args.cell_cycle_override_reason,
                                'continuous_covariate_keys': []}
        report['warnings'].append('Cell-cycle scoring/correction disabled by the recorded user override.')
        # Do not pass through stale scores as if computed by this run.
        for key in ('S_score', 'G2M_score', 'phase'):
            if key in a.obs:
                del a.obs[key]
        return []
    if args.cell_cycle_override_reason:
        raise ValueError('Override reason supplied without --skip-cell-cycle')
    if args.min_cycle_genes < 2:
        raise ValueError('--min-cycle-genes must be at least 2')
    path = args.cell_cycle_genes
    if path is None:
        if args.species != 'human':
            raise ValueError('Provide --cell-cycle-genes with documented species/identifier mapping for mouse')
        path = Path(__file__).resolve().parents[2] / 'assets/cell_cycle_human.json'
    spec = read_json(path)
    if spec.get('species') != args.species or not isinstance(spec.get('source'), str) or not spec['source'].strip():
        raise ValueError('Cell-cycle JSON requires matching species and a nonempty source')
    for key in ('s_genes', 'g2m_genes'):
        genes = spec.get(key)
        if not isinstance(genes, list) or not genes or any(not isinstance(g, str) or not g.strip() for g in genes):
            raise ValueError(f'{key} must be a nonempty list of exact gene identifiers')
        if len(genes) != len(set(genes)):
            raise ValueError(f'Duplicate cell-cycle identifiers in {key}')
    if set(spec['s_genes']) & set(spec['g2m_genes']):
        raise ValueError('S and G2M gene sets must not overlap')
    coverage = {'source': spec['source'], 'species': args.species, 'gene_set_sha256': sha256(path),
                'min_genes_per_phase': args.min_cycle_genes, 'expression': 'full-gene log1p(CP10K)',
                'status': 'checking', 'continuous_covariate_keys': ['S_score', 'G2M_score']}
    for key in ('s_genes', 'g2m_genes'):
        coverage[key] = {'matched': [g for g in spec[key] if g in a.var_names],
                         'missing': [g for g in spec[key] if g not in a.var_names]}
        matched = coverage[key]['matched']
        if matched:
            from scipy import sparse
            x = a[:, matched].X
            mean = np.asarray(x.mean(axis=0)).ravel()
            square = x.multiply(x) if sparse.issparse(x) else np.square(x)
            variance = np.asarray(square.mean(axis=0)).ravel() - mean**2
            usable = np.isfinite(variance) & (variance > 1e-12) & (mean > 0)
            coverage[key]['informative'] = [g for g, keep in zip(matched, usable) if keep]
            coverage[key]['unexpressed_or_constant'] = [g for g, keep in zip(matched, usable) if not keep]
        else:
            coverage[key]['informative'] = []
            coverage[key]['unexpressed_or_constant'] = []
    report['cell_cycle'] = coverage
    write_json(args.outdir / 'cell_cycle_coverage.json', coverage)
    if any(len(coverage[k]['informative']) < args.min_cycle_genes for k in ('s_genes', 'g2m_genes')):
        raise ValueError('Insufficient cell-cycle gene coverage; inspect cell_cycle_coverage.json and supply a mapped gene set')
    import scanpy as sc
    sc.tl.score_genes_cell_cycle(a, s_genes=coverage['s_genes']['informative'],
                                g2m_genes=coverage['g2m_genes']['informative'], use_raw=False,
                                random_state=args.seed, n_bins=min(25, max(2, a.n_vars // 10)))
    scores = a.obs[['S_score', 'G2M_score']].to_numpy()
    if not np.isfinite(scores).all() or np.any(np.ptp(scores, axis=0) <= 1e-12):
        raise ValueError('Cell-cycle scores must be finite and nonconstant; inspect coverage and expression')
    coverage['status'] = 'scored'
    coverage['phase_counts'] = {str(k): int(v) for k, v in a.obs['phase'].value_counts().items()}
    a.obs[['S_score', 'G2M_score', 'phase']].to_csv(args.outdir / 'cell_cycle_scores.csv', index_label='cell_id')
    write_json(args.outdir / 'cell_cycle_coverage.json', coverage)
    return ['S_score', 'G2M_score']

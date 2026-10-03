"""Focused descriptive expression analysis; no benchmark or quality score imports."""
from html import escape

from .common import load_counts, require_columns, write_json


def summarize(a, genes, celltype_key, donor_key, condition_key, min_cells=20):
    """One expression observation per donor/condition/cell type/gene.

    Use all genes for each cell's library size, then extract requested genes.
    Zero-cell groups stay absent, not zero expression. Low-support groups remain
    visible in the detailed table but are excluded from condition summaries.
    """
    import numpy as np
    import pandas as pd
    from scipy import sparse

    if min_cells < 1:
        raise ValueError("min_cells must be positive")
    keys = [donor_key, condition_key, celltype_key]
    if len(set(keys)) != 3:
        raise ValueError("Donor, condition and cell type must use different columns")
    require_columns(a.obs, keys)
    genes = list(dict.fromkeys(genes))
    found = [g for g in genes if g in a.var_names]
    missing = [g for g in genes if g not in a.var_names]
    if not found:
        raise ValueError("None of the requested gene identifiers occurs in var_names")
    counts = a.layers['counts']
    totals = np.asarray(counts.sum(axis=1)).ravel()
    if np.any(totals <= 0):
        raise ValueError("Zero-library cells found; inspect QC before expression analysis")
    subset = counts[:, a.var_names.get_indexer(found)]
    subset = subset.toarray() if sparse.issparse(subset) else np.asarray(subset)
    normalized = np.log1p(subset / totals[:, None] * 10000)
    metadata = a.obs[keys].astype(str).reset_index(drop=True)
    rows = []
    for (donor, condition, celltype), indices in metadata.groupby(keys, sort=True).indices.items():
        for j, gene in enumerate(found):
            rows.append(dict(donor=donor, condition=condition, cell_type=celltype,
                             gene=gene, n_cells=len(indices),
                             mean_log1p_cp10k=float(normalized[indices, j].mean()),
                             fraction_detected=float((subset[indices, j] > 0).mean()),
                             eligible=len(indices) >= min_cells))
    detail = pd.DataFrame(rows)
    eligible = detail[detail.eligible]
    overview = eligible.groupby(['condition', 'cell_type', 'gene'], as_index=False).agg(
        n_donors=('donor', 'nunique'), n_cells=('n_cells', 'sum'),
        mean_log1p_cp10k=('mean_log1p_cp10k', 'mean'),
        fraction_detected=('fraction_detected', 'mean'))
    return detail, overview, missing


def run(args, report):
    import matplotlib.pyplot as plt

    if not args.question.strip() or not args.label_source.strip():
        raise ValueError("Question and label source must be nonempty")
    a = load_counts(args.input)
    detail, overview, missing = summarize(a, args.genes, args.celltype_key,
                                          args.donor_key, args.condition_key, args.min_cells)
    detail.to_csv(args.outdir / 'donor_expression.csv', index=False)
    overview.to_csv(args.outdir / 'condition_summary.csv', index=False)
    limitations = [
        "Descriptive expression only: no significance test or causal conclusion.",
        "Condition summaries give each eligible donor equal weight; repeated donors across conditions are paired observations.",
        "A missing cell type in a donor is not treated as zero expression. Cell recovery and sorting affect observed proportions.",
        "Label provenance is user-declared; this command does not validate annotation accuracy or mark labels as reviewed."
    ]
    if args.label_status == 'exploratory':
        limitations.append("Cell labels are exploratory; conclusions depend on annotation review.")
    if missing:
        report['warnings'].append('Requested genes absent: ' + ', '.join(missing))
    if (~detail.eligible).any():
        report['warnings'].append('Low-cell groups remain in donor_expression.csv but are excluded from condition summaries.')
    if overview.empty:
        report['status'] = 'blocked'
        report['warnings'].append('No donor/cell-type group meets min_cells; no condition-level result.')
    elif (overview.n_donors < 3).any():
        report['warnings'].append('Some summaries have fewer than three donors; donor support is shown in the table.')
    payload = dict(question=args.question, label_source=args.label_source, label_status=args.label_status,
                   present_genes=[g for g in dict.fromkeys(args.genes) if g not in missing],
                   missing_genes=missing, cells=int(a.n_obs), donors=int(a.obs[args.donor_key].nunique()),
                   status=report['status'] if report['status'] == 'blocked' else 'complete',
                   limitations=limitations, warnings=report['warnings'])
    write_json(args.outdir / 'research_summary.json', payload)
    # Keep every requested gene in tables; bound only this overview figure.
    shown = detail[detail.eligible].copy()
    shown = shown[shown.gene.isin(payload['present_genes'][:12])]
    shown['label'] = shown['cell_type'] + ' | ' + shown['gene']
    categories = sorted(shown.label.unique())[:60]
    if categories:
        fig, ax = plt.subplots(figsize=(10, max(4, len(categories) * .25)))
        for condition, group in shown.groupby('condition', sort=True):
            group = group[group.label.isin(categories)]
            ax.scatter(group.mean_log1p_cp10k, [categories.index(x) for x in group.label],
                       alpha=.6, label=str(condition), s=18)
        ax.set_yticks(range(len(categories)), categories)
        ax.set_xlabel('Mean log1p(CP10K) within each donor and cell type')
        ax.set_title('Donor observations (first 12 genes / 60 rows; full results in CSV)')
        ax.legend(title='Condition'); fig.tight_layout()
        fig.savefig(args.outdir / 'donor_expression.png', dpi=140); plt.close(fig)
    html = '<!doctype html><html lang="en"><meta charset="utf-8"><title>Research results</title>'
    html += '<style>body{font:16px system-ui;margin:3em;max-width:1100px}td,th{padding:6px;text-align:left}img{max-width:100%}</style>'
    html += '<h1>' + escape(args.question) + '</h1><p>Label status: ' + escape(args.label_status)
    html += '. Source: ' + escape(args.label_source) + '</p>'
    html += '<p><a href="donor_expression.csv">Donor expression</a> | <a href="condition_summary.csv">Condition summaries</a> | <a href="report.json">Run provenance</a></p>'
    html += '<ul>' + ''.join('<li>' + escape(x) + '</li>' for x in limitations + report['warnings']) + '</ul>'
    if categories:
        html += '<img src="donor_expression.png" alt="Expression for individual donor groups">'
    html += overview.to_html(index=False, escape=True) + '</html>'
    (args.outdir / 'research_report.html').write_text(html, encoding='utf-8')
    report['dimensions'] = {'cells': int(a.n_obs), 'genes': int(a.n_vars)}

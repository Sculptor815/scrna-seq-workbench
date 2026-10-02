"""Evidence and review gates for HPA-guided annotation; not an HPA classifier."""
import numpy as np
import pandas as pd

FIELDS = ['cluster', 'cell_type', 'cell_type_detail', 'decision', 'reviewer',
          'reviewer_type', 'markers_for', 'markers_against', 'evidence_source',
          'qc_review', 'subcluster_review', 'rationale']


def marker_statistics(a, cluster_key, markers):
    clusters = a.obs[cluster_key].astype(str)
    rows = []
    for cluster in sorted(clusters.unique()):
        mask = (clusters == cluster).to_numpy()
        for candidate, genes in markers.items():
            for gene in genes:
                present = gene in a.var_names
                idx = a.var_names.get_loc(gene) if present else None
                rows.append({'cluster': cluster, 'candidate': candidate, 'gene': gene,
                    'present': present, 'n_cells': int(mask.sum()),
                    'fraction_detected': float((a.layers['counts'][mask, idx] > 0).mean()) if present else np.nan,
                    'mean_lognorm': float(a.layers['lognorm'][mask, idx].mean()) if present else np.nan})
    return pd.DataFrame(rows)


def export_packet(a, cluster_key, markers, table, outdir):
    stats = marker_statistics(a, cluster_key, markers)
    stats.to_csv(outdir/'marker_expression.csv', index=False)
    review = pd.DataFrame('', index=range(len(table)), columns=FIELDS)
    review['cluster'] = table['cluster'].astype(str).to_numpy()
    review['cell_type'] = 'Unknown'
    review['cell_type_detail'] = 'Unknown'
    review['decision'] = 'pending'
    review.to_csv(outdir/'hpa_review.template.csv', index=False)
    import matplotlib.pyplot as plt
    matrix = stats[stats.present].drop_duplicates(['cluster', 'gene']).pivot(index='cluster', columns='gene', values='mean_lognorm')
    if not matrix.empty:
        fig, ax = plt.subplots(figsize=(max(8, min(26, len(matrix.columns)*.25)), max(4, len(matrix)*.25)))
        im = ax.imshow(matrix.to_numpy(), aspect='auto', cmap='viridis', vmin=0)
        ax.set_xticks(range(len(matrix.columns)), matrix.columns, rotation=90, fontsize=6)
        ax.set_yticks(range(len(matrix)), matrix.index, fontsize=7)
        ax.set_ylabel('Cluster'); ax.set_title('Marker evidence: mean log-normalized expression')
        fig.colorbar(im, ax=ax, label='Mean log1p normalized counts')
        fig.tight_layout(); fig.savefig(outdir/'marker_heatmap.png', dpi=140); plt.close(fig)
    return stats


def validate_hpa_review(review, clusters, gene_names):
    missing = set(FIELDS) - set(review.columns)
    if missing:
        raise ValueError(f'HPA-guided review is missing fields: {sorted(missing)}')
    review = review[FIELDS].fillna('').astype(str).apply(lambda col: col.str.strip()).copy()
    if review.cluster.duplicated().any() or set(review.cluster) != set(map(str, clusters)):
        raise ValueError('HPA-guided review must cover every cluster exactly once')
    if not review.decision.isin(['accept', 'unresolved', 'mixed']).all():
        raise ValueError('Pending review cannot create final labels; use accept, unresolved or mixed')
    if not review.reviewer_type.eq('human').all():
        raise ValueError('HPA-style manual finalization requires a real human review; agent proposals remain provisional')
    required = ['reviewer', 'cell_type', 'cell_type_detail', 'evidence_source', 'qc_review', 'subcluster_review', 'rationale', 'markers_against']
    if (review[required] == '').any().any():
        raise ValueError('Review needs identity, two label levels, sources, QC/subcluster assessment and rationale')
    genes = set(gene_names)
    for row in review.itertuples():
        if row.decision == 'accept':
            supporting = set(g.strip() for g in row.markers_for.split(';') if g.strip())
            if len(supporting) < 2 or not supporting <= genes or row.cell_type.lower() in {'unknown', 'mixed', 'doublet'}:
                raise ValueError('Accepted labels require at least two available supporting markers and a resolved main type')
            if row.cell_type_detail.lower() in {'', 'unknown', 'mixed', 'doublet'}:
                raise ValueError('Use the supported main type as the detailed label when finer resolution is unavailable')
        elif row.cell_type != 'Unknown' or row.cell_type_detail != 'Unknown':
            raise ValueError('Unresolved/mixed clusters must remain Unknown at both levels')
    return review

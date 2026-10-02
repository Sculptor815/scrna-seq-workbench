"""Generate HPA-guided review packets from existing frozen seed-0 benchmark runs.

No training, QC change, label approval, or HPA accuracy claim is performed.
Reference labels are joined only after all marker proposals and packets are made.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import anndata as ad
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'plugins/scrna-seq-workbench/scripts'))
from scrna_core.annotate import propose
from scrna_core.annotation_policy import export_packet


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark-work',type=Path,required=True)
    parser.add_argument('--outdir',type=Path,required=True)
    args=parser.parse_args()
    args.outdir.mkdir(parents=True,exist_ok=False)
    records=[]
    for name in ['kang','haber','paul','zeisel','baron']:
        d=args.benchmark_work/name
        source=d/'scvi_0_annotation/annotated.h5ad'
        a=ad.read_h5ad(source)
        assert not ({'reference_fine','reference_broad','fine','broad','truth_cell_type'} & set(a.obs.columns))
        panel=json.loads((d/'panel.json').read_text(encoding='utf-8'))
        out=args.outdir/name; out.mkdir()
        table,evidence=propose(a,'leiden',panel['markers'])
        export_packet(a,'leiden',panel['markers'],table,out)
        table.to_csv(out/'annotation_proposals.csv',index=False)
        evidence.to_csv(out/'annotation_evidence.csv',index=False)
        (out/'panel.json').write_text(json.dumps(panel,indent=2),encoding='utf-8')
        predicted=a.obs.leiden.astype(str).map(table.set_index('cluster').cell_type_proposal)
        assert predicted.astype(str).tolist()==a.obs.cell_type_proposal.astype(str).tolist(), 'Baseline proposals changed unexpectedly'
        # Evaluation boundary: author/reference labels enter only here.
        reference=pd.read_csv(d/'reference_labels.csv',index_col=0).loc[a.obs_names]
        xy=a.obsm['X_umap']
        frame=pd.DataFrame({'cell_id':a.obs_names,'umap_1':xy[:,0],'umap_2':xy[:,1],
            'reference_fine':reference.fine.to_numpy(),'reference_broad':reference.broad.to_numpy(),
            'cluster':a.obs.leiden.astype(str).to_numpy(),'proposal':predicted.astype(str).to_numpy()})
        frame.to_csv(out/'embedding.csv',index=False,float_format='%.7g')
        record={'dataset':name,'cells':a.n_obs,'backend':'scvi','seed':0,
            'embedding_origin':'frozen baseline-1; unchanged coordinates',
            'annotation_origin':'marker proposals; HPA-guided evidence added, human review pending',
            'hpa_exact_replication':False,'human_review_complete':False,
            'input_sha256':sha(source),'panel_sha256':sha(d/'panel.json'),
            'reference_labels_sha256':sha(d/'reference_labels.csv'),
            'reference_labels_used_for_proposals':False,
            'species_scope':'human HPA-inspired procedure' if panel['species']=='human' else 'mouse adaptation; not HPA reference annotation'}
        (out/'provenance.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
        records.append(record)
        print(name,a.n_obs,'cells; review packet exported; original predictions verified',flush=True)
        del a
    (args.outdir/'status.json').write_text(json.dumps(records,indent=2),encoding='utf-8')


if __name__=='__main__': main()

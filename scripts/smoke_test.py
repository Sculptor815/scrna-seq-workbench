"""Opt-in full execution check on artificial counts; not a scientific benchmark."""
import argparse
from pathlib import Path
import subprocess
import sys
import json
import anndata as ad
import pandas as pd

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--outdir',type=Path,required=True)
    ap.add_argument('--backend',choices=['scvi'],default='scvi'); args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]; runner=root/'plugins/scrna-seq-workbench/scripts/scrna.py'
    out=args.outdir.resolve(); out.mkdir(parents=True,exist_ok=False)
    log=out/'commands.log'
    def run(script,*argv):
        cmd=[sys.executable,str(script),*map(str,argv)]
        with log.open('a',encoding='utf-8') as f:
            f.write('\n'+repr(cmd)+'\n'); f.flush()
            result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
        if result.returncode: raise RuntimeError(f'Stage failed ({result.returncode}); see {log}')
    run(root/'examples/make_synthetic.py','--outdir',out/'fixture')
    f=out/'fixture'
    run(runner,'report','--metrics',f/'metrics.json','--source',f/'vendor.txt','--outdir',out/'01-report')
    run(runner,'qc','--input',f/'raw.h5ad','--config',f/'qc.json','--species','human','--outdir',out/'02-qc')
    run(runner,'integrate','--input',out/'02-qc/filtered.h5ad','--backend',args.backend,'--batch-key','batch',
        '--species','human','--hvg',80,'--max-epochs',2,'--no-early-stopping','--latent',5,
        '--neighbors',15,'--neighbors-grid',15,'--resolutions-grid',1,'--outdir',out/'03-integrate')
    integrated=ad.read_h5ad(out/'03-integrate/integrated.h5ad')
    original=ad.read_h5ad(out/'02-qc/filtered.h5ad')
    assert list(integrated.var_names)==list(original.var_names)
    assert (integrated.layers['counts']!=original.layers['counts']).nnz==0
    run(runner,'annotate','--input',out/'03-integrate/integrated.h5ad','--panel',f/'panel.json',
        '--species','human','--tissue','blood','--outdir',out/'04-proposals')
    # This artificial fixture has a known label; this is NOT permission to
    # manufacture human approval or benchmark truth on real study data.
    rows=[]
    for cluster,g in integrated.obs.groupby('leiden',observed=True):
        rows.append({'cluster':str(cluster),'cell_type':g.truth_cell_type.mode().iloc[0],
                     'reviewer':'synthetic-test-oracle','rationale':'Artificial data truth; majority per cluster, execution check only'})
    pd.DataFrame(rows).to_csv(out/'fixture_review.csv',index=False)
    run(runner,'annotate','--input',out/'03-integrate/integrated.h5ad','--panel',f/'panel.json','--species','human',
        '--tissue','blood','--annotation-policy','legacy','--reviewed-labels',out/'fixture_review.csv','--outdir',out/'04-reviewed')
    # Exercise the DE fitting API independently of a two-epoch model's accuracy.
    # Use an explicitly named synthetic truth column, never overwrite its proposals.
    run(runner,'de','--input',out/'04-reviewed/annotated.h5ad','--case','stimulated','--control','control',
        '--celltype-key','truth_cell_type','--labels-reviewed',
        '--design','paired','--outdir',out/'05-de')
    stages={d.name:json.loads((d/'report.json').read_text(encoding='utf-8'))['status'] for d in out.iterdir() if d.is_dir() and (d/'report.json').exists()}
    summary={'kind':'synthetic execution smoke, not biological validation','backend':args.backend,
             'de_labels':'synthetic truth; not model predictions','stages':stages}
    (out/'smoke_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8'); print(json.dumps(summary,indent=2))

if __name__=='__main__': main()

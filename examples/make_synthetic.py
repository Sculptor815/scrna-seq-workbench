"""Generate artificial data for execution checks, never biological claims."""
import argparse
from pathlib import Path
import json
import numpy as np
import pandas as pd
import anndata as ad
from scipy import sparse

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--outdir',type=Path,required=True); args=ap.parse_args()
    args.outdir.mkdir(parents=True,exist_ok=False)
    rng=np.random.default_rng(11)
    rows=[]; matrices=[]
    # Four true synthetic pairs, two cell types. This is simulated truth only.
    for d in range(4):
        for condition in ('control','stimulated'):
            for ct in ('T cells','B cells'):
                means=np.full(100,3.0)*rng.uniform(0.7,1.3)
                if ct=='T cells': means[:3]+=12
                if ct=='B cells': means[3:6]+=12
                if condition=='stimulated': means[10:18]*=3
                x=rng.negative_binomial(10,10/(10+means),size=(25,100))
                matrices.append(x)
                rows.extend([{'sample_id':f'd{d}_{condition}','capture_id':f'd{d}_{condition}',
                              'donor_id':f'd{d}','condition':condition,'truth_cell_type':ct,'batch':f'b{d%2}'}]*25)
    a=ad.AnnData(sparse.csr_matrix(np.vstack(matrices)),obs=pd.DataFrame(rows))
    a.obs_names=[f'synthetic_c{i}' for i in range(a.n_obs)]
    a.var_names=['CD3D','CD3E','TRAC','MS4A1','CD79A','CD79B','MT-CO1']+[f'G{i}' for i in range(93)]
    a.layers['counts']=a.X.copy()
    a.uns['synthetic_only']=True
    a.write_h5ad(args.outdir/'raw.h5ad')
    a.obs.rename_axis('cell_id').to_csv(args.outdir/'cells.csv')
    (args.outdir/'vendor.txt').write_text('Synthetic fixture. Estimated cells = 400. Not an experimental sample.\n')
    (args.outdir/'metrics.json').write_text(json.dumps({'sample_id':'synthetic_cohort','platform':'synthetic','species':'human','report_version':'fixture-1',
        'metrics':{'estimated_cells':{'value':400,'unit':'cells','evidence':'vendor.txt line 1: Estimated cells = 400','verified':True}}},indent=2))
    (args.outdir/'qc.json').write_text(json.dumps({'defaults':{'min_genes':10},'min_cells_per_gene':3}))
    (args.outdir/'panel.json').write_text(json.dumps({'species':'human','tissue':'blood','source':'Synthetic fixture, not a validated reference',
        'markers':{'T cells':['CD3D','CD3E','TRAC'],'B cells':['MS4A1','CD79A','CD79B']}}))
    print(args.outdir/'raw.h5ad')

if __name__=='__main__': main()

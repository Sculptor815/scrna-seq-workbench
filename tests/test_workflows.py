from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import gzip

import anndata as ad
import numpy as np
import pandas as pd
from scipy import sparse

ROOT=Path(__file__).resolve().parents[1]
PLUGIN=ROOT/'plugins'/'scrna-seq-workbench'
sys.path.insert(0,str(PLUGIN/'scripts'))
from scrna_core.common import validate_counts,stage_run,load_counts,source_hashes
from scrna_core.qc import filter_cells,validate_gene_sets
from scrna_core.annotate import propose,apply_review
from scrna_core.de import pseudobulk


def fixture():
    rng=np.random.default_rng(7)
    x=rng.poisson(2,size=(80,60)).astype(float)
    x[:40,:3]+=8; x[40:,3:6]+=8
    a=ad.AnnData(sparse.csr_matrix(x))
    a.obs_names=[f'c{i}' for i in range(80)]
    a.var_names=['CD3D','CD3E','TRAC','MS4A1','CD79A','CD79B','MT-CO1']+[f'G{i}' for i in range(53)]
    a.obs['sample_id']=['s1']*40+['s2']*40
    a.obs['leiden']=pd.Categorical(['0']*40+['1']*40)
    a.layers['counts']=a.X.copy()
    a.layers['lognorm']=np.log1p(x)
    return a


class Invariants(unittest.TestCase):
    def test_mitochondrial_suggestion_has_only_an_upper_bound(self):
        obs=pd.DataFrame({'sample_id':['s1']*5,'total_counts':[10,20,30,40,50],
                          'n_genes_by_counts':[3,4,5,6,7],'pct_counts_mt':[10,20,30,40,50],
                          'pct_counts_hb':[0]*5})
        _,_,suggestions=filter_cells(obs,'sample_id',{'defaults':{'min_genes':0}})
        self.assertIsNone(suggestions['s1']['pct_counts_mt']['suggested_lower'])
        self.assertGreater(suggestions['s1']['pct_counts_mt']['suggested_upper'],30)
        self.assertIsNotNone(suggestions['s1']['total_counts']['suggested_lower'])

    def test_10x_duplicate_symbols_are_not_silently_renamed(self):
        from scipy.io import mmwrite
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)
            with gzip.open(folder/'matrix.mtx.gz','wb') as f:
                mmwrite(f,sparse.coo_matrix(np.ones((3,3))))
            with gzip.open(folder/'features.tsv.gz','wt') as f:
                f.write('id1\tDUP\tGene Expression\nid2\tDUP\tGene Expression\nid3\tOTHER\tGene Expression\n')
            with gzip.open(folder/'barcodes.tsv.gz','wt') as f:
                f.write('c1\nc2\nc3\n')
            with self.assertRaisesRegex(ValueError,'identifiers must be unique'):
                load_counts(folder,allow_x=True)

    def test_absent_hb_cannot_pass_enabled_filter(self):
        with self.assertRaises(ValueError):
            validate_gene_sets({'mt':1,'hb':0,'ribo':1},{'defaults':{'max_pct_hb':5}},['s1'],{'warnings':[]})

    def test_constant_metrics_have_no_mad_cutoff(self):
        obs=pd.DataFrame({'sample_id':['s1']*4,'total_counts':[20]*4,
                          'n_genes_by_counts':[4]*4,'pct_counts_mt':[0]*4,'pct_counts_hb':[0]*4})
        _,_,suggestions=filter_cells(obs,'sample_id',{'defaults':{'min_genes':0}})
        self.assertEqual(suggestions['s1']['pct_counts_mt']['status'],'degenerate_mad')
        self.assertIsNone(suggestions['s1']['pct_counts_mt']['suggested_upper'])

    def test_source_manifest_includes_cli_and_dependencies(self):
        self.assertIn('scripts/scrna.py',source_hashes())
        self.assertIn('requirements.txt',source_hashes())

    def test_output_cannot_contaminate_input_directory(self):
        with tempfile.TemporaryDirectory() as t, self.assertRaises(ValueError):
            with stage_run('test',Path(t)/'results',{},[t]): pass

    def test_counts_reject_invalid_dense_and_sparse(self):
        for val in [-1,float('inf'),float('nan'),100000.4]:
            for x in [np.array([[val]]),sparse.csr_matrix([[val]])]:
                with self.subTest(val=val,sparse=sparse.issparse(x)), self.assertRaises(ValueError):
                    validate_counts(x)
        validate_counts(sparse.csr_matrix([[0,2],[3,0]]))

    def test_sample_quantiles_do_not_pool(self):
        obs=pd.DataFrame({'sample_id':['A']*4+['B']*4,'total_counts':[10,20,30,40,1000,2000,3000,4000],
                          'n_genes_by_counts':[3]*8,'pct_counts_mt':[0]*8,'pct_counts_hb':[0]*8})
        reasons,applied,_=filter_cells(obs,'sample_id',{'defaults':{'min_genes':0,'max_counts_quantile':0.5}})
        self.assertEqual(reasons.eq('').groupby(obs.sample_id).sum().to_dict(),{'A':2,'B':2})
        self.assertEqual(applied['A']['max_counts'],25)
        self.assertEqual(applied['B']['max_counts'],2500)

    def test_metadata_typo_is_error(self):
        with self.assertRaises(ValueError):
            filter_cells(pd.DataFrame({'sample':['a']}),'sample_id',{})

    def test_proposal_requires_competitor(self):
        a=fixture()
        table,_=propose(a,'leiden',{'T':['CD3D','CD3E','TRAC'],'absent':['missing1','missing2']})
        self.assertTrue(table.cell_type_proposal.eq('Unknown').all())
        self.assertTrue(table.margin.isna().all())

    def test_annotation_and_review_preserve_clusters(self):
        a=fixture(); before=a.obs.leiden.copy()
        table,_=propose(a,'leiden',{'T':['CD3D','CD3E','TRAC'],'B':['MS4A1','CD79A','CD79B']})
        self.assertEqual(table.cell_type_proposal.tolist(),['T','B'])
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'review.csv'
            pd.DataFrame({'cluster':['0','1'],'cell_type':['T','B'],'reviewer':['fixture']*2,'rationale':['synthetic truth']*2}).to_csv(p,index=False)
            apply_review(a,p,'leiden')
        self.assertTrue(a.uns['cell_type_reviewed']); pd.testing.assert_series_equal(before,a.obs.leiden)

    def test_one_cluster_abstains(self):
        a=fixture(); a.obs.leiden=pd.Categorical(['0']*a.n_obs)
        table,_=propose(a,'leiden',{'T':['CD3D','CD3E'],'B':['MS4A1','CD79A']})
        self.assertEqual(table.cell_type_proposal.tolist(),['Unknown'])

    def test_constant_markers_do_not_pad_coverage(self):
        a=fixture(); a.layers['lognorm'][:,6:]=1
        constant=list(a.var_names[6:])
        table,evidence=propose(a,'leiden',{'T':['CD3D','CD3E']+constant,'B':['MS4A1','CD79A']+constant})
        self.assertTrue(table.cell_type_proposal.eq('Unknown').all())
        self.assertTrue(evidence.marker_overlap.eq(1).all())
        self.assertTrue(evidence.informative_overlap.lt(0.5).all())

    def test_whitespace_unknown_is_excluded(self):
        a=fixture(); a.obs['cell_type']=' Unknown '; a.obs['donor_id']='d1'
        a.obs['condition']=['A']*40+['B']*40
        result,excluded=pseudobulk(a,'cell_type','donor_id','condition','A','B')
        self.assertEqual(result,{})
        self.assertEqual(excluded[0]['reason'],'unresolved_or_doublet_label')

    def test_pairing_only_requested_contrast(self):
        obs=[]
        for donor,conds in [('d1',['A','B']),('d2',['A','C']),('d3',['B','C'])]:
            for condition in conds: obs.extend([{'donor_id':donor,'condition':condition,'cell_type':'T'}]*20)
        a=ad.AnnData(np.ones((120,4)),obs=pd.DataFrame(obs,index=[f'c{i}' for i in range(120)])); a.layers['counts']=a.X.copy()
        results,excluded=pseudobulk(a,'cell_type','donor_id','condition','A','B')
        self.assertEqual(results['T']['status'],'disabled'); self.assertEqual(results['T']['n_pairs'],1)

    def test_real_pair_aggregation_and_unpaired_rejection(self):
        obs=[]
        for donor in ['d1','d2','d3']:
            for condition in ['A','B']: obs.extend([{'donor_id':donor,'condition':condition,'cell_type':'T'}]*20)
        a=ad.AnnData(np.ones((120,4)),obs=pd.DataFrame(obs,index=[f'c{i}' for i in range(120)])); a.layers['counts']=a.X.copy()
        results,_=pseudobulk(a,'cell_type','donor_id','condition','A','B')
        self.assertEqual(results['T']['counts'].shape,(6,4)); self.assertTrue((results['T']['counts']==20).all().all())
        with self.assertRaises(ValueError): pseudobulk(a,'cell_type','donor_id','condition','A','B','unpaired')

    def test_failed_run_records_failure_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'run'
            with self.assertRaises(ValueError):
                with stage_run('test',out,{},[]): raise ValueError('deliberate failure')
            self.assertEqual(json.loads((out/'report.json').read_text())['status'],'failed')
            with self.assertRaises(ValueError):
                with stage_run('test',out,{},[]): pass

    def test_metadata_alignment_rejects_missing_cells(self):
        with tempfile.TemporaryDirectory() as t:
            a=fixture(); p=Path(t)/'a.h5ad'; a.write_h5ad(p)
            m=Path(t)/'metadata.csv'; m.write_text('cell_id,donor_id\nc0,d1\n')
            with self.assertRaises(ValueError): load_counts(p,m)


class CLI(unittest.TestCase):
    def test_report_and_qc_cli(self):
        with tempfile.TemporaryDirectory() as t:
            t=Path(t)
            source=t/'vendor.txt'; source.write_text('Synthetic report: estimated cells = 80')
            metrics=t/'metrics.json'; metrics.write_text(json.dumps({'sample_id':'synthetic','platform':'synthetic',
                'report_version':'fixture','species':'human','metrics':{'estimated_cells':{'value':80,'unit':'cells',
                    'evidence':'line 1: estimated cells = 80','verified':True}}}))
            proc=subprocess.run([sys.executable,str(PLUGIN/'scripts/scrna.py'),'report','--metrics',str(metrics),
                                 '--source',str(source),'--outdir',str(t/'report')],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            a=fixture(); inp=t/'raw.h5ad'; a.write_h5ad(inp)
            cfg=t/'qc.json'; cfg.write_text(json.dumps({'defaults':{'min_genes':1},'min_cells_per_gene':1}))
            proc=subprocess.run([sys.executable,str(PLUGIN/'scripts/scrna.py'),'qc','--input',str(inp),
                                 '--config',str(cfg),'--species','human','--outdir',str(t/'qc')],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            b=ad.read_h5ad(t/'qc/filtered.h5ad')
            self.assertEqual((a.layers['counts']!=b.layers['counts']).nnz,0)
            rep=json.loads((t/'qc/report.json').read_text())
            self.assertEqual(rep['n_cells_out'],b.n_obs); self.assertIn('filtered.h5ad',rep['artifacts'])


if __name__=='__main__': unittest.main()

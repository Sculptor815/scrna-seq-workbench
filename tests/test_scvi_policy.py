"""Numerical count/covariate contracts plus a real CPU save/reload integration."""
from pathlib import Path
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest

import anndata as ad
import numpy as np
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/scrna-seq-workbench'
sys.path.insert(0, str(PLUGIN / 'scripts'))
import scrna
from scrna_core.common import lognormalize, stage_run
from scrna_core.cell_cycle import score_cell_cycle
from scrna_core.integrate import run


def fixture():
    spec = json.loads((PLUGIN / 'assets/cell_cycle_human.json').read_text())
    genes = spec['s_genes'] + spec['g2m_genes'] + [f'G{i}' for i in range(100)]
    rng = np.random.default_rng(41)
    means = rng.uniform(0.5, 6, len(genes))
    x = rng.negative_binomial(3, 3/(3+means), size=(120, len(genes)))
    x[:40, :len(spec['s_genes'])] += rng.poisson(3, size=(40, len(spec['s_genes'])))
    start = len(spec['s_genes'])
    x[40:80, start:start+len(spec['g2m_genes'])] += 3
    a = ad.AnnData(sparse.csr_matrix(x))
    a.obs_names = [f'cell_{i}' for i in range(a.n_obs)]
    a.var_names = genes
    a.obs['batch'] = ['one', 'two'] * 60
    a.layers['counts'] = a.X.copy()
    return a


def args_for(folder, *extra):
    return scrna.parser().parse_args(['integrate', '--input', str(folder/'input.h5ad'),
                                     '--outdir', str(folder/'result'), '--species', 'human', *extra])


class CycleContracts(unittest.TestCase):
    def test_pca_is_rejected_and_species_is_required(self):
        with contextlib.redirect_stderr(io.StringIO()):
            for tail in (['--species', 'human', '--backend', 'pca'], []):
                with self.assertRaises(SystemExit):
                    scrna.parser().parse_args(['integrate', '--input', 'x', '--outdir', 'y', *tail])

    def test_scores_use_full_counts_not_inherited_raw_and_preserve_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); args = args_for(folder); args.outdir.mkdir()
            a = fixture(); before = a.layers['counts'].copy()
            a.raw = ad.AnnData(np.zeros(a.shape), obs=a.obs.copy(), var=a.var.copy())
            lognormalize(a)
            report = {'warnings': []}
            self.assertEqual(score_cell_cycle(a, args, report), ['S_score', 'G2M_score'])
            self.assertEqual((before != a.layers['counts']).nnz, 0)
            self.assertTrue(np.isfinite(a.obs[['S_score', 'G2M_score']]).all().all())
            self.assertGreater(a.obs['S_score'].iloc[:40].mean(), a.obs['S_score'].iloc[80:].mean())
            self.assertGreater(a.obs['G2M_score'].iloc[40:80].mean(), a.obs['G2M_score'].iloc[80:].mean())
            self.assertEqual(len(report['cell_cycle']['s_genes']['missing']), 0)

    def test_missing_genes_and_wrong_species_do_not_silently_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); args = args_for(folder); args.outdir.mkdir()
            a = fixture(); a.var_names = [f'id{i}' for i in range(a.n_vars)]; lognormalize(a)
            with self.assertRaisesRegex(ValueError, 'Insufficient'):
                score_cell_cycle(a, args, {'warnings': []})
            args.species = 'mouse'
            with self.assertRaisesRegex(ValueError, 'documented'):
                score_cell_cycle(a, args, {'warnings': []})
            args.cell_cycle_genes = PLUGIN / 'assets/cell_cycle_human.json'
            with self.assertRaisesRegex(ValueError, 'matching species'):
                score_cell_cycle(a, args, {'warnings': []})

    def test_documented_mouse_identifier_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); args = args_for(folder); args.outdir.mkdir()
            a = fixture(); original = list(a.var_names)
            spec = json.loads((PLUGIN / 'assets/cell_cycle_human.json').read_text())
            mapping = dict(zip(original, [f'mapped{i}' for i in range(a.n_vars)]))
            a.var_names = [mapping[g] for g in original]
            for key in ('s_genes', 'g2m_genes'):
                spec[key] = [mapping[g] for g in spec[key]]
            spec.update(species='mouse', source='Synthetic exact-ID mapping for contract testing only')
            path = folder/'mapping.json'; path.write_text(json.dumps(spec))
            args.species = 'mouse'; args.cell_cycle_genes = path
            lognormalize(a)
            self.assertEqual(score_cell_cycle(a, args, {'warnings': []}), ['S_score', 'G2M_score'])

    def test_present_but_unexpressed_cycle_genes_do_not_count_as_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); args = args_for(folder); args.outdir.mkdir()
            a = fixture(); spec = json.loads((PLUGIN/'assets/cell_cycle_human.json').read_text())
            x = a.layers['counts'].toarray(); x[:, :len(spec['s_genes'])] = 0
            a.layers['counts'] = sparse.csr_matrix(x); lognormalize(a)
            report = {'warnings': []}
            with self.assertRaisesRegex(ValueError, 'Insufficient'):
                score_cell_cycle(a, args, report)
            self.assertEqual(report['cell_cycle']['s_genes']['informative'], [])

    def test_override_requires_reason_and_removes_stale_scores(self):
        with tempfile.TemporaryDirectory() as temp:
            args = args_for(Path(temp), '--skip-cell-cycle'); a = fixture()
            with self.assertRaisesRegex(ValueError, 'override reason'):
                score_cell_cycle(a, args, {'warnings': []})
            args.cell_cycle_override_reason = 'Synthetic test of the explicit user-override path'
            a.obs['S_score'] = 1; a.obs['G2M_score'] = 1; a.obs['phase'] = 'S'
            report = {'warnings': []}
            self.assertEqual(score_cell_cycle(a, args, report), [])
            self.assertNotIn('S_score', a.obs)
            self.assertEqual(report['cell_cycle']['status'], 'user_override')


@unittest.skipUnless(importlib.util.find_spec('scvi'), 'Install requirements-scvi.txt for real CPU training tests')
class RealSCVI(unittest.TestCase):
    def test_with_and_without_batch_save_reload_counts_covariates_and_candidates(self):
        import scvi
        import torch
        torch.set_num_threads(2)
        for with_batch in (False, True):
            with self.subTest(with_batch=with_batch), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                a = fixture(); a.write_h5ad(folder/'input.h5ad')
                extra = ['--batch-key', 'batch'] if with_batch else []
                args = args_for(folder, '--device', 'cpu', '--max-epochs', '2', '--latent', '4', '--hvg', '80',
                                '--batch-size', '32', '--neighbors', '10', '--neighbors-grid', '10', '15',
                                '--resolutions-grid', '0.5', '1', *extra)
                with stage_run('integrate', args.outdir, vars(args), [args.input]) as report:
                    run(args, report)
                b = ad.read_h5ad(args.outdir/'integrated.h5ad')
                self.assertEqual((a.layers['counts'] != b.layers['counts']).nnz, 0)
                self.assertEqual(list(a.var_names), list(b.var_names))
                self.assertEqual(list(a.obs_names), list(b.obs_names))
                self.assertEqual(b.obsm['X_scvi'].shape, (120, 4))
                self.assertNotIn('X_pca_baseline', b.obsm)
                self.assertEqual(report['continuous_covariate_keys'], ['S_score', 'G2M_score'])
                self.assertEqual(report['actual_batch_key'], 'batch' if with_batch else None)
                self.assertEqual(len(report['parameter_candidates']), 4)
                self.assertEqual(report['parameter_selection']['status'], 'pending_review')
                self.assertTrue(np.array_equal(b.obsm['X_umap'], b.obsm['X_umap_scvi_n10']))
                self.assertEqual(b.uns['neighbors']['params']['use_rep'], 'X_scvi')
                self.assertEqual(report['status'], 'complete')
                self.assertEqual(report['training']['epochs_completed'], 2)
                self.assertEqual(sum(report['training']['actual_split_counts'].values()), 120)
                self.assertNotIn('unassigned', report['training']['actual_split_counts'])
                self.assertEqual(report['training']['actual_split_counts']['validation'], 12)
                saved = scvi.model.SCVI.load(str(args.outdir/'model'), accelerator='cpu')
                np.testing.assert_allclose(saved.get_latent_representation(), b.obsm['X_scvi'], rtol=1e-5, atol=1e-5)
                np.testing.assert_allclose(saved.adata.obsm['_scvi_extra_continuous_covs'],
                                           b.obs[['S_score', 'G2M_score']].to_numpy())
                self.assertTrue((args.outdir/'umap_cell_cycle.png').exists())
                self.assertTrue((args.outdir/'cell_cycle_pca_before_scvi.png').exists())
                self.assertTrue(report['knowledge_base']['sha256'])


if __name__ == '__main__':
    unittest.main()

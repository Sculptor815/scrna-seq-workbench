"""Backend choice, hardware dispatch and real Harmony count/graph contracts."""
import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import anndata as ad
import numpy as np
import scanpy as sc

from test_scvi_policy import args_for, fixture
from scrna_core.common import lognormalize, stage_run
from scrna_core.integrate import run, validate_parameters
from scrna_core.runtime import announce_runtime, resolve_device


class RuntimeChoices(unittest.TestCase):
    def test_default_is_scvi_auto_and_notice_is_visible(self):
        args = args_for(Path('unused'))
        self.assertEqual((args.backend, args.device), ('scvi', 'auto'))
        report = {'warnings': []}
        stream = io.StringIO()
        with contextlib.redirect_stderr(stream):
            announce_runtime(args, report)
        self.assertIn('more than 1 hour', stream.getvalue())
        self.assertIn('CPU scVI', stream.getvalue())
        self.assertIn('Harmony', stream.getvalue())
        self.assertIsNone(report['runtime_choice']['decision_reason'])
        self.assertFalse(report['runtime_choice']['automatic_backend_fallback'])

    def test_cuda_auto_and_explicit_cpu_never_change_backend(self):
        for available, requested, expected in [(True, 'auto', 'gpu'), (False, 'auto', 'cpu'), (True, 'cpu', 'cpu')]:
            with self.subTest(available=available, requested=requested):
                args = args_for(Path('unused'), '--device', requested)
                report = {'runtime_choice': {}, 'warnings': []}
                torch = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: available))
                with patch.dict(sys.modules, {'torch': torch}):
                    self.assertEqual(resolve_device(args, report), expected)
                self.assertEqual(args.backend, 'scvi')

    def test_explicit_unavailable_gpu_fails_without_fallback(self):
        args = args_for(Path('unused'), '--device', 'gpu')
        torch = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False))
        with patch.dict(sys.modules, {'torch': torch}), self.assertRaisesRegex(ValueError, 'unavailable'):
            resolve_device(args, {'runtime_choice': {}, 'warnings': []})

    def test_harmony_does_not_need_torch_and_rejects_gpu(self):
        args = args_for(Path('unused'), '--backend', 'harmony', '--batch-key', 'batch')
        with patch.dict(sys.modules, {'torch': None, 'scvi': None}):
            self.assertEqual(resolve_device(args, {'runtime_choice': {}, 'warnings': []}), 'cpu')
        args.device = 'gpu'
        with self.assertRaisesRegex(ValueError, 'Harmony uses CPU'):
            resolve_device(args, {'runtime_choice': {}, 'warnings': []})

    def test_missing_backend_dependencies_do_not_switch_methods(self):
        for backend, module, requirement in [('scvi', 'torch', 'requirements-scvi'), ('harmony', 'harmonypy', 'requirements-harmony')]:
            with self.subTest(backend=backend), tempfile.TemporaryDirectory() as temp:
                args = args_for(Path(temp), '--backend', backend, '--batch-key', 'batch')
                with patch.dict(sys.modules, {module: None}), self.assertRaisesRegex(RuntimeError, requirement):
                    run(args, {'warnings': []})
                self.assertEqual(args.backend, backend)
                self.assertFalse((args.outdir / 'integrated.h5ad').exists())

    def test_harmony_requires_batch_key(self):
        args = args_for(Path('unused'), '--backend', 'harmony')
        with self.assertRaisesRegex(ValueError, 'verified technical batch'):
            validate_parameters(args)


@unittest.skipUnless(importlib.util.find_spec('harmonypy'), 'Install requirements-harmony.txt for real Harmony tests')
class RealHarmony(unittest.TestCase):
    def test_counts_expression_cycles_and_selected_representation(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            a = fixture(); a.write_h5ad(folder / 'input.h5ad')
            expected = a.copy(); lognormalize(expected)
            args = args_for(folder, '--backend', 'harmony', '--batch-key', 'batch',
                            '--backend-reason', 'Explicit synthetic test choice',
                            '--hvg', '80', '--latent', '4', '--neighbors', '10',
                            '--neighbors-grid', '10', '15', '--resolutions-grid', '0.5', '1')
            with patch('scanpy.pp.regress_out', wraps=sc.pp.regress_out) as regress:
                with stage_run('integrate', args.outdir, vars(args), [args.input]) as report:
                    run(args, report)
                self.assertEqual(regress.call_args.kwargs['keys'], ['S_score', 'G2M_score'])
            b = ad.read_h5ad(args.outdir / 'integrated.h5ad')
            self.assertEqual((a.layers['counts'] != b.layers['counts']).nnz, 0)
            self.assertEqual((expected.X != b.X).nnz, 0)
            self.assertEqual(list(a.var_names), list(b.var_names))
            self.assertEqual(list(a.obs_names), list(b.obs_names))
            self.assertEqual(b.obsm['X_pca_harmony'].shape, (120, 4))
            self.assertTrue(np.isfinite(b.obsm['X_pca_harmony']).all())
            self.assertNotIn('X_scvi', b.obsm)
            self.assertFalse((args.outdir / 'model').exists())
            self.assertNotIn('training', report)
            self.assertEqual(report['backend'], 'harmony')
            self.assertEqual(report['continuous_covariate_keys'], [])
            self.assertEqual(report['cell_cycle']['status'], 'regressed_before_pca')
            self.assertEqual(b.uns['neighbors']['params']['use_rep'], 'X_pca_harmony')
            self.assertEqual(len(report['parameter_candidates']), 4)
            np.testing.assert_array_equal(b.obsm['X_umap'], b.obsm['X_umap_harmony_n10'])
            self.assertEqual(report['parameter_selection']['status'], 'pending_review')
            self.assertEqual(report['runtime_choice']['actual_device'], 'cpu')
            self.assertGreater(report['runtime_choice']['integration_elapsed_seconds'], 0)
            for filename in ['umap_cell_cycle.png', 'cell_cycle_pca_before_harmony.png', 'harmony_objective.csv']:
                self.assertTrue((args.outdir / filename).exists())

    def test_single_missing_or_null_batch_fails_before_fitting(self):
        for kind in ('single', 'missing', 'null'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp); a = fixture()
                if kind == 'single':
                    a.obs['batch'] = 'one'
                elif kind == 'missing':
                    del a.obs['batch']
                else:
                    a.obs.loc[a.obs_names[0], 'batch'] = None
                a.write_h5ad(folder / 'input.h5ad')
                args = args_for(folder, '--backend', 'harmony', '--batch-key', 'batch')
                with patch('scrna_core.integrate.fit_harmony') as fit:
                    with self.assertRaises(ValueError):
                        run(args, {'warnings': []})
                    fit.assert_not_called()


if __name__ == '__main__':
    unittest.main()

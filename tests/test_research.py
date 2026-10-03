"""Focused analysis invariants and separation of developer evaluation."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
import uuid

import anndata as ad
import numpy as np
import pandas as pd
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/scrna-seq-workbench'
sys.path.insert(0, str(PLUGIN / 'scripts'))
from scrna_core.research import summarize
from scrna_core.common import sha256



def fixture():
    a = ad.AnnData(sparse.csr_matrix([[9, 1], [9, 1], [9, 1], [1, 9]], dtype=float))
    a.var_names = ['TARGET', 'OTHER']
    a.obs['donor'] = ['a', 'a', 'a', 'b']
    a.obs['condition'] = ['case'] * 4
    a.obs['type'] = ['T'] * 4
    a.layers['counts'] = a.X.copy()
    return a


class FocusedAnalysis(unittest.TestCase):
    def test_donors_equal_weight_and_all_genes_normalization(self):
        a = fixture()
        before = a.layers['counts'].copy()
        detail, overview, missing = summarize(a, ['TARGET', 'ABSENT'], 'type', 'donor', 'condition', 1)
        self.assertEqual(missing, ['ABSENT'])
        self.assertEqual(overview.iloc[0].n_donors, 2)
        expected = (np.log1p(9000) + np.log1p(1000)) / 2
        self.assertAlmostEqual(overview.iloc[0].mean_log1p_cp10k, expected)
        self.assertNotAlmostEqual(overview.iloc[0].mean_log1p_cp10k,
                                 (3 * np.log1p(9000) + np.log1p(1000)) / 4)
        self.assertEqual((before != a.layers['counts']).nnz, 0)
        self.assertEqual(len(detail), 2)

    def test_low_support_retained_but_not_averaged(self):
        detail, overview, _ = summarize(fixture(), ['TARGET'], 'type', 'donor', 'condition', 2)
        self.assertEqual(len(detail), 2)
        self.assertEqual(int(detail.eligible.sum()), 1)
        self.assertEqual(overview.iloc[0].n_donors, 1)

    def test_missing_group_not_imputed_as_zero(self):
        a = fixture(); a.obs.loc[a.obs_names[-1], 'type'] = 'B'
        _, overview, _ = summarize(a, ['TARGET'], 'type', 'donor', 'condition', 1)
        self.assertEqual(overview.n_donors.tolist(), [1, 1])

    def test_invalid_metadata_and_genes_stop(self):
        a = fixture()
        with self.assertRaisesRegex(ValueError, 'different columns'):
            summarize(a, ['TARGET'], 'type', 'donor', 'donor', 1)
        with self.assertRaisesRegex(ValueError, 'None of'):
            summarize(a, ['ABSENT'], 'type', 'donor', 'condition', 1)
        a.obs.loc[a.obs_names[0], 'donor'] = None
        with self.assertRaisesRegex(ValueError, 'Missing/empty'):
            summarize(a, ['TARGET'], 'type', 'donor', 'condition', 1)

    def test_paired_donor_keeps_conditions_separate(self):
        a = fixture(); a.obs['condition'] = ['before', 'before', 'after', 'after']
        detail, _, _ = summarize(a, ['TARGET'], 'type', 'donor', 'condition', 1)
        self.assertEqual(len(detail[detail.donor == 'a']), 2)

    def test_cli_outputs_provenance_without_modifying_input(self):
        folder = ROOT / 'work' / ('research-test-' + uuid.uuid4().hex)
        folder.mkdir(parents=True)
        path = folder / 'input.h5ad'; fixture().write_h5ad(path)
        original_hash = sha256(path)
        command = [sys.executable, str(PLUGIN / 'scripts/scrna.py'), 'research',
                   '--input', str(path), '--outdir', str(folder / 'results'),
                   '--question', '<script>question</script>', '--genes', 'TARGET', 'ABSENT',
                   '--celltype-key', 'type', '--donor-key', 'donor', '--condition-key', 'condition',
                   '--label-source', 'synthetic fixture', '--label-status', 'exploratory', '--min-cells', '1']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sha256(path), original_hash)
        run = json.loads((folder / 'results/report.json').read_text())
        self.assertEqual(run['status'], 'complete')
        self.assertIn('donor_expression.csv', run['artifacts'])
        html = (folder / 'results/research_report.html').read_text(encoding='utf-8')
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>', html)
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('not empty', result.stderr)


class AnalysisBoundary(unittest.TestCase):
    def test_no_scoring_command(self):
        from scrna import parser
        commands = parser()._subparsers._group_actions[0].choices
        self.assertIn('research', commands)
        self.assertNotIn('score', commands)
        self.assertNotIn('benchmark', commands)


if __name__ == '__main__':
    unittest.main()

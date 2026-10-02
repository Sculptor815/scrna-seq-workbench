"""Regression checks for immutable benchmark verification."""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import subprocess
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from verify_benchmark import check_dimensions, rows, verify_archive


class BenchmarkIntegrity(unittest.TestCase):
    def test_generators_refuse_committed_evidence_destinations(self):
        commands = [
            ['scripts/render_comparisons.py', '--outdir', str(ROOT/'docs/figures')],
            ['scripts/build_benchmark_evidence.py', '--benchmark-work', str(ROOT/'benchmarks/evidence'),
             '--outdir', str(ROOT/'benchmarks/reproduced')],
        ]
        for command in commands:
            with self.subTest(script=command[0]):
                result = subprocess.run([sys.executable, *command], cwd=ROOT, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('outside', result.stderr)
        self.assertFalse((ROOT/'benchmarks/reproduced').exists())

    def test_modified_archive_rejected_even_with_recomputed_archive_hash(self):
        original = b'{"version":"0.1.0"}'
        changed = b'{"version":"0.2.1"}'
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as z:
            z.writestr('plugin.json', changed)
        content = stream.getvalue()
        with self.assertRaisesRegex(ValueError, 'Frozen source hash mismatch'):
            verify_archive(content, hashlib.sha256(content).hexdigest(),
                           {'plugin.json': hashlib.sha256(original).hexdigest()}, '0.1.0')

    def test_before_and_after_qc_dimensions_are_not_interchangeable(self):
        b = ROOT/'benchmarks'
        manifest = json.loads((b/'legacy/data_manifest.json').read_text())
        qc = rows(b/'legacy/qc_summary.csv')
        metrics = rows(b/'legacy/metrics.csv')
        dimensions = json.loads((b/'dimensions.json').read_text())['datasets']
        check_dimensions(manifest, qc, metrics, dimensions)
        changed = copy.deepcopy(manifest)
        changed[0]['genes'] = int(qc[0]['genes_out'])
        with self.assertRaisesRegex(ValueError, 'input genes'):
            check_dimensions(changed, qc, metrics, dimensions)

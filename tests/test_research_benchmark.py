import copy
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'plugins/scrna-seq-workbench/scripts'))
spec = importlib.util.spec_from_file_location('research_score', ROOT / 'benchmarks/research/score.py')
score_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score_module)


class DeveloperReview(unittest.TestCase):
    def record(self):
        return dict(schema_version='1.0', case_id='synthetic-test', run_id='test',
                    review_status='final', completion='complete', critical_errors=[],
                    review_record_paths=['review-a.json', 'review-b.json'],
                    dimensions={k: dict(score=4, rationale='Test fixture only', evidence=['fixture'])
                                for k in score_module.WEIGHTS})

    def test_weighting_and_critical_error_gate(self):
        record = self.record()
        self.assertEqual(score_module.calculate(record)['weighted_score'], 100)
        record['dimensions']['evidence_reasoning']['score'] = 0
        self.assertEqual(score_module.calculate(record)['weighted_score'], 70)
        record['critical_errors'] = ['Invented donors in synthetic negative example']
        self.assertFalse(score_module.calculate(record)['eligible'])

    def test_pending_and_execution_errors_not_scores(self):
        for key, value in [('review_status', 'pending'), ('completion', 'execution_error')]:
            record = self.record(); record[key] = value
            result = score_module.calculate(record)
            self.assertIsNone(result['weighted_score'])
            self.assertFalse(result['eligible'])

    def test_bad_scores_and_missing_evidence_rejected(self):
        for value in [True, -1, 5, 2.5, float('nan')]:
            record = self.record(); record['dimensions']['data_suitability']['score'] = value
            with self.assertRaises(ValueError): score_module.calculate(record)
        record = self.record(); record['dimensions']['data_suitability']['evidence'] = []
        with self.assertRaises(ValueError): score_module.calculate(record)

    def test_model_name_does_not_change_score(self):
        record = self.record(); other = copy.deepcopy(record)
        record['model'] = 'model-a'; other['model'] = 'model-b'
        self.assertEqual(score_module.calculate(record), score_module.calculate(other))

    def test_analysis_parser_has_no_evaluation_command(self):
        from scrna import parser
        commands = parser()._subparsers._group_actions[0].choices
        self.assertIn('research', commands)
        self.assertNotIn('score', commands)
        self.assertNotIn('benchmark', commands)


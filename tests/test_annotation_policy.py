import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'plugins/scrna-seq-workbench/scripts'))
from scrna_core.annotation_policy import FIELDS, validate_hpa_review, marker_statistics
from test_workflows import fixture


def review():
    return pd.DataFrame([['0','T cells','T cells','accept','test-human','human','CD3D;CD3E',
        'B-cell markers not enriched','synthetic fixture','checked','no split needed','synthetic validation']], columns=FIELDS)


class HPAPolicy(unittest.TestCase):
    def test_pending_is_not_final(self):
        r=review(); r.loc[0,'decision']='pending'
        with self.assertRaises(ValueError): validate_hpa_review(r,['0'],['CD3D','CD3E'])

    def test_agent_is_not_manual_review(self):
        r=review(); r.loc[0,'reviewer_type']='agent'
        with self.assertRaises(ValueError): validate_hpa_review(r,['0'],['CD3D','CD3E'])

    def test_absent_marker_cannot_support_acceptance(self):
        with self.assertRaises(ValueError): validate_hpa_review(review(),['0'],['CD3D'])

    def test_both_levels_and_full_cluster_coverage(self):
        r=review(); r.loc[0,'cell_type_detail']=''
        with self.assertRaises(ValueError): validate_hpa_review(r,['0'],['CD3D','CD3E'])
        with self.assertRaises(ValueError): validate_hpa_review(review(),['0','1'],['CD3D','CD3E'])

    def test_mixed_is_unknown(self):
        r=review(); r.loc[0,'decision']='mixed'
        with self.assertRaises(ValueError): validate_hpa_review(r,['0'],['CD3D','CD3E'])
        r.loc[0,['cell_type','cell_type_detail']]='Unknown'
        self.assertEqual(validate_hpa_review(r,['0'],['CD3D','CD3E']).iloc[0].cell_type,'Unknown')

    def test_valid_hierarchical_review_and_marker_measurements(self):
        self.assertEqual(validate_hpa_review(review(),['0'],['CD3D','CD3E']).iloc[0].cell_type,'T cells')
        a=fixture(); s=marker_statistics(a,'leiden',{'T':['CD3D','absent']})
        self.assertTrue(s.loc[s.gene.eq('absent'),'fraction_detected'].isna().all())
        self.assertTrue(s.loc[s.present,'fraction_detected'].between(0,1).all())


if __name__=='__main__': unittest.main()

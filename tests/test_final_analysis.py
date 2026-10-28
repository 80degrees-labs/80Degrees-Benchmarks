import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('analysis',Path(__file__).resolve().parents[1]/'tooling/final_analysis.py')
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)

def row(reward,unknown=False,i=10,o=2):
    return dict(raw_reward=reward,unresolved=unknown,classification='verified_fail',input_tokens=i,output_tokens=o)

class StatisticsTests(unittest.TestCase):
    def test_equal_scores_do_not_prove_noninferiority(self):
        p=[(row(1),row(1))]*10
        self.assertLess(a.paired_stats(p)['noninferiority_lower'],-.05)

    def test_exact_discordant_probability(self):
        p=[(row(1),row(0))]*6
        self.assertAlmostEqual(a.paired_stats(p)['mcnemar_p'],.03125)

    def test_missing_outcomes_sensitivity(self):
        self.assertEqual(a.sensitivity([(row(0,True),row(1))]),[-1,0])
        self.assertEqual(a.sensitivity([(row(0,True),row(0,True))]),[-1,1])

    def test_unknown_usage_is_not_zero(self):
        self.assertEqual(a.tokens([(row(1,i=None),row(1))]),{'n':0})

    def test_setup_errors_not_credited_passes(self):
        c,unknown,note=a.classify('Failed to download; operation timed out',0)
        self.assertTrue(unknown)
        self.assertEqual(c,'verifier_dependency_download_timeout')

    def test_task_error_not_infrastructure(self):
        self.assertFalse(a.classify('AssertionError: output file absent',0)[1])

if __name__=='__main__': unittest.main()

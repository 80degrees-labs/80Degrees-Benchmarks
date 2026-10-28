import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('price',Path(__file__).resolve().parents[1]/'tooling/price_usage.py')
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

class PricingTests(unittest.TestCase):
    def test_cache_not_billed_twice(self):
        row=dict(model='gpt-6.1-sol',input_tokens=1000000,cache_tokens=800000,output_tokens=100000)
        self.assertAlmostEqual(p.estimate(row),.4+.08+1)

    def test_all_cache(self):
        row=dict(model='gpt-6-astra',input_tokens=1000000,cache_tokens=1000000,output_tokens=0)
        self.assertEqual(p.estimate(row),1)

    def test_model_rates_differ(self):
        row=dict(model='gpt-6-astra',input_tokens=1000000,cache_tokens=0,output_tokens=1000000)
        self.assertEqual(p.estimate(row),60)

if __name__=='__main__': unittest.main()

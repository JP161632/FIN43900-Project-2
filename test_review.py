"""Independent checks for supplemental monitoring, constraints and liquidity units."""
import copy
import io
import json
from pathlib import Path
import unittest

import numpy as np

import analysis as a
import review_analysis as r


class ReviewAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output=json.loads((a.ROOT/'outputs/visible_output.json').read_text())
        prices,_=a.audit_sources()
        cls.returns=prices.pct_change(fill_method=None).iloc[1:]
        cls.liquidity=r.daily_dollar_volume()

    def test_subperiod_compounding_known_answer(self):
        result=r.period_metrics([{'date':'2000-01-31','net_return':.10},
                                 {'date':'2000-02-29','net_return':-.10}])
        self.assertAlmostEqual(result['net_total_return'],-.01)
        self.assertAlmostEqual(result['month_end_max_drawdown'],-.10)

    def test_monitoring_warmup_and_strict_threshold(self):
        rows=[{'date':str(i),'net_return':.20 if i%2 else -.20,
               'rebalance':True,'target_change_points':15 if i<12 else 20,
               'infeasible_at_rebalance':False} for i in range(13)]
        result=r.monitoring(rows)
        self.assertTrue(all(row['trailing_12_month_net_volatility'] is None for row in result[:11]))
        self.assertTrue(result[11]['volatility_breach'])
        self.assertFalse(result[11]['target_movement_breach'])
        self.assertTrue(result[12]['target_movement_breach'])

    def test_liquidity_dollars_and_nav_scaling(self):
        run=self.output['replays']['equal_10bps']
        one=r.capacity_and_constraints(self.returns,run,self.liquidity,1_000_000)
        two=r.capacity_and_constraints(self.returns,run,self.liquidity,2_000_000)
        self.assertEqual(len(one),32)
        self.assertAlmostEqual(one[0]['absolute_trade_dollars_at_illustrative_nav'],250_000/1.001)
        self.assertAlmostEqual(two[0]['participation_fraction'],2*one[0]['participation_fraction'])
        self.assertAlmostEqual(one[0]['participation_fraction'],
            one[0]['absolute_trade_dollars_at_illustrative_nav']/one[0]['prior_20_session_average_dollar_volume'])
        self.assertTrue(all(row['latest_liquidity_date']<=row['information_cutoff'] for row in one))

    def test_constraint_violation_is_rejected(self):
        run=copy.deepcopy(self.output['replays']['candidate_10bps'])
        run['monthly'][0]['start_weights']={'NVDA':-.10,'MSFT':.50,'TSM':.40,'QCOM':.20}
        with self.assertRaisesRegex(ValueError,'constraint audit failed'):
            r.capacity_and_constraints(self.returns,run,self.liquidity)

    def test_replay_periods_reconcile_and_all_targets_pass(self):
        for rule in ['equal','inverse_vol','candidate']:
            run=self.output['replays'][f'{rule}_10bps']
            first=r.period_metrics(run['monthly'][:12]);last=r.period_metrics(run['monthly'][12:])
            self.assertAlmostEqual((1+first['net_total_return'])*(1+last['net_total_return'])-1,
                                   run['summary']['net_total_return'])
            self.assertTrue(all(row['constraint_pass'] for row in
                r.capacity_and_constraints(self.returns,run,self.liquidity)))


if __name__=='__main__':
    buffer=io.StringIO()
    result=unittest.TextTestRunner(stream=buffer,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ReviewAudit))
    report={'passed':result.wasSuccessful(),'tests_run':result.testsRun,'output':buffer.getvalue()}
    (a.ROOT/'evidence/review-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(buffer.getvalue())
    raise SystemExit(0 if result.wasSuccessful() else 1)

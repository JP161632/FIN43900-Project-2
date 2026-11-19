"""Independent numeric checks and failure injections; no human activity claimed."""
import copy
import io
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

import analysis as a


class FinanceAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prices, cls.sources = a.audit_sources()
        cls.returns = cls.prices.pct_change(fill_method=None).iloc[1:]
        cls.result = a.calculate()

    def test_all_244_prices_reconstruct_from_raw_sources(self):
        self.assertEqual(sum(s['monthly_values_reconstructed'] for s in self.sources), 244)
        self.assertEqual(len(self.returns), 60)

    def test_source_corruption_is_rejected(self):
        with patch.object(a, 'sha', return_value='invalid'):
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                a.audit_sources()

    def test_independent_known_answer(self):
        sleeves = {name: {'return': .10, 'volatility': .20, 'reserve_eligible': False} for name in a.TICKERS}
        covariance = a.lab.covariance_matrix(sleeves, np.eye(4).tolist())
        weights = dict.fromkeys(a.TICKERS, .25)
        self.assertAlmostEqual(a.lab.expected_return(weights, sleeves), .10)
        self.assertAlmostEqual(a.lab.portfolio_volatility(weights, sleeves, covariance), .10)
        answer = a.candidate(sleeves, np.eye(4).tolist())
        self.assertEqual(answer['weights'], weights)

    def test_covariance_independent_sample_formula(self):
        sleeves, corr = a.estimates(self.returns)
        covariance = a.lab.covariance_matrix(sleeves, corr)
        # Explicit centered-products calculation, independent of corr/std pipeline.
        for i, j in [(0, 0), (0, 2), (1, 3)]:
            x, y = self.returns.iloc[:, i].tolist(), self.returns.iloc[:, j].tolist()
            mx, my = sum(x)/len(x), sum(y)/len(y)
            expected = 12*sum((u-mx)*(v-my) for u, v in zip(x, y))/(len(x)-1)
            self.assertAlmostEqual(covariance[i][j], expected, places=12)

    def test_grid_and_infeasible_bounds(self):
        sleeves, corr = a.estimates(self.returns)
        answer = a.candidate(sleeves, corr)
        self.assertIsNone(a.candidate(sleeves, corr, hurdle=10))
        capped = a.candidate(sleeves, corr, cap=.5)
        self.assertLessEqual(max(capped['weights'].values()), .5)
        self.assertAlmostEqual(sum(answer['weights'].values()), 1)
        self.assertTrue(all(v >= 0 for v in answer['weights'].values()))
        inherited = a.lab.search_mix(sleeves, corr, .1, 0)
        self.assertEqual(answer['weights'], inherited['weights'])

    def test_trade_fee_independent_exact_answers(self):
        cost, traded = a.trade_cost([0,0,0,0], [.25]*4, 10)
        self.assertAlmostEqual(cost, .001/1.001, places=14)
        self.assertAlmostEqual(traded, 1/1.001, places=14)
        cost, traded = a.trade_cost([1,0,0,0], [0,1,0,0], 10)
        self.assertAlmostEqual(cost, .002/1.001, places=14)
        self.assertAlmostEqual(cost, .001*traded, places=14)
        self.assertEqual(a.trade_cost([.25]*4, [.25]*4, 0)[0], 0)
        with self.assertRaises(ValueError):
            a.trade_cost([0]*4, [.25]*4, 10001)

    def test_first_month_manual_and_drift(self):
        run = self.result['replays']['equal_10bps']
        first = run['monthly'][0]
        manual_return = sum(float(x) for x in self.returns.iloc[36])/4
        expected_net = (1-.001/1.001)*(1+manual_return)-1
        self.assertAlmostEqual(first['net_return'], expected_net, places=13)
        second = run['monthly'][1]
        expected_weights = .25*(1+self.returns.iloc[36].to_numpy())/(1+manual_return)
        np.testing.assert_allclose(list(second['start_weights'].values()), expected_weights)
        self.assertEqual(second['cost_fraction_nav'], 0)

    def test_future_return_changes_cannot_change_prior_weights(self):
        original = a.replay(self.returns, 'candidate')
        mutated = self.returns.copy()
        mutated.iloc[48:] = mutated.iloc[48:]*-1
        changed = a.replay(mutated, 'candidate')
        for i in range(13):  # includes first changed return's start-of-month weights
            self.assertEqual(original['monthly'][i]['start_weights'], changed['monthly'][i]['start_weights'])
        self.assertTrue(all(row['training_end'] < row['date'] for row in original['monthly']))

    def test_costs_and_wealth_accounting(self):
        for rule in ['equal', 'inverse_vol', 'candidate']:
            totals = [self.result['replays'][f'{rule}_{bps}bps']['summary']['net_total_return'] for bps in [0,10,25,50]]
            self.assertEqual(totals, sorted(totals, reverse=True))
            run = self.result['replays'][f'{rule}_10bps']
            wealth = 1.
            for row in run['monthly']:
                wealth *= (1-row['cost_fraction_nav'])*(1+row['gross_return'])
                self.assertAlmostEqual(wealth, row['net_wealth'], places=12)
            self.assertAlmostEqual(wealth-1, run['summary']['net_total_return'])

    def test_bad_prices_missing_and_duplicate_months(self):
        frame = self.prices.reset_index()
        for kind in ['missing', 'duplicate', 'zero', 'nan', 'reverse']:
            changed = frame.copy()
            if kind == 'missing': changed = changed.drop(index=5)
            elif kind == 'duplicate': changed.iloc[5,0] = changed.iloc[4,0]
            elif kind == 'zero': changed.iloc[5,1] = 0
            elif kind == 'nan': changed.iloc[5,1] = float('nan')
            else: changed = changed.iloc[::-1]
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp)/'bad.csv'
                changed.to_csv(path, index=False)
                with self.assertRaises(ValueError, msg=kind):
                    a.read_prices(path)

    def test_cash_fallback_and_rule_rejection(self):
        with patch.object(a, 'candidate', return_value=None):
            run = a.replay(self.returns, 'candidate')
        self.assertEqual(run['summary']['infeasible_rebalances'], 8)
        self.assertEqual(run['summary']['net_total_return'], 0)
        with self.assertRaises(ValueError): a.replay(self.returns, 'unknown')

    def test_uncertainty_reproducible_and_descriptive(self):
        x = a.moving_block_interval([.01]*24, 50)
        self.assertAlmostEqual(x['lower'], .12)
        self.assertAlmostEqual(x['upper'], .12)
        self.assertEqual(x, a.moving_block_interval([.01]*24, 50))

    def test_variable_lookback_uses_only_synthetic_training_windows(self):
        synthetic = pd.DataFrame(np.random.default_rng(42).normal(.01,.03,(60,4)),
                                 index=pd.date_range('2000-01-31',periods=60,freq='ME'),columns=a.TICKERS)
        original = a.estimates
        with patch.object(a,'estimates',wraps=original) as observed:
            run = a.replay(synthetic,'equal',lookback=24)
        self.assertEqual(len(run['monthly']),24)
        self.assertEqual(len(observed.call_args_list),8)
        self.assertTrue(all(len(call.args[0])==24 for call in observed.call_args_list))
        self.assertEqual(run['summary']['lookback_months'],24)
        for value in [0,11,37,True,24.5]:
            with self.assertRaises(ValueError):a.replay(synthetic,'equal',lookback=value)

    def test_locked_record_safeguards_with_synthetic_prediction_only(self):
        import contextlib
        import locked_exercise as locked
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            source=root/'synthetic.txt';source.write_text('synthetic fixture; not course evidence')
            prediction={key:'Synthetic test fixture only; not a student prediction.' for key in locked.FIELDS}
            prediction['new_lookback_months']=24
            input_path=root/'input.json';input_path.write_text(json.dumps(prediction))
            def fixture_manifest():return {'synthetic.txt':a.sha(source)}
            with patch.object(locked,'ROOT',root),patch.object(locked,'DEST',root/'record'),patch.object(locked,'snapshot_files',side_effect=fixture_manifest),contextlib.redirect_stdout(io.StringIO()):
                locked.freeze(input_path)
                self.assertTrue((root/'record/snapshot.zip').exists())
                self.assertFalse((root/'record/execution.json').exists())
                with self.assertRaises(ValueError):locked.freeze(input_path)
                synthetic_returns=np.random.default_rng(71).normal(.01,.03,(60,4))
                synthetic_prices=pd.DataFrame(np.vstack([np.ones(4),np.cumprod(1+synthetic_returns,axis=0)])*100,
                                              index=pd.date_range('2000-01-31',periods=61,freq='ME'),columns=a.TICKERS)
                with patch.object(a,'audit_sources',return_value=(synthetic_prices,[])):
                    locked.execute()
                self.assertTrue((root/'record/execution.json').exists())
                self.assertTrue((root/'record/student-reconciliation.md').exists())
                with self.assertRaisesRegex(ValueError,'already exists'):locked.execute()
                source.write_text('changed fixture')
                with self.assertRaisesRegex(ValueError,'changed after prediction'):locked.execute()
            with self.assertRaises(ValueError):locked.validate({'new_lookback_months':36})


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FinanceAudit)
    buffer = io.StringIO()
    result = unittest.TextTestRunner(stream=buffer, verbosity=2).run(suite)
    report = {'passed': result.wasSuccessful(), 'tests_run': result.testsRun,
              'failures': len(result.failures), 'errors': len(result.errors),
              'output': buffer.getvalue()}
    (a.ROOT/'evidence/verification-results.json').write_text(json.dumps(report, indent=2)+'\n')
    print(buffer.getvalue())
    raise SystemExit(0 if result.wasSuccessful() else 1)

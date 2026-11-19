"""Live Video 2 demonstration of existing tests; not the locked exercise.

Run from any working directory. Does not rewrite project evidence or results.
"""
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from tests import FinanceAudit


if __name__ == '__main__':
    print('PROJECT 2 - LIVE VALIDATION DEMONSTRATION', flush=True)
    print('Existing tests; no result files or locked records are changed.\n', flush=True)
    names = [
        'test_independent_known_answer',
        'test_trade_fee_independent_exact_answers',
        'test_source_corruption_is_rejected',
        'test_first_month_manual_and_drift',
    ]
    suite = unittest.TestSuite(FinanceAudit(name) for name in names)
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    print('\nExpected: Ran 4 tests, then OK. If any test fails, stop and investigate.', flush=True)
    raise SystemExit(0 if result.wasSuccessful() else 1)

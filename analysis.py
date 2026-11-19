"""Offline, traceable portfolio research. All rates and weights are decimals."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from vendor import portfolio as lab

ROOT = Path(__file__).resolve().parent
TICKERS = ['NVDA', 'MSFT', 'TSM', 'QCOM']
HURDLE = .10


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_prices(path):
    frame = pd.read_csv(path)
    if list(frame.columns) != ['Date', *TICKERS]:
        raise ValueError('Expected Date, NVDA, MSFT, TSM, QCOM in that order.')
    dates = pd.to_datetime(frame.pop('Date'), errors='raise')
    if dates.isna().any() or dates.duplicated().any() or not dates.is_monotonic_increasing:
        raise ValueError('Dates must be present, unique and increasing.')
    months = dates.dt.year * 12 + dates.dt.month
    if not months.diff().iloc[1:].eq(1).all():
        raise ValueError('One price per consecutive month required; no filling.')
    values = frame.to_numpy(dtype=float)
    if len(frame) < 37 or not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError('Need at least 37 rows of finite positive prices.')
    frame.index = pd.DatetimeIndex(dates)
    return frame


def audit_sources():
    """Verify hashes AND independently reconstruct every monthly input."""
    provenance = json.loads((ROOT / 'data/price-provenance.json').read_text())
    price_path = ROOT / 'data/prices.csv'
    if sha(price_path) != provenance['prices_sha256']:
        raise ValueError('Price hash mismatch.')
    prices = read_prices(price_path)
    records = []
    for source in provenance['sources']:
        raw_path = ROOT / 'data' / source['raw_file']
        if sha(raw_path) != source['raw_sha256']:
            raise ValueError('Raw source hash mismatch: ' + source['ticker'])
        result = json.loads(raw_path.read_text())['chart']['result'][0]
        ticker = source['ticker']
        if result['meta']['symbol'] != ticker or result['meta']['currency'] != 'USD':
            raise ValueError('Wrong source ticker or currency.')
        timestamps = result['timestamp']
        values = result['indicators']['adjclose'][0]['adjclose']
        if len(timestamps) != len(values):
            raise ValueError('Timestamp/price length mismatch.')
        monthly = {}
        for stamp, value in zip(timestamps, values):
            date = datetime.fromtimestamp(stamp, timezone.utc).date().isoformat()
            if prices.index[0].strftime('%Y-%m') <= date[:7] <= prices.index[-1].strftime('%Y-%m'):
                if value is None or not math.isfinite(value) or value <= 0:
                    raise ValueError('Missing/invalid daily adjusted close.')
                if date[:7] not in monthly or date > monthly[date[:7]][0]:
                    monthly[date[:7]] = (date, value)
        for date, value in prices[ticker].items():
            raw_date, raw_value = monthly[date.strftime('%Y-%m')]
            if raw_date != date.date().isoformat() or not math.isclose(value, raw_value, rel_tol=1e-13):
                raise ValueError('Monthly reconstruction failed: ' + ticker)
        records.append({**source, 'hash_verified': True,
                        'monthly_values_reconstructed': len(prices)})
    if sorted(x['ticker'] for x in records) != sorted(TICKERS):
        raise ValueError('Missing or duplicate source ticker.')
    return prices, records


def estimates(returns):
    values = returns.to_numpy(dtype=float)
    if len(returns) < 2 or not np.isfinite(values).all():
        raise ValueError('Insufficient or nonfinite returns.')
    sleeves = {name: {'return': float(returns[name].mean() * 12),
                     'volatility': float(returns[name].std(ddof=1) * math.sqrt(12)),
                     'reserve_eligible': False} for name in TICKERS}
    corr = returns.corr().to_numpy().tolist()
    lab.validate_inputs(sleeves, corr)
    return sleeves, corr


def candidate(sleeves, corr, hurdle=HURDLE, cap=1.):
    if not math.isfinite(hurdle) or not 0 < cap <= 1:
        raise ValueError('Invalid hurdle or target weight cap.')
    covariance = lab.covariance_matrix(sleeves, corr)
    best = None
    for a in range(21):
        for b in range(21 - a):
            for c in range(21 - a - b):
                weights = dict(zip(TICKERS, [a / 20, b / 20, c / 20, (20-a-b-c) / 20]))
                if max(weights.values()) > cap + 1e-12:
                    continue
                mean = lab.expected_return(weights, sleeves)
                if mean + 1e-12 < hurdle:
                    continue
                vol = lab.portfolio_volatility(weights, sleeves, covariance)
                if best is None or vol < best['volatility'] - 1e-12:
                    best = {'weights': weights, 'return': mean, 'volatility': vol}
    return best


def trade_cost(prior, target, bps):
    """Solve self-financing fee: c = k * sum(abs((1-c)*target-prior)).

    Cash earns zero; only equity purchases and sales incur cost. c and dollar
    turnover are fractions of pretrade NAV. Initial cash deployment is included.
    """
    prior, target = np.asarray(prior, dtype=float), np.asarray(target, dtype=float)
    if not np.isfinite(bps) or not 0 <= bps <= 100 or prior.shape != target.shape:
        raise ValueError('One-way cost must be 0-100 bps; weight dimensions must agree.')
    if not np.isfinite(prior).all() or not np.isfinite(target).all() or (prior < 0).any() or (target < 0).any():
        raise ValueError('Invalid trade weights.')
    if prior.sum() > 1 + 1e-12 or target.sum() > 1 + 1e-12:
        raise ValueError('Unfunded trade weights.')
    rate = bps / 10000
    lo, hi = 0., .03
    for _ in range(60):
        mid = (lo + hi) / 2
        if mid - rate * np.abs((1-mid)*target-prior).sum() > 0:
            hi = mid
        else:
            lo = mid
    cost = (lo + hi) / 2 if bps else 0.
    traded = float(np.abs((1-cost)*target-prior).sum())
    return cost, traded


def replay(returns, rule, bps=10, cap=1., lookback=36):
    """Rolling estimates; fixed evaluation start after month 36; quarterly trades."""
    if isinstance(lookback, bool) or not isinstance(lookback, int) or not 12 <= lookback <= 36:
        raise ValueError('Lookback must be an integer from 12 to 36 monthly returns.')
    prior = np.zeros(4)
    rows = []
    last_target = None
    for i in range(36, len(returns)):
        training = returns.iloc[i-lookback:i]
        rebalance = (i-36) % 3 == 0
        infeasible = False
        cost = traded = change = 0.
        training_end = training.index[-1].date().isoformat()
        if rebalance:
            sleeves, corr = estimates(training)
            if rule == 'candidate':
                result = candidate(sleeves, corr, cap=cap)
                infeasible = result is None
                target = np.array(list(result['weights'].values())) if result else np.zeros(4)
            elif rule == 'equal':
                target = np.ones(4) / 4
            elif rule == 'inverse_vol':
                target = np.array(list(lab.inverse_volatility_weights(sleeves).values()))
            else:
                raise ValueError('Unknown portfolio rule.')
            change = float(np.max(np.abs(target-last_target))) if last_target is not None else 0.
            last_target = target.copy()
            cost, traded = trade_cost(prior, target, bps)
            prior = target
        start_weights = prior.copy()
        gross = float(start_weights @ returns.iloc[i].to_numpy())
        net = (1-cost) * (1+gross) - 1
        prior = start_weights * (1 + returns.iloc[i].to_numpy()) / (1+gross)
        rows.append({'date': returns.index[i].date().isoformat(), 'training_end': training_end,
                     'rebalance': rebalance, 'infeasible_at_rebalance': infeasible,
                     'start_weights': dict(zip(TICKERS, map(float, start_weights))),
                     'gross_return': gross, 'net_return': net,
                     'cost_fraction_nav': cost, 'dollars_traded_fraction_nav': traded,
                     'target_change_points': change * 100})
    if not rows:
        raise ValueError('No replay period after the 36-month training window.')
    net = np.array([row['net_return'] for row in rows])
    gross = np.array([row['gross_return'] for row in rows])
    wealth = np.r_[1., np.cumprod(1+net)]
    for row, value in zip(rows, wealth[1:]):
        row['net_wealth'] = float(value)
    summary = {'rule': rule, 'cost_bps_one_way': bps, 'target_cap': cap, 'lookback_months': lookback,
               'months': len(rows), 'start': rows[0]['date'], 'end': rows[-1]['date'],
               'gross_total_return': float(np.prod(1+gross)-1),
               'net_total_return': float(wealth[-1]-1),
               'net_cagr': float(wealth[-1]**(12/len(rows))-1),
               'net_volatility': float(net.std(ddof=1)*math.sqrt(12)),
               'max_drawdown_month_end': float((wealth/np.maximum.accumulate(wealth)-1).min()),
               'traded_nav_sum': sum(row['dollars_traded_fraction_nav'] for row in rows),
               'max_target_change_points': max(row['target_change_points'] for row in rows),
               'infeasible_rebalances': sum(row['infeasible_at_rebalance'] for row in rows),
               'max_start_equity_weight': max(max(row['start_weights'].values()) for row in rows)}
    return {'summary': summary, 'monthly': rows}


def comparison(sleeves, corr):
    covariance = lab.covariance_matrix(sleeves, corr)
    out = {}
    for name, weights in [('equal', lab.equal_weights(sleeves)),
                          ('inverse_vol', lab.inverse_volatility_weights(sleeves))]:
        out[name] = {'weights': weights, 'return': lab.expected_return(weights, sleeves),
                     'volatility': lab.portfolio_volatility(weights, sleeves, covariance)}
    out['candidate'] = candidate(sleeves, corr)
    return out


def moving_block_interval(differences, repetitions=2000):
    """Descriptive paired monthly mean difference; fixed 3-month circular blocks."""
    rng = np.random.default_rng(439)
    n = len(differences)
    draws = []
    for _ in range(repetitions):
        starts = rng.integers(0, n, size=math.ceil(n/3))
        indexes = np.concatenate([(start + np.arange(3)) % n for start in starts])[:n]
        draws.append(float(np.asarray(differences)[indexes].mean()*12))
    return {'lower': float(np.quantile(draws, .025)), 'upper': float(np.quantile(draws, .975)),
            'metric': 'Annualized arithmetic mean of paired monthly net return differences',
            'block_months': 3, 'repetitions': repetitions, 'seed': 439,
            'limitation': '24 previously inspected months; descriptive only; does not repair selection, timing or regime risk.'}


def calculate():
    prices, sources = audit_sources()
    returns = prices.pct_change(fill_method=None).iloc[1:]
    full, corr = estimates(returns)
    recent, recent_corr = estimates(returns.tail(36))
    stressed = {name: dict(values) for name, values in full.items()}
    stressed['TSM']['return'] -= .01
    replays, ledger = {}, []
    for bps in [0, 10, 25, 50]:
        for rule in ['equal', 'inverse_vol', 'candidate']:
            name = f'{rule}_{bps}bps'
            replays[name] = replay(returns, rule, bps)
            ledger.append({'id': name, 'type': 'chronological replay', 'rule': rule,
                           'cost_bps': bps, 'target_cap': 1., 'status': 'executed'})
    replays['candidate_cap50_10bps'] = replay(returns, 'candidate', 10, cap=.50)
    ledger.append({'id': 'candidate_cap50_10bps', 'type': 'cap sensitivity', 'status': 'executed'})
    window = candidate(recent, recent_corr)
    base = candidate(full, corr)
    attack = candidate(stressed, corr)
    infeasible = candidate(full, corr, hurdle=10.)
    for name in ['all_60_estimates', 'last_36_estimates', 'TSM_mean_minus_1pp', 'hurdle_1000pct']:
        ledger.append({'id': name, 'type': 'full-sample sensitivity', 'status': 'executed'})
    delta = max(abs(base['weights'][name]-window['weights'][name]) for name in TICKERS)*100
    a = replays['candidate_10bps']['monthly']
    b = replays['equal_10bps']['monthly']
    differences = [x['net_return']-y['net_return'] for x, y in zip(a, b)]
    source_files = ['analysis.py', 'vendor/portfolio.py', 'data/prices.csv',
                    'data/price-provenance.json', 'docs/research-design.md']
    return {'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'information_boundary': 'Retrospective study using 2026-10-22 adjusted-price snapshot; price observations end 2026-09-30.',
            'study_type': 'Previously inspected chronological replay; no untouched holdout',
            'decision': 'Continue paper research only; do not approve capital deployment.',
            'decision_reason': 'Independent prospective validation, executable timing and suitability evidence are missing; historical optimization cannot supply them.',
            'edition_a_status': 'Selected prior portfolio results are Edition A, a retrospective comparison baseline; the original checkpoint receipt is not established.',
            'sources': sources, 'file_hashes': {name: sha(ROOT/name) for name in source_files},
            'estimates_all': full, 'correlations_all': corr,
            'full_sample_comparison': comparison(full, corr),
            'sensitivities': {'last_36': window, 'TSM_minus_1pp': attack,
                              'window_largest_weight_change_points': delta,
                              'hurdle_1000pct': infeasible},
            'replays': replays, 'selection_ledger': ledger,
            'paired_block_interval': moving_block_interval(differences),
            'required_human_evidence': ['Edition A checkpoint resolution', 'Locked changed-input exercise',
                                        'Student code defense', 'Three actual videos and transcripts',
                                        'Repository/video access checks', 'Brightspace submission receipt']}


def main():
    output = calculate()
    (ROOT/'outputs').mkdir(exist_ok=True)
    (ROOT/'outputs/visible_output.json').write_text(json.dumps(output, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(output['decision'])
    for name in ['equal_10bps', 'inverse_vol_10bps', 'candidate_10bps']:
        s = output['replays'][name]['summary']
        print(f"{name}: net cumulative {s['net_total_return']:.2%}; annual volatility {s['net_volatility']:.2%}; max drawdown {s['max_drawdown_month_end']:.2%}")


if __name__ == '__main__':
    main()

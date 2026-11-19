"""Supplemental model-risk evidence. Does not retune or alter the frozen strategy."""
from datetime import datetime, timezone
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import analysis as a

ROOT = Path(__file__).resolve().parent


def period_metrics(rows):
    net=np.array([row['net_return'] for row in rows],dtype=float)
    wealth=np.r_[1.,np.cumprod(1+net)]
    return {'months':len(rows),'start':rows[0]['date'],'end':rows[-1]['date'],
            'net_total_return':float(wealth[-1]-1),
            'net_volatility':float(np.std(net,ddof=1)*math.sqrt(12)),
            'month_end_max_drawdown':float(np.min(wealth/np.maximum.accumulate(wealth)-1))}


def daily_dollar_volume():
    """Raw same-day unadjusted close times reported volume; no split-unit mixing."""
    answer={}
    for ticker in a.TICKERS:
        path=ROOT/f'data/sources/{ticker}-yahoo-daily.json'
        result=json.loads(path.read_text())['chart']['result'][0]
        quote=result['indicators']['quote'][0]
        stamps,closes,volumes=result['timestamp'],quote['close'],quote['volume']
        if len({len(stamps),len(closes),len(volumes)})!=1:
            raise ValueError('Volume/close timestamp length mismatch: '+ticker)
        rows=[]
        for stamp,close,volume in zip(stamps,closes,volumes):
            date=datetime.fromtimestamp(stamp,timezone.utc).date().isoformat()
            if close is None or volume is None or not np.isfinite([close,volume]).all() or close<=0 or volume<0:
                raise ValueError('Invalid raw liquidity field: '+ticker+' '+date)
            rows.append({'date':date,'dollar_volume':float(close*volume)})
        answer[ticker]=rows
    return answer


def capacity_and_constraints(returns,run,liquidity,illustrative_nav=1_000_000):
    """Audit target constraints and a labelled historical participation proxy.

    Fixed illustrative pretrade NAV on every trade date isolates participation;
    it is not a simulated dollar NAV path or a live account instruction.
    """
    previous=np.zeros(4)
    records=[]
    for offset,row in enumerate(run['monthly']):
        weights=np.array([row['start_weights'][ticker] for ticker in a.TICKERS])
        if row['rebalance']:
            delta=(1-row['cost_fraction_nav'])*weights-previous
            training=returns.iloc[36+offset-36:36+offset]
            historical_mean=float(training.mean().to_numpy() @ weights *12)
            cash=float(1-weights.sum())
            valid=(weights>=-1e-12).all() and weights.sum()<=1+1e-12
            if not row['infeasible_at_rebalance']:
                valid=valid and abs(weights.sum()-1)<1e-12
            if run['summary']['rule']=='candidate' and not row['infeasible_at_rebalance']:
                valid=valid and historical_mean>=a.HURDLE-1e-12
                valid=valid and weights.max()<=run['summary']['target_cap']+1e-12
            if not valid:raise ValueError('Target constraint audit failed on '+row['date'])
            for i,ticker in enumerate(a.TICKERS):
                eligible=[item for item in liquidity[ticker] if item['date']<=row['training_end']][-20:]
                if len(eligible)!=20:raise ValueError('Need 20 valid prior daily liquidity observations.')
                adv=float(np.mean([item['dollar_volume'] for item in eligible]))
                if adv<=0:raise ValueError('No positive trailing dollar volume.')
                records.append({'date':row['date'],'ticker':ticker,'information_cutoff':row['training_end'],
                    'target_weight':float(weights[i]),'historical_mean_portfolio':historical_mean,
                    'constraint_pass':True,'target_cash_weight':cash,
                    'trade_fraction_pretrade_nav':float(delta[i]),
                    'absolute_trade_dollars_at_illustrative_nav':abs(float(delta[i]))*illustrative_nav,
                    'prior_20_session_average_dollar_volume':adv,
                    'latest_liquidity_date':eligible[-1]['date'],
                    'participation_fraction':abs(float(delta[i]))*illustrative_nav/adv,
                    'hypothetical_nav_at_1pct_participation':.01*adv/abs(float(delta[i])) if abs(delta[i])>1e-12 else None})
        gross=row['gross_return']
        asset_return=returns.iloc[36+offset].to_numpy()
        previous=weights*(1+asset_return)/(1+gross)
    return records


def monitoring(rows):
    observations=[]
    for i,row in enumerate(rows):
        window=[item['net_return'] for item in rows[max(0,i-11):i+1]]
        vol=float(np.std(window,ddof=1)*math.sqrt(12)) if len(window)==12 else None
        observations.append({'date':row['date'],'trailing_12_month_net_volatility':vol,
                             'target_movement_points':row['target_change_points'],
                             'target_movement_breach':row['rebalance'] and row['target_change_points']>15+1e-12,
                             'volatility_breach':vol is not None and vol>.22,
                             'infeasible_at_rebalance':row['infeasible_at_rebalance']})
    return observations


def build():
    result=json.loads((ROOT/'outputs/visible_output.json').read_text())
    for name,digest in result['file_hashes'].items():
        if a.sha(ROOT/name)!=digest:raise ValueError('Stale main output: '+name)
    prices,sources=a.audit_sources()
    returns=prices.pct_change(fill_method=None).iloc[1:]
    liquidity=daily_dollar_volume()
    subperiods={}
    constraints={}
    for rule in ['equal','inverse_vol','candidate']:
        run=result['replays'][f'{rule}_10bps']
        subperiods[rule]={'first_12':period_metrics(run['monthly'][:12]),'last_12':period_metrics(run['monthly'][12:])}
        constraints[rule]=capacity_and_constraints(returns,run,liquidity)
    rows=result['replays']['candidate_10bps']['monthly']
    checks=monitoring(rows)
    all_trades=[item for values in constraints.values() for item in values]
    cap_rows=capacity_and_constraints(returns,result['replays']['candidate_cap50_10bps'],liquidity)
    lowest=[item['hypothetical_nav_at_1pct_participation'] for item in all_trades if item['hypothetical_nav_at_1pct_participation'] is not None]
    locked_path=ROOT/'evidence/locked-exercise/execution.json'
    locked=json.loads(locked_path.read_text()) if locked_path.exists() else None
    files=['review_analysis.py','outputs/visible_output.json','data/prices.csv','data/price-provenance.json']
    if locked:files+=['evidence/locked-exercise/execution.json','evidence/locked-exercise/precommit.json']
    baseline=json.loads((ROOT/'baseline/prior-portfolio-snapshot/personal-results.json').read_text())
    files+=['baseline/prior-portfolio-snapshot/personal-results.json']
    out={'generated_at_utc':datetime.now(timezone.utc).isoformat(),
         'purpose':'Post-result audit; no strategy retuning or new independent holdout claimed.',
         'file_hashes':{name:a.sha(ROOT/name) for name in files},
         'source_checks':{'monthly_prices_reconstructed':sum(item['monthly_values_reconstructed'] for item in sources),
                          'price_months':len(prices),'return_months':len(returns),
                          'missing_prices':int(prices.isna().sum().sum()),'filled_prices':0},
         'edition_a':{'label':'Edition A - retrospective baseline',
                      'source':'Unchanged selected earlier portfolio results; original provenance retained.',
                      'checkpoint_status':'Original designated Brightspace checkpoint receipt is not established.',
                      'estimated_all_months':baseline['runs']['all_months'],
                      'estimated_last_36':baseline['runs']['last_36'],
                      'metric_boundary':'These are full-sample estimated annual metrics, not the rolling replay cumulative returns.'},
         'subperiods':subperiods,'constraints_and_liquidity':constraints,
         'cap50_constraint_audit':cap_rows,
         'capacity_proxy':{'illustrative_pretrade_nav_usd':1_000_000,'participation_threshold':.01,
                           'lookback_sessions':20,'max_participation_fraction':max(item['participation_fraction'] for item in all_trades),
                           'minimum_hypothetical_nav_at_threshold_usd':min(lowest),
                           'limitation':'Historical close times raw volume proxy, not an executable capacity estimate; fixed $1m pretrade NAV is illustrative. Same-boundary timing, spreads, impact, routing and source revisions remain unverified.'},
         'monitoring':{'observations':checks,'target_breach_count':sum(x['target_movement_breach'] for x in checks),
                       'volatility_breach_count':sum(x['volatility_breach'] for x in checks),
                       'unavailable_volatility_months':sum(x['trailing_12_month_net_volatility'] is None for x in checks),
                       'interpretation':'Diagnostic application of accepted limits to past returns; the replay was not halted or retuned at these breaches.'},
         'locked_comparison':{'before':locked['before']['summary'],'after':locked['after']['summary']} if locked else None,
         'additional_selection_ledger':[
             {'case':'first and last 12 replay months','scope':'all three baseline-cost rules','status':'executed','claim':'post-result descriptive subperiod check'},
             {'case':'prior-20-session dollar volume','scope':'all three rules; $1m illustrative NAV; 1% proxy limit','status':'executed','claim':'liquidity proxy only'},
             {'case':'monitor existing 15-point and 22% limits','scope':'candidate, same replay','status':'executed','claim':'diagnostic only'},
             {'case':'student-selected 24-month window','scope':'preserved prior execution record','status':'retained','claim':'not a new untouched test'}]}
    (ROOT/'outputs/review_evidence.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'source_checks':out['source_checks'],'capacity_proxy':out['capacity_proxy'],
                      'monitoring':{k:v for k,v in out['monitoring'].items() if k!='observations'},'subperiods':subperiods},indent=2))
    return out


if __name__=='__main__':build()

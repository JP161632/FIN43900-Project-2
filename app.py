"""Render frozen, validated results; no portfolio calculations in the UI."""
import json
import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent


def load_contract(path):
    contract=json.loads(path.read_text(encoding='utf-8'))
    for name,digest in contract.get('file_hashes',{}).items():
        source=ROOT/name
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=digest:
            raise ValueError('Frozen output is stale or missing an input: '+name)
    return contract

st.set_page_config(page_title='Portfolio Committee Review', layout='wide')
st.title('Portfolio Committee Review')
st.caption('NVDA / MSFT / TSM / QCOM | Portfolio process evaluation')
try:
    result = load_contract(ROOT/'outputs/visible_output.json')
except (OSError, ValueError) as error:
    st.error(f'Cannot load research output. Run python analysis.py first. Detail: {error}')
    st.stop()
st.warning(result['decision'])
st.write(result['decision_reason'])
st.caption(result['information_boundary'])
st.info('Previously inspected historical replay, not an untouched holdout. Modeled same-boundary execution is idealized. No real-money pilot has occurred.')
st.header('Compare portfolio rules')
cost = st.selectbox('One-way trading cost (basis points)', [0, 10, 25, 50], index=1)
names = ['equal', 'inverse_vol', 'candidate']
labels = {'equal': 'Equal weight', 'inverse_vol': 'Inverse volatility', 'candidate': 'Minimum estimated volatility'}
summaries = [result['replays'][f'{name}_{cost}bps']['summary'] for name in names]
table = pd.DataFrame([{'Rule': labels[s['rule']],
                      'Net cumulative return': f"{s['net_total_return']:.2%}",
                      'Net CAGR': f"{s['net_cagr']:.2%}",
                      'Annualized net volatility': f"{s['net_volatility']:.2%}",
                      'Month-end max drawdown': f"{s['max_drawdown_month_end']:.2%}",
                      'Infeasible rebalances': s['infeasible_rebalances']} for s in summaries])
st.dataframe(table, hide_index=True, width='stretch')
series = {labels[name]: {row['date']: row['net_wealth'] for row in result['replays'][f'{name}_{cost}bps']['monthly']} for name in names}
chart = pd.DataFrame(series)
chart.index = pd.to_datetime(chart.index)
st.line_chart(chart)
st.caption('Net wealth per $1 at replay start; first plotted point is after the first return. Includes initial purchase costs. Monthly adjusted-price returns; quarterly target rebalancing with drift between trades. Drawdown uses the initial $1 as well as subsequent month-end wealth.')
st.header('Historical estimates and stability')
weights = pd.DataFrame({labels[name]: item['weights'] for name, item in result['full_sample_comparison'].items()})
st.dataframe(weights.style.format('{:.1%}'), width='stretch')
st.caption('Full 60-month estimated weights are descriptive outputs, not the rolling allocations used in the replay or a current trading instruction.')
st.metric('Largest weight shift: 60-month vs 36-month estimates', f"{result['sensitivities']['window_largest_weight_change_points']:.1f} percentage points")
with st.expander('50% target concentration-cap scenario'):
    st.json(result['replays']['candidate_cap50_10bps']['summary'])
    st.write('The cap applies at target trades; market drift can breach it between trades. It is a separate research scenario, not an approved client rule.')
with st.expander('Data provenance and conventions'):
    st.dataframe(pd.DataFrame([{k: s[k] for k in ['ticker','currency','retrieved_at_utc','first_price_date','last_price_date','monthly_values_reconstructed']} for s in result['sources']]), hide_index=True, width='stretch')
    st.write('Arithmetic monthly mean × 12; sample monthly standard deviation × sqrt(12); covariance from aligned monthly returns. Annualized historical means are not forecasts. Adjustments are those in the archived download, not historical vintages.')
    st.write('One-way cost is applied to every dollar bought or sold, including initial deployment. Cash fallback earns zero. Taxes, market impact, bid/ask variation, ADR fees and execution delay are unmodeled.')
with st.expander('Uncertainty and evidence limits'):
    st.json(result['paired_block_interval'])
    st.write('The interval describes the annualized arithmetic mean return difference between candidate and equal weight. It is not a confidence interval for CAGR or future performance.')
    st.write('Suitability, independent holdout, source redistribution rights and executable timing remain unresolved. Three investor personas sharing SEC facts do not provide independent corroboration.')
st.download_button('Download complete frozen research output', json.dumps(result, indent=2), 'visible_output.json', 'application/json')

st.header('Model-risk review')
try:
    review=load_contract(ROOT/'outputs/review_evidence.json')
except (OSError,ValueError):
    st.warning('Supplemental review is unavailable. Run python review_analysis.py.')
else:
    st.subheader('Edition A - retrospective baseline')
    st.dataframe(pd.DataFrame([
        {'Estimate window':'All 60 monthly returns',
         'Historical annual mean':f"{review['edition_a']['estimated_all_months']['return']:.2%}",
         'Estimated annual volatility':f"{review['edition_a']['estimated_all_months']['volatility']:.2%}"},
        {'Estimate window':'Final 36 monthly returns',
         'Historical annual mean':f"{review['edition_a']['estimated_last_36']['return']:.2%}",
         'Estimated annual volatility':f"{review['edition_a']['estimated_last_36']['volatility']:.2%}"}
    ]),hide_index=True,width='stretch')
    st.caption(review['edition_a']['metric_boundary'])
    st.caption(review['edition_a']['checkpoint_status'])
    st.subheader('Subperiod comparison')
    period_rows=[]
    for rule,periods in review['subperiods'].items():
        for label,item in periods.items():
            period_rows.append({'Rule':labels[rule],'Period':f"{item['start']} to {item['end']}",
                               'Net cumulative return':f"{item['net_total_return']:.2%}",
                               'Annualized net volatility':f"{item['net_volatility']:.2%}"})
    st.dataframe(pd.DataFrame(period_rows),hide_index=True,width='stretch')
    st.caption('Descriptive split after seeing the original results. Same strategy and costs; no tuning or independent holdout claim.')
    st.subheader('Monitoring and constraint audit')
    first,second=st.columns(2)
    first.metric('Quarterly target-change breaches',str(review['monitoring']['target_breach_count']))
    second.metric('Trailing-volatility breach months',str(review['monitoring']['volatility_breach_count']))
    st.write('The first 11 replay months have insufficient history for the 12-month realized-volatility check. These are diagnostic flags; the historical replay was not halted at the flags.')
    with st.expander('Illustrative liquidity and target-constraint evidence'):
        proxy=review['capacity_proxy']
        st.write(f"At an illustrative $1 million pretrade NAV, the largest trade was {proxy['max_participation_fraction']:.4%} of the prior 20-session average daily dollar volume.")
        st.write(proxy['limitation'])
        st.write('Target checks cover funding, long-only bounds, the candidate historical-mean hurdle and the separate concentration cap. A passing liquidity proxy does not override a failed investment case.')
    st.subheader('Preserved changed-input comparison')
    if review['locked_comparison']:
        before=review['locked_comparison']['before'];after=review['locked_comparison']['after']
        st.dataframe(pd.DataFrame([
            {'Estimation window':'36 months','Net cumulative return':f"{before['net_total_return']:.2%}",
             'Realized net volatility':f"{before['net_volatility']:.2%}",'Largest quarterly target change':f"{before['max_target_change_points']:.0f} percentage points"},
            {'Estimation window':'24 months','Net cumulative return':f"{after['net_total_return']:.2%}",
             'Realized net volatility':f"{after['net_volatility']:.2%}",'Largest quarterly target change':f"{after['max_target_change_points']:.0f} percentage points"}
        ]),hide_index=True,width='stretch')
        st.caption('Exact prior prediction and execution retained separately. Results were not retuned to match the prediction.')

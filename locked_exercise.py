"""Freeze a student-written prediction, then run one unseen lookback case.

Never invoke execute on the student's real case before its genuine prediction is
preserved. An exclusive-create archive and hashes detect later changes but are
not external timestamp certification or proof of authorship.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

import analysis as a

ROOT = Path(__file__).resolve().parent
DEST = ROOT/'evidence/locked-exercise'
FIELDS = ['expected_output_direction', 'finance_reasoning', 'expected_decision_effect', 'authorship_attestation']


def validate(record):
    value = record.get('new_lookback_months')
    if isinstance(value, bool) or not isinstance(value, int) or not 12 <= value <= 35:
        raise ValueError('Choose an integer lookback from 12 to 35; original value is 36 monthly returns.')
    for name in FIELDS:
        if not isinstance(record.get(name), str) or len(record[name].strip()) < 15:
            raise ValueError('Write your own substantive response in '+name)
    return record


def snapshot_files():
    paths = [ROOT/'analysis.py', ROOT/'vendor/portfolio.py', ROOT/'locked_exercise.py',
             ROOT/'requirements.txt', ROOT/'docs/research-design.md',
             ROOT/'data/prices.csv', ROOT/'data/price-provenance.json']
    paths += sorted((ROOT/'data/sources').glob('*.json'))
    return {str(path.relative_to(ROOT)).replace('\\','/'): a.sha(path) for path in paths}


def freeze(path):
    record = validate(json.loads(Path(path).read_text(encoding='utf-8-sig')))
    DEST.mkdir(parents=True, exist_ok=True)
    if any((DEST/name).exists() for name in ['precommit.json','snapshot.zip','execution.json']):
        raise ValueError('Existing record preserved. Do not overwrite or reconstruct the prediction.')
    manifest = snapshot_files()
    saved = {'precommitted_at_utc': datetime.now(timezone.utc).isoformat(),
             'input': 'rolling estimation lookback', 'old_value': 36, 'units': 'monthly returns',
             'prediction': record, 'files': manifest,
             'limitations': 'Local clock and hashes are not an externally authenticated timestamp or proof of authorship.'}
    with zipfile.ZipFile(DEST/'snapshot.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for name in manifest: archive.write(ROOT/name,name)
        archive.writestr('student-prediction.json', json.dumps(record,indent=2))
    saved['snapshot_sha256'] = a.sha(DEST/'snapshot.zip')
    with (DEST/'precommit.json').open('x',encoding='utf-8') as handle:
        json.dump(saved,handle,indent=2);handle.write('\n')
    print('Prediction and exact code/data archive preserved. No portfolio case was run.')
    print('Snapshot SHA-256: '+saved['snapshot_sha256'])


def execute():
    precommit_bytes = (DEST/'precommit.json').read_bytes()
    saved = json.loads(precommit_bytes)
    if snapshot_files() != saved['files'] or a.sha(DEST/'snapshot.zip') != saved['snapshot_sha256']:
        raise ValueError('Code, data or archive changed after prediction; preserve and resolve the discrepancy.')
    if (DEST/'execution.json').exists():
        raise ValueError('Execution record already exists. Preserve the original run.')
    record = validate(saved['prediction'])
    prices, _ = a.audit_sources()
    returns = prices.pct_change(fill_method=None).iloc[1:]
    before = a.replay(returns,'candidate',lookback=36)
    after = a.replay(returns,'candidate',lookback=record['new_lookback_months'])
    metric_names = ['net_total_return','net_cagr','net_volatility','max_drawdown_month_end',
                    'max_target_change_points','infeasible_rebalances']
    out = {'executed_at_utc':datetime.now(timezone.utc).isoformat(),
           'precommit_sha256':hashlib.sha256(precommit_bytes).hexdigest(),
           'snapshot_sha256':saved['snapshot_sha256'], 'preserved_prediction':record,
           'before':before,'after':after,
           'differences':{name:after['summary'][name]-before['summary'][name] for name in metric_names},
           'student_interpretation_status':'Pending actual decision effect and prediction reconciliation.'}
    with (DEST/'execution.json').open('x',encoding='utf-8') as handle:
        json.dump(out,handle,indent=2,allow_nan=False);handle.write('\n')
    lines=['# Preserved locked execution','',
           'Original lookback: 36 monthly returns. Changed lookback: '+str(record['new_lookback_months'])+'.',
           'Evaluation months, costs, universe, grid, hurdle and trade schedule are held fixed.','',
           '| Metric | Before | After |','|---|---:|---:|']
    for name in metric_names:
        lines.append(f"| {name} | {before['summary'][name]:.8f} | {after['summary'][name]:.8f} |")
    lines += ['', 'Return/volatility/drawdown are decimals. Target movement is in percentage points.',
              '', '## Student must complete after reviewing the actual result',
              '', '- Actual decision effect:', '- Prediction reconciliation:',
              '- Failure diagnosis or why the action did not change:',
              '', 'Do not edit the saved prediction, archive or execution JSON.']
    with (DEST/'student-reconciliation.md').open('x',encoding='utf-8') as handle:
        handle.write('\n'.join(lines)+'\n')
    print('Saved execution.json and student-reconciliation.md. Complete your own interpretation.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--freeze',metavar='STUDENT_JSON')
    group.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    try:
        freeze(args.freeze) if args.freeze else execute()
    except (OSError,ValueError,KeyError) as error:
        parser.exit(1,'Cannot continue: '+str(error)+'\n')

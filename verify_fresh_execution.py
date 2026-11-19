"""Verify saved student evidence without executing another portfolio scenario."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import zipfile

ROOT=Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_record(root=ROOT):
    folder=root/'evidence/fresh-locked-exercise'
    pre=json.loads((folder/'precommit.json').read_text(encoding='utf-8'))
    execution=json.loads((folder/'execution.json').read_text(encoding='utf-8'))
    prediction=json.loads((root/'docs/fresh-prediction-input.json').read_text(encoding='utf-8'))
    checks=[]
    if sha(folder/'precommit.json')!=execution['precommit_sha256']:raise ValueError('Precommit hash differs')
    if sha(folder/'snapshot.zip')!=pre['snapshot_sha256'] or pre['snapshot_sha256']!=execution['snapshot_sha256']:raise ValueError('Snapshot hash differs')
    checks.append('Precommit and code/data archive hashes match execution')
    if prediction!=pre['prediction'] or prediction!=execution['preserved_prediction']:raise ValueError('Saved prediction differs')
    receipt=json.loads((root/'evidence/fresh-prediction-receipt.json').read_text(encoding='utf-8'))
    for name,digest in receipt['file_hashes'].items():
        if sha(root/name)!=digest:raise ValueError('Collected prediction source changed: '+name)
    checks.append('Collected and frozen prediction remain unchanged')
    with zipfile.ZipFile(folder/'snapshot.zip') as saved:
        for name,digest in pre['files'].items():
            if hashlib.sha256(saved.read(name)).hexdigest()!=digest:raise ValueError('Archive member differs: '+name)
        if json.loads(saved.read('student-prediction.json'))!=prediction:raise ValueError('Archived prediction differs')
    checks.append('All archived source/data members and archived prediction match')
    if not datetime.fromisoformat(receipt['preserved_at_utc'])<datetime.fromisoformat(pre['precommitted_at_utc'])<datetime.fromisoformat(execution['executed_at_utc']):raise ValueError('Local record order differs')
    checks.append('Recorded collection precedes freeze and execution; local timestamps only')
    visible=json.loads((root/'outputs/visible_output.json').read_text(encoding='utf-8'))
    if execution['before']!=visible['replays']['candidate_10bps']:raise ValueError('Before case differs from original visible output')
    checks.append('Before case matches original 36-month replay')
    for name,lookback in [('before',36),('after',30)]:
        run=execution[name];summary=run['summary'];rows=run['monthly']
        if summary['lookback_months']!=lookback or len(rows)!=24 or summary['cost_bps_one_way']!=10:raise ValueError('Wrong scenario controls')
        if any(row['training_end']>=row['date'] for row in rows):raise ValueError('Training boundary is not earlier')
        returns=[row['net_return'] for row in rows]
        wealth=[1.0]
        for value in returns:wealth.append(wealth[-1]*(1+value))
        peak=1.0;drawdown=0.0
        for value in wealth:
            peak=max(peak,value);drawdown=min(drawdown,value/peak-1)
        targets=[row['start_weights'] for row in rows if row['rebalance']]
        target_change=max(max(abs(a[t]-b[t])*100 for t in a) for a,b in zip(targets,targets[1:]))
        calculated={'net_total_return':wealth[-1]-1,'net_cagr':wealth[-1]**(12/len(rows))-1,
                    'net_volatility':statistics.stdev(returns)*math.sqrt(12),
                    'max_drawdown_month_end':drawdown,'max_target_change_points':target_change}
        for metric,value in calculated.items():
            if not math.isclose(value,summary[metric],rel_tol=1e-11,abs_tol=1e-12):raise ValueError('Saved monthly rows fail reconciliation: '+name+' '+metric)
        checks.append(name+': compound return, CAGR, sample volatility, drawdown and target changes reconcile independently')
    text=(folder/'student-reconciliation.md').read_text(encoding='utf-8')
    for field in ['Actual decision effect:','Prediction reconciliation:','Failure diagnosis or why the action did not change:']:
        if field not in text or len(text.split(field,1)[1].split('\n')[0].strip())<20:raise ValueError('Missing student reconciliation: '+field)
    checks.append('Saved student reconciliation supplies direction, decision effect and explanation')
    return {'passed':True,'method':'Read-only hash, ordering and independent saved-ledger arithmetic checks; no portfolio scenario rerun.',
            'checks':checks,'snapshot_sha256':pre['snapshot_sha256'],'precommit_sha256':execution['precommit_sha256'],
            'prediction_at_utc':pre['precommitted_at_utc'],'execution_at_utc':execution['executed_at_utc'],
            'before':execution['before']['summary'],'after':execution['after']['summary'],
            'human_evidence':'Student reports independent closed-tool drafting and execution; tool state and identity are self-attested, not independently observed.',
            'original_history':'Earlier 24-month assistant execution remains preserved separately.'}

if __name__=='__main__':
    result=verify_record();result['verified_at_utc']=datetime.now(timezone.utc).isoformat()
    (ROOT/'evidence/fresh-execution-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

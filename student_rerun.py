"""Student rerun of the original archived case, after its outcome was already seen.

This preserves the original prediction/run and makes no new unseen-test claim.
The assistant may verify the archive but must not launch a purported student run.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path,PurePosixPath
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parent
EVIDENCE=ROOT/'evidence/locked-exercise'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    original=json.loads((EVIDENCE/'precommit.json').read_text())
    execution=json.loads((EVIDENCE/'execution.json').read_text())
    archive=EVIDENCE/'snapshot.zip'
    if digest(archive)!=original['snapshot_sha256'] or digest(archive)!=execution['snapshot_sha256']:
        raise ValueError('Original snapshot hash mismatch.')
    if digest(EVIDENCE/'precommit.json')!=execution['precommit_sha256']:
        raise ValueError('Original prediction/precommit hash mismatch.')
    with zipfile.ZipFile(archive) as saved:
        for name in saved.namelist():
            normalized=PurePosixPath(name)
            if normalized.is_absolute() or '..' in normalized.parts or ':' in name or '\\' in name:
                raise ValueError('Unsafe archive member: '+name)
        for name,expected in original['files'].items():
            if hashlib.sha256(saved.read(name)).hexdigest()!=expected:
                raise ValueError('Archived source mismatch: '+name)
        if json.loads(saved.read('student-prediction.json'))!=original['prediction']:
            raise ValueError('Archived prediction mismatch.')
    return original,execution


def run(tools_closed):
    if not tools_closed:raise ValueError('Close generative tools, then use --tools-closed only if that statement is true.')
    original,execution=verify()
    record=EVIDENCE/'student-rerun.json'
    if record.exists():raise ValueError('A student rerun is already preserved; do not overwrite it.')
    with tempfile.TemporaryDirectory(prefix='project2-student-rerun-') as temporary:
        target=Path(temporary).resolve()
        with zipfile.ZipFile(EVIDENCE/'snapshot.zip') as saved:
            for name in saved.namelist():
                destination=(target/name).resolve()
                if target not in destination.parents:raise ValueError('Archive member leaves the replay directory.')
            saved.extractall(target)
        script=('import json; import analysis as a; '
                'p,_=a.audit_sources(); r=p.pct_change(fill_method=None).iloc[1:]; '
                'pred=json.load(open("student-prediction.json")); '
                'print(json.dumps({"before":a.replay(r,"candidate",lookback=36),'
                '"after":a.replay(r,"candidate",lookback=pred["new_lookback_months"])}))')
        completed=subprocess.run([sys.executable,'-c',script],cwd=target,capture_output=True,text=True,timeout=120)
        if completed.returncode:raise RuntimeError(completed.stderr)
        actual=json.loads(completed.stdout)
    matches=actual['before']==execution['before'] and actual['after']==execution['after']
    out={'rerun_at_utc':datetime.now(timezone.utc).isoformat(),
         'record_type':'Student-labelled rerun after original outcome was reviewed; not a new unseen prediction exercise.',
         'tools_closed_self_attestation':tools_closed,
         'operator_identity':'Not independently observed; student initiates the prescribed command.',
         'original_snapshot_sha256':original['snapshot_sha256'],
         'original_prediction_unchanged':True,'matches_original_result':matches,
         'before':actual['before']['summary'],'after':actual['after']['summary'],
         'formal_requirement':'A rerun demonstrates reproduction; acceptance as checkpoint recovery is not inferred.'}
    with record.open('x',encoding='utf-8') as handle:json.dump(out,handle,indent=2);handle.write('\n')
    print('Student-labelled rerun saved. Exact match to original result: '+str(matches))
    print('This is a rerun after outcome review; original history and prediction remain unchanged.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--verify-only',action='store_true')
    mode.add_argument('--run',action='store_true')
    parser.add_argument('--tools-closed',action='store_true')
    args=parser.parse_args()
    try:
        if args.verify_only:verify();print('Original archive and prediction verified. No scenario executed.')
        else:run(args.tools_closed)
    except (OSError,ValueError,KeyError,RuntimeError) as error:parser.exit(1,str(error)+'\n')

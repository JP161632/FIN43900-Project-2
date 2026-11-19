"""Verify an isolated project copy using a separately installed Python environment."""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parent


def comparable(document,review=False):
    copy=json.loads(json.dumps(document))
    copy.pop('generated_at_utc',None)
    if review:copy.get('file_hashes',{}).pop('outputs/visible_output.json',None)
    return copy


def main():
    clean_python=Path(sys.argv[1]).resolve()
    if not clean_python.is_file():raise ValueError('Provide the installed clean-environment Python executable.')
    started=time.monotonic();commands=[]
    env=dict(os.environ);env.pop('PYTHONPATH',None)
    with tempfile.TemporaryDirectory(prefix='project2-clean-') as temporary:
        target=Path(temporary)/'project'
        shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('tmp','.venv','__pycache__','pdf-qa'))
        for script in ['analysis.py','review_analysis.py','tests.py','test_review.py','verify_app.py']:
            completed=subprocess.run([str(clean_python),str(target/script)],cwd=temporary,
                                     env=env,capture_output=True,text=True,timeout=120)
            commands.append({'script':script,'exit_code':completed.returncode,
                             'stdout':completed.stdout,'stderr':completed.stderr})
            if completed.returncode:break
        comparisons={}
        for name,review in [('visible_output.json',False),('review_evidence.json',True)]:
            original=json.loads((ROOT/'outputs'/name).read_text())
            reproduced=json.loads((target/'outputs'/name).read_text())
            comparisons[name]=comparable(original,review)==comparable(reproduced,review)
        dependencies=subprocess.run([str(clean_python),'-m','pip','check'],capture_output=True,text=True,timeout=30)
        freeze=subprocess.run([str(clean_python),'-m','pip','freeze'],capture_output=True,text=True,timeout=30)
        report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),
                'passed':all(item['exit_code']==0 for item in commands) and all(comparisons.values()) and dependencies.returncode==0,
                'method':'New venv without system-site-packages; requirements installed from package index; isolated copied project and unrelated working directory.',
                'first_failure':'Existing course environment had no pip module; initial sandbox package download was denied.',
                'resolution':'Created a new venv with ensurepip and installed pinned requirements with approved network access.',
                'remaining_limit':'Automated clean installation and replay, not an observed unaided human reviewer or evidence of student code ownership.',
                'elapsed_seconds':round(time.monotonic()-started,3),'material_output_comparisons':comparisons,
                'dependency_check':dependencies.stdout,'commands':commands}
        (ROOT/'evidence/clean-install.json').write_text(json.dumps(report,indent=2)+'\n')
        if freeze.returncode==0:(ROOT/'requirements-lock.txt').write_text(freeze.stdout)
    print(json.dumps({key:value for key,value in report.items() if key!='commands'},indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()

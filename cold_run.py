"""Fresh process and isolated project copy; not a clean dependency install."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
start = time.monotonic()
with tempfile.TemporaryDirectory(prefix='project2-replay-') as temporary:
    target = Path(temporary)/'project'
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__', '.venv', '*.pdf', 'pdf-qa', 'tmp'))
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    completed = subprocess.run([sys.executable, str(target/'analysis.py')], cwd=temporary,
                               env=env, capture_output=True, text=True, timeout=120)
    identical = False
    if completed.returncode == 0:
        original = json.loads((ROOT/'outputs/visible_output.json').read_text())
        replayed = json.loads((target/'outputs/visible_output.json').read_text())
        original.pop('generated_at_utc'); replayed.pop('generated_at_utc')
        identical = original == replayed
    record = {'passed': completed.returncode == 0 and identical,
              'method': 'Fresh Python process, isolated copied project, unrelated working directory, existing course interpreter',
              'command': 'python <isolated-copy>/analysis.py', 'python': sys.version,
              'environment_limitation': 'Existing installed dependencies reused. No clean dependency installation or unaided human cold run claimed.',
              'first_failure': None if completed.returncode == 0 else completed.stderr,
              'exit_code': completed.returncode, 'identical_except_run_timestamp': identical,
              'elapsed_seconds': round(time.monotonic()-start, 3), 'stdout': completed.stdout}
(ROOT/'evidence/cold-run.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record, indent=2))
raise SystemExit(0 if record['passed'] else 1)

"""Prepare a fresh 30-month case without supplying a prediction or running it here.

The student must write the prediction and launch both phases with generative tools
closed. Original 24-month evidence is never modified. No result is precomputed.
"""
import argparse
from pathlib import Path
import locked_exercise as original

ROOT=Path(__file__).resolve().parent
original.DEST=ROOT/'evidence/fresh-locked-exercise'
base_snapshot=original.snapshot_files
base_validate=original.validate

def snapshot_files():
    files=base_snapshot()
    files['fresh_locked_exercise.py']=original.a.sha(ROOT/'fresh_locked_exercise.py')
    return files

def validate(record):
    record=base_validate(record)
    if record['new_lookback_months']!=30:
        raise ValueError('This prepared case changes 36 to 30 monthly returns. The previously revealed 24-month case is excluded.')
    for field in original.FIELDS:
        if 'WRITE YOUR' in record[field].upper():
            raise ValueError('Replace every prediction placeholder yourself with generative tools closed.')
    return record

original.snapshot_files=snapshot_files
original.validate=validate

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--freeze',type=Path)
    action.add_argument('--execute',action='store_true')
    parser.add_argument('--tools-closed',action='store_true')
    args=parser.parse_args()
    if not args.tools_closed:parser.error('Close generative tools before either phase; use --tools-closed only when true.')
    try:
        if args.freeze:original.freeze(args.freeze)
        else:original.execute()
    except (OSError,ValueError,KeyError,RuntimeError) as error:parser.exit(1,str(error)+'\n')

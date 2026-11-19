"""Freeze an honest inventory and mechanical readiness report; never assign grades."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import analysis

ROOT = Path(__file__).resolve().parent
ITEMS = [
    ('Research-Evolution.pdf', 'Research-Evolution.pdf'),
    ('Repository', 'README.md'),
    ('Visible executed output', 'outputs/visible_output.json'),
    ('Decision memo or deck', 'Decision-Memo.pdf'),
    ('Validation-and-AI-Use.pdf', 'Validation-and-AI-Use.pdf'),
    ('Video 1', ''), ('Transcript Video 1', ''),
    ('Video 2', ''), ('Transcript Video 2', ''),
    ('Video 3', ''), ('Transcript Video 3', ''), ('Optional deployed output', '')]
COLUMNS = ['item','required','location_or_url','title','duration_or_as_of',
           'timestamp_index','access_checked','frozen_or_commit_id','notes']


def main():
    result = json.loads((ROOT/'outputs/visible_output.json').read_text())
    stale = [name for name, digest in result['file_hashes'].items() if analysis.sha(ROOT/name) != digest]
    if stale: raise ValueError('Regenerate analysis output for changed inputs: '+', '.join(stale))
    records = []
    manifest = ROOT/'submission-manifest.csv'
    existing = {}
    if manifest.exists():
        with manifest.open(newline='',encoding='utf-8') as handle:
            existing = {row['item']: row for row in csv.DictReader(handle)}
    for item, local in ITEMS:
        row = {key: '' for key in COLUMNS}
        row.update(item=item,required='no' if item == 'Optional deployed output' else 'yes')
        if item in existing: row.update(existing[item])
        if local:
            # Preserve published reviewer URLs; a local artifact is still hashed below.
            if not row['location_or_url'].startswith(('https://', 'http://')):
                row['location_or_url'] = local
            if item != 'Repository' or not row['frozen_or_commit_id'].startswith('tag:'):
                row['frozen_or_commit_id'] = 'sha256:'+analysis.sha(ROOT/local)
            if item != 'Repository':
                row['duration_or_as_of'] = result['generated_at_utc']
            row['notes'] = ('Local artifact hash verified. '+
                ('Access confirmed in retained evidence.' if row['access_checked'].lower()=='yes'
                 else 'Instructional-team access remains unverified.'))
        elif row['location_or_url'] and item.startswith('Transcript'):
            transcript=ROOT/'docs'/('transcript-video-'+item[-1]+'.txt')
            if not transcript.is_file():raise ValueError('Missing transcript: '+str(transcript))
            row['frozen_or_commit_id']='sha256:'+analysis.sha(transcript)
        elif not row['location_or_url']:
            row['notes'] = 'Not created; rehearsal scripts are not recorded videos or actual transcripts.' if row['required']=='yes' else 'Optional; no deployment performed.'
        records.append(row)
    with manifest.open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=COLUMNS);writer.writeheader();writer.writerows(records)
    inventory={}
    for directory,subdirectories,filenames in ROOT.walk():
        subdirectories[:]=[name for name in subdirectories if name not in ['__pycache__','.venv','.git','pdf-qa','tmp','dist','submission-files']]
        for filename in sorted(filenames):
            path=directory/filename
            relative=path.relative_to(ROOT).as_posix()
            if relative not in ['evidence/file-integrity.json','evidence/package-readiness.json']:
                inventory[relative]=analysis.sha(path)
    (ROOT/'evidence/file-integrity.json').write_text(json.dumps(inventory,indent=2)+'\n')
    gaps=list(result['required_human_evidence'])
    if (ROOT/'evidence/locked-exercise/execution.json').exists():
        gaps=[('Locked-test execution-mode condition unresolved; prediction, result and reflection recorded'
               if item=='Locked changed-input exercise' else item) for item in gaps]
    if (ROOT/'evidence/locked-exercise/student-rerun-attestation.json').exists():
        gaps=[('AI-closed student rerun self-reported; saved rerun output still requires verification'
               if item.startswith('Locked-test execution-mode') else item) for item in gaps]
    fresh_verification=None
    if (ROOT/'evidence/fresh-locked-exercise/execution.json').exists():
        from verify_fresh_execution import verify_record
        fresh_verification=verify_record()
        gaps=[item for item in gaps if not item.startswith(('Locked changed-input','Locked-test execution-mode','AI-closed student rerun'))]
    video_items=[r for r in records if r['item'].startswith('Video ')]
    transcript_items=[r for r in records if r['item'].startswith('Transcript Video ')]
    if len(video_items)==3 and len(transcript_items)==3 and all(r['location_or_url'] for r in video_items+transcript_items):
        gaps=[item for item in gaps if item!='Three actual videos and transcripts']
        gaps.append('Webcam presence and audiovisual alignment require verification; durations verified from public page metadata')
    gaps=[('Student code defense: recorded captions supplied; actual visual demonstration remains unverified'
           if item=='Student code defense' else item) for item in gaps]
    gaps.append('Video 1 explicit AI-output check/disposition not established by supplied transcript')
    if all(row['access_checked'].lower()=='yes' for row in video_items):
        gaps=[('Private-repository instructional-team access remains unverified'
               if item=='Repository/video access checks' else item) for item in gaps]
    report={'audited_at_utc':datetime.now(timezone.utc).isoformat(),
            'manifest_rows':len(records),'required_rows':sum(r['required']=='yes' for r in records),
            'missing_required_locations':[r['item'] for r in records if r['required']=='yes' and not r['location_or_url']],
            'access_unverified':[r['item'] for r in records if r['required']=='yes' and r['access_checked'].lower()!='yes'],
            'substantive_gaps':gaps,
            'fresh_student_record_verified':fresh_verification is not None,
            'submission_ready':False,
            'meaning':'Mechanical inventory only; no grade, authorship or instructor approval inferred.'}
    (ROOT/'evidence/package-readiness.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

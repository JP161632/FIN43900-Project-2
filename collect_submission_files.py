"""Collect final attachments and related documents without changing source evidence."""
import hashlib
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parent
ATTACHMENTS=['Research-Evolution.pdf','Decision-Memo.pdf','Validation-and-AI-Use.pdf',
             'transcript-video-1.txt','transcript-video-2.txt','transcript-video-3.txt',
             'submission-manifest.csv']

def copy_verified(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
    if hashlib.sha256(source.read_bytes()).digest()!=hashlib.sha256(target.read_bytes()).digest():
        raise ValueError('Collection copy mismatch: '+str(source))

def main():
    collection=ROOT/'submission-files'
    uploads=collection/'01-UPLOAD-TO-BRIGHTSPACE'
    supporting=collection/'02-SUPPORTING-DOCUMENTS'
    for name in ATTACHMENTS:
        source=ROOT/'docs'/name if name.startswith('transcript-') else ROOT/name
        copy_verified(source,collection/name)
        copy_verified(source,uploads/name)
    copy_verified(ROOT/'Edition-A-Retrospective-Baseline.pdf',supporting/'Edition-A-Retrospective-Baseline.pdf')
    related_docs=['decision-memo.md','research-evolution.md','validation-and-ai-use.md',
                  'edition-a-retrospective-baseline.md','fresh-prediction-input.json',
                  'fresh-prediction-original.txt','fresh-student-reconciliation-edited.md',
                  'locked-changed-input-record.md','brightspace-rubric-reference.md',
                  'rubric-evidence-map.md','final-grade-review.md','manual-final-steps.md',
                  'research-design.md','prospective-protocol.md','student-decisions.md']
    for name in related_docs:copy_verified(ROOT/'docs'/name,supporting/name)
    for name in ['precommit.json','execution.json','student-reconciliation.md','snapshot.zip','run-log.txt']:
        copy_verified(ROOT/'evidence/fresh-locked-exercise'/name,supporting/'Fresh-30-Month-Exercise'/name)
    for name in ['fresh-execution-verification.json','repository-access-check.json']:
        copy_verified(ROOT/'evidence'/name,supporting/'Verification'/name)
    for name in ['visible_output.json','selection-ledger-addendum.json']:
        copy_verified(ROOT/'outputs'/name,supporting/'Executed-Output'/name)
    copy_verified(ROOT/'docs/manual-final-steps.md',collection/'MANUAL-STEPS.md')
    instructions='''PROJECT 2 - FINAL SUBMISSION COLLECTION

OPEN 01-UPLOAD-TO-BRIGHTSPACE. Its seven files are the required attachments:
Research-Evolution.pdf
Decision-Memo.pdf
Validation-and-AI-Use.pdf
transcript-video-1.txt
transcript-video-2.txt
transcript-video-3.txt
submission-manifest.csv

Paste BRIGHTSPACE-COMMENT.txt into the assignment Comments box. It contains
the public repository link, visible-output link and three YouTube links.

The repository is public and anonymous access was verified. No grader invitation
is required while it remains public. Keep the repository/videos available through
the grade-appeal window.

02-SUPPORTING-DOCUMENTS contains related report sources, the separately labeled
retrospective baseline summary, actual fresh prediction/run/reconciliation and
verification records. These remain in the repository too. They are supporting
copies, not additional mandatory Brightspace attachments.

Your fresh 30-month exercise is complete. Your existing videos are retained.
Known original Edition A and Video 1 evidence gaps remain disclosed. If an
original checkpoint receipt exists, preserve it unchanged. Confirm the remaining
recordings have the required webcam/visual evidence and clear audio.

Submit the seven attachments by the current Brightspace deadline (last inspected:
November 23, 2026 at 11:59 PM), reopen the submission and save the successful receipt.
The ZIP is a convenience archive; attach the seven individual files unless the
assignment explicitly permits the ZIP instead.
'''
    (collection/'START-HERE.txt').write_text(instructions,encoding='utf-8')
    archive=ROOT/'dist/Project-2-Submission-Package.zip'
    archive.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as output:
        for path in sorted(collection.rglob('*')):
            if path.is_file():output.write(path,'Project-2-Submission/'+path.relative_to(collection).as_posix())
    with zipfile.ZipFile(archive) as check:
        if check.testzip():raise ValueError('ZIP integrity check failed')
        for name in ATTACHMENTS:
            if check.read('Project-2-Submission/01-UPLOAD-TO-BRIGHTSPACE/'+name)!=(uploads/name).read_bytes():
                raise ValueError('ZIP attachment differs: '+name)
    print('Collected seven verified attachments and related supporting documents.')
    print(str(archive))

if __name__=='__main__':main()

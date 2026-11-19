"""Regression checks for reviewer URLs and attachment consistency."""
import csv
import contextlib
import io
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import audit_package
import prepare_submission
ROOT=Path(__file__).resolve().parent

class SubmissionChecks(unittest.TestCase):
    def test_audit_preserves_published_reviewer_urls(self):
        import json
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'outputs').mkdir();(root/'evidence').mkdir();(root/'docs').mkdir()
            (root/'outputs/visible_output.json').write_text(json.dumps({'file_hashes':{},'generated_at_utc':'test','required_human_evidence':[]}))
            for _,local in audit_package.ITEMS:
                if local and not (root/local).exists():(root/local).write_text('fixture')
            with (root/'submission-manifest.csv').open('w',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=audit_package.COLUMNS);writer.writeheader()
                writer.writerow({'item':'Repository','required':'yes','location_or_url':'https://example.org/review/repository','access_checked':''})
            def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
            with patch.object(audit_package,'ROOT',root),patch.object(audit_package.analysis,'sha',digest),contextlib.redirect_stdout(io.StringIO()):
                audit_package.main()
            with (root/'submission-manifest.csv').open() as handle:rows=list(csv.DictReader(handle))
            repository=next(row for row in rows if row['item']=='Repository')
            self.assertEqual(repository['location_or_url'],'https://example.org/review/repository')
            self.assertNotEqual(repository['access_checked'],'yes')

    def test_current_manifest_has_all_three_distinct_videos_and_transcripts(self):
        with (ROOT/'submission-manifest.csv').open(encoding='utf-8-sig') as handle:rows=list(csv.DictReader(handle))
        self.assertEqual(len(rows),12);self.assertEqual(sum(row['required']=='yes' for row in rows),11)
        urls=[]
        for number,video_id in prepare_submission.VIDEO_IDS.items():
            video=next(row for row in rows if row['item']==f'Video {number}')
            urls.append(video['location_or_url']);self.assertIn(video_id,video['location_or_url'])
            self.assertIn(video_id,(ROOT/'docs'/f'transcript-video-{number}.txt').read_text())
        self.assertEqual(len(set(urls)),3)

    def test_upload_copies_match_canonical_files(self):
        for name in ['Research-Evolution.pdf','Decision-Memo.pdf','Validation-and-AI-Use.pdf','submission-manifest.csv']:
            self.assertEqual((ROOT/name).read_bytes(),(ROOT/'submission-files'/name).read_bytes())
        for number in range(1,4):
            name=f'transcript-video-{number}.txt'
            self.assertEqual((ROOT/'docs'/name).read_bytes(),(ROOT/'submission-files'/name).read_bytes())

if __name__=='__main__':
    import json
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(SubmissionChecks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    record={'passed':result.wasSuccessful(),'tests_run':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),
            'scope':'Reviewer URL preservation, distinct video/transcript matching, and byte-identical Brightspace attachment copies.'}
    (ROOT/'evidence/submission-checks.json').write_text(json.dumps(record,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)

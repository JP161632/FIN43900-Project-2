"""Refresh linked submission manifest and the seven Brightspace attachments."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
REPO='https://github.com/JP161632/FIN43900-Project-2'
TAG='project-2-review-2026-11-19-final'
LABELS={1:'Research Evolution',2:'Codebase Walkthrough and Validation',3:'Committee Presentation'}
VIDEO_IDS={1:'tMAmXiDBVBg',2:'EZolrbd3xOQ',3:'sqgNrHPguZ4'}
FILES={'Research-Evolution.pdf':'Research-Evolution.pdf','Repository':'README.md',
       'Visible executed output':'outputs/visible_output.json','Decision memo or deck':'Decision-Memo.pdf',
       'Validation-and-AI-Use.pdf':'Validation-and-AI-Use.pdf'}

def main():
    path=ROOT/'submission-manifest.csv'
    with path.open(encoding='utf-8-sig',newline='') as handle:
        reader=csv.DictReader(handle);columns=reader.fieldnames;rows=list(reader)
    metadata={}
    access_path=ROOT/'evidence/video-access-confirmation.json'
    confirmed_ids=(json.loads(access_path.read_text()).get('confirmed_video_ids',[])
                   if access_path.exists() else [])
    if (ROOT/'evidence/video-metadata.json').exists():
        metadata={v['video']:v for v in json.loads((ROOT/'evidence/video-metadata.json').read_text())['videos']}
    for row in rows:
        item=row['item']
        if item in FILES:
            local=FILES[item]
            row['location_or_url']=(REPO+'/tree/'+TAG if item=='Repository' else REPO+'/blob/'+TAG+'/'+local)
            row['title']=row['title'] or item
            row['frozen_or_commit_id']=('tag:'+TAG if item=='Repository' else
                'sha256:'+hashlib.sha256((ROOT/local).read_bytes()).hexdigest())
            row['notes']='Included in private course-review package; grader must be granted access. See release evidence for publication status.'
        if item.startswith('Video '):
            number=int(item[-1]);row['location_or_url']='https://youtu.be/'+VIDEO_IDS[number]
            row['title']='Project 2 Video '+str(number)+' - '+LABELS[number]
            meta=metadata.get(number,{})
            if meta.get('duration_seconds') is not None:
                seconds=meta['duration_seconds'];row['duration_or_as_of']=f'{seconds//60}:{seconds%60:02d} (YouTube page metadata)'
                row['notes']='Student confirmed video links work on November 19. Public page duration within '+('3:00' if number==1 else '5:00')+' limit. Full audiovisual review remains separate.'
            row['access_checked']='yes' if VIDEO_IDS[number] in confirmed_ids else ''
            row['frozen_or_commit_id']='YouTube ID:'+VIDEO_IDS[number]
        if item.startswith('Transcript Video '):
            number=int(item[-1]);local=f'docs/transcript-video-{number}.txt'
            row['location_or_url']=REPO+'/blob/'+TAG+'/'+local
            row['frozen_or_commit_id']='sha256:'+hashlib.sha256((ROOT/local).read_bytes()).hexdigest()
    with path.open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=columns);writer.writeheader();writer.writerows(rows)
    target=ROOT/'submission-files';target.mkdir(exist_ok=True)
    for name in ['Research-Evolution.pdf','Decision-Memo.pdf','Validation-and-AI-Use.pdf','submission-manifest.csv']:
        shutil.copyfile(ROOT/name,target/name)
    for number in VIDEO_IDS:
        name=f'transcript-video-{number}.txt';shutil.copyfile(ROOT/'docs'/name,target/name)
    # Reviewer-facing links stay readable outside a spreadsheet.
    lines=['# Project 2 - submission links','',f'[Private repository]({REPO}/tree/{TAG})','',
           f'[Visible executed output]({REPO}/blob/{TAG}/outputs/visible_output.json)','']
    for number in VIDEO_IDS:
        lines.extend([f'## Video {number} - {LABELS[number]}',f'https://youtu.be/{VIDEO_IDS[number]}',''])
    lines.extend(['Grant the instructional team access to the private repository. Video access and webcam/visual evidence still require human verification.'])
    (target/'OPEN-VIDEO-LINKS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (target/'VIDEO-AND-REPOSITORY-LINKS.txt').write_text('\n'.join(line for line in lines if not line.startswith('#'))+'\n',encoding='utf-8')
    comment=['Project 2 - Portfolio Committee Review','',
             'Repository (private instructional-team review): '+REPO+'/tree/'+TAG,
             'Visible executed output: '+REPO+'/blob/'+TAG+'/outputs/visible_output.json','']
    for number in VIDEO_IDS:comment.append(f'Video {number} - {LABELS[number]}: https://youtu.be/{VIDEO_IDS[number]}')
    comment.extend(['','Recommendation: no capital deployment; further paper research only.',
                    'The attached manifest contains video evidence indices, artifact locations and frozen versions. The three PDFs and three corrected transcripts are attached separately.'])
    (target/'BRIGHTSPACE-COMMENT.txt').write_text('\n'.join(comment)+'\n',encoding='utf-8')
    print('Refreshed manifest, seven required attachments and readable link index.')

if __name__=='__main__':main()

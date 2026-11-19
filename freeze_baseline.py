"""Preserve existing portfolio evidence; no original checkpoint receipt inferred."""
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil

import analysis as a

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'lab-15-portfolio-stability'
DEST=ROOT/'baseline/prior-portfolio-snapshot'
NAMES=['lab-15-writeup.md','personal-results.json','personal-results.md','portfolio.py',
       'analyze_personal.py','prices.csv','price-provenance.json']


def main():
    DEST.mkdir(parents=True,exist_ok=True)
    records=[]
    for name in NAMES:
        source=SOURCE/name;target=DEST/name
        if target.exists() and a.sha(target)!=a.sha(source):
            raise ValueError('Retained baseline differs; preserve both versions rather than overwrite.')
        if not target.exists():shutil.copy2(source,target)
        records.append({'original_path':str(source.relative_to(ROOT.parent.parent)).replace('\\','/'),
                        'preserved_file':name,'sha256':a.sha(target)})
    manifest=DEST/'baseline-manifest.json'
    if not manifest.exists():
        manifest.write_text(json.dumps({'preserved_at_utc':datetime.now(timezone.utc).isoformat(),
            'purpose':'Student-selected retrospective comparison baseline',
            'checkpoint_status':'Original Project 2 Edition A submission and receipt not established; instructor acceptance of substitute unverified.',
            'files':records},indent=2)+'\n',encoding='utf-8')
    print('Preserved '+str(len(records))+' unchanged baseline files and provenance manifest.')


if __name__=='__main__':main()

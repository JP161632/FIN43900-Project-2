"""Create a local review archive from a verified inventory, without publishing."""
import hashlib
import json
from pathlib import Path
import zipfile

import analysis

ROOT=Path(__file__).resolve().parent


def main():
    inventory=json.loads((ROOT/'evidence/file-integrity.json').read_text())
    stale=[name for name,digest in inventory.items() if analysis.sha(ROOT/name)!=digest]
    if stale:raise ValueError('Re-run audit_package.py for changed files: '+', '.join(stale))
    target=ROOT/'dist';target.mkdir(exist_ok=True)
    archive=target/'Project-2-Review-Package.zip'
    names=list(inventory)+['evidence/file-integrity.json','evidence/package-readiness.json']
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as output:
        for name in sorted(set(names)):output.write(ROOT/name,'project-2/'+name)
    with zipfile.ZipFile(archive) as check:
        failure=check.testzip()
        if failure:raise ValueError('Archive CRC failure: '+failure)
        for name,digest in inventory.items():
            if hashlib.sha256(check.read('project-2/'+name)).hexdigest()!=digest:
                raise ValueError('Archive content mismatch: '+name)
    digest=analysis.sha(archive)
    (target/'Project-2-Review-Package.sha256.txt').write_text(digest+'  '+archive.name+'\n')
    print('Created and verified '+archive.name+'; '+str(len(set(names)))+' files.')
    print('Verified local review archive. See current manifest and readiness report for supplied links and remaining human/access conditions.')


if __name__=='__main__':main()

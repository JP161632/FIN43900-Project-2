"""Render every report page and flag text outside page bounds."""
import json
from pathlib import Path
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'evidence/pdf-qa'
OUT.mkdir(exist_ok=True)
images=[]
checks=[]
for name in ['Edition-A-Retrospective-Baseline','Decision-Memo','Research-Evolution','Validation-and-AI-Use']:
    with fitz.open(ROOT/f'{name}.pdf') as document:
        for number,page in enumerate(document,1):
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        x0,y0,x1,y1=span['bbox']
                        if not (0<=x0<=x1<=page.rect.width and 0<=y0<=y1<=page.rect.height):
                            raise ValueError(f'Out-of-page text: {name} {number}')
            output=OUT/f'{name}-{number}.png'
            page.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(output)
            images.append((output,f'{name} / {number}'))
            checks.append({'document':name,'page':number,'text_within_bounds':True})
tile_w,tile_h=620,850
sheet=Image.new('RGB',(tile_w*3,tile_h*((len(images)+2)//3)),'#dfe5eb')
draw=ImageDraw.Draw(sheet)
for index,(path,title) in enumerate(images):
    im=Image.open(path).convert('RGB');im.thumbnail((600,800))
    x=(index%3)*tile_w+10;y=(index//3)*tile_h+30
    sheet.paste(im,(x,y));draw.text((x,y-20),title,fill='black')
sheet.save(OUT/'contact-sheet.png')
(ROOT/'evidence/pdf-layout-checks.json').write_text(json.dumps({'rendered_pages':checks,
    'visual_review':'Pending assistant image inspection; geometric checks alone do not establish layout quality.'},indent=2)+'\n')
print(f'Rendered {len(images)} pages; all text within page bounds.')

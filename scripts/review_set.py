"""Assemble separately rendered anonymous sets into one initially empty folder."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import shutil
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from blindcheck import check

DESCRIPTIONS={
    '01':'Face 1 size and weight ladder; reading samples',
    '02':'Face 2 size and weight ladder; reading samples',
    '03':'Face 3 size and weight ladder; reading samples',
    '04':'Weather numerals, hourly tables, units and fractions',
    '05':'Weather answer card mockup; weather icon/text fits and 13 px tab labels when available',
    '06':'Code ligatures and terminal samples',
    '07':'Glyph detail views',
    '08':'Named icons at 16 / 20 / 24 / 32 px',
    '09':'Icon font glyphs; named size ladder',
    '10':'Rounded temperatures 24–96 px, hourly row, percentages and times',
    '11':'Same weather card with Rounded and regular numerals',
    '12':'Regular above Rounded: matching strings at 24 / 48 / 96 px',
}


def assemble(inputs,out,guide,images_only=False):
    if out.exists() and any(out.iterdir()):raise ValueError('Reviewer OUT must be empty')
    out.mkdir(parents=True,exist_ok=True)
    rows=[];names=set();findings=[]
    for folder in inputs:
        check(folder)
        report=folder/'findings.json'
        if report.exists():
            fields=['label','image','sheet','theme','status','line_boxes','components','threshold','neighbors','scale']
            findings.extend({key:row[key] for key in fields} for row in json.loads(report.read_text())['headline_collisions'])
        for row in json.loads((folder/'index.json').read_text())['sheets']:
            row={key:row[key] for key in ['label','image','sheet','theme','width','height','scale']}
            name=row['image']
            if name in names:raise ValueError('Duplicate anonymous sheet')
            names.add(name);shutil.copyfile(folder/name,out/name);rows.append(row)
    rows.sort(key=lambda r:r['image'])
    if not images_only:
        (out/'index.json').write_text(json.dumps({'sheets':rows},indent=2)+'\n')
        (out/'findings.json').write_text(json.dumps({'headline_collisions':sorted(findings,key=lambda r:r['image'])},indent=2)+'\n')
    image_dir=Path(os.path.relpath(out,guide.parent))
    lines=['# Review sheets','','Each file starts with its opaque label and sheet number. Sizes are CSS pixels; images use 2× raster scale. Compare like sheets and surfaces.',
           '',('Headline line-contact results for every card surface are listed below.' if images_only else f'Headline line-contact results for every card surface are in [findings.json]({image_dir}/findings.json).')+' A finding is a review result; it does not stop rendering. Icon rows use 13 / 15 / 17 px text and 16 / 20 px icons; tab labels use 13 px. Type-only cards omit icon rows.','']
    lines+=['| Label | Sheets | Headline surfaces checked | Surfaces with line contact |','| --- | ---: | ---: | --- |']
    for label,count in sorted(Counter(row['label'] for row in rows).items()):
        contacts=[row for row in findings if row['label']==label]
        result=str(sum(bool(row['components']) for row in contacts)) if contacts else 'n/a'
        lines.append(f'| {label} | {count} | {len(contacts)} | {result} |')
    lines+=['']
    if findings:
        lines+=['| Label | Surface | Headline line contact |','| --- | --- | --- |']
        for row in sorted(findings,key=lambda r:r['image']):
            count=len(row['components']);status=f'finding: {count} joined component'+('s' if count!=1 else '') if count else 'clear'
            lines.append(f'| {row["label"]} | {row["theme"]} | [{status}]({image_dir}/{row["image"]}) |')
        lines+=['']
    lines+=['| Label | Sheet | View | Surface |','| --- | ---: | --- | --- |']
    for row in rows:
        number=Path(row['image']).stem.rsplit('-',1)[-1]
        lines.append(f'| {row["label"]} | [{number}]({image_dir}/{row["image"]}) | {DESCRIPTIONS[row["sheet"]]} | {row["theme"]} |')
    guide.write_text('\n'.join(lines)+'\n')
    # Audit the guide as well as the image directory.
    check(out.parent)
    return len(rows)


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,action='append',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--guide',type=Path,required=True);p.add_argument('--images-only',action='store_true',help='Keep the reviewer directory to PNGs and the guide; inline anonymous contacts in the guide');a=p.parse_args()
    print(f'Assembled {assemble(a.input,a.out,a.guide,a.images_only)} sheets; blind check PASS')

if __name__=='__main__':main()

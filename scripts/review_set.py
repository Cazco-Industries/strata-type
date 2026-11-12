"""Assemble separately rendered anonymous sets into one initially empty folder."""
import argparse
import json
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
    '05':'Weather answer card mockup',
    '06':'Code ligatures and terminal samples',
    '07':'Glyph detail views',
    '08':'Icon size ladder and grid',
    '09':'Filled icon glyphs',
    '10':'Rounded temperatures 24–96 px, hourly row, percentages and times',
    '11':'Same weather card with Rounded and regular numerals',
}


def assemble(inputs,out,guide):
    if out.exists() and any(out.iterdir()):raise ValueError('Reviewer OUT must be empty')
    out.mkdir(parents=True,exist_ok=True)
    rows=[];names=set()
    for folder in inputs:
        check(folder)
        for row in json.loads((folder/'index.json').read_text())['sheets']:
            row={key:row[key] for key in ['label','image','sheet','theme','width','height','scale']}
            name=row['image']
            if name in names:raise ValueError('Duplicate anonymous sheet')
            names.add(name);shutil.copyfile(folder/name,out/name);rows.append(row)
    rows.sort(key=lambda r:r['image'])
    (out/'index.json').write_text(json.dumps({'sheets':rows},indent=2)+'\n')
    lines=['# Round 0 sheets','','Each file starts with its opaque label and sheet number. Sizes are CSS pixels; images use 2× raster scale. Compare like sheets and surfaces.','',
           '| Label | Sheet | View | Surface |','| --- | ---: | --- | --- |']
    for row in rows:
        number=Path(row['image']).stem.rsplit('-',1)[-1]
        lines.append(f'| {row["label"]} | [{number}](renders/{row["image"]}) | {DESCRIPTIONS[row["sheet"]]} | {row["theme"]} |')
    guide.write_text('\n'.join(lines)+'\n')
    # Audit the guide as well as the image directory.
    check(out.parent)
    return len(rows)


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,action='append',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--guide',type=Path,required=True);a=p.parse_args()
    print(f'Assembled {assemble(a.input,a.out,a.guide)} sheets; blind check PASS')

if __name__=='__main__':main()

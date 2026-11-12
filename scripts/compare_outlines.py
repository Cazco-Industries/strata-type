"""Compare regenerated UFO geometry or compiled variable outline tables exactly."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont


def sources(before,after):
    def records(base):
        result={}
        for path in sorted(base.rglob('*.glif')):
            root=ET.parse(path).getroot()
            outline=root.find('outline')
            def node(element):
                # Coordinate spellings such as 1 and 1.0 describe the same point.
                attrs=tuple(sorted((k,float(v) if k in {'x','y','xScale','xyScale','yxScale','yScale','xOffset','yOffset','width','height'} else v) for k,v in element.attrib.items()))
                return (element.tag,attrs,tuple(node(child) for child in element))
            result[str(path.relative_to(base))]=(node(outline) if outline is not None else None,
                tuple(node(el) for el in root if el.tag in {'advance','unicode','anchor'}))
        return result
    left,right=records(Path(before)),records(Path(after))
    if not left:raise ValueError('No glyph records to compare')
    differences=[name for name in left.keys()|right.keys() if left.get(name)!=right.get(name)]
    if differences:raise ValueError(f'{len(differences)} changed glyph records: {differences[:12]}')
    return {'status':'PASS','glyph_records':len(left),'comparison':'all contour points, components, advances, Unicode mappings and anchors'}


def binaries(before,after):
    with TTFont(before,recalcTimestamp=False) as left,TTFont(after,recalcTimestamp=False) as right:
        if left.getGlyphOrder()!=right.getGlyphOrder():raise ValueError('Glyph order differs')
        hashes={}
        for tag in ['glyf','gvar','hmtx','loca','fvar','avar']:
            if (tag in left)!=(tag in right):raise ValueError(f'{tag} presence differs')
            if tag not in left:continue
            a,b=left.getTableData(tag),right.getTableData(tag)
            if a!=b:raise ValueError(f'{tag} table bytes differ')
            hashes[tag]=hashlib.sha256(a).hexdigest()
        return {'status':'PASS','glyphs':len(left.getGlyphOrder()),'comparison':'byte-identical outline, variation, metrics and axis tables','sha256':hashes}


def main():
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['sources','binaries']);p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
    result=(sources if a.kind=='sources' else binaries)(a.before,a.after)
    value=json.dumps(result,indent=2)+'\n'
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(value)
    print(value,end='')

if __name__=='__main__':main()

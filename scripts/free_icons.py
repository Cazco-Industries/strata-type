"""Convert only the locked public free package's array data; never run its JS."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def svg_data(path):
    data=Path(path).read_text()
    literal=data[data.index('['):data.index('\n];')+2]
    literal=re.sub(r'([,{]\s*)([A-Za-z][A-Za-z0-9]*):',r'\1"\2":',literal)
    nodes=json.loads(literal)
    root=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','viewBox':'0 0 24 24','fill':'none','stroke':'currentColor','stroke-width':'1.5','stroke-linecap':'round','stroke-linejoin':'round'})
    for tag,attrs in nodes:
        if tag not in {'path','circle','ellipse','line','polyline','polygon','rect'}:raise ValueError('Unexpected free-package SVG element')
        attrs={re.sub('[A-Z]',lambda m:'-'+m[0].lower(),k):str(v) for k,v in attrs.items() if k!='key'}
        if any(k.startswith('on') or k in ('href','style') for k in attrs):raise ValueError('Unexpected active SVG attribute')
        ET.SubElement(root,tag,attrs)
    return ET.tostring(root,encoding='unicode')


def convert_package(package,out):
    package=Path(package);out=Path(out)
    paths=sorted((package/'dist/esm').glob('*Icon.js'))
    if not paths:raise ValueError('Free package has no icon data')
    out.mkdir(parents=True,exist_ok=True)
    for path in paths:
        target=out/(path.stem+'.svg')
        if not target.exists():target.write_text(svg_data(path)+'\n')
    (out/'LICENSE.md').write_text((package/'LICENSE.md').read_text())
    return len(paths)

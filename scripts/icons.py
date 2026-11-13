"""Normalize SVG data and build matching React and stroke-expanded font outputs."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib import SVGPath
from common import ROOT, UPSTREAM, dump, digest

ET.register_namespace('', 'http://www.w3.org/2000/svg')
DRAW={'path','circle','ellipse','line','polyline','polygon','rect','g'}
# Weather icons group tintable parts; renderers tone layers, fonts ignore them.
LAYERS={'sun','moon','cloud','rain','snow','ice','bolt','wind','fog','heat'}
ATTR={'d','cx','cy','r','rx','ry','x','y','x1','x2','y1','y2','width','height','points','fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','viewBox','xmlns','opacity'}


def parse_svg(path):
    data=Path(path).read_text()
    if '<!DOCTYPE' in data or '<!ENTITY' in data:raise ValueError(f'XML entities forbidden: {path}')
    root=ET.fromstring(data)
    if root.tag.split('}')[-1]!='svg':raise ValueError(f'Not SVG: {path}')
    return root


def validate(root):
    errors=[]
    if root.get('viewBox')!='0 0 24 24':errors.append('viewBox must be 0 0 24 24')
    if root.get('fill')!='none':errors.append('root fill must be none')
    if root.get('stroke')!='currentColor':errors.append('root stroke must be currentColor')
    if root.get('stroke-linecap')!='round' or root.get('stroke-linejoin')!='round':errors.append('round cap/join required')
    width=root.get('stroke-width')
    if width is None or not 0<float(width)<=3:errors.append('invalid stroke width')
    for el in root.iter():
        tag=el.tag.split('}')[-1]
        if el is not root and tag not in DRAW:errors.append(f'unsupported element {tag}')
        for key,value in el.attrib.items():
            if key=='data-layer':
                if tag!='g':errors.append('data-layer only on <g>')
                elif value not in LAYERS:errors.append(f'unknown layer {value}')
                continue
            if key not in ATTR:errors.append(f'unexpected attribute {key}')
            if key=='fill' and value!='none':errors.append('unexpected fill')
            if key=='stroke' and value!='currentColor':errors.append('unexpected stroke')
            if key=='stroke-width' and value!=width:errors.append('inconsistent stroke width')
            if key in ('stroke-linecap','stroke-linejoin') and value!='round':errors.append('inconsistent cap/join')
    return sorted(set(errors))


def normalize(path):
    root=parse_svg(path)
    root.attrib={k:v for k,v in root.attrib.items() if k in ('viewBox','fill','stroke','stroke-width','stroke-linecap','stroke-linejoin')}
    root.set('viewBox','0 0 24 24');root.set('fill','none');root.set('stroke','currentColor')
    root.set('stroke-width','2');root.set('stroke-linecap','round');root.set('stroke-linejoin','round')
    # Tiny filled Lucide dots are already fully covered by their round stroke.
    for el in root.iter():
        if el.tag.split('}')[-1]=='circle' and el.get('fill')=='currentColor' and float(el.get('r','0'))<=1:
            el.attrib.pop('fill')
    errors=validate(root)
    if errors:raise ValueError(f'{path}: {errors}')
    return ET.tostring(root,encoding='unicode')+'\n'


def prepare_icons(out):
    out.mkdir(parents=True,exist_ok=True)
    inventory=json.loads((ROOT/'inventory/icons.json').read_text())
    iconroot=UPSTREAM/'lucide/icons'
    available={p.stem:p for p in iconroot.glob('*.svg')}
    aliases={}
    for p in iconroot.glob('*.json'):
        for alias in json.loads(p.read_text()).get('aliases',[]):
            if isinstance(alias,str):aliases[alias]=p.stem
            elif isinstance(alias,dict):aliases[alias['name']]=p.stem
    aliases.update({'bar-chart-3':'chart-no-axes-column-increasing','globe-2':'earth','layers-3':'layers','home':'house','alert-triangle':'triangle-alert','check-circle-2':'circle-check','loader-2':'loader-circle','help-circle':'circle-help','check-circle':'circle-check-big'})
    weather={'clear-day':'sun','clear-night':'moon','partly-cloudy-day':'cloud-sun','partly-cloudy-night':'cloud-moon','cloudy':'cloud','fog':'cloud-fog','haze':'haze','drizzle':'cloud-drizzle','rain':'cloud-rain','heavy-rain':'cloud-rain','showers-day':'cloud-sun-rain','showers-night':'cloud-moon-rain','thunderstorm':'cloud-lightning','snow':'cloud-snow','sleet':'cloud-hail','freezing-rain':'cloud-rain','hail':'cloud-hail','wind':'wind','hot':'thermometer-sun','cold':'thermometer-snowflake','tornado':'tornado','hurricane':'wind','sunrise':'sunrise','sunset':'sunset','unknown':'circle-help','flood':'waves','tsunami':'waves','fire':'flame','dust':'haze','smoke':'cloud-fog','smog':'haze','na':'circle-help','umbrella':'umbrella','moonrise':'moon-star','moonset':'moon','snowflake-cold':'snowflake','strong-wind':'wind','windy':'wind'}
    entries={i['semantic_name']:i['semantic_name'] for i in inventory['lucide']}
    for i in inventory['condition_glyphs']+inventory['erik_flowers_referenced']+inventory['gaps']:entries.setdefault(i['semantic_name'],None)
    manifest=[];missing=[]
    for semantic,ui in sorted(entries.items()):
        source=ui or weather.get(semantic)
        if not source:
            for key in ['thunderstorm','snow','sleet','hail','rain','drizzle','fog','haze','wind','cloudy','clear','moon','tide','uv','air-quality','alert']:
                if key in semantic:
                    source={'thunderstorm':'cloud-lightning','snow':'cloud-snow','sleet':'cloud-hail','hail':'cloud-hail','rain':'cloud-rain','drizzle':'cloud-drizzle','fog':'cloud-fog','haze':'haze','wind':'wind','cloudy':'cloud','clear':'sun' if 'day' in semantic else 'moon','moon':'moon','tide':'waves','uv':'sun','air-quality':'leaf','alert':'triangle-alert'}[key];break
        source=aliases.get(source,source)
        if source not in available:
            missing.append((semantic,source));continue
        (out/f'{semantic}.svg').write_text(normalize(available[source]))
        manifest.append({'semantic_name':semantic,'upstream_svg':source,'role':'ui' if ui else 'weather','status':'baseline upstream geometry' if ui else 'approximation; weather design pending'})
    if missing:raise ValueError(f'Explicit icon mapping needed: {missing}')
    dump(out/'manifest.json',{'license':'ISC; see bundled notices','icons':manifest})
    print(f'icons: {len(manifest)} normalized SVGs',flush=True)


def huge_svg(name):
    from free_icons import svg_data
    svg=svg_data(UPSTREAM/'hugeicons-free/dist/esm'/f'{name}Icon.js')
    errors=validate(ET.fromstring(svg))
    if errors:raise ValueError(f'Free SVG conversion failed: {errors}')
    return svg


def build_icons(source,out):
    source=Path(source).expanduser().resolve()
    paths=sorted(source.glob('*.svg'))
    if not paths:raise ValueError('No candidate icons found')
    out.mkdir(parents=True,exist_ok=True)
    svgs=out/'svg';react=out/'react';svgs.mkdir(exist_ok=True);react.mkdir(exist_ok=True)
    # Stable codepoints: per-build sorted names, manifest is the authoritative mapping.
    mapping={};components=set();widths=set();glyphs={};metrics={};cmap={};exports=[]
    notdef=TTGlyphPen(None);glyphs['.notdef']=notdef.glyph();metrics['.notdef']=(1000,0)
    for index,path in enumerate(paths):
        if path.is_symlink() or not re.fullmatch('[a-z][a-z0-9-]*',path.stem):raise ValueError(f'Unsafe semantic SVG name: {path.name}')
        root=parse_svg(path);errors=validate(root)
        if errors:raise ValueError(f'{path}: {errors}')
        widths.add(root.get('stroke-width'))
        svg=re.sub(r'>\s+<','><',ET.tostring(root,encoding='unicode')).strip()
        (svgs/path.name).write_text(svg+'\n')
        component=''.join(w.title() for w in path.stem.split('-'))+'Icon'
        if component in components:raise ValueError(f'Component name collision: {component}')
        components.add(component)
        attrs={'stroke-width':'strokeWidth','stroke-linecap':'strokeLinecap','stroke-linejoin':'strokeLinejoin','fill-rule':'fillRule','clip-rule':'clipRule'}
        body=svg[svg.index('>')+1:svg.rindex('</')]
        body=re.sub(r'\bns\d+:','',body)
        for a,b in attrs.items():body=body.replace(a+'=',b+'=')
        text='// ISC and MIT notices accompany this component set.\nimport type { SVGProps } from "react";\n'
        text+=f'export function {component}(props: SVGProps<SVGSVGElement>) {{ return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={{{root.get("stroke-width")}}} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {{...props}}>{body}</svg>; }}\n'
        (react/f'{component}.tsx').write_text(text)
        exports.append(f'export {{ {component} }} from "./{component}";')
        # Expand the exact SVG strokes to filled glyph contours; never use an open
        # centerline in a font (browsers fill font outlines instead of stroking).
        pathops_path=pathops.Path()
        SVGPath.fromstring(svg).draw(pathops_path.getPen())
        pathops_path.stroke(float(root.get('stroke-width')),pathops.LineCap.ROUND_CAP,pathops.LineJoin.ROUND_JOIN,4)
        pathops_path.convertConicsToQuads(0.001)
        pathops_path.simplify()
        pen=TTGlyphPen(None)
        pathops_path.draw(TransformPen(Cu2QuPen(pen,0.5,reverse_direction=True),(1000/24,0,0,-1000/24,0,850)))
        glyph='i'+str(index);glyphs[glyph]=pen.glyph();metrics[glyph]=(1000,0)
        codepoint=0xe000+index;cmap[codepoint]=glyph;mapping[path.stem]={'codepoint':f'{codepoint:04X}','component':component,'svg':f'svg/{path.name}'}
    if len(widths)!=1:raise ValueError('Candidate uses inconsistent icon stroke widths')
    (react/'index.ts').write_text('\n'.join(exports)+'\n')
    fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(list(glyphs));fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(metrics);fb.setupHorizontalHeader(ascent=850,descent=-150)
    fb.setupNameTable({'familyName':'Strata Icons','styleName':'Regular','uniqueFontIdentifier':'StrataIcons-Regular;1.000','fullName':'Strata Icons','psName':'StrataIcons-Regular','version':'Version 1.000','copyright':'ISC and MIT; notices accompany this font.'})
    fb.setupOS2(sTypoAscender=850,sTypoDescender=-150,usWinAscent=1000,usWinDescent=150);fb.setupPost();fb.setupMaxp()
    fb.font['head'].created=fb.font['head'].modified=3406620153
    fb.font.flavor='woff2';fb.save(out/'StrataIcons.woff2')
    dump(out/'manifest.json',{'sha256':digest(source),'stroke_width':float(next(iter(widths))),'icons':mapping})
    notices=out/'licenses';notices.mkdir(exist_ok=True)
    for pattern in ['lucide-*','hugeicons-free-*']:
        for path in (ROOT/'licenses').glob(pattern):shutil.copyfile(path,notices/path.name)
    return {'icons':len(mapping),'woff2_bytes':(out/'StrataIcons.woff2').stat().st_size,'source_sha256':digest(source)}

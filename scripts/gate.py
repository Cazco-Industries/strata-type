"""Produce auditable reports; --strict also rejects baseline quality failures."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import time
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from common import checkpoint, ROOT, ALL_FACES, CORE, ROUNDED_CORE, FORBIDDEN, candidate_faces, candidate, digest, dump
from icons import parse_svg, validate


def figures(path,feature):
    face=hb.Face(path.read_bytes());font=hb.Font(face);font.scale=(face.upem,face.upem)
    buffer=hb.Buffer();buffer.add_str('0123456789');buffer.guess_segment_properties()
    hb.shape(font,buffer,{'tnum':feature=='tnum','pnum':feature=='pnum'})
    return [round(p.x_advance/face.upem,5) for p in buffer.glyph_positions]


def metrics(font,path):
    upm=font['head'].unitsPerEm;o=font['OS/2'];h=font['hhea']
    def normalized(table,attrs):return {key:round(getattr(table,key)/upm,5) for key in attrs}
    return {'upm':upm,**normalized(o,['sxHeight','sCapHeight','sTypoAscender','sTypoDescender','sTypoLineGap','usWinAscent','usWinDescent']),
            'hhea':normalized(h,['ascent','descent','lineGap']),
            'axes':{a.axisTag:[a.minValue,a.defaultValue,a.maxValue] for a in font['fvar'].axes},
            'figures_tnum':figures(path,'tnum'),'figures_pnum':figures(path,'pnum'),
            'layout_features':sorted({r.FeatureTag for tag in ['GSUB','GPOS'] if tag in font and font[tag].table.FeatureList for r in font[tag].table.FeatureList.FeatureRecord})}


def checked_build(cand,icons_dir=None):
    path=candidate(cand);out=ROOT/'build'/cand
    report=json.loads((out/'build.json').read_text())
    if set(report['faces'])!=set(candidate_faces(path)):raise ValueError('Changed face set; run make build')
    for face in candidate_faces(path):
        if report['faces'][face]['source_sha256']!=digest(path/'fonts'/face):raise ValueError(f'Stale {face} build; run make build')
        for format in ['ttf','woff2']:
            if report['faces'][face][f'{format}_sha256']!=digest(out/report['faces'][face][format]):raise ValueError(f'Changed binary: {face} {format}')
    source=Path(icons_dir).expanduser().resolve() if icons_dir else path/'icons'
    if report['icons']['source_sha256']!=digest(source):raise ValueError('Stale icon build or wrong ICONS_DIR; run make build with the same input')
    return path,out,report,source


def main():
    p=argparse.ArgumentParser();p.add_argument('--cand',required=True);p.add_argument('--icons-dir');p.add_argument('--strict',action='store_true');p.add_argument('--summary');a=p.parse_args()
    start=time.monotonic();path,out,build,icons=checked_build(a.cand,a.icons_dir)
    report={'candidate':a.cand,'subset':build['subset'],'core_codepoints':len(CORE),'faces':{},'hard_failures':[]}
    for face,family in candidate_faces(path).items():
        checkpoint()
        before=time.monotonic();ttf=out/build['faces'][face]['ttf'];font=TTFont(ttf)
        required=ROUNDED_CORE if face=='sans-rounded' else CORE
        missing=sorted(required-set(font.getBestCmap()))
        names=[{'id':n.nameID,'platform':n.platformID,'value':n.toUnicode()} for n in font['name'].names if FORBIDDEN.search(n.toUnicode())]
        if names:report['hard_failures'].append(f'{face}: reserved upstream name in name table')
        bakery=out/f'{face}-fontbakery.json'
        with (out/f'{face}-fontbakery.log').open('w') as log:
            result=subprocess.run([sys.executable,'-I','-m','fontbakery','check-universal',str(ttf),'--skip-network','--json',str(bakery),'--no-colors','--no-progress','--jobs','1'],stdout=log,stderr=subprocess.STDOUT)
        if result.returncode not in (0,1) or not bakery.exists():raise RuntimeError(f'Fontbakery did not run: {face}; inspect log')
        fb=json.loads(bakery.read_text())
        interp=out/f'{face}-interpolatable.json'
        with (out/f'{face}-interpolatable.log').open('w') as log:
            result=subprocess.run([sys.executable,'-I','-m','fontTools.varLib.interpolatable',str(next((path/'fonts'/face).glob('*.designspace'))),'--json','--output',str(interp)],stdout=log,stderr=subprocess.STDOUT)
        if result.returncode not in (0,1) or not interp.exists():raise RuntimeError(f'Interpolatable did not run: {face}; inspect log')
        problems=json.loads(interp.read_text() or '{}')
        types=Counter(p['type'] for values in problems.values() for p in values)
        item={'fontbakery':{'profile':'universal','network':'skipped','counts':fb['result']},'interpolatable':{'glyphs_with_findings':len(problems),'counts':dict(types),'report':interp.name},'coverage':{'required':len(required),'present':len(required)-len(missing),'missing':[f'U+{c:04X}' for c in missing],'status':'FAIL' if missing else 'PASS'},'names':{'status':'FAIL' if names else 'PASS','violations':names},'metrics':metrics(font,ttf),'woff2_bytes':ttf.with_suffix('.woff2').stat().st_size,'seconds':round(time.monotonic()-before,3)}
        item['figures']={'tabular_equal_width':len(set(item['metrics']['figures_tnum']))==1,'proportional_varied_width':len(set(item['metrics']['figures_pnum']))>1,'tnum_feature':'tnum' in item['metrics']['layout_features'],'pnum_feature':'pnum' in item['metrics']['layout_features']}
        report['faces'][face]=item
        print(f'{face}: {json.dumps(item["fontbakery"]["counts"])}, missing={len(missing)}, interpolation={dict(types)}',flush=True)
    svgerrors={};widths=set()
    for svg in sorted((out/'icons/svg').glob('*.svg')):
        root=parse_svg(svg);widths.add(root.get('stroke-width'));errors=validate(root)
        if errors:svgerrors[svg.name]=errors
    if len(widths)!=1:svgerrors['set']=['inconsistent stroke widths']
    if svgerrors:report['hard_failures'].append('SVG contract failed')
    report['icons']={'status':'FAIL' if svgerrors else 'PASS','count':len(list((out/'icons/svg').glob('*.svg'))),'violations':svgerrors,'stroke_widths':sorted(widths),'woff2_bytes':(out/'icons/StrataIcons.woff2').stat().st_size}
    # The generated TSX is typechecked with the locked compiler and React types.
    result=subprocess.run(['node',str(ROOT/'node_modules/typescript/bin/tsc'),'--noEmit','--jsx','react-jsx','--target','ES2022','--module','ESNext','--moduleResolution','Bundler','--strict',*map(str,(out/'icons/react').glob('*.tsx'))],capture_output=True,text=True)
    (out/'icons/typecheck.log').write_text(result.stdout+result.stderr)
    report['icons']['tsx_typecheck']='PASS' if result.returncode==0 else 'FAIL'
    if result.returncode:report['hard_failures'].append('Generated TSX typecheck failed')
    inherited=any(v['coverage']['missing'] or v['interpolatable']['glyphs_with_findings'] or any(v['fontbakery']['counts'].get(k,0) for k in ['FAIL','ERROR','FATAL']) for v in report['faces'].values())
    report['quality_status']='FAIL' if inherited or report['hard_failures'] else 'PASS'
    report['seconds']=round(time.monotonic()-start,3)
    dump(out/'gate.json',report)
    lines=[f'# Gate report: {a.cand}',f'Quality status: **{report["quality_status"]}**. Hard failures: {len(report["hard_failures"])}.',
      'Baseline reports preserve geometry, compilation, subset, and Fontbakery findings. No upstream warnings were fixed. `--strict` rejects all quality failures. Name-table and icon-contract violations always fail the command.',
      '| Face | Pass | Warn | Fail | Error | Core present | Interpolation glyphs | WOFF2 bytes |',
      '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for face,item in report['faces'].items():
        c=item['fontbakery']['counts'];lines.append(f'| {ALL_FACES[face]} | {c.get("PASS",0)} | {c.get("WARN",0)} | {c.get("FAIL",0)} | {c.get("ERROR",0)} | {item["coverage"]["present"]}/{item["coverage"]["required"]} | {item["interpolatable"]["glyphs_with_findings"]} | {item["woff2_bytes"]} |')
    lines+=['','Metrics are UPM-normalized (default variable location). Figure advances are shaped with HarfBuzz, with tnum/pnum explicitly requested.','', '| Face | UPM | x-height | Cap | Typo asc/desc/gap | hhea asc/desc/gap | Win asc/desc | Weight range |','| --- | ---: | ---: | ---: | --- | --- | --- | --- |']
    for face,item in report['faces'].items():
        m=item['metrics'];lines.append(f'| {ALL_FACES[face]} | {m["upm"]} | {m["sxHeight"]} | {m["sCapHeight"]} | {m["sTypoAscender"]}/{m["sTypoDescender"]}/{m["sTypoLineGap"]} | {m["hhea"]["ascent"]}/{m["hhea"]["descent"]}/{m["hhea"]["lineGap"]} | {m["usWinAscent"]}/{m["usWinDescent"]} | {m["axes"]["wght"]} |')
        lines += []
    for face,item in report['faces'].items():
        lines+=['',f'## {ALL_FACES[face]}',f'Name/RFN: {item["names"]["status"]}',f'Missing required: {", ".join(item["coverage"]["missing"]) or "none"}',f'Figure gates: {item["figures"]}',f'Tabular advances 0–9: {item["metrics"]["figures_tnum"]}',f'Proportional advances 0–9: {item["metrics"]["figures_pnum"]}',f'Interpolation findings: {item["interpolatable"]["counts"]}']
    lines+=['',f'Icons: {report["icons"]}',f'Elapsed: {report["seconds"]} seconds.']
    summary=Path(a.summary).expanduser() if a.summary else out/'gate.md'
    summary.parent.mkdir(parents=True,exist_ok=True)
    summary.write_text('\n'.join(lines)+'\n')
    if report['hard_failures'] or (a.strict and report['quality_status']=='FAIL'):raise SystemExit(1)
    print(f'gate report complete: {report["seconds"]:.3f}s; quality={report["quality_status"]}',flush=True)

if __name__=='__main__':main()

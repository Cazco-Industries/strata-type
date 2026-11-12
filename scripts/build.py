"""Compile candidate UFO masters; cache by all source bytes, never by mtime."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from fontTools import subset
from fontTools.ttLib import TTFont
from common import checkpoint, ROOT, ALL_FACES, CORE, candidate_faces, candidate, digest, dump, rename_binary
from icons import build_icons


def compile_face(face,source,out):
    designspaces=list(source.glob('*.designspace'))
    if len(designspaces)!=1:raise ValueError(f'{source}: expected exactly one designspace')
    # Source data must never select code-loading plugins.
    from fontTools.designspaceLib import DesignSpaceDocument
    from ufoLib2 import Font
    ds=DesignSpaceDocument.fromfile(designspaces[0])
    for src in ds.sources:
        path=Path(src.path).resolve()
        if not path.is_relative_to(source.resolve()):raise ValueError('Master outside candidate source directory')
        with Font.open(path,lazy=True) as font:
            for key in ('com.github.googlei18n.ufo2ft.filters','com.github.googlei18n.ufo2ft.featureWriters'):
                if font.lib.get(key):raise ValueError(f'Executable UFO configuration rejected: {key}')
    out.parent.mkdir(parents=True,exist_ok=True)
    log=out.with_suffix('.log')
    with log.open('w') as stream:
        subprocess.run([sys.executable,'-I','-m','fontmake','-m',str(designspaces[0]),'-o','variable','--output-path',str(out),'--keep-overlaps','--no-autohint','--verbose','WARNING'],cwd=source,stdout=stream,stderr=subprocess.STDOUT,check=True)
    font=TTFont(out,recalcTimestamp=False)
    rename_binary(font,ALL_FACES[face]);font['head'].created=font['head'].modified=3406620153
    font.save(out)
    return out


def font_output(source,dest,subset_name):
    font=TTFont(source,recalcTimestamp=False)
    if subset_name=='core':
        options=subset.Options();options.layout_features=['*'];options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*'];options.notdef_outline=True;options.recommended_glyphs=True;options.glyph_names=True
        sub=subset.Subsetter(options);sub.populate(unicodes=CORE);sub.subset(font)
    font['head'].created=font['head'].modified=3406620153
    font.flavor=None;font.save(dest)
    font.flavor='woff2';font.save(dest.with_suffix('.woff2'))


def build(cand,subset_name,icons_dir=None):
    start=time.monotonic();path=candidate(cand);out=ROOT/'build'/cand
    out.mkdir(parents=True,exist_ok=True)
    report={'candidate':cand,'subset':subset_name,'faces':{}}
    cache=ROOT/'build/.cache';cache.mkdir(parents=True,exist_ok=True)
    toolhash=digest(ROOT/'.python-version')+digest(ROOT/'uv.lock')+digest(ROOT/'scripts/build.py')+digest(ROOT/'scripts/common.py')
    import hashlib
    faces=candidate_faces(path)
    for face,family in faces.items():
        checkpoint()
        before=time.monotonic();source=path/'fonts'/face
        fingerprint=hashlib.sha256((digest(source)+toolhash).encode()).hexdigest()
        cached=cache/fingerprint/f'{family.replace(" ","")}.ttf'
        ready=cached.with_suffix('.ready.json')
        hit=cached.is_file() and ready.is_file() and json.loads(ready.read_text()).get('sha256')==digest(cached)
        if not hit:
            compile_face(face,source,cached)
            dump(ready,{'sha256':digest(cached)})
        target=out/f'{family.replace(" ","")}.ttf'
        font_output(cached,target,subset_name)
        report['faces'][face]={'source_sha256':digest(source),'cache_hit':hit,'full_ttf':str(cached.relative_to(ROOT)),'seconds':round(time.monotonic()-before,3),'ttf':target.name,'woff2':target.with_suffix('.woff2').name,'ttf_sha256':digest(target),'woff2_sha256':digest(target.with_suffix('.woff2'))}
        print(f'{face}: {report["faces"][face]["seconds"]:.3f}s (cached={hit})',flush=True)
    source=Path(icons_dir).expanduser().resolve() if icons_dir else path/'icons'
    # Replace only generated icon output so removed semantic names cannot linger.
    shutil.rmtree(out/'icons',ignore_errors=True)
    report['icons']=build_icons(source,out/'icons')
    report['icons']['external']=bool(icons_dir)
    report['icons']['source']=str(source)
    notices=out/'licenses';shutil.copytree(ROOT/'licenses',notices,dirs_exist_ok=True)
    for face,family in faces.items():
        for filename in ['COPYRIGHT.txt','OFL.txt']:
            notice=path/'fonts'/face/filename
            if face=='sans-rounded' and not notice.is_file():notice=path/'fonts/sans'/filename
            if notice.is_file():
                shutil.copyfile(notice,notices/(family.replace(' ','')+'-'+filename))
    report['seconds']=round(time.monotonic()-start,3)
    dump(out/'build.json',report)
    print(f'build {subset_name}: {report["seconds"]:.3f}s',flush=True)
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--cand',required=True);p.add_argument('--subset',choices=['core','full'],default='core');p.add_argument('--icons-dir');a=p.parse_args()
    build(a.cand,a.subset,a.icons_dir)

if __name__=='__main__':main()

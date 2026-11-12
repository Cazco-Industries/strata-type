"""Create immutable-shape upright baselines from locked public sources."""
import argparse
import io
import json
from pathlib import Path
import plistlib
import re
import shutil
import time
import glyphsLib
import ufoLib2
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.feaLib.parser import Parser
from common import checkpoint, ROOT, UPSTREAM, FACES, FORBIDDEN, dump, digest


def clean(value, family):
    if isinstance(value, str):
        value=re.sub(r'\b(?:Inter|Source\s*Serif\s*(?:4|Pro)?|Fira\s*Code|Fira\s*Mono)\b',family,value,flags=re.I)
        return value
    if isinstance(value,list):return [clean(v,family) for v in value]
    if isinstance(value,dict):return {k:clean(v,family) for k,v in value.items()}
    return value


def flatten_fea(text, directory, seen=()):
    # FEA include paths are relative to the original UFO, including nested includes.
    def expand(match):
        path=(directory/match.group(1).strip()).resolve()
        if not path.is_relative_to(UPSTREAM.resolve()) or path in seen:
            raise ValueError(f'Unsafe or recursive feature include: {path}')
        return flatten_fea(path.read_text(),directory,(*seen,path))
    return re.sub(r'include\s*\(\s*([^\)]+)\s*\)\s*;',expand,text)


def save_face(face, out):
    family=FACES[face]
    if face=='serif':
        ds=DesignSpaceDocument.fromfile(UPSTREAM/'serif-sources/Roman/SourceSerif4Variable-Roman.designspace')
        for src in ds.sources:
            src.font=ufoLib2.Font.open(src.path)
            src.font.features.text=flatten_fea(src.font.features.text,Path(src.path).parent)
    else:
        source=UPSTREAM/('sans/src/Inter-Roman.glyphspackage' if face=='sans' else 'mono/FiraCode.glyphs')
        font=glyphsLib.GSFont(source)
        if face=='mono':
            # Upstream's variable build excludes the non-VF Retina instance.
            for instance in font.instances:
                if instance.name=='Retina':instance.active=False
        ds=glyphsLib.to_designspace(font,expand_includes=(face=='sans'),ufo_module=ufoLib2,minimal=True)
    out.mkdir(parents=True,exist_ok=True)
    fonts={}
    copyrights=[]
    for src in ds.sources:
        font=src.font
        key=id(font)
        if key not in fonts:
            name=f'{family.replace(" ","")}-m{len(fonts):02d}.ufo'
            fonts[key]=name
            if font.info.copyright and font.info.copyright not in copyrights:copyrights.append(font.info.copyright)
            if face=='mono':
                font.features.text=re.sub(r'(feature cv\d+ \{)\s*featureNames \{(.*?)\};',r'\1\ncvParameters { FeatUILabelNameID {\2}; };',font.features.text,flags=re.S)
            font.info.familyName=family
            font.info.styleMapFamilyName=family
            font.info.postscriptFontName=family.replace(' ','')+'-'+re.sub('[^A-Za-z0-9]','',font.info.styleName or 'Regular')
            font.info.postscriptFullName=family+' '+(font.info.styleName or 'Regular')
            font.info.openTypeNamePreferredFamilyName=family
            font.info.openTypeNameCompatibleFullName=family+' '+(font.info.styleName or 'Regular')
            font.info.openTypeNameUniqueID=font.info.postscriptFontName+';1.000'
            font.info.trademark=None
            font.info.openTypeNameLicense='Licensed under the SIL Open Font License, Version 1.1. See accompanying notices.'
            font.info.openTypeNameLicenseURL='https://openfontlicense.org'
            if font.info.openTypeNameRecords:
                font.info.openTypeNameRecords=clean(font.info.openTypeNameRecords,family)
            # Prevent loading arbitrary filter/feature-writer modules from data.
            font.lib.pop('com.github.googlei18n.ufo2ft.filters',None)
            font.lib.pop('com.github.googlei18n.ufo2ft.featureWriters',None)
            font.lib=clean(dict(font.lib),family)
            font.save(out/name)
            # UFO filename encodings are implementation details, not glyph names.
            for contents in (out/name).glob('*/contents.plist'):
                mapping=plistlib.loads(contents.read_bytes())
                for glyph, filename in list(mapping.items()):
                    if FORBIDDEN.search(filename):
                        new='glyph-'+__import__('hashlib').sha256(glyph.encode()).hexdigest()[:16]+'.glif'
                        (contents.parent/filename).rename(contents.parent/new)
                        mapping[glyph]=new
                contents.write_bytes(plistlib.dumps(mapping,sort_keys=True))
        src.path=str(out/fonts[key]);src.filename=fonts[key]
        src.familyName=family
        src.name=clean(src.name,family)
        src.font=None
    for index,instance in enumerate(ds.instances):
        instance.familyName=family
        instance.styleMapFamilyName=family
        instance.name=clean(instance.name,family)
        instance.postScriptFontName=family.replace(' ','')+'-'+re.sub('[^A-Za-z0-9]','',instance.styleName or f'Instance{index}')
        instance.path=str(out/f'{family.replace(" ","")}-instance-{index:03d}.ufo')
        instance.filename=Path(instance.path).name
        instance.lib=clean(dict(instance.lib),family)
    ds.lib=clean(dict(ds.lib),family)
    ds.write(out/f'{family.replace(" ","")}.designspace')
    (out/'OFL.txt').write_text((ROOT/'licenses'/({'sans':'sans-LICENSE.txt','serif':'serif-sources-LICENSE.md','mono':'mono-LICENSE'}[face])).read_text())
    (out/'COPYRIGHT.txt').write_text('\n\n'.join(copyrights)+'\n')
    return {'masters':len(fonts),'copyrights':copyrights,'sha256':digest(out)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--force',action='store_true');p.add_argument('--resume',action='store_true');args=p.parse_args()
    start=time.monotonic();out=ROOT/'candidates/baseline'
    if (out/'fonts').exists() and not args.force and not args.resume:raise SystemExit('Baseline exists; use --force deliberately to regenerate it')
    if args.force:shutil.rmtree(out/'fonts',ignore_errors=True)
    report={}
    for face in FACES:
        checkpoint()
        before=time.monotonic()
        folder=out/'fonts'/face
        if args.resume and list(folder.glob('*.designspace')):
            report[face]={'masters':len(list(folder.glob('*.ufo'))),'sha256':digest(folder)}
        else:
            if folder.exists():shutil.rmtree(folder)
            report[face]=save_face(face,folder)
        print(f'{face}: {report[face]["masters"]} masters, {time.monotonic()-before:.2f}s',flush=True)
    from icons import prepare_icons
    prepare_icons(out/'icons')
    dump(out/'provenance.json',{'lock_sha256':digest(ROOT/'upstream.lock.json'),'faces':report,'scope':'upright variable baselines; names and compilation only, no design edits'})
    print(f'prepare: {time.monotonic()-start:.2f}s',flush=True)

if __name__=='__main__':main()

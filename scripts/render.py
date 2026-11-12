"""Headless Chromium/WebKit specimens. No server, installed font reads, or exports."""
import argparse
from collections import defaultdict
import hashlib
import io
import uharfbuzz as hb
from html import escape
import json
from pathlib import Path
import re
import shutil
import time
from PIL import Image
from fontTools.ttLib import TTFont
from playwright.sync_api import sync_playwright
from common import checkpoint, ROOT, UPSTREAM, FACES, dump, digest
from gate import checked_build
from icons import huge_svg
from newlabel import labels
from blindcheck import clean_png,check
import specimens as s

FONT_TEST='Hamburgefontsiv 0123456789'
SYSTEM=['system-ui, -apple-system','ui-serif','ui-monospace']
# Literal system symbol codepoints, never outlines or files. Probe every one.
SYMBOLS=[0x1001ad,0x1001c3,0x1001d4,0x1001e3,0x1001f1,0x100200,0x100171,0x10017c]


def font_probe(page,fonts):
    report=page.evaluate('''async ({custom,sample}) => {
      await document.fonts.ready;
      const c=document.createElement('canvas'); const x=c.getContext('2d');x.fontKerning='none';
      const rows=[];
      for(let i=0;i<3;i++){
        const family=custom?'p'+i:['system-ui, -apple-system','ui-serif','ui-monospace'][i];
        if(custom){await document.fonts.load('400 32px p'+i,sample);if(!document.fonts.check('400 32px p'+i,sample))throw Error('Font failed to load');}
        x.font='400 32px '+family;const width=x.measureText(sample).width;
        x.font='400 32px monospace';const mono=x.measureText(sample).width;
        x.font='400 32px serif';const serif=x.measureText(sample).width;
        if(custom && (Math.abs(width-mono)<.01 || Math.abs(width-serif)<.01))throw Error('Font fell back to a generic family');
        rows.push({width,mono,serif,loaded:!custom||document.fonts.check('400 32px p'+i,sample)});
      }
      return rows;
    }''',{'custom':isinstance(fonts,dict),'sample':FONT_TEST})
    if isinstance(fonts,dict):
        # Require the actual loaded FontFace objects, not merely fonts.check's
        # generic-family success. Then check text cmap for each sheet separately.
        loaded=page.evaluate("[...document.fonts].filter(f=>/^p[012]$/.test(f.family)&&f.status==='loaded').length")
        if loaded!=3:raise ValueError(f'FontFace load count {loaded}, expected 3')
        for index,face in enumerate(list(fonts.values())[:3]):
            with TTFont(face) as font:
                cmap=font.getBestCmap()
                if any(ord(c) not in cmap for c in FONT_TEST):raise ValueError('Probe glyph missing')
                font.flavor=None;data=io.BytesIO();font.save(data)
                axes={axis.axisTag:axis.defaultValue for axis in font['fvar'].axes} if 'fvar' in font else {}
            hbface=hb.Face(data.getvalue());expected=[]
            for optical in [None,32]:
                hbfont=hb.Font(hbface);hbfont.scale=(hbface.upem,hbface.upem)
                location={**axes,'wght':400}
                if optical is not None and 'opsz' in axes:location['opsz']=optical
                hbfont.set_variations(location)
                buffer=hb.Buffer();buffer.add_str(FONT_TEST);buffer.guess_segment_properties()
                hb.shape(hbfont,buffer,{'kern':False})
                if any(info.codepoint==0 for info in buffer.glyph_infos):raise ValueError('Probe mapped to .notdef')
                expected.append(sum(pos.x_advance for pos in buffer.glyph_positions)*32/hbface.upem)
            report[index]['expected_widths']=expected
            if min(abs(report[index]['width']-value) for value in expected)>.65:
                raise ValueError(f'Font fingerprint mismatch: measured {report[index]["width"]}, expected {expected}')
    return report


def text_coverage(page,fonts):
    if not isinstance(fonts,dict):return
    texts=page.locator('[data-face]').evaluate_all('(els)=>els.map(e=>({index:Number(e.dataset.face),family:getComputedStyle(e).fontFamily,text:e.textContent}))')
    for row in texts:
        if row['family'].strip('\"').split(',')[0] != 'p'+str(row['index']):raise ValueError('Specimen CSS points to the wrong family')
        path=list(fonts.values())[row['index']]
        with TTFont(path,lazy=True) as font:cmap=font.getBestCmap()
        missing={f'U+{ord(c):04X}' for c in row['text'] if not c.isspace() and ord(c) not in cmap}
        if missing:raise ValueError(f'Would fall back for missing glyphs: {sorted(missing)}')


def rounded_probe(page,path=None):
    sample='72° −3° 104°F 18℃ 0123456789 08:00 100%'
    result=page.evaluate('''async ({sample,custom})=>{
        const c=document.createElement('canvas');c.width=2048;c.height=100;
        const x=c.getContext('2d');
        const family=custom?'p3':'ui-rounded';
        if(custom)await document.fonts.load('400 48px p3',sample);
        function width(f){x.font='400 48px '+f;return x.measureText(sample).width;}
        function raster(f){x.clearRect(0,0,c.width,c.height);x.font='400 48px '+f;x.fillText(sample,4,70);
          const d=x.getImageData(0,0,c.width,c.height).data;let hash=2166136261,ink=0;
          for(let i=3;i<d.length;i+=4){hash=Math.imul(hash^d[i],16777619);if(d[i])ink++;}
          return {hash:hash>>>0,ink};}
        return {width:width(family),regular:width('system-ui'),mono:width('monospace'),serif:width('serif'),
          rasters:custom?null:[family,'system-ui','monospace','serif','sans-serif','__missing_round_0__'].map(f=>({family:f,...raster(f)})),
          loaded:!custom||[...document.fonts].some(f=>f.family==='p3'&&f.status==='loaded')};
    }''',{'sample':sample,'custom':path is not None})
    if not result['loaded']:raise ValueError('Rounded FontFace did not load')
    if path is not None:
        with TTFont(path) as font:
            font.flavor=None;data=io.BytesIO();font.save(data)
            axes={a.axisTag:a.defaultValue for a in font['fvar'].axes}
        face=hb.Face(data.getvalue());widths=[]
        for optical in [None,48]:
            font=hb.Font(face);font.scale=(face.upem,face.upem)
            location={**axes,'wght':400}
            if optical is not None and 'opsz' in axes:location['opsz']=optical
            font.set_variations(location);buffer=hb.Buffer();buffer.add_str(sample);buffer.guess_segment_properties()
            hb.shape(font,buffer)
            if any(info.codepoint==0 for info in buffer.glyph_infos):raise ValueError('Rounded probe missing a glyph')
            widths.append(sum(p.x_advance for p in buffer.glyph_positions)*48/face.upem)
        result['expected_widths']=widths
        if min(abs(result['width']-w) for w in widths)>.65:raise ValueError('Rounded font fingerprint mismatch')
    else:
        rasters=result['rasters']
        result['available']=rasters[0]['ink']>20 and all(rasters[0]['hash']!=r['hash'] for r in rasters[1:])
    return result


def symbol_probe(page):
    return page.evaluate('''(points)=>{
      const c=document.createElement('canvas');c.width=96;c.height=96;const x=c.getContext('2d');
      function fingerprint(t,f){x.clearRect(0,0,96,96);x.fillStyle='black';x.font='48px '+f;x.fillText(t,8,64);const d=x.getImageData(0,0,96,96).data;let h=2166136261,ink=0;for(let i=3;i<d.length;i+=4){h=Math.imul(h^d[i],16777619);if(d[i])ink++;}return {hash:h>>>0,ink,width:x.measureText(t).width};}
      const unknown=fingerprint(String.fromCodePoint(0x10ffff),'system-ui');
      return points.map(cp=>{const value=fingerprint(String.fromCodePoint(cp),'system-ui');const generic=fingerprint(String.fromCodePoint(cp),'monospace');return {cp,...value,rendered:value.ink>20&&value.hash!==unknown.hash&&value.hash!==generic.hash};});
    }''',SYMBOLS)


def main():
    p=argparse.ArgumentParser();p.add_argument('--cand',required=True);p.add_argument('--out',required=True);p.add_argument('--map',required=True);p.add_argument('--refs',choices=['0','1'],default='0');p.add_argument('--icons-dir');a=p.parse_args()
    if not a.out or not a.map:raise ValueError('OUT and MAP are required; MAP belongs outside OUT')
    start=time.monotonic();path,build,buildinfo,icon_source=checked_build(a.cand,a.icons_dir)
    out=Path(a.out).expanduser().resolve();mapfile=Path(a.map).expanduser().resolve()
    if mapfile.is_relative_to(out):raise ValueError('Lead-only MAP cannot be inside OUT')
    if out.exists() and any(out.iterdir()):raise ValueError('OUT must be empty, to prevent stale labels or leaked files')
    out.mkdir(parents=True,exist_ok=True)
    scratch=build/'render-html';scratch.mkdir(exist_ok=True)
    keys=[a.cand]+(['ref:open','ref:system','ref:hugeicons','ref:symbols','ref:rounded'] if a.refs=='1' else [])
    mapping=labels(mapfile,keys)
    candidatefonts={face:build/buildinfo['faces'][face]['woff2'] for face in FACES}
    if 'sans-rounded' in buildinfo['faces']:candidatefonts['sans-rounded']=build/buildinfo['faces']['sans-rounded']['woff2']
    svgpaths=sorted((build/'icons/svg').glob('*.svg'));svgs=[p.read_text() for p in svgpaths]
    rows=[];audit={'controls':{'open':'Pinned unmodified upstream binaries','system':'CSS system-ui/ui-serif/ui-monospace; installed rendering only'},'candidate':a.cand,'font_checks':{},'system_engine_check':{},'skipped':[],'output':str(out)}
    counters=defaultdict(int)
    def save(page,key,fonts,body,theme,kind,engine):
        checkpoint()
        label=mapping[key];counters[label]+=1;number=counters[label]
        html=s.document(label,fonts,body,theme)
        (scratch/f'{label}-{number:02}.html').write_text(html)
        page.set_content(html,wait_until='load');page.evaluate('document.fonts.ready')
        if isinstance(fonts,dict):
            page.evaluate('async () => { await Promise.all([0,1,2].map(i=>document.fonts.load("400 32px p"+i))); }')
        text_coverage(page,fonts)
        if page.locator('[data-face="3"]').count() and isinstance(fonts,dict):
            audit['font_checks'][key+':rounded']=rounded_probe(page,fonts['sans-rounded'])
        # Asset failure must fail the command instead of generating an attractive fallback.
        if isinstance(fonts,dict):
            for i in range(3):
                if not page.evaluate(f'document.fonts.check("400 32px p{i}")'):raise ValueError('Font unloaded during specimen render')
        filename=f'{label}-{number:02}.png';dest=out/filename
        if page.evaluate('document.documentElement.scrollWidth')>1120:raise ValueError('Specimen overflows sheet width')
        page.screenshot(path=str(dest),full_page=True,animations='disabled');clean_png(dest)
        with Image.open(dest) as image:width,height=image.size
        rows.append({'label':label,'image':filename,'sheet':kind,'theme':theme,'width':width,'height':height,'scale':2})
        return dest
    def suite(browser,key,fonts,engine):
        page=browser.new_page(viewport={'width':1120,'height':900},device_scale_factor=2)
        page.route('**/*',lambda route:route.abort())
        page.set_content(s.document(mapping[key],fonts,'<p>0123456789</p>'))
        audit['font_checks'][key+':'+engine]=font_probe(page,fonts)
        for face in range(3):
            for theme in ['light','dark','sky','glass']:save(page,key,fonts,s.waterfall(face),theme,f'{face+1:02}',engine)
        for theme in ['light','dark']:
            save(page,key,fonts,s.weather(),theme,'04',engine)
            save(page,key,fonts,s.card(),theme,'05',engine)
        save(page,key,fonts,s.card(),'glass','05',engine)
        save(page,key,fonts,s.code(),'light','06',engine)
        save(page,key,fonts,s.code(),'dark','06',engine)
        for face in range(3):
            if isinstance(fonts,dict):body=s.outlines(fonts[list(FACES)[face]],face)
            else:body='<div class="f'+str(face)+'">'+''.join('<div class="zoom">'+escape(c)+'</div>' for c in s.KEYS)+'</div>'
            save(page,key,fonts,body,'light','07',engine)
        if isinstance(fonts,dict) and 'sans-rounded' in fonts:
            for theme in ['light','dark','sky']:
                save(page,key,fonts,s.rounded(),theme,'10',engine)
                save(page,key,fonts,s.rounded_cards(),theme,'11',engine)
        page.close()
    def icon_sheets(browser,key,icons,fonts,engine):
        page=browser.new_page(viewport={'width':1120,'height':900},device_scale_factor=2)
        for startindex in range(0,len(icons),48):
            body=s.icon_sheet(icons[startindex:startindex+48],startindex)
            for theme in ['light','dark','light grid']:save(page,key,fonts,body,theme,'08',engine)
        page.close()
    with sync_playwright() as pw:
        with pw.chromium.launch() as chromium:
            suite(chromium,a.cand,candidatefonts,'chromium')
            icon_sheets(chromium,a.cand,svgs,candidatefonts,'chromium')
            # Also prove the stroke-expanded icon font loads and has every codepoint.
            page=chromium.new_page(viewport={'width':1120,'height':900},device_scale_factor=2)
            imap=json.loads((build/'icons/manifest.json').read_text())['icons']
            chars=''.join(chr(int(v['codepoint'],16)) for v in imap.values())
            body=s.icon_font(build/'icons/StrataIcons.woff2',chars)
            save(page,a.cand,candidatefonts,body,'light','09','chromium')
            if not page.evaluate('document.fonts.check("32px q")'):raise ValueError('Icon font fallback')
            page.close()
            if a.refs=='1':
                controls={'sans':UPSTREAM/'sans/docs/font-files/InterVariable.woff2','serif':UPSTREAM/'serif/VAR/SourceSerif4Variable-Roman.ttf','mono':UPSTREAM/'mono-release/StrataMonoUpstream.ttf'}
                suite(chromium,'ref:open',controls,'chromium')
                icon_sheets(chromium,'ref:open',svgs,controls,'chromium')
                huge=[huge_svg(n) for n in ['Sun03','Moon02','Cloud','CloudAngledRain','CloudLittleRain','CloudSnow','CloudFastWind','SunCloud01','SunCloudLittleRain01','SunCloudSnow01','WindPower','Umbrella','Search01','Location01','ArrowLeft01','ArrowRight01','Settings01','Notification01','Calendar01','Clock01','Menu01','Cancel01','Add01','MinusSign']]
                icon_sheets(chromium,'ref:hugeicons',huge,controls,'chromium')
                cp=chromium.new_page();cp.set_content(s.document(mapping['ref:system'],SYSTEM,'<p>0123456789</p>'))
                audit['system_engine_check']['chromium']=font_probe(cp,SYSTEM);cp.close()
                with pw.webkit.launch() as webkit:
                    wp=webkit.new_page();wp.set_content(s.document(mapping['ref:system'],SYSTEM,'<p>0123456789</p>'))
                    audit['system_engine_check']['webkit']=font_probe(wp,SYSTEM)
                    symbols=symbol_probe(wp);audit['system_symbol_probe']=symbols;wp.close()
                    if any(abs(row['width']-row['serif'])<.01 or abs(row['width']-row['mono'])<.01 for row in audit['system_engine_check']['webkit']):
                        raise ValueError('An installed system reference fell back in WebKit')
                    suite(webkit,'ref:system',SYSTEM,'webkit')
                    rp=webkit.new_page(viewport={'width':1120,'height':900},device_scale_factor=2)
                    rp.set_content(s.document(mapping['ref:rounded'],SYSTEM+['ui-rounded'],s.rounded()))
                    audit['system_rounded_probe']=rounded_probe(rp)
                    if audit['system_rounded_probe']['available']:
                        for theme in ['light','dark','sky']:
                            save(rp,'ref:rounded',SYSTEM+['ui-rounded'],s.rounded(),theme,'10','webkit')
                            save(rp,'ref:rounded',SYSTEM+['ui-rounded'],s.rounded_cards(),theme,'11','webkit')
                    else:audit['skipped'].append('WebKit ui-rounded raster matched a fallback family; skipped')
                    rp.close()
                    # System references do not produce outline diagrams; raster zooms only.
                    audit['skipped'].append('Apple outline views forbidden; replaced with rendered text zooms without stored outlines')
                    good=[chr(r['cp']) for r in symbols if r['rendered']]
                    if len(good)>=3:
                        page=webkit.new_page(viewport={'width':1120,'height':900},device_scale_factor=2)
                        body='<div style="font-family:system-ui" class="icons">'+''.join('<div class="tile">'+''.join(f'<span style="font-size:{size}px">{glyph}</span>' for size in [16,20,24,32])+'</div>' for glyph in good)+'</div>'
                        for theme in ['light','dark','light grid']:save(page,'ref:symbols',SYSTEM,body,theme,'08','webkit')
                        page.close()
                    else:audit['skipped'].append('SF Symbols private-use probes did not resolve reliably through system-ui in WebKit; no symbols reference emitted')
                delta=max(abs(c['width']-w['width']) for c,w in zip(audit['system_engine_check']['chromium'],audit['system_engine_check']['webkit']))
                audit['system_engine_check']['max_width_delta']=delta
                chrome_valid=all(abs(row['width']-row['serif'])>.01 and abs(row['width']-row['mono'])>.01 for row in audit['system_engine_check']['chromium'])
                if delta>.1 and chrome_valid:suite(chromium,'ref:system',SYSTEM,'chromium')
                elif not chrome_valid:audit['skipped'].append('Chromium falls back for system serif/mono on this Mac; installed system references emitted in WebKit only')
                else:audit['skipped'].append('System font width probes agree across Chromium/WebKit; system sheets emitted in WebKit only')
    dump(out/'index.json',{'sheets':rows})
    count=check(out);audit['seconds']=round(time.monotonic()-start,3);audit['png_count']=count;audit['blind_byte_scan']='PASS'
    dump(build/'render-audit.json',audit)
    print(f'render: {count} PNGs, {audit["seconds"]:.3f}s; blind byte scan PASS',flush=True)
    for skip in audit['skipped']:print(skip,flush=True)

if __name__=='__main__':main()

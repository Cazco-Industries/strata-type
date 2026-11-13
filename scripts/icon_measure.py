"""Isolate built icon glyphs and their own SVGs in equal em boxes, offline."""
import argparse
import base64
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from playwright.sync_api import sync_playwright
from common import checkpoint, dump
from gate import checked_build
from specimens import re_size


def raster(image,size,dpr,stem=False):
    """Coverage-weighted area and stem; bbox uses >=50% black coverage."""
    image=image.convert('L');pixels=image.load();area=mx=my=0;points=[]
    for y in range(image.height):
        for x in range(image.width):
            coverage=(255-pixels[x,y])/255
            area+=coverage;mx+=coverage*(x+.5);my+=coverage*(y+.5)
            if coverage>=.5:points.append((x,y))
    if not points:raise ValueError('Empty icon raster')
    xs,ys=zip(*points);bbox=[min(xs)/dpr-8,min(ys)/dpr-8,(max(xs)+1)/dpr-8,(max(ys)+1)/dpr-8]
    # add.svg has an isolated vertical shaft through viewBox y=8.
    rows=range(round((8+size*8/24)*dpr),round((8+size*8/24)*dpr)+max(1,dpr))
    width=sum(sum((255-pixels[x,y])/255 for x in range(image.width))/dpr for y in rows)/len(rows) if stem else None
    return {'ink_area_px2':area/dpr**2,'stem_width_px':width,'bbox_px':bbox,
            'ink_centroid_px':[mx/area/dpr-8,my/area/dpr-8]}


def measure(cand,icons_dir,out):
    _,build,_,_=checked_build(cand,icons_dir);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((build/'icons/manifest.json').read_text())
    fontpath=build/'icons/StrataIcons.woff2';fontdata=base64.b64encode(fontpath.read_bytes()).decode()
    with TTFont(fontpath) as font:
        cmap=font.getBestCmap()
        bearings={name:{'xMin':font['glyf'][cmap[int(v['codepoint'],16)]].xMin,
                        'lsb':font['hmtx'][cmap[int(v['codepoint'],16)]][1]} for name,v in manifest['icons'].items()}
    report={'candidate':cand,'stroke_width':manifest['stroke_width'],'font_metrics':bearings,
            'method':'Black on white; identical CSS em boxes; line-height 1; weight 400; coverage area=sum(1-gray/255); stem=integrated coverage across add vertical shaft at SVG y=8; bbox=50% coverage, relative to em box; no network',
            'rows':[]}
    names=[n for n in ['add' if 'add' in manifest['icons'] else 'plus',
                       'rain','thunderstorm','alert' if 'alert' in manifest['icons'] else 'alert-triangle'] if n in manifest['icons']]
    with sync_playwright() as pw:
        for engine in ['chromium','webkit']:
            checkpoint()
            with getattr(pw,engine).launch() as browser:
                for dpr in [1,2]:
                    page=browser.new_page(viewport={'width':800,'height':600},device_scale_factor=dpr)
                    page.route('**/*',lambda route:route.abort())
                    tiles=[]
                    for name in names:
                        svg=(build/'icons/svg'/f'{name}.svg').read_text()
                        char=chr(int(manifest['icons'][name]['codepoint'],16))
                        for size in [16,20,24,32]:
                            checkpoint()
                            css=f'''@font-face{{font-family:q;src:url(data:font/woff2;base64,{fontdata})}}
                              *{{box-sizing:border-box}}body{{margin:0;background:white;color:black}}
                              .box{{padding:8px;width:{size+16}px;height:{size+16}px;overflow:visible}}
                              .glyph{{display:block;width:1em;height:1em;font:400 {size}px/1 q;font-synthesis:none}}
                              svg{{display:block}}.unitgrid{{display:none}}'''
                            page.set_content(f'<style>{css}</style><div class="box" id="font"><span class="glyph">{char}</span></div><div class="box" id="svg">{re_size(svg,size)}</div>')
                            page.evaluate('document.fonts.ready')
                            if not page.evaluate("[...document.fonts].some(f=>f.family==='q'&&f.status==='loaded')"):
                                raise ValueError('Icon FontFace did not load')
                            images={kind:Image.open(io.BytesIO(page.locator('#'+kind).screenshot(animations='disabled'))).convert('RGB') for kind in ['font','svg']}
                            metrics={kind:raster(image,size,dpr,name in {'add','plus'}) for kind,image in images.items()}
                            a,b=metrics['font'],metrics['svg']
                            row={'engine':engine,'dpr':dpr,'icon':name,'size_px':size,**metrics,
                                 'area_difference_percent':(a['ink_area_px2']/b['ink_area_px2']-1)*100,
                                 'bbox_offset_px':[a['bbox_px'][i]-b['bbox_px'][i] for i in range(2)],
                                 'centroid_offset_px':[a['ink_centroid_px'][i]-b['ink_centroid_px'][i] for i in range(2)]}
                            report['rows'].append(row)
                            if dpr==2:
                                tile=Image.new('RGB',(240,144),'white');draw=ImageDraw.Draw(tile);draw.text((3,3),f'{name} {size}px: font / SVG',fill='black')
                                tile.paste(images['font'],(8,25));tile.paste(images['svg'],(125,25));tiles.append(tile)
                    page.close()
                    if tiles:
                        montage=Image.new('RGB',(960,144*len(names)),'#eeeeee')
                        for i,tile in enumerate(tiles):montage.paste(tile,((i%4)*240,(i//4)*144))
                        montage.save(out/f'{engine}.png')
    dump(out/'measurements.json',report)
    lines=['engine DPR size | font / SVG area px² | font / SVG stem px | bbox offset x,y px']
    for row in report['rows']:
        if row['icon'] not in {'add','plus'}:continue
        a,b=row['font'],row['svg']
        lines.append(f'{row["engine"]} {row["dpr"]} {row["size_px"]} | {a["ink_area_px2"]:.3f} / {b["ink_area_px2"]:.3f} ({row["area_difference_percent"]:+.2f}%) | {a["stem_width_px"]:.3f} / {b["stem_width_px"]:.3f} | {row["bbox_offset_px"]}')
    text='\n'.join(lines)+'\n';(out/'measurements.txt').write_text(text);print(text,flush=True)
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--cand',required=True);p.add_argument('--icons-dir');p.add_argument('--out',required=True);a=p.parse_args()
    measure(a.cand,a.icons_dir,a.out)


if __name__=='__main__':main()

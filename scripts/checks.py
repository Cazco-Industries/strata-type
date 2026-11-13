"""Review checks on built candidate fonts; failures remain separate from renders."""
import argparse
import io
import itertools
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from common import ROOT, checkpoint, dump
from gate import checked_build

STRINGS = ['104°F', '72°', '18:30', '−3°']


def locations(tt):
    if 'fvar' not in tt:return [{}]
    axes=tt['fvar'].axes
    values=[{a.axisTag:v for a,v in zip(axes,combo)} for combo in
            itertools.product(*[(a.minValue,a.defaultValue,a.maxValue) for a in axes])]
    values += [dict(i.coordinates) for i in tt['fvar'].instances]
    return [dict(v) for v in sorted({tuple(sorted(v.items())) for v in values})]


def ink_width(path,text,size=96):
    """Shaped outline union, not the run's advance or a system fallback.

    Match CSS normal figures, weight 400 and automatic optical size at 96 px.
    Requested axis values are clamped to the font's own supported range.
    """
    with TTFont(path) as tt:
        axes={a.axisTag:a for a in tt['fvar'].axes} if 'fvar' in tt else {}
        loc={tag:max(a.minValue,min(a.maxValue,{'wght':400,'opsz':size}.get(tag,a.defaultValue))) for tag,a in axes.items()}
        glyphs=tt.getGlyphSet(location=loc);order=tt.getGlyphOrder()
        tt.flavor=None;data=io.BytesIO();tt.save(data)
        face=hb.Face(data.getvalue());font=hb.Font(face);font.scale=(face.upem,face.upem);font.set_variations(loc)
        buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(font,buf,{})
        if any(i.codepoint==0 for i in buf.glyph_infos):raise ValueError(f'Missing glyph in {text!r}')
        left=right=None;x=0
        for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
            pen=BoundsPen(glyphs);glyphs[order[info.codepoint]].draw(pen)
            if pen.bounds:
                x0,_,x1,_=pen.bounds
                lo=x+pos.x_offset+x0;hi=x+pos.x_offset+x1
                left=lo if left is None else min(left,lo)
                right=hi if right is None else max(right,hi)
            x+=pos.x_advance
        if left is None:raise ValueError(f'No ink in {text!r}')
        return {'ink_width_px':(right-left)*size/face.upem,'advance_px':x*size/face.upem,'location':loc}


def tabular(path,required):
    with TTFont(path) as tt:
        cmap=tt.getBestCmap();names=[cmap.get(ord(c)) for c in '0123456789']
        if not all(names):return {'status':'FAIL','required':required,'error':'Missing default cmap figure'}
        tt.flavor=None;data=io.BytesIO();tt.save(data);face=hb.Face(data.getvalue())
        rows=[]
        for loc in locations(tt):
            glyphs=tt.getGlyphSet(location=loc)
            direct=[glyphs[n].width for n in names]
            font=hb.Font(face);font.scale=(face.upem,face.upem);font.set_variations(loc)
            buf=hb.Buffer();buf.add_str('0123456789');buf.guess_segment_properties();hb.shape(font,buf,{})
            shaped=[p.x_advance for p in buf.glyph_positions]
            ok=len(set(direct))==1 and len(shaped)==10 and len(set(shaped))==1 and all(i.codepoint for i in buf.glyph_infos)
            rows.append({'location':loc,'cmap_advances':direct,'default_shaped_advances':shaped,'tabular':bool(ok)})
        all_equal=all(r['tabular'] for r in rows)
        return {'status':('PASS' if all_equal else 'FAIL') if required else 'INFO',
                'required':required,'tabular_at_all_locations':all_equal,'locations':rows}


def run(cand,icons_dir=None):
    _,build,info,_=checked_build(cand,icons_dir)
    result={'candidate':cand,'rounded_ink_width':{'status':'NOT_APPLICABLE','reason':'Candidate has no Rounded face'},'tabular_default':{}}
    if 'sans-rounded' in info['faces']:
        rows=[]
        for text in STRINGS:
            checkpoint()
            try:
                a=ink_width(build/info['faces']['sans']['ttf'],text)
                b=ink_width(build/info['faces']['sans-rounded']['ttf'],text)
                delta=(b['ink_width_px']/a['ink_width_px']-1)*100
                rows.append({'text':text,'regular':a,'rounded':b,'difference_percent':delta,'status':'PASS' if abs(delta)<=1 else 'FAIL'})
            except ValueError as e:rows.append({'text':text,'status':'FAIL','error':str(e)})
        result['rounded_ink_width']={'status':'PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',
                                     'size_px':96,'weight':400,'threshold_percent':1,'method':'HarfBuzz shaping plus exact outline ink bounds; CSS automatic optical size; default features','rows':rows}
    for face,record in info['faces'].items():
        checkpoint();result['tabular_default'][face]=tabular(build/record['ttf'],face!='serif')
    failed=result['rounded_ink_width']['status']=='FAIL' or any(v['status']=='FAIL' for v in result['tabular_default'].values())
    result['status']='FAIL' if failed else 'PASS'
    dump(build/'checks.json',result)
    lines=[f'# Review checks: {result["status"]}', '',f'Rounded / Regular ink width: {result["rounded_ink_width"]["status"]} (96 px, 400, limit 1%)','']
    for row in result['rounded_ink_width'].get('rows',[]):
        if 'error' in row:lines.append(f'- {row["text"]}: FAIL — {row["error"]}');continue
        lines.append(f'- {row["text"]}: {row["status"]}; Regular {row["regular"]["ink_width_px"]:.3f} px, Rounded {row["rounded"]["ink_width_px"]:.3f} px; {row["difference_percent"]:+.3f}%')
    lines+=['','Default cmap and default shaped figures (all named instances and axis min/default/max combinations):']
    for face,row in result['tabular_default'].items():
        lines.append(f'- {face}: {row["status"]}; tabular={row.get("tabular_at_all_locations",False)}; {len(row.get("locations",[]))} locations')
    text='\n'.join(lines)+'\n';(build/'checks.md').write_text(text)
    print(text,flush=True)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--cand',required=True);p.add_argument('--icons-dir');a=p.parse_args()
    raise SystemExit(0 if run(a.cand,a.icons_dir)['status']=='PASS' else 1)


if __name__=='__main__':main()

"""Rebuild the editable family from the untouched baseline, deterministically."""
from pathlib import Path
import copy
import argparse
import json
import math
import re
import shutil
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.bezierTools import splitCubicAtT
from ufoLib2 import Font
from ufoLib2.objects import Component

HERE = Path(__file__).resolve().parent
CAND = HERE.parent
ROOT = CAND.parents[1]
BASE = ROOT / 'candidates' / 'baseline' / 'fonts'
WORK = Path.home() / 'strata-ml/type-climb-work/quartz-571'
DIGITS = 'zero one two three four five six seven eight nine'.split()
K = 0.5522847498307936


def bounds(font, name):
    p = BoundsPen(font)
    font[name].draw(p)
    return p.bounds


def replace(font, name, cp=None, width=None):
    if name in font:
        g = font[name]
        g.clearContours()
        g.clearComponents()
    else:
        g = font.newGlyph(name)
    if cp is not None:
        for other in font:
            if other.name != name and cp in other.unicodes:
                other.unicodes.remove(cp)
        g.unicodes = [cp]
    if width is not None:
        g.width = width
    return g


def polygon(glyph, pts):
    p = glyph.getPen()
    p.moveTo(pts[0])
    for pt in pts[1:]:
        p.lineTo(pt)
    p.closePath()


def ellipse(glyph, cx, cy, rx, ry, reverse=False):
    pts = [(cx+rx,cy), (cx+rx,cy+ry*K), (cx+rx*K,cy+ry), (cx,cy+ry),
           (cx-rx*K,cy+ry), (cx-rx,cy+ry*K), (cx-rx,cy),
           (cx-rx,cy-ry*K), (cx-rx*K,cy-ry), (cx,cy-ry),
           (cx+rx*K,cy-ry), (cx+rx,cy-ry*K), (cx+rx,cy)]
    if reverse:
        pts = [pts[0], *reversed(pts[1:-1]), pts[0]]
    p = glyph.getPen()
    p.moveTo(pts[0])
    for i in range(1, 13, 3):
        p.curveTo(*pts[i:i+3])
    p.closePath()


def affine_family(font, maps):
    """Conjugate component transforms so composite geometry receives one map."""
    for g in font:
        t = maps[g.name]
        for contour in g.contours:
            for pt in contour.points:
                pt.x, pt.y = t.transformPoint((pt.x, pt.y))
        for anchor in g.anchors:
            anchor.x, anchor.y = t.transformPoint((anchor.x, anchor.y))
        for comp in g.components:
            comp.transformation = t.transform(comp.transformation).transform(maps[comp.baseGlyph].inverse())
        g.width = round(g.width*t.xx + 2*t.dx) if g.width else 0


def sanitize(font, family):
    for attr in ('familyName','styleMapFamilyName','postscriptFontName','postscriptFullName',
                 'openTypeNamePreferredFamilyName','openTypeNameCompatibleFullName',
                 'openTypeNameWWSFamilyName'):
        old = getattr(font.info, attr, None)
        if old:
            setattr(font.info, attr, re.sub(r'Source\s*Serif\s*(?:4|Pro)?|Inter(?: Variable)?|Fira\s*Code', family, old, flags=re.I))
    font.info.familyName = family
    font.info.copyright = 'Copyright notices retained verbatim in the accompanying licenses directory.'
    font.info.trademark = None
    if font.info.openTypeNameRecords:
        for record in font.info.openTypeNameRecords:
            record.string = re.sub(r'Inter|Source|Fira', '', record.string, flags=re.I)
    font.features.text = re.sub(r'(nameid\s+\d+\s+)"[^"]*";',
        lambda m: m.group(0) if not re.search(r'Inter|Source|Fira', m.group(0), re.I)
        else m.group(1)+'"See accompanying copyright and license notices.";', font.features.text)
    # Keep only portable public metadata and remove stale editor family records.
    font.lib = {k:v for k,v in font.lib.items() if k.startswith('public.')}
    for g in font:
        g.lib.clear()


def info_metrics(font, xheight, cap):
    upm = font.info.unitsPerEm
    font.info.xHeight = round(xheight)
    font.info.capHeight = round(cap)
    font.info.ascender = round(upm*1.14)
    font.info.descender = -round(upm*.36)
    for key, value in {'openTypeOS2TypoAscender':1.14,'openTypeOS2TypoDescender':-.36,
        'openTypeOS2TypoLineGap':0,'openTypeHheaAscender':1.14,'openTypeHheaDescender':-.36,
        'openTypeHheaLineGap':0,'openTypeOS2WinAscent':1.20,'openTypeOS2WinDescent':.40}.items():
        setattr(font.info, key, round(upm*value))
    # Explicit baseline hhea declarations otherwise override the UFO metrics.
    font.features.text = re.sub(r'table hhea\s*\{.*?\}\s*hhea;', '', font.features.text, flags=re.S)
    font.features.text = re.sub(r'table head\s*\{.*?\}\s*head;', '', font.features.text, flags=re.S)
    font.features.text = re.sub(r'table OS/2\s*\{.*?\}\s*OS/2;', '', font.features.text, flags=re.S)
    font.info.versionMajor = 1
    font.info.versionMinor = 1


def sans_details(font, display):
    """Keep point correspondence for local edits; replace figures identically."""
    for name in ('a','a.1'):
        if name not in font:
            continue
        g = font[name]
        if name == 'a' and len(g.contours) == 2:
            # Enlarge the lower counter and give the shoulder a less pinched exit.
            for pt in g.contours[1].points:
                pt.x = 530 + (pt.x-530)*1.055
                pt.y = 345 + (pt.y-345)*1.045
            for i in (13,14):
                g.contours[0].points[i].y += 16 if display else 27
    for name in ('r',):
        g = font[name]
        for i in (6,7,8,9,10,11,12):
            g.contours[0].points[i].x -= 32 if display else 44
        g.contours[0].points[8].y += 12
    g=font['G']
    for i in (4,5):
        g.contours[0].points[i].y -= 23
    for i in (5,6):
        g.contours[0].points[i].x += 45
    g=font['R']
    for i in (0,1):
        g.contours[1].points[i].x += 36
    # Narrower, upright ovals: broaden their shoulders without disturbing extrema.
    for name in ('o','O','zero','six','nine'):
        for contour in font[name].contours:
            xs=[p.x for p in contour.points];ys=[p.y for p in contour.points]
            cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
            for pt in contour.points:
                if pt.type is None:
                    pt.x = cx+(pt.x-cx)*1.018
                    pt.y = cy+(pt.y-cy)*1.006
    # The crossbar extends more to the right, giving t a forward reading rhythm.
    for p in font['t'].contours[0].points:
        if p.x > 300:
            p.x += 28
    for name in ('one','one.tf'):
        old=font[name];width=old.width
        stem=font['one'].contours[0].points[-1].x-font['one'].contours[0].points[-2].x if name=='one' else saved_stem
        if name=='one':saved_stem=stem
        stem=max(40,abs(stem));cap=1490;cx=width*.55
        l=cx-stem/2;r=cx+stem/2;foot=width*.36
        g=replace(font,name,width=width)
        polygon(g,[(r,cap),(l-12,cap),(width*.10,cap*.835),(width*.10,cap*.835-stem*1.05),
                   (l,cap-stem*.94),(l,stem*.84),(cx-foot,stem*.84),(cx-foot,0),
                   (cx+foot,0),(cx+foot,stem*.84),(r,stem*.84)])
    # An unmistakably open-top four. Retain the vertical stroke and its weight.
    g=font['four'];p=g.contours[0].points
    stem_left=min(v.x for v in g.contours[1].points)
    stem_width=max(v.x for v in g.contours[1].points)-stem_left
    diagonal_right=stem_left-max(52,stem_width*.20)
    diagonal_left=diagonal_right-stem_width*.90
    vertices=[(p[0].x,p[0].y),(p[1].x,p[1].y),(p[2].x,p[2].y),
              (p[3].x,p[3].y),(diagonal_right,1490),(diagonal_left,1490),
              (p[9].x,p[9].y)]
    vertical=copy.deepcopy(g.contours[1])
    g.clearContours();polygon(g,vertices);g.appendContour(vertical)


def common_weather(font, face, display):
    u=font.info.unitsPerEm;cap=font.info.capHeight
    cpmap={c:g.name for g in font for c in g.unicodes}
    width=font['zero.tf'].width if face=='sans' else font['zero'].width
    # The sign's advance is one figure, with its ink centred on lining figures.
    old=font['minus'];b=bounds(font,'minus');thick=(b[3]-b[1])
    for name in ('minus','minus.tf') if face=='sans' else ('minus',):
        g=replace(font,name,0x2212 if name=='minus' else None,width)
        x0=width*.16;x1=width*.84;y=cap*.5
        polygon(g,[(x0,y-thick/2),(x0,y+thick/2),(x1,y+thick/2),(x1,y-thick/2)])
    diameter=u*(.218 if display else .232)
    stem=bounds(font,'H')[2]-bounds(font,'H')[0]
    # Weight-dependent ring thickness measured from the real minus stroke.
    ring=min(diameter*.31,max(u*.017,thick*.55))
    advance=width if face=='mono' else u*(.295 if display else .315)
    cx=u*.145 if face=='mono' else advance*.48
    cy=cap+u*.006-diameter/2
    g=replace(font,'degree',0x00b0,round(advance))
    ellipse(g,cx,cy,diameter/2,diameter/2,True)
    ellipse(g,cx,cy,diameter/2-ring,diameter/2-ring)
    for cp,letter,name in ((0x2103,'C','degreecentigrade'),(0x2109,'F','degreefahrenheit')):
        if face=='mono':
            g=replace(font,name,cp,width)
            g.components.append(Component('degree',(0.66,0,0,.66,0,cap*.34)))
            lb=bounds(font,letter)
            scale=.66;dx=width*.33-lb[0]*scale
            g.components.append(Component(letter,(scale,0,0,1,dx,0)))
        else:
            offset=round(advance*.88)
            g=replace(font,name,cp,font[letter].width+offset)
            g.components.append(Component('degree'))
            g.components.append(Component(letter,(1,0,0,1,offset,0)))
    # Default tabular cmap in the interface/numeric cut; pnum reverses it.
    if face=='sans':
        for i,name in enumerate(DIGITS):
            cp=ord('0')+i
            for n in (name,name+'.tf'):
                font[n].unicodes=[v for v in font[n].unicodes if v!=cp]
            font[name+'.tf'].unicodes.append(cp)
    cpmap={c:g.name for g in font for c in g.unicodes}
    spaces={0x2000:u/2,0x2001:u,0x2002:u/2,0x2003:u,0x2004:u/3,
            0x2005:u/4,0x2006:u/6,0x2007:width,0x2008:font['period'].width,
            0x2009:u/5,0x200a:u/10,0x202f:u/5}
    for cp,w in spaces.items():
        if cp not in cpmap:
            replace(font,f'uni{cp:04X}',cp,round(w))
    aliases={0x00ad:'hyphen',0x2010:'hyphen',0x2011:'hyphen',0x201b:'quoteleft',
             0x2032:'quotesingle',0x2033:'quotedbl',0x2071:'i'}
    for cp,base in aliases.items():
        if cp not in cpmap:
            g=replace(font,f'uni{cp:04X}',cp,font[base].width)
            if cp==0x201b:
                g.components.append(Component('quoteright',(-1,0,0,1,font['quoteright'].width,0)))
            elif cp in (0x2032,0x2033):
                g.components.append(Component(base,(1,0,.14,1,-cap*.07,0)))
            elif cp==0x2071:
                g.components.append(Component(base,(.58,0,0,.58,0,u*.36)))
            else:g.components.append(Component(base))
            if cp in (0x201b,0x2032,0x2033):
                decompose(font,g.name)
    fractions={0x2150:(1,7),0x2151:(1,9),0x2152:(1,10),0x2153:(1,3),0x2154:(2,3),
        0x2155:(1,5),0x2156:(2,5),0x2157:(3,5),0x2158:(4,5),0x2159:(1,6),0x215a:(5,6),
        0x215b:(1,8),0x215c:(3,8),0x215d:(5,8),0x215e:(7,8)}
    for cp,(num,den) in fractions.items():
        if cp in cpmap:continue
        fw=width if face=='mono' else u*(.92 if den==10 else .76)
        g=replace(font,f'uni{cp:04X}',cp,round(fw))
        # Use reduced lining figures, not differently sized numerator alternates.
        scale=.32 if den==10 else .39
        for val,y,x in ((str(num),cap*.59,u*.025),(str(den),0,fw*(.47 if den!=10 else .41))):
            for j,ch in enumerate(val):
                base=DIGITS[int(ch)]
                g.components.append(Component(base,(scale,0,0,scale,x+j*fw*.26,y)))
        slash=font['fraction'];bb=bounds(font,'fraction')
        sy=cap*.89/(bb[3]-bb[1]);sx=.5
        g.components.append(Component('fraction',(sx,0,0,sy,fw*.42-(bb[0]+bb[2])*.25,-bb[1]*sy)))
    for cp,vertical in ((0x2194,False),(0x2195,True)):
        if cp in cpmap:continue
        w=width if face=='mono' else u*.86;h=u*.30;t=max(u*.028,thick*.6)
        pts=[(w*.08,0),(w*.30,h*.5),(w*.30,t/2),(w*.70,t/2),(w*.70,h*.5),
             (w*.92,0),(w*.70,-h*.5),(w*.70,-t/2),(w*.30,-t/2),(w*.30,-h*.5)]
        if vertical:pts=[(w/2-y,x-w/2+cap*.5) for x,y in pts]
        else:pts=[(x,y+cap*.5) for x,y in pts]
        g=replace(font,f'uni{cp:04X}',cp,round(w));polygon(g,pts)


def design_face(face):
    dest=CAND/'fonts'/face
    if dest.exists():shutil.rmtree(dest)
    shutil.copytree(BASE/face,dest)
    dsfile=next(dest.glob('*.designspace'));ds=DesignSpaceDocument.fromfile(dsfile)
    family='Strata '+face.title()
    for src in ds.sources:
        font=Font.open(src.path);u=font.info.unitsPerEm
        optical=src.location.get('Optical size',src.location.get('optical',14))
        display=optical>25
        oldx=font.info.xHeight;oldcap=font.info.capHeight
        if face=='sans':
            sans_details(font,display)
            sx=.965 if display else .978;sy=1.005 if display else 1.014
            pad=-1 if display else 11
            maps={g.name:Transform(sx,0,0,sy,pad,0) for g in font}
            xh=oldx*sy;cap=oldcap*sy
        elif face=='serif':
            xnorm=.562 if optical==8 else (.542 if optical==20 else .518)
            capnorm=.738 if not display else .731
            xh=u*xnorm;cap=u*capnorm;sx=1.018 if not display else 1.0;pad=3 if not display else -1
            maps={}
            for g in font:
                lower=g.name[0].islower() and g.name.split('.')[0] not in DIGITS and not any(s in g.name for s in ['sups','numr','dnom','subs'])
                sy=xh/oldx if lower else cap/oldcap
                maps[g.name]=Transform(sx,0,0,sy,pad,0)
            # Leave the four inherited diagnostic shapes exactly as the baseline.
            # They are outside the core; changing their master scaling creates new kinks.
            for name in ('be.srb','dagger','daggerdbl','f.ligalong'):
                maps[name]=Transform()
        else:
            xh=u*.554;cap=u*.738
            maps={}
            for g in font:
                lower=g.name[0].islower() and g.name.split('.')[0] not in DIGITS and not any(s in g.name for s in ['superior','inferior','numr','dnom','tosf'])
                sy=xh/oldx if lower else cap/oldcap
                maps[g.name]=Transform(.976,0,0,sy,u*.007385,0)
            # Stronger shoulders in the coding bowls, preserving all terminals.
            for name in ('o','O','zero','zero.cv11','zero.cv12'):
                if name not in font:continue
                for contour in font[name].contours:
                    if not contour.points:continue
                    xs=[p.x for p in contour.points];cx=(max(xs)+min(xs))/2
                    for pt in contour.points:
                        if pt.type is None:pt.x=cx+(pt.x-cx)*1.055
        affine_family(font,maps)
        if face=='sans':
            factor=.84 if display else .97
            font.kerning={k:round(v*factor) for k,v in font.kerning.items()}
            # Explicit pair exceptions: looser small text; close display joins.
            for pair,value in {( 'T','o'):-72,('T','a'):-63,('A','V'):-112,('W','a'):-54,
                               ('r','period'):-45,('f','o'):-12}.items():
                font.kerning[pair]=round(value*(.90 if display else .80))
        info_metrics(font,xh,cap)
        common_weather(font,face,display)
        sanitize(font,family)
        order=font.lib.get('public.glyphOrder',list(font.keys()))
        font.lib['public.glyphOrder']=order+[n for n in font.keys() if n not in order]
        font.save(src.path,overwrite=True)
    # Metadata does not participate in the design and must not retain old names.
    ds.lib.clear()
    for instance in ds.instances:instance.lib.clear()
    if face=='mono':
        # Keep the existing 300–700 design and give variable Regular its proper default.
        axis=ds.axes[0];axis.default=400
        # Correct five inherited ligature contour permutations before interpolation.
        bold_path=Path(ds.sources[1].path)
        bold=Font.open(bold_path)
        repairs={
            'bar_bar_equal_end.seq.cv30':[0,1,3,2],
            'bar_bar_equal_middle.seq.cv30':[0,1,2,3,5,4],
            'bar_bar_equal_start.seq.cv30':[0,1,3,2],
            'bar_bar_hyphen_end.seq.cv30':[0,2,1],
            'bar_bar_hyphen_middle.seq.cv30':[0,1,3,2],
        }
        for name,order in repairs.items():
            # The permuted contours are the two trailing bar components.
            g=bold[name]
            assert len(g.components)==2
            g.components.reverse()
        bold.save(bold_path,overwrite=True)
        # Materialize a compatible Regular master by pointwise interpolation.
        light=Font.open(ds.sources[0].path);bold=Font.open(ds.sources[1].path)
        mid=copy.deepcopy(light);fraction=(84-62)/(158-62)
        for g in mid:
            b=bold[g.name]
            assert [len(c.points) for c in g.contours]==[len(c.points) for c in b.contours],g.name
            for c,bc in zip(g.contours,b.contours):
                for p,bp in zip(c.points,bc.points):
                    p.x+=fraction*(bp.x-p.x);p.y+=fraction*(bp.y-p.y)
            for c,bc in zip(g.components,b.components):
                c.transformation=Transform(*(a+fraction*(z-a) for a,z in zip(c.transformation,bc.transformation)))
            g.width+=fraction*(b.width-g.width)
        mid.info.styleName='Regular';mid.info.openTypeOS2WeightClass=400
        mid.info.openTypeNamePreferredSubfamilyName='Regular'
        mid.info.postscriptFontName='StrataMono-Regular'
        mid.info.postscriptFullName='Strata Mono Regular'
        regular=dest/'StrataMono-Regular.ufo';mid.save(regular)
        from fontTools.designspaceLib import SourceDescriptor
        s=SourceDescriptor();s.path=str(regular);s.name='Strata Mono Regular';s.familyName=family;s.styleName='Regular';s.location={'Weight':84.0}
        for old in ds.sources:
            old.copyInfo=old.copyLib=old.copyGroups=old.copyFeatures=False
        s.copyInfo=s.copyLib=s.copyGroups=s.copyFeatures=True;ds.addSource(s)
    ds.write(dsfile)


def decompose(font,name):
    g=font[name]
    if not g.components:return
    pen=DecomposingRecordingPen(font);g.draw(pen)
    g.clearContours();g.clearComponents();pen.replay(g.getPen())


def segments(g):
    result=[]
    for contour in g.contours:
        points=contour.points;on=[i for i,p in enumerate(points) if p.type is not None]
        ring=[]
        for j,i in enumerate(on):
            ni=on[(j+1)%len(on)];between=[];k=(i+1)%len(points)
            while k!=ni:
                between.append((points[k].x,points[k].y));k=(k+1)%len(points)
            a=(points[i].x,points[i].y);b=(points[ni].x,points[ni].y)
            if not between:
                between=[(a[0]+(b[0]-a[0])/3,a[1]+(b[1]-a[1])/3),
                         (a[0]+2*(b[0]-a[0])/3,a[1]+2*(b[1]-a[1])/3)]
            assert len(between)==2,(g.name,len(between))
            ring.append((a,*between,b))
        result.append(ring)
    return result


def corner_masks(segs):
    masks=[]
    for ring in segs:
        mask=[]
        for i,s in enumerate(ring):
            prev=ring[i-1];v=s[0]
            incoming=(v[0]-prev[2][0],v[1]-prev[2][1]);out=(s[1][0]-v[0],s[1][1]-v[1])
            a=math.hypot(*incoming);b=math.hypot(*out)
            cosine=sum(x*y for x,y in zip(incoming,out))/max(a*b,1e-6)
            mask.append(a>1 and b>1 and -.985<cosine<.94)
        masks.append(mask)
    return masks


def rounded_glyph(g,masks,radius):
    rings=segments(g);g.clearContours()
    pen=g.getPen()
    for ring,mask in zip(rings,masks):
        clipped=[]
        for i,s in enumerate(ring):
            length=sum(math.dist(s[j],s[j+1]) for j in range(3))
            t=min(.46,radius/max(length,1))
            a=t if mask[i] else 0;b=1-t if mask[(i+1)%len(mask)] else 1
            if a>0:s=splitCubicAtT(*s,a)[1]
            if b<1:s=splitCubicAtT(*s,(b-a)/(1-a))[0]
            clipped.append(s)
        joined=[]
        for i,s in enumerate(clipped):
            joined.append(s);n=clipped[(i+1)%len(clipped)]
            if mask[(i+1)%len(mask)]:
                a=s[-1];b=n[0];incoming=(a[0]-s[2][0],a[1]-s[2][1]);out=(n[1][0]-b[0],n[1][1]-b[1])
                ai=max(math.hypot(*incoming),1e-6);bi=max(math.hypot(*out),1e-6)
                handle=math.dist(a,b)*.39
                vertex=ring[(i+1)%len(ring)][0]
                hi=min(handle,math.dist(a,vertex)*.85)
                ho=min(handle,math.dist(b,vertex)*.85)
                joined.append((a,(a[0]+incoming[0]/ai*hi,a[1]+incoming[1]/ai*hi),
                            (b[0]-out[0]/bi*ho,b[1]-out[1]/bi*ho),b))
        # Equal paired handles keep every smooth join collinear at intermediate
        # locations too, rather than only at the six original masters.
        joined=[list(s) for s in joined]
        for i,s in enumerate(joined):
            prev=joined[i-1];v=s[0]
            incoming=(v[0]-prev[2][0],v[1]-prev[2][1]);out=(s[1][0]-v[0],s[1][1]-v[1])
            a=math.hypot(*incoming);b=math.hypot(*out)
            axis_aligned=(max(abs(incoming[0]),abs(out[0]))<1e-6 or
                          max(abs(incoming[1]),abs(out[1]))<1e-6)
            if not axis_aligned and a*b and sum(x*y for x,y in zip(incoming,out))/(a*b)>.90:
                length=min(a,b)
                tangent=((incoming[0]/a+out[0]/b)*length/2,
                         (incoming[1]/a+out[1]/b)*length/2)
                prev[2]=(v[0]-tangent[0],v[1]-tangent[1])
                s[1]=(v[0]+tangent[0],v[1]+tangent[1])
        pen.moveTo(joined[0][0])
        for s in joined:pen.curveTo(*s[1:])
        pen.closePath()


def make_rounded():
    base=CAND/'fonts/sans';dest=CAND/'fonts/sans-rounded'
    if dest.exists():shutil.rmtree(dest)
    dest.mkdir()
    ds=DesignSpaceDocument.fromfile(base/'StrataSans.designspace')
    fonts=[Font.open(s.path) for s in ds.sources]
    names=set()
    for f in fonts:
        for g in f:
            if any(cp in set(range(48,58))|{0x00b0,0x2103,0x2109,0x2212,37,58,46} for cp in g.unicodes):names.add(g.name)
    names|=set(DIGITS)|{n+'.tf' for n in DIGITS}|{'degree','degreecentigrade','degreefahrenheit','minus','minus.tf','percent','colon','period','colon.tf','period.tf','C','F'}
    for f in fonts:
        for n in sorted(names):decompose(f,n)
    regular=fonts[2]
    masks={n:corner_masks(segments(regular[n])) for n in sorted(names)}
    for font,src in zip(fonts,ds.sources):
        b=bounds(font,'minus');radius=max(11,(b[3]-b[1])*.46)
        for n in sorted(names):rounded_glyph(font[n],masks[n],radius)
        sanitize(font,'Strata Sans Rounded')
        filename=Path(src.path).name.replace('StrataSans','StrataSansRounded')
        src.path=str(dest/filename);src.filename=filename
        src.familyName='Strata Sans Rounded';src.name=src.name.replace('Strata Sans','Strata Sans Rounded')
        font.save(src.path)
    for instance in ds.instances:
        instance.familyName='Strata Sans Rounded'
        for attr in ('name','postScriptFontName','styleMapFamilyName'):
            value=getattr(instance,attr,None)
            if value:setattr(instance,attr,value.replace('StrataSans','StrataSansRounded').replace('Strata Sans','Strata Sans Rounded'))
    ds.write(dest/'StrataSansRounded.designspace')
    # Masks are derived deterministically; no additional source file is needed.


def icons():
    # The finished icon set is an input. Never rewrite the designer's work area.
    folder=ICON_INPUT
    if folder.resolve()!=(CAND/'icons').resolve():
        shutil.copytree(folder,CAND/'icons',dirs_exist_ok=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('faces',nargs='*')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--icons-dir',type=Path,default=CAND/'review-icons')
    args=parser.parse_args();ICON_INPUT=args.icons_dir
    if args.output_dir:
        CAND=args.output_dir.resolve();CAND.mkdir(parents=True,exist_ok=True)
    selected=args.faces or ['sans','serif','mono']
    assert set(selected)<= {'sans','serif','mono','rounded'}
    for face in selected:
        if face=='rounded':continue
        design_face(face)
        print(face+' transformed',flush=True)
    if 'sans' in selected or 'rounded' in selected:
        make_rounded()
    icons()
    print('selected masters and icon weight complete',flush=True)

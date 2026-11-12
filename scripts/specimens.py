"""Self-contained specimens. The review directory receives raster images only."""
import base64
from html import escape
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPointPen

SIZES=[9,11,13,15,17,20,24,32,40,48,60,72]
KEYS='a e g n o s t R 0 1 2 3 4 5 6 7 8 9 @ & ?'.split()
PARAGRAPH='Clouds thin after noon. A mild breeze turns toward the lake as the next shower passes east. Take a light layer for the evening walk. The air cools quickly after sunset.'
MAP='<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="1800"><rect width="1120" height="1800" fill="#7a958a"/><path d="M-40 180Q340 380 440 40T1100 500M0 720Q500 430 1100 850M200 1800Q530 800 1000 1100" stroke="#cad2b2" stroke-width="80" fill="none"/><path d="M-10 1600Q700 400 400 0" stroke="#75a3b3" stroke-width="150" fill="none"/><path d="M0 300H1120M0 600H1120M0 900H1120M0 1200H1120M240 0V1800M540 0V1800M840 0V1800" stroke="#ecddbe" stroke-width="10"/></svg>'


def document(label,fonts,body,theme='light'):
    rules=[]
    if isinstance(fonts,dict):
        for index,path in enumerate(fonts.values()):
            mime='font/woff2' if path.suffix=='.woff2' else 'font/ttf'
            rules.append(f'@font-face{{font-family:p{index};src:url(data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()});font-style:normal;font-weight:100 900;font-display:block}}')
        families=['p'+str(i) for i in range(len(fonts))]
    else:families=fonts
    for index,family in enumerate(families):rules.append(f'.f{index}{{font-family:{family};font-optical-sizing:auto}}')
    mapurl='data:image/svg+xml;base64,'+base64.b64encode(MAP.encode()).decode()
    css='''*{box-sizing:border-box}html,body{margin:0}body{width:1120px;padding:40px;background:#f6f5f1;color:#172529;font-family:system-ui}h1{font-size:22px;font-weight:500;margin:0 0 26px}h2{font-size:14px;font-weight:500;margin:0 0 16px}small,.label{font-family:system-ui;font-size:11px;opacity:.65}section{border-top:1px solid #89939144;padding:22px 0}.weights{display:grid;grid-template-columns:1fr 1fr;gap:30px}.row{line-height:1.25;padding:7px 0;white-space:nowrap}.paragraph{line-height:1.55;max-width:58ch;margin:12px 0 24px}.dark{background:#121d25;color:#e5e8e8}.sky{background:linear-gradient(160deg,#dce8ef,#75a6c5 65%,#294c77);color:#122836}.glass{background-image:url("MAPURL");background-size:cover;color:#102b2a}.glass main{padding:28px;background:#f3f7efca;backdrop-filter:blur(20px);border:1px solid #fff9;border-radius:22px}.card{padding:30px;border:1px solid #81999966;border-radius:24px;background:#fff9}.dark .card{background:#20323c}.big{font-size:94px;font-weight:500;line-height:1.08}.columns{display:grid;grid-template-columns:1fr 1fr;gap:26px}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}td,th{text-align:right;padding:14px 8px;border-bottom:1px solid #80909044;font-weight:400}th:first-child,td:first-child{text-align:left}pre{padding:24px;line-height:1.6;font-size:17px;white-space:pre-wrap;background:#deebe766;border-radius:12px}.terminal{background:#11262b;color:#e0eadb;padding:24px;border-radius:16px}.icons{display:grid;grid-template-columns:repeat(8,1fr);gap:12px}.tile{min-height:116px;border:1px solid #849b9b55;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:10px;border-radius:9px}.iconrow{display:flex;align-items:center;gap:8px}.iconrow svg{flex:none}.unitgrid{display:none}.grid .unitgrid{display:block}.grid .tile{background-image:linear-gradient(#6594b433 1px,transparent 1px),linear-gradient(90deg,#6594b433 1px,transparent 1px);background-size:8px 8px}.outlines{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}.outlines svg{width:100%;height:200px;border:1px solid #85989844}.zoom{font-size:140px;line-height:1.2;text-align:center}.thin{font-size:13px;color:#587375}'''.replace('MAPURL',mapurl)
    return '<!doctype html><html><head><meta charset="utf-8"><title>'+escape(label)+'</title><style>'+css+''.join(rules)+'</style></head><body class="'+theme+'"><h1>'+escape(label)+'</h1><main>'+body+'</main></body></html>'


def waterfall(face):
    out=f'<div class="f{face}" data-face="{face}">'
    for weight in [400,600]:
        out+=f'<section style="font-weight:{weight}"><h2 class="label">{weight}</h2>'
        out+='<div class="weights">'
        for sizes in [SIZES[:6],SIZES[6:]]:
            out+='<div>'
            for size in sizes:
                sample='Age 0123' if size>=40 else 'A quiet sky, 0123456789'
                out+=f'<div class="row" style="font-size:{size}px"><small>{size}</small> {sample}</div>'
            out+='</div>'
        out+='</div></section>'
    out+='<section><div class="weights">'
    for weight in [400,600]:
        out+=f'<div style="font-weight:{weight}">'
        for size in [13,15,17]:out+=f'<small>{size} / {weight}</small><p class="paragraph" style="font-size:{size}px">{PARAGRAPH}</p>'
        out+='</div>'
    return out+'</div></section></div>'


def weather():
    out='<div class="f0" data-face="0"><section class="big">72° &nbsp; −3° &nbsp; 104°F</section><div class="columns">'
    for mode in ['tabular-nums','proportional-nums']:
        out+=f'<section style="font-variant-numeric:{mode}"><h2 class="label">'+('01' if mode.startswith('t') else '02')+f'</h2><table style="font-variant-numeric:{mode}"><tr><th>Time</th><th>°</th><th>%</th></tr>'
        for time,temp,pop in [('8 AM','72','10'),('9 AM','73','8'),('10 AM','74','15'),('11 AM','71','35'),('12 PM','69','80'),('1 PM','70','9')]:out+=f'<tr><td>{time}</td><td>{temp}°</td><td>{pop}%</td></tr>'
        out+='</table></section>'
    return out+'</div><section style="font-size:38px">30.16 inHg &nbsp; 12 mph NNW &nbsp; 3:45 PM</section><section style="font-size:24px">¼ ½ ¾ &nbsp; 10/12 &nbsp; 72° → 68°</section></div>'


def rounded():
    out='<h2>Rounded numerals</h2><div class="f3" data-face="3" style="font-variant-numeric:tabular-nums">'
    for size in [24,32,48,64,96]:
        out+=f'<section><small>{size}</small><div class="columns" style="font-size:{size}px;line-height:1.25">'
        out+=''.join(f'<div>{value}</div>' for value in ['72°','−3°','104°F','18℃'])+'</div></section>'
    out+='<section style="font-size:24px"><table><tr>'+''.join(f'<td>{t}</td>' for t in ['08:00','09:00','10:00','11:00','12:00'])+'</tr><tr>'
    out+=''.join(f'<td>{t}°</td>' for t in ['72','73','74','71','69'])+'</tr><tr>'
    out+=''.join(f'<td>{t}%</td>' for t in ['10','8','15','35','80'])+'</tr></table></section>'
    return out+'<section style="font-size:48px">0% &nbsp; 8% &nbsp; 100%<br>03:45 &nbsp; 18:30</section></div>'


def rounded_cards():
    out='<p class="label">Mockup · same card, two numeral styles</p><div class="columns">'
    for face,title in [(3,'Rounded numerals'),(0,'Regular numerals')]:
        out+=f'<div><h2>{title}</h2><div class="card"><p class="f0" data-face="0">Thursday · Lakeside</p><p class="f1" data-face="1" style="font-size:32px">A quiet afternoon.</p>'
        out+=f'<div class="f{face}" data-face="{face}" style="font-size:96px;line-height:1.15">72°</div><p class="f0" data-face="0">Clouds build after noon.</p>'
        out+=f'<div class="f{face}" data-face="{face}" style="font-size:24px;font-variant-numeric:tabular-nums"><table><tr><td>08:00</td><td>09:00</td><td>10:00</td></tr><tr><td>72°</td><td>71°</td><td>69°</td></tr><tr><td>10%</td><td>35%</td><td>80%</td></tr></table></div></div></div>'
    return out+'</div>'


def card():
    return '''<p class="label">Mockup</p><div class="card"><p class="f0" data-face="0" style="font-size:15px">Thursday · Lakeside</p><p class="f1" data-face="1" style="font-size:48px;line-height:1.13;max-width:19ch">A quiet afternoon before the rain returns.</p><div class="f0 big" data-face="0">72°</div><p class="f0" data-face="0" style="font-size:17px;line-height:1.55;max-width:58ch">Clouds build after 4 PM. A light breeze keeps the lake path comfortable through the afternoon.</p><div class="f0" data-face="0" style="font-size:23px">12 mph NNW &nbsp; 30.16 inHg &nbsp; 20%</div><table class="f0" data-face="0"><tr><th>Now</th><th>4 PM</th><th>5 PM</th><th>6 PM</th></tr><tr><td>72°</td><td>71°</td><td>69°</td><td>68°</td></tr></table></div>'''


def code():
    snippets=[('TS','type Hour = { temp: number; pop: number };\nconst dry = hours.filter(h => h.pop <= 20);\nconst label = dry.length !== 0 ? "walk" : "wait";\n// === !== => <= >= != -> ++ && ||'),('Python','def celsius(f):\n    return (f - 32) * 5 / 9\n\nfor hour in hours:\n    if hour["pop"] >= 60:\n        print(f"Rain at {hour[\'time\']}")'),('Shell','#!/bin/sh\nset -eu\nfor day in today tomorrow; do\n    printf "%s: 72 degrees\\n" "$day"\ndone')]
    out='<div class="f2" data-face="2">'
    for enabled in [True,False]:
        out+=f'<section style="font-variant-ligatures:{"normal" if enabled else "none"};font-feature-settings:\'calt\' {1 if enabled else 0}, \'liga\' {1 if enabled else 0}"><h2 class="label">'+('01' if enabled else '02')+'</h2>'
        for language,snippet in snippets:out+=f'<small>{language}</small><pre>{escape(snippet)}</pre>'
        out+='</section>'
    out+='<section class="terminal"><small>Terminal</small><pre>$ forecast --hourly\n08:00  72°   10%  NNW 12 mph\n09:00  73°    8%  NNW 11 mph\n10:00  74°   15%  NNW 12 mph\n$ echo "Ready"\nReady</pre></section></div>'
    return out


def outlines(path,face):
    font=TTFont(path);glyphset=font.getGlyphSet();cmap=font.getBestCmap();upm=font['head'].unitsPerEm
    out='<div class="outlines">'
    for char in KEYS:
        if ord(char) not in cmap:raise ValueError('Missing outline glyph '+char)
        name=cmap[ord(char)];glyph=glyphset[name]
        bounds=BoundsPen(glyphset);glyph.draw(bounds);x0,y0,x1,y1=bounds.bounds
        margin=upm*.07;svg=SVGPathPen(glyphset);glyph.draw(svg)
        points=DecomposingRecordingPointPen(glyphset);glyph.drawPoints(points)
        dots=[]
        for op,args,kwargs in points.value:
            if op=='addPoint':
                xy,segment=args[:2];x,y=xy;on=segment is not None
                dots.append(f'<circle cx="{x}" cy="{y}" r="{upm*.006}" fill="{"#d34a26" if on else "white"}" stroke="#2474a2" stroke-width="{upm*.002}"/>')
        out+=f'<div><small>{escape(char)}</small><svg viewBox="{x0-margin} {-y1-margin} {x1-x0+2*margin} {y1-y0+2*margin}"><g transform="scale(1,-1)"><path d="{svg.getCommands()}" fill="#223a3d"/>'+''.join(dots)+'</g></svg></div>'
    font.close()
    return out+'</div>'


def icon_font(path,chars):
    data=base64.b64encode(path.read_bytes()).decode()
    return ('<style>@font-face{font-family:q;src:url(data:font/woff2;base64,'+data+');font-display:block}</style>'
            '<div style="font-family:q;font-size:32px;line-height:1.8;display:grid;grid-template-columns:repeat(16,minmax(0,1fr));gap:8px">'
            +''.join('<span>'+char+'</span>' for char in chars)+'</div>')


def icon_sheet(svgs,start=0):
    out='<div class="icons">'
    for index,svg in enumerate(svgs,start=start):
        out+='<div class="tile"><div class="iconrow">'
        for size in [16,20,24,32]:out+=re_size(svg,size)
        out+=f'</div><small>{index+1:03d}</small></div>'
    return out+'</div>'


def re_size(svg,size):
    import re
    end=svg.index('>')
    header=re.sub(r'\s(?:width|height)="[^"]*"','',svg[:end])
    svg=header+svg[end:]
    grid=''.join(f'M{n} 0V24M0 {n}H24' for n in range(0,25,2))
    svg=svg.replace('</svg>',f'<path class="unitgrid" d="{grid}" fill="none" stroke="#4a92b777" stroke-width=".1"/></svg>')
    return svg.replace('<svg ',f'<svg width="{size}" height="{size}" ',1)

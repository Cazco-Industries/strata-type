"""Audit the text actually painted on each sheet, without changing its layout."""
import io
import math
from functools import lru_cache
from PIL import Image
from fontTools.ttLib import TTFont

FONT_TEST='Hamburgefontsiv 0123456789'


def face_audit(page,fonts,icon_font=None):
    families=['p'+str(i)+',specimen-missing' for i in range(len(fonts))] if isinstance(fonts,dict) else fonts
    result=page.evaluate('''async ({families,sample}) => {
      await document.fonts.ready;
      const walker=document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT);
      const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');
      const texts=[],probes=new Map(),pres=[];
      while(walker.nextNode()){
        const node=walker.currentNode,el=node.parentElement;
        if(!node.textContent.trim()||el.closest('style,script,small,.label,[data-annotation]'))continue;
        const owner=el.closest('[data-face],[data-font-family]');
        if(!owner)continue;
        const face=owner.dataset.face,expected=owner.dataset.fontFamily||families[Number(face)];
        const css=getComputedStyle(el),actual=css.fontFamily.replaceAll('"','').replaceAll("'",'');
        if(actual.replaceAll(/\\s/g,'')!==expected.replaceAll(/\\s/g,''))
          throw Error('Specimen family mismatch in '+el.tagName+': '+actual+'; expected '+expected);
        const primary=expected.split(',')[0];
        if(/^(p\\d+|q)$/.test(primary)){
          await document.fonts.load(css.fontWeight+' '+css.fontSize+' '+primary,node.textContent);
          if(![...document.fonts].some(f=>f.family===primary&&f.status==='loaded'))throw Error('Unloaded face '+primary);
        }
        texts.push({face:face===undefined?null:Number(face),family:primary,text:node.textContent});
        // Use the actual first code line for every PRE. Other faces use a stable
        // mixed run (or the numeric/PUA repertoire) so one narrow glyph cannot
        // accidentally equal a generic glyph's advance.
        const run=el.tagName==='PRE'?node.textContent.split('\\n').find(t=>t.trim()):
          expected==='q'?node.textContent:face==='3'?'72° −3° 104°F 18:30 80%':sample;
        const key=[expected,css.fontSize,css.fontWeight,run].join('|');
        if(!probes.has(key)){
          ctx.font=css.fontWeight+' '+css.fontSize+' '+expected;
          const width=ctx.measureText(run).width,generic={};
          for(const fallback of ['monospace','serif','sans-serif']){
            ctx.font=css.fontWeight+' '+css.fontSize+' '+fallback;
            generic[fallback]=ctx.measureText(run).width;
            if(Math.abs(width-generic[fallback])<.01)throw Error('Generic width fallback in '+el.tagName+' for '+expected+' / '+fallback);
          }
          probes.set(key,{family:expected,size:css.fontSize,weight:css.fontWeight,run,width,generic});
        }
        if(el.tagName==='PRE')pres.push({family:actual,...probes.get(key)});
      }
      return {texts,probes:[...probes.values()],pres};
    }''',{'families':families,'sample':FONT_TEST})
    cmaps={};missing_runs=[]
    for row in result.pop('texts'):
        path=icon_font if row['family']=='q' else (list(fonts.values())[row['face']] if isinstance(fonts,dict) else None)
        if path is None:continue
        if path not in cmaps:
            with TTFont(path,lazy=True) as font:cmaps[path]=set(font.getBestCmap())
        missing=sorted({f'U+{ord(c):04X}' for c in row['text'] if not c.isspace() and ord(c) not in cmaps[path]})
        if missing:
            if row['family']=='q':raise ValueError(f'Missing icon glyphs: {missing}')
            # document() embeds a synthetic tofu with a nonzero glyph for every
            # character in this sheet. Verify it loaded instead of permitting
            # the browser's automatic installed-font fallback.
            if not page.evaluate("[...document.fonts].some(f=>f.family==='specimen-missing'&&f.status==='loaded')"):
                raise ValueError('Explicit missing-glyph font did not load')
            missing_runs.append({'family':row['family'],'text':row['text'],'codepoints':missing,'rendered_as':'explicit tofu'})
    result['missing_glyphs']=missing_runs
    result['status']='PASS'
    return result


@lru_cache(maxsize=4096)
def luminance(rgb):
    values=[v/255 for v in rgb]
    return sum(w*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for w,v in zip([.2126,.7152,.0722],values))


def contrast(foreground,background,alpha=1):
    foreground=tuple(round(f*alpha+b*(1-alpha)) for f,b in zip(foreground,background))
    a,b=sorted([luminance(foreground),luminance(tuple(background))])
    return (b+.05)/(a+.05)


def contrast_audit(page,theme):
    selector='body' if theme=='sky' else '.terminal'
    if not page.locator(selector).count():return None
    runs=page.evaluate('''selector=>{
      const root=document.querySelector(selector),walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),runs=[];
      while(walker.nextNode()){
        const n=walker.currentNode,e=n.parentElement;
        if(!n.textContent.trim()||e.closest('style,script'))continue;
        const css=getComputedStyle(e);if(css.display==='none'||css.visibility==='hidden')continue;
        let alpha=1;for(let p=e;p;p=p.parentElement)alpha*=Number(getComputedStyle(p).opacity);
        const color=css.color.match(/[\\d.]+/g).map(Number);alpha*=color[3]??1;
        const range=document.createRange();range.selectNodeContents(n);
        for(const r of range.getClientRects())if(r.width&&r.height)runs.push({text:n.textContent.trim().slice(0,64),color:color.slice(0,3),alpha,box:{x:r.x,y:r.y,width:r.width,height:r.height}});
      }
      return runs;
    }''',selector)
    style=page.add_style_tag(content='*{color:transparent!important;text-shadow:none!important}svg{visibility:hidden!important}')
    try:
        with Image.open(io.BytesIO(page.screenshot(full_page=True,animations='disabled'))) as image:background=image.convert('RGB')
    finally:style.evaluate('(e)=>e.remove()')
    scale=page.evaluate('devicePixelRatio');worst=None
    for run in runs:
        b=run['box'];box=(max(0,math.floor(b['x']*scale)),max(0,math.floor(b['y']*scale)),min(background.width,math.ceil((b['x']+b['width'])*scale)),min(background.height,math.ceil((b['y']+b['height'])*scale)))
        crop=background.crop(box)
        for _,rgb in crop.getcolors(crop.width*crop.height) or []:
            ratio=contrast(run['color'],rgb,run['alpha'])
            if worst is None or ratio<worst['ratio']:worst={'ratio':ratio,'text':run['text'],'foreground':run['color'],'background':rgb,'opacity':run['alpha']}
    threshold=4.5 if theme=='sky' else 7
    if worst is None:raise ValueError('No text measured for contrast')
    report={'surface':'sky' if theme=='sky' else 'terminal','minimum':round(worst['ratio'],4),'required':threshold,'runs':len(runs),'worst':worst}
    if worst['ratio']<threshold:raise ValueError(f'Rendered contrast below {threshold}: {report}')
    return report


def collision_components(image,line_images,scale=2,origin=(0,0)):
    """8-connected raster ink must contain pixels from two distinct DOM lines."""
    mask=image.convert('L').point(lambda v:255 if v<128 else 0)
    width,height=mask.size;data=bytearray(mask.tobytes())
    lines=[im.convert('L').point(lambda v:255 if v<128 else 0).tobytes() for im in line_images]
    if any(im.size!=mask.size for im in line_images):raise ValueError('Line mask size mismatch')
    findings=[]
    for start in range(len(data)):
        if not data[start]:continue
        data[start]=0;stack=[start];pixels=[];members=set();x0=x1=start%width;y0=y1=start//width
        while stack:
            p=stack.pop();pixels.append(p);x,y=p%width,p//width
            x0=min(x0,x);x1=max(x1,x);y0=min(y0,y);y1=max(y1,y)
            for i,line in enumerate(lines):
                if line[p]:members.add(i)
            for yy in range(max(0,y-1),min(height,y+2)):
                for xx in range(max(0,x-1),min(width,x+2)):
                    q=yy*width+xx
                    if data[q]:data[q]=0;stack.append(q)
        pairs=[[a+1,a+2] for a in sorted(members) if a+1 in members]
        if pairs:findings.append({'lines':pairs,'bounds':[round(origin[0]+x0/scale,3),round(origin[1]+y0/scale,3),round((x1-x0+1)/scale,3),round((y1-y0+1)/scale,3)],'ink_pixels':len(pixels)})
    return findings


def headline_collisions(page):
    if not page.locator('[data-headline]').count():return None
    headline=page.locator('[data-headline]');original=headline.inner_html()
    layout=headline.evaluate('''el=>{
      if(el.childNodes.length!==1||el.firstChild.nodeType!==Node.TEXT_NODE)throw Error('Headline must be a plain text run');
      const node=el.firstChild,text=node.textContent,groups=[];
      for(let i=0;i<text.length;i++){
        const r=document.createRange();r.setStart(node,i);r.setEnd(node,i+1);const box=r.getBoundingClientRect();
        let group=groups.at(-1);if(!group||Math.abs(group.y-box.y)>.5){group={y:box.y,text:'',box:{x:box.x,y:box.y,width:0,height:box.height}};groups.push(group);}
        group.text+=text[i];group.box.width=Math.max(group.box.width,box.right-group.box.x);
      }
      const box=el.getBoundingClientRect(),pad=parseFloat(getComputedStyle(el).fontSize);
      el.replaceChildren(...groups.map((g,i)=>{const span=document.createElement('span');span.dataset.inkLine=i;span.textContent=g.text;return span;}));
      [...el.children].forEach((span,i)=>{
        const rects=[...span.getClientRects()].filter(r=>r.width>.01);
        if(rects.some(r=>Math.abs(r.y-groups[i].y)>.5))throw Error('Line mask changed headline wrapping');
      });
      return {lines:groups.map(g=>g.box),clip:{x:Math.max(0,Math.floor(box.x-pad)),y:Math.max(0,Math.floor(box.y-pad)),width:Math.ceil(box.width+pad*2),height:Math.ceil(box.height+pad*2)}};
    }''')
    style=None
    try:
        # Color-only changes preserve the original font shaping and line layout.
        style=page.add_style_tag(content='*{color:transparent!important;text-shadow:none!important;background:none!important;border-color:transparent!important;box-shadow:none!important}body{background:white!important}svg{visibility:hidden!important}[data-ink-line].ink-active{color:black!important}')
        headline.locator('[data-ink-line]').evaluate_all('(els)=>els.forEach(e=>e.classList.add("ink-active"))')
        full=Image.open(io.BytesIO(page.screenshot(clip=layout['clip'],animations='disabled'))).convert('L')
        line_images=[]
        for index in range(len(layout['lines'])):
            headline.locator('[data-ink-line]').evaluate_all('(els,i)=>els.forEach((e,j)=>e.classList.toggle("ink-active",i===j))',index)
            line_images.append(Image.open(io.BytesIO(page.screenshot(clip=layout['clip'],animations='disabled'))).convert('L'))
        findings=collision_components(full,line_images,page.evaluate('devicePixelRatio'),(layout['clip']['x'],layout['clip']['y']))
        return {'status':'finding' if findings else 'clear','line_boxes':layout['lines'],'components':findings,'threshold':128,'neighbors':8,'scale':page.evaluate('devicePixelRatio')}
    finally:
        if style:style.evaluate('(e)=>e.remove()')
        headline.evaluate('(el,html)=>el.innerHTML=html',original)

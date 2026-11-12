"""Audit review files, including PNG bytes; split IDAT chunks at accidental words."""
import argparse
import json
from pathlib import Path
import re
import struct
import zlib
from PIL import Image

def word_pattern(word):
    variants={'s':b'(?:s|\xc5\xbf)','i':b'(?:i|\xc4\xb0|\xc4\xb1)','k':b'(?:k|\xe2\x84\xaa)'}
    return b''.join(variants.get(char,char.encode()) for char in word.lower())

PATTERN=re.compile(b'|'.join(word_pattern(word) for word in ['Strata','Inter','Source','Fira','SF','Lucide','Hugeicons','baseline','reference','lumen','quartz','opus','sol','claude','codex','gpt'])+b'|'+word_pattern('New')+b'[ _-]?'+word_pattern('York'),re.I)


def png_chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)


def clean_png(path):
    # No text/exif chunks. Fragmenting IDAT changes no pixels and also prevents
    # random compressed bytes from looking like a leaked two-letter font name.
    path=Path(path)
    with Image.open(path) as im:im.save(path,format='PNG',pnginfo=None)
    raw=path.read_bytes();pos=8;fixed=[];compressed=b''
    while pos<len(raw):
        length=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8];data=raw[pos+8:pos+8+length];pos+=12+length
        if kind==b'IDAT':compressed+=data
        elif kind in (b'IHDR',b'IEND'):fixed.append((kind,data))
        else:raise ValueError(f'Unexpected PNG chunk: {kind}')
    out=raw[:8]+png_chunk(*fixed[0]);offset=0
    while offset<len(compressed):
        size=min(4096,len(compressed)-offset)
        found=PATTERN.search(compressed[offset:offset+size])
        if found:size=found.start()+1
        while size:
            chunk=png_chunk(b'IDAT',compressed[offset:offset+size])
            if not PATTERN.search(chunk):break
            size-=1
        if not size:raise ValueError('PNG framing collision; rerender to change compression')
        out+=chunk;offset+=size
    out+=png_chunk(*fixed[-1])
    if PATTERN.search(out):raise ValueError('PNG header collision')
    path.write_bytes(out)
    # Reopen and decode after lossless reframing.
    with Image.open(path) as im:im.load()


def check(out):
    out=Path(out);failures=[]
    for path in out.rglob('*'):
        if PATTERN.search(str(path.relative_to(out)).encode()):failures.append(str(path)+' filename')
        if path.is_file() and PATTERN.search(path.read_bytes()):failures.append(str(path)+' bytes')
        if path.suffix=='.png':
            with Image.open(path) as im:
                if im.text or im.getexif():failures.append(str(path)+' metadata')
    if failures:raise ValueError('Blind output leaked identity: '+', '.join(failures))
    return len(list(out.glob('*.png')))


def main():
    p=argparse.ArgumentParser();p.add_argument('out');a=p.parse_args();print(f'Clean: {check(a.out)} PNGs')

if __name__=='__main__':main()

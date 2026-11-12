#!/usr/bin/env python3
"""Mint opaque labels in a lead-owned JSON map; never place the map in OUT."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import secrets

WORDS=('amber','birch','cedar','cobalt','copper','coral','dawn','dune','elm','fern','flint','grove','hazel','jade','lake','linen','maple','moss','opal','pearl','pine','reed','river','slate','stone','teal','vale','willow')
LEAK=re.compile(r'Strata|Inter|Source|Fira|SF|New[ _-]?York|Lucide|Hugeicons|baseline|reference',re.I)


def labels(path,keys):
    path=Path(path).expanduser().resolve();path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_RDWR|os.O_CREAT,0o600)
    with os.fdopen(fd,'r+') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        raw=stream.read();mapping=json.loads(raw) if raw.strip() else {}
        if not isinstance(mapping,dict):raise ValueError('MAP must be a JSON object mapping identities to opaque labels')
        for value in mapping.values():
            if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',value) or LEAK.search(value):raise ValueError('Map contains a nonopaque label')
        if len(set(mapping.values()))!=len(mapping):raise ValueError('Labels must be unique')
        for key in keys:
            if key not in mapping:
                while True:
                    words=secrets.SystemRandom().sample(WORDS,2)
                    value='-'.join(words)+f'-{secrets.randbelow(1000):03d}'
                    if value not in mapping.values():break
                mapping[key]=value
        stream.seek(0);stream.write(json.dumps(mapping,indent=2)+'\n');stream.truncate();stream.flush();os.fsync(stream.fileno())
    return mapping


def main():
    p=argparse.ArgumentParser();p.add_argument('--map',required=True);p.add_argument('--key','--id',required=True,action='append');a=p.parse_args()
    mapping=labels(a.map,a.key)
    # The command is lead-only. The renderer never writes this reverse mapping.
    for key in a.key:print(mapping[key])

if __name__=='__main__':main()

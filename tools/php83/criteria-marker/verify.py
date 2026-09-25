#!/usr/bin/env python3
"""Fixture verification against a manifest hash supplied by the parent host."""
import hashlib,json,re,sys
from pathlib import Path
EXPECTED={'original.php','declaration.php','criteriaFilter.php','probe.php','run.sh','verify.py'}
def verify(base,pin):
    if not re.fullmatch('[0-9a-f]{64}',pin): raise ValueError('Bad manifest pin')
    if base.is_symlink() or base.resolve()!=base.absolute(): raise ValueError('Symlink stage path')
    p=base/'identities.json'
    if p.is_symlink(): raise ValueError('Symlink manifest')
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin: raise ValueError('Manifest drift')
    m=json.loads(raw)
    if set(m['files'])!=EXPECTED: raise ValueError('Fixture inventory drift')
    for name,h in m['files'].items():
        f=base/name
        if f.is_symlink() or hashlib.sha256(f.read_bytes()).hexdigest()!=h: raise ValueError('Fixture drift: '+name)
    return m
if __name__=='__main__': verify(Path(sys.argv[1]),sys.argv[2])

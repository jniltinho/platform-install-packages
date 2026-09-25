#!/usr/bin/env python3
"""Reconstruct candidate using only independently recorded paired token offsets."""
import hashlib

def verify(before, after, proof):
    sha=lambda data:hashlib.sha256(data).hexdigest()
    if len(before)!=len(after):raise ValueError('Source length changed')
    if sha(before)!=proof['before_sha256'] or sha(after)!=proof['after_sha256']:
        raise ValueError('Source hash mismatch')
    expected=bytearray(before);seen=set();count=0
    for pair in proof['offset_pairs']:
        opening,closing=pair['open'],pair['close']
        if type(opening['offset']) is not int or type(closing['offset']) is not int or not 0<=opening['offset']<closing['offset']<len(before):
            raise ValueError('Invalid pair offsets')
        for part,old,new in [(opening,'{','['),(closing,'}',']')]:
            i=part['offset']
            if i in seen or before[i]!=ord(old) or part['before']!=old or part['after']!=new:
                raise ValueError('Duplicate or wrong bracket substitution')
            if part['line']!=before[:i].count(b'\n')+1 or part['column']!=i-before.rfind(b'\n',0,i):
                raise ValueError('Reported token location mismatch')
            seen.add(i);expected[i]=ord(new);count+=1
    if not count or count!=proof['changed_bytes'] or bytes(expected)!=after:
        raise ValueError('Unexpected non-offset change or incomplete proof')
    if proof['all_other_bytes_tokens_identical'] is not True:
        raise ValueError('Missing native token proof')
    return count

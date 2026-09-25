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
            if type(part['line']) is not int or type(part['column']) is not int or part['line']!=before[:i].count(b'\n')+1 or part['column']!=i-before.rfind(b'\n',0,i):
                raise ValueError('Reported token location mismatch')
            seen.add(i);expected[i]=ord(new);count+=1
    if not count or count!=proof['changed_bytes'] or bytes(expected)!=after:
        raise ValueError('Unexpected non-offset change or incomplete proof')
    if proof['all_other_bytes_tokens_identical'] is not True:
        raise ValueError('Missing native token proof')
    return count


def validate_report(report):
    for key,want in [('scan_before_exit',1),('fix_exit',0),('scan_after_exit',0)]:
        if type(report[key]) is not int or report[key]!=want:
            raise ValueError('Invalid analyzer exit status')
    if report['analyzer_unchanged'] is not True:
        raise ValueError('Analyzer unchanged claim must be true')
    before,after=report['analyzer_before'],report['analyzer_after']
    if not isinstance(before,dict) or not isinstance(after,dict) or not before or before!=after:
        raise ValueError('Invalid analyzer identity maps')
    if before.get('composer.lock')!='1349200f714f39615153d319d88046b1f34b91a782954b76a7fe538c9b8b5e33' or before.get('vendor/composer/installed.json')!='232acd1afb737bb24508f52b99383cf0a0e13c7ea6afb70ec880bca256eb920a':
        raise ValueError('Unexpected analyzer dependency pins')
    if report['phpcbf_version']!='PHP_CodeSniffer version 4.0.4 (stable) by Squiz and PHPCSStandards' or report['sniff']!='PHPCompatibility.Syntax.RemovedCurlyBraceArrayAccess' or report['testVersion']!='7.4-8.3':
        raise ValueError('Unexpected analyzer policy')
    if set(report['scan_after_totals'])!={'errors','warnings','fixable'} or any(type(n) is not int or n!=0 for n in report['scan_after_totals'].values()):
        raise ValueError('Targeted findings remain or invalid totals')

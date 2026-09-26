#!/usr/bin/env python3
"""Exact metadata/omission contract, never positive rank/API/SQL acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import observe

MODES=['74-original','74-candidate','83-original','83-candidate']
MESSAGE='Optional parameter $entryType declared before required parameter $rank is implicitly treated as a required parameter'
SNAPSHOT_PIN='f2985a7d3f054c3a743535009e0ad2937545d05e1c0d9e7c936a24acf13da463'
def exact(a,b):
    return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))
def expected(mode):
    runtime,variant=mode.split('-');parameters=[]
    for i,name in enumerate(['entryId','entryType','rank']):
        available=mode=='74-original' and i==1
        parameters.append({'name':name,'position':i,'optional':False,'default_available':available,
            'allows_null':True,'type':'','by_reference':False,'variadic':False,
            'default':['value',None] if available else ['unavailable','ReflectionException']})
    calls=[['positional'+str(i),'ArgumentCountError','Too few arguments to function KalturaEntryService::anonymousRankEntry(), '+str(i)+' passed and exactly 3 expected'] for i in range(3)]
    if runtime=='83':
        calls += [['named_missing_middle','ArgumentCountError','KalturaEntryService::anonymousRankEntry(): Argument #2 ($entryType) not passed'],['named_missing_leading','ArgumentCountError','KalturaEntryService::anonymousRankEntry(): Argument #1 ($entryId) not passed']]
    return {'runtime':'7.4.33' if runtime=='74' else '8.3.6','variant':variant,'required':3,'parameters':parameters,'calls':calls,
        'diagnostics':[[8192,MESSAGE,'/audit/probe/original.php',1836]] if mode=='83-original' else [],
        'autoload_requests':[],'entry_peer_loaded':False,'kvote_loaded':False,'rank_positive_body_tested':False,'application_acceptance':False}

def validate(report):
    if report.get('status')!='OBSERVED_NOT_ACCEPTED':raise ValueError('Incomplete observation')
    if report.get('application_acceptance') is not False or report.get('rank_positive_body_tested') is not False:raise ValueError('Scope drift')
    rows=report.get('records',[])
    if [r.get('mode') for r in rows]!=MODES:raise ValueError('Matrix mismatch')
    data=observe.files();identities={p:observe.prepare.sha(b) for p,b in data.items()}
    sums=''.join(h+'  '+p+'\n' for p,h in sorted(identities.items())).encode();pin=observe.prepare.sha(sums)
    source={**identities,'SHA256SUMS':pin}
    if report.get('files')!=identities or report.get('checksum_manifest_sha256')!=pin:raise ValueError('Harness/source drift')
    if report.get('source_before')!=source or report.get('source_after')!=source:raise ValueError('Stage drift')
    if report.get('collector_sha256')!=observe.prepare.sha(Path(observe.__file__).read_bytes()):raise ValueError('Collector drift')
    before=report.get('runtime_before');after=report.get('runtime_after')
    if not before or not exact(before,after) or before.get('collector_sha256')!=SNAPSHOT_PIN:raise ValueError('Runtime drift/missing')
    if before.get('identity',{}).get('host')!='kaltura-php74-baseline' or not before.get('identity',{}).get('files'):raise ValueError('Wrong runtime host/inventory')
    if type(before.get('exit')) is not int or before['exit']!=0:raise ValueError('Runtime collector failure')
    stage=report.get('stage','')
    if not re.fullmatch(r'/home/vagrant/php-rank-signature\.[a-f0-9]{32}',stage):raise ValueError('Stage name')
    for row in rows:
        mode=row['mode'];runtime,variant=mode.split('-')
        if type(row.get('exit')) is not int or row['exit']!=0:raise ValueError('Probe failure')
        if not exact(row.get('body'),expected(mode)):raise ValueError('Body contract '+mode)
        if not exact(json.loads(row.get('stdout','')),expected(mode)):raise ValueError('Raw stdout disagreement')
        stderr='Deprecated: '+MESSAGE+' in /audit/probe/original.php on line 1836\n' if mode=='83-original' else ''
        if row.get('stderr')!=stderr:raise ValueError('Native diagnostic contract '+mode)
        if row.get('command')!='bash '+stage+'/run.sh '+stage+' '+runtime+' '+variant+' '+pin:raise ValueError('Command mismatch')
    return {'status':'BOUNDED_SIGNATURE_CONTRACT_PASS','processes':4,'omission_calls':16,
        'metadata74_delta':{'parameter':'entryType','default_available':[True,False],'default':[['value',None],['unavailable','ReflectionException']]},
        'metadata83_unchanged':True,'original83_deprecations':1,'candidate83_deprecations':0,
        'rank_positive_body_tested':False,'artifact_selected':False,'application_acceptance':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Do not overwrite evidence')
    raw=a.input.read_bytes();result=validate(json.loads(raw));result['input_sha256']=hashlib.sha256(raw).hexdigest();result['validator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

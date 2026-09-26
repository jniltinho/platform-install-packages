#!/usr/bin/env python3
"""Offline bounded contract reconciliation; never runs PHP or promotes an artifact."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('collector', HERE / 'collect-r2.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
E = Path('doc/php83/evidence/serialization-contracts')

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def equal(a, b, label):
    if canonical(a) != canonical(b):
        raise ValueError(label)

def reconcile(reports, manifest):
    index = {}
    closure = collector.collector_identity()
    pin = hashlib.sha256((E / 'r3-stage-identities.json').read_bytes()).hexdigest()
    for mode in ['74', '83']:
        report = reports[mode]
        equal(report['collector_closure'], closure, 'collector closure')
        equal(report['collector_closure_after'], closure, 'collector closure after')
        equal(report['stage_manifest_sha256'], pin, 'stage pin')
        equal(report['application_acceptance'], False, 'acceptance flag')
        equal(report['status'], 'OBSERVED_NOT_ACCEPTED', 'status')
        equal(report['errors'], [], 'execution errors')
        expected = [(v,k,op,None) for v in (['original'] if mode=='74' else ['original','candidate']) for k in collector.KINDS for op in collector.OPS]
        for reader in (['original'] if mode=='74' else ['original','candidate']):
            expected += [(reader,k,'read',w) for w in (['original83','candidate83'] if mode=='74' else ['original83-r2','candidate83-r2','original74']) for k in collector.KINDS]
        expected += [(v,'cache',op,'recorded83-'+op[-1] if op.startswith('read-') else None) for v in (['original'] if mode=='74' else ['original','cachefix','candidate']) for op in collector.CACHE]
        equal([tuple(r[k] for k in ['variant','kind','operation','writer']) for r in report['records']], expected, 'exact ordered inventory')
        for r in report['records']:
            for channel in ['stdout','stderr']:
                equal(base64.b64decode(r[channel+'_base64'],validate=True).decode(),r[channel],'raw channel')
            body = collector.validate(r, mode, manifest)
            index[(mode,r['variant'],r['kind'],r['operation'],r['writer'])] = body
    def body(mode, variant, kind, op, writer=None):
        return index[(mode,variant,kind,op,writer)]
    def result(*args):
        return body(*args)['result']
    checks = []
    for kind in collector.KINDS:
        for op in collector.OPS:
            old = result('74','original',kind,op)
            equal(old,result('83','original',kind,op),'original runtime result '+kind+'/'+op)
            new = result('83','candidate',kind,op)
            equal({k:v for k,v in old.items() if k!='wire'}, {k:v for k,v in new.items() if k!='wire'},'typed behavior '+kind+'/'+op)
            if 'wire' in old:
                equal(old['wire']['format'],'C','legacy frame')
                equal(new['wire']['format'],'O','new frame')
                collector.wiredata(old['wire']); collector.wiredata(new['wire'])
        if kind != 'null':
            invalid = result('83','candidate',kind,'invalid-utf8')
            equal('wire' in invalid,False,'invalid UTF8 emitted wire')
            equal(invalid['exception'],{'class':'Exception','message':invalid['before']['class']+'::serialize() must return a string or NULL'},'invalid UTF8 write exception')
        for mode, readers, writers in [('74',['original'],['original83','candidate83']),('83',['original','candidate'],['original83-r2','candidate83-r2','original74'])]:
            for reader in readers:
                for writer in writers:
                    expected = {'type':'boolean','value':False} if reader=='original' and writer.startswith('candidate') else result(mode,reader,kind,'roundtrip')['restored']
                    equal(result(mode,reader,kind,'read',writer)['restored'],expected,'reader contract '+kind+'/'+reader+'/'+writer)
        checks.append('typed wire behavior and C/O readers: '+kind)
    for op in collector.CACHE:
        writer = 'recorded83-'+op[-1] if op.startswith('read-') else None
        old = result('74','original','cache',op,writer)
        equal(result('83','original','cache',op,writer),{'exception':{'class':'TypeError','message':'implode(): Argument #2 ($array) must be of type ?array, string given','phase':'namespace'},'target_exists':False},'original83 implode control')
        equal(result('83','cachefix','cache',op,writer),old,'cachefix typed baseline '+op)
        new = result('83','candidate','cache',op,writer)
        if op=='read-O':
            expected = dict(old)
            expected['fetch'] = result('74','original','cache','read-C','recorded83-C')['fetch']
        else:
            expected = old
        equal(new,expected,'candidate typed cache '+op)
        if op=='invalid-utf8':
            equal(new,{'exception':{'class':'Exception','message':'Aws\\Common\\Credentials\\Credentials::serialize() must return a string or NULL','phase':'save'},'target_exists':False},'reject before object cache write')
        if op=='malformed' and not body('83','candidate','cache',op)['diagnostics']:
            raise ValueError('malformed warning lost')
        checks.append('real filesystem cache: '+op)
    for key,b in index.items():
        if key[1]=='candidate' and any(d.get('severity')==8192 for d in b['diagnostics']):
            raise ValueError('candidate deprecation remains')
    return checks

def main():
    reports = {}
    hashes = {}
    for mode in ['74','83']:
        raw = (E/f'r3-primary{mode}.json').read_bytes()
        repeat = (E/f'r3-claude{mode}.json').read_bytes()
        if raw != repeat: raise ValueError('repeat differs')
        reports[mode] = json.loads(raw)
        hashes[mode] = hashlib.sha256(raw).hexdigest()
        snapshots = [(E/f'r3-{who}{mode}-{when}.json').read_bytes() for who in ['primary','claude'] for when in ['before','after']]
        if any(s!=snapshots[0] for s in snapshots): raise ValueError('runtime identity drift')
    raw74 = (E/'r3-primary74.json').read_bytes()
    equal(reports['83']['input_report74'],{'sha256':hashes['74'],'bytes':len(raw74),'collector_closure_sha256':collector.collector_identity()['sha256']},'consumed74 input')
    manifest = json.loads((E/'r3-stage-identities.json').read_text())
    equal(manifest['collector_closure'],collector.collector_identity(),'manifest closure')
    checks = reconcile(reports,manifest)
    print(json.dumps({'status':'BOUNDED_FUNCTIONAL_CHECKS_MATCH_WITH_KNOWN_WIRE_BREAK','application_acceptance':False,'artifact_selected':False,'rollback_compatible':False,'primary_counts':{'74':38,'83':96},'actual_claude_repeats_byte_identical':True,'report_sha256':hashes,'reconciler_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,'limitations':['C-to-O wire change is incompatible with original74/original83 readers; cache namespace/snapshot/rollback policy is not selected or tested.','Wire hashes prove internal consistency, not authenticity. Native execution provenance is in retained CLI calls.','Synthetic credentials only; no real backend, role refresh, application configuration, or whole-application acceptance.','Native diagnostics are retained/repeated; PHP74/83 warning severity parity is not claimed.','External Serializable subclasses returning NULL are outside the six-class corpus.']},indent=2))
if __name__=='__main__':
    main()

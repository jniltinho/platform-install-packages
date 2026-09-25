#!/usr/bin/env python3
"""Compare four isolated process reports; representation changes are never parity."""
import argparse, base64, hashlib, json
from pathlib import Path
import prepare
MODES=['original74','declaration74','original83','declaration83']
CASES=['fresh','disabled','once_twice','two_filters','preset_true','preset_false','preset_null','unset_reapply','clone','clear','empty_filter','nested_order','duplicate_constraint','exception_marker','serialize_attached']

def representations(value,path=''):
    found={}
    if isinstance(value,dict):
        if 'serialized_base64' in value:
            raw=base64.b64decode(value['serialized_base64'],validate=True)
            if len(raw)!=value['serialized_bytes'] or hashlib.sha256(raw).hexdigest()!=value['serialized_sha256']: raise ValueError('Serialization hash/length mismatch')
            if value['roundtrip_bytes_identical'] is not True: raise ValueError('Broken roundtrip')
            found[path]=value
        else:
            for k,v in value.items(): found.update(representations(v,path+'/'+str(k)))
    elif isinstance(value,list):
        for i,v in enumerate(value): found.update(representations(v,path+'/'+str(i)))
    return found

def semantics(value):
    if isinstance(value,dict):
        if 'serialized_base64' in value: return {'representation_reported_separately':True}
        return {k:semantics(v) for k,v in value.items()}
    if isinstance(value,list): return [semantics(v) for v in value]
    return value

def validate(records,identities):
    if [r['mode'] for r in records]!=MODES: raise ValueError('Exact ordered four modes required')
    baseline=None; reps={}; events={}; diagnostics={}; marker_events={}
    for r in records:
        if type(r['exit']) is not int or r['exit']!=0 or not isinstance(r['stderr'],str): raise ValueError('Process failure')
        b=r['body']
        if not isinstance(r.get('stdout'),str) or json.loads(r['stdout'])!=b: raise ValueError('Raw stdout/body binding mismatch')
        variant=r['mode'][:-2]; version=r['mode'][-2:]
        if b.get('schema')!=1 or b['variant']!=variant or not b['php'].startswith({'74':'7.4.','83':'8.3.'}[version]): raise ValueError('Runtime/variant mismatch')
        if list(b['rows'])!=CASES: raise ValueError('Case inventory/order mismatch')
        if b['source_sha256']!={'criteria':identities['files'][variant+'.php'],'filter':identities['files']['criteriaFilter.php']}: raise ValueError('Source identity mismatch')
        native=[e for e in b['events'] if 'Creation of dynamic property' in e['message'] and '::$creteria_filter_attached' in e['message']]
        if r['mode']=='original83':
            if not native or not any(e['phase']=='once_twice' and e['severity']==8192 and e['file']=='criteriaFilter.php' and e['line']==51 for e in native): raise ValueError('Missing exact marker control')
            if 'Creation of dynamic property Criteria::$creteria_filter_attached is deprecated' not in r['stderr']: raise ValueError('Native stderr control missing')
        elif native: raise ValueError('Unexpected marker diagnostic')
        marker_events[r['mode']]=native
        unrelated=[e for e in b['events'] if e not in native]
        diagnostics[r['mode']]=unrelated
        functional=semantics(b['rows'])
        if baseline is None: baseline=functional
        elif functional!=baseline: raise ValueError('Observed filter behavior differs')
        reps[r['mode']]=representations(b['rows']);events[r['mode']]=b['events']
        if set(reps[r['mode']])!={'/fresh/representation','/once_twice/2','/clone/2','/serialize_attached/1'}: raise ValueError('Required representation inventory missing')
    # Compare unrelated diagnostics per runtime, not across74/83. The sole
    # declared source edit adds one line after original line38. Keep raw events
    # and report exact differences; normalize only this recorded source mapping.
    def mapped(events,variant):
        out=[]
        for e in events:
            e=dict(e)
            if e['file']==variant+'.php':
                e['file']='Criteria.php'
                if variant=='declaration' and e['line']>=40:e['line']-=1
            out.append(e)
        return out
    deltas={}
    for version in ('74','83'):
        left=diagnostics['original'+version];right=diagnostics['declaration'+version]
        if mapped(left,'original')!=mapped(right,'declaration'): raise ValueError('Unrelated diagnostic regression on '+version)
        deltas[version]={'original':left,'declaration':right,'equal_after_exact_added_line_mapping':True}
    changes=[]
    for mode in MODES[1:]:
        if reps[mode].keys()!=reps['original74'].keys(): raise ValueError('Representation inventory mismatch')
        for path,a in reps['original74'].items():
            b=reps[mode][path]
            if a!=b: changes.append({'mode':mode,'case_path':path,'before':a,'after':b,'serialized_byte_delta':b['serialized_bytes']-a['serialized_bytes']})
    return {'status':'OBSERVED_FUNCTIONAL_PARITY_REPRESENTATION_DELTAS_SEPARATE','cases':len(CASES),'modes':MODES,'representation_changes':changes,'exact_representation_parity':not changes,'native_stderr_sha256':{r['mode']:hashlib.sha256(r['stderr'].encode()).hexdigest() for r in records},'events':events,'target_events':marker_events,'unrelated_diagnostics':deltas,'patch_selected':False,'application_acceptance':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('records',type=Path);p.add_argument('identities',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists(): raise ValueError('Refuse existing output')
    a.output.write_text(json.dumps(validate(json.loads(a.records.read_text()),json.loads(a.identities.read_text())),indent=2)+'\n')

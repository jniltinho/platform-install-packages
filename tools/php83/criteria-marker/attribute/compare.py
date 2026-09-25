#!/usr/bin/env python3
"""Strict bounded layout/state comparison for an unselected attribute experiment."""
import base64,hashlib,json
MODES=['original74','attribute74','original83','attribute83']
CASES=['fresh','disabled','once_twice','two_filters','preset_true','preset_false','preset_null','unset_reapply','clone','clear','empty_filter','nested_order','duplicate_constraint','exception_marker','serialize_attached','mycriteria_hint','mycriteria_marker','kalturacriteria_marker','unrelated_control']
REP_PATHS={'/fresh/representation','/once_twice/2','/clone/2','/serialize_attached/1','/mycriteria_hint/representation','/mycriteria_marker/representation','/kalturacriteria_marker/representation'}

def snapshots(v,path=''):
    out={}
    if isinstance(v,dict):
        if 'serialized_base64' in v:
            b=base64.b64decode(v['serialized_base64'],validate=True)
            if len(b)!=v['serialized_bytes'] or hashlib.sha256(b).hexdigest()!=v['serialized_sha256'] or v['roundtrip_bytes_identical'] is not True:raise ValueError('Serialization integrity failure')
            out[path]=v
        else:
            for k,x in v.items():out.update(snapshots(x,path+'/'+str(k)))
    elif isinstance(v,list):
        for i,x in enumerate(v):out.update(snapshots(x,path+'/'+str(i)))
    return out

def legacy(rows):
    found=snapshots(rows)
    if set(found)!=REP_PATHS:raise ValueError('Representation inventory mismatch')
    return {k:v['serialized_base64'] for k,v in found.items()}

def validate(records,identities74,identities83,payloads):
    if [r['mode'] for r in records]!=MODES:raise ValueError('Four ordered modes required')
    for ids,data in [(identities74,{}),(identities83,payloads)]:
        raw=(json.dumps(data,sort_keys=True,indent=2)+'\n').encode()
        if ids['files'].get('legacy.json')!=hashlib.sha256(raw).hexdigest():raise ValueError('Legacy fixture hash binding')
    original_rows=None;by_mode={};targets={}
    for r in records:
        v=r['mode'][:-2];version=r['mode'][-2:];ids=identities74 if version=='74' else identities83
        if type(r['exit']) is not int or r['exit']!=0:raise ValueError('Process exit')
        b=r['body']
        if json.loads(r['stdout'])!=b or b['schema']!=2 or b['variant']!=v or not b['php'].startswith({'74':'7.4.','83':'8.3.'}[version]):raise ValueError('Output/mode binding')
        if b['source_sha256']!={'criteria':ids['files'][v+'.php'],'filter':ids['files']['criteriaFilter.php']}:raise ValueError('Source identity')
        if list(b['rows'])!=CASES:raise ValueError('Case inventory')
        if original_rows is None:original_rows=b['rows']
        elif b['rows']!=original_rows:raise ValueError('Exact state/representation differs')
        legacy(b['rows'])
        target=[e for e in b['events'] if e['message'].startswith('Creation of dynamic property ') and any(c in e['message'] for c in ('Criteria::$creteria_filter_attached','myCriteria::$hint'))]
        unrelated=[e for e in b['events'] if e['message']=='Creation of dynamic property UnrelatedMarkerControl::$fixtureMarker is deprecated']
        if version=='83':
            if len(unrelated)!=1 or unrelated[0]['severity']!=8192:raise ValueError('Missing unrelated-class negative control')
            if unrelated[0]['message'] not in r['stderr']:raise ValueError('Missing unrelated native stderr')
        elif target or unrelated:raise ValueError('Unexpected74 diagnostic')
        if r['mode']=='original83':
            if not any(e['message']=='Creation of dynamic property myCriteria::$hint is deprecated' for e in target):raise ValueError('Missing real hint diagnostic')
            if not any(e['message']=='Creation of dynamic property KalturaCriteria::$creteria_filter_attached is deprecated' for e in target):raise ValueError('Missing inherited marker diagnostic')
            if 'Creation of dynamic property Criteria::$creteria_filter_attached is deprecated' not in r['stderr']:raise ValueError('Missing native marker')
        elif target:raise ValueError('Attribute/74 unexpected hierarchy warning')
        targets[r['mode']]=target;by_mode[r['mode']]=b
        if version=='74':
            if b['imports'] not in ({},[]):raise ValueError('Unexpected74 imports')
        else:
            if set(b['imports'])!=REP_PATHS:raise ValueError('Legacy import inventory')
            for path,record in b['imports'].items():
                snapshots({'import':record['representation']})
                if record['representation']['serialized_base64']!=payloads[path]:raise ValueError('Legacy imported representation differs')
    if payloads!=legacy(original_rows):raise ValueError('Payloads not bound to original74')
    if by_mode['original83']['imports']!=by_mode['attribute83']['imports']:raise ValueError('Legacy import behavior differs')
    diagnostics={}
    for version in ['74','83']:
        def normalized(mode):
            result=[]
            for e in by_mode[mode]['events']:
                if e in targets[mode]:continue
                x=dict(e)
                if x['file']==mode[:-2]+'.php':
                    x['file']='Criteria.php'
                    if mode.startswith('attribute') and x['line']>=39:x['line']-=1
                result.append(x)
            return result
        if normalized('original'+version)!=normalized('attribute'+version):raise ValueError('Unrelated diagnostic regression')
        diagnostics[version]={'original':by_mode['original'+version]['events'],'attribute':by_mode['attribute'+version]['events']}
    return {'status':'BOUNDED_STATE_AND_LAYOUT_PARITY_ATTRIBUTE_NOT_SELECTED','cases':19,'legacy_payloads':7,'exact_rows':True,'exact_imports':True,'target_events':targets,'diagnostics':diagnostics,'attribute74_executed':True,'hierarchy_exemption_broader_than_marker':True,'patch_selected':False,'application_acceptance':False}

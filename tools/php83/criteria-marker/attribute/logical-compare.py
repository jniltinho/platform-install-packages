#!/usr/bin/env python3
"""Separately classify logical values, never replace strict serialized-byte FAIL."""
import base64,hashlib,json
MODES=['original74','original83','attribute83']
def validate(records,payloads):
    if [r['mode'] for r in records]!=MODES or len(payloads)!=7:raise ValueError('Exact three-mode/seven-payload inventory')
    baseline=None;result={}
    for r in records:
        if type(r['exit']) is not int or r['exit']!=0:raise ValueError('Native process failure')
        b=r['body'];version=r['mode'][-2:];variant=r['mode'][:-2]
        if json.loads(r['stdout'])!=b or b['schema']!=1 or b['variant']!=variant or not b['php'].startswith({'74':'7.4.','83':'8.3.'}[version]):raise ValueError('Output identity')
        if set(b['rows'])!=set(payloads):raise ValueError('Payload inventory mismatch')
        logical={}
        for name,row in b['rows'].items():
            if row['input_sha256']!=hashlib.sha256(base64.b64decode(payloads[name],validate=True)).hexdigest():raise ValueError('Input payload drift')
            logical[name]=row['logical']
        if baseline is None:baseline=logical
        elif json.dumps(baseline,sort_keys=True,separators=(',',':'))!=json.dumps(logical,sort_keys=True,separators=(',',':')):raise ValueError('Typed logical state differs')
        result[r['mode']]={name:{'raw_bytes_equal':row['input_sha256']==row['reserialized_sha256'],'input_sha256':row['input_sha256'],'reserialized_sha256':row['reserialized_sha256']} for name,row in b['rows'].items()}
    return {'status':'BOUNDED_TYPED_IMPORT_VALUES_MATCH_RAW_LAYOUT_GATE_STILL_FAILED','rows_per_mode':7,'modes':MODES,'representation':result,'object_property_order_ignored_explicitly':True,'array_order_and_types_preserved':True,'object_aliases_preserved':True,'array_reference_identity_not_tested':True,'application_acceptance':False,'attribute_selected':False}

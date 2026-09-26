#!/usr/bin/env python3
"""Read-only exact comparison for the authorized bounded observation phase."""
import copy,hashlib,json,pathlib
P=pathlib.Path(__file__).resolve().parent
names=['native-primary.json','native-authorized-independent.json','baseline74-authorized-primary.json']
a,b,c=[json.loads((P/n).read_text()) for n in names]
def eq(x,y):return json.dumps(x,sort_keys=True,separators=(',',':'))==json.dumps(y,sort_keys=True,separators=(',',':'))
for report,modes in [(a,['original','public-comparison','attribute-comparison','rank']),(b,['original','public-comparison','attribute-comparison','rank']),(c,['original','public-comparison','attribute-comparison'])]:
 assert report['status']=='OBSERVED_NOT_ACCEPTED'
 assert [r['mode'] for r in report['records']]==modes
 assert all(type(r['exit']) is int and r['exit']==0 for r in report['records'])
 assert eq(report['source_before'],report['source_after'])
 assert eq(report['runtime_before'],report['runtime_after'])
 assert all(r['body'] is not None for r in report['records'])
for key in ['records','files','checksum_manifest_sha256']:assert eq(a[key],b[key])
for r in c['records']:
 assert r['body']['diagnostics']==[] and r['stderr']==''
 assert r['body']['constructor_executed'] is True
 assert r['body']['request_parser_exercised'] is False
original74=c['records'][0]['body']['rows'];attribute74=c['records'][2]['body']['rows'];attribute83=copy.deepcopy(b['records'][2]['body']['rows'])
assert len(original74)==len(attribute83)==9
assert eq(original74,attribute74)
# Exact seven direct-class metadata changes; descendant reports no own attribute.
for i in range(7):
 assert original74[i][1]['class_attributes']==[]
 assert attribute83[i][1]['class_attributes']==['AllowDynamicProperties']
 attribute83[i][1]['class_attributes']=[]
assert eq(original74,attribute83)
assert len(b['records'][2]['body']['diagnostics'])==1
assert 'KalturaDispatcher::$unrelatedDiagnosticControl' in b['records'][2]['body']['diagnostics'][0][1]
print(json.dumps({'status':'BOUNDED_TYPED_STATE_PARITY','input_sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in names},'native_independent_records_exact':True,'baseline74_original_attribute_all_9_rows_exact':True,'baseline74_original_attribute83_rows_exact_except_7_class_attribute_metadata':True,'serialized_states_exact':8,'baseline74_diagnostics_each':0,'attribute83_unrelated_control_diagnostics':1,'metadata_exemption':'AllowDynamicProperties attribute explicit; descendants/future properties exempt','baseline74_executor':'Codex','native83_repeat_executor':'actual Claude CLI','application_acceptance':False,'rank_successful_body_exercised':False},indent=2))

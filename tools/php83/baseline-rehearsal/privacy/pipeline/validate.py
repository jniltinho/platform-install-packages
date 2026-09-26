"""Typed synthetic observation contract; never declares privacy repaired."""
import hashlib,re
CASES=['plain','prefix-context','message-extra','previous','intrinsic','pre-rendered']
BOOLS=['instrumented_bytes_identical','writer_throwable','writer_same_message','formatter_same_message','writer_formatter_same_message','exception_state_unchanged','context_unchanged','full_marker_present','prefix15_present','has_diagnostic','has_frame','prefix_context_present','message_override_exact']
def validate(body,manifest):
 if body['runtime']!='8.3.6' or body['sapi']!='cli' or body['ignore_args_ini']!='0':raise ValueError('Wrong native mode')
 if body['product_changes']!=0 or body['privacy_acceptance'] is not False or body['application_acceptance'] is not False:raise ValueError('Scope')
 want={p[len('source/'):]:v for p,v in manifest['files'].items() if p.startswith('source/')}
 if body['loaded']!=want or len(want)!=11:raise ValueError('Actual full source closure mismatch')
 if [r['case'] for r in body['records']]!=CASES:raise ValueError('Case inventory')
 for row in body['records']:
  n=row['case'];override=n=='message-extra';string=n=='pre-rendered'
  if row['writer_class']!='KalturaSerializableStream' or row['formatter_class']!='Zend_Log_Formatter_Simple' or row['write_declaring']!='Zend_Log_Writer_Stream':raise ValueError('Wrong product class')
  if type(row['priority']) is not int or row['priority']!=3 or row['priority_name']!='ERR':raise ValueError('Priority')
  if row['writer_message_type']!=('string' if override or string else 'object'):raise ValueError('Message type')
  expected={k:True for k in ['instrumented_bytes_identical','writer_formatter_same_message','exception_state_unchanged','context_unchanged']}
  expected.update(writer_throwable=not (override or string),writer_same_message=not override,formatter_same_message=not override,
   full_marker_present=n=='intrinsic',prefix15_present=not override,has_diagnostic=n not in ('intrinsic','message-extra'),
   has_frame=n not in ('intrinsic','message-extra'),prefix_context_present=n=='prefix-context',message_override_exact=override)
  for key in BOOLS:
   if type(row[key]) is not bool or row[key]!=expected[key]:raise ValueError('Observed contract '+n+'/'+key)
  if not re.fullmatch('[0-9a-f]{64}',row['sink_sha256']):raise ValueError('Sink hash')
 return {'status':'SYNTHETIC_PIPELINE_OBSERVED_EXPECTED_LEAK','cases':6,'writer_receives_original_throwable_in_normal_cases':True,
  'message_extra_can_replace_object':True,'pre_rendered_string_is_not_throwable':True,'privacy_acceptance':False,'application_acceptance':False}

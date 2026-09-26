"""Typed synthetic-native report comparison. Never labels full privacy accepted."""
TRUE_FIELDS={'request_input_unchanged','ordinary_strings_not_indiscriminately_replaced','request_key_order_preserved','actual_dispatch_arguments_unchanged','positional_nonsensitive_types_preserved','real_dto_unchanged','dto_private_nonsensitive_value_preserved','typed_array_items_kept','exception_object_identity_preserved','exception_priority_preserved'}
MASK_FIELDS={'request_sensitive_fields_absent','native_decoded_post_fields_absent','positional_secret_absent','dto_token_absent','typed_array_otp_absent','additional_auth_fields_absent'}
def need(ok):
 if not ok:raise ValueError('Synthetic log-copy contract mismatch')
def validate(report,variant,version,pins):
 need(type(report) is dict and set(report)=={'variant','php','sapi','sources','rows'})
 need(report['variant']==variant and type(report['php']) is str and report['php'].startswith(version+'.') and report['sapi']=='cli')
 need(report['sources']==pins and type(pins) is dict and set(pins)=={'log','front','dispatcher','formatter','formatter_interface'})
 r=report['rows'];privacy=variant=='privacy';extra={'mapping_failure_visible','depth_bounded'} if privacy else set()
 need(type(r) is dict and set(r)==TRUE_FIELDS|MASK_FIELDS|extra|{'dto_log_shape','analytics_null','analytics_empty','analytics_string','trace_observation','privacy_accepted'})
 for key in TRUE_FIELDS|extra:need(r[key] is True)
 for key in MASK_FIELDS:need(r[key] is privacy)
 need(r['privacy_accepted'] is False and r['dto_log_shape']==('class-tagged-visibility-field-array' if privacy else 'original-object-print'))
 for label in ['null','empty','string']:
  a=r['analytics_'+label]
  need(type(a) is dict and set(a)=={'level','event_type','field_count','request_end','partner','ks_field_expected','context_unchanged','unrelated_fields'})
  need(type(a['level']) is int and a['level']==5 and a['event_type']=='LOG_TYPE_ANALYTICS' and type(a['field_count']) is int and a['field_count']==10)
  need(a['request_end']=='request_end' and a['partner']=='102' and a['ks_field_expected'] is True and a['context_unchanged'] is True)
  need(a['unrelated_fields']==['102','','0','"fixture-user"','1','','7'] and all(type(x) is str for x in a['unrelated_fields']))
 trace=r['trace_observation'];need(type(trace) is dict and set(trace)=={'full_marker_present','prefix15_present','ignore_args_ini','formatter_contains_diagnostic','formatter_contains_frame'})
 need(type(trace['full_marker_present']) is bool and type(trace['prefix15_present']) is bool and trace['ignore_args_ini']=='0' and trace['formatter_contains_diagnostic'] is True and trace['formatter_contains_frame'] is True)
 return r
def compare(original,privacy,version,original_pins,privacy_pins):
 a=validate(original,'original',version,original_pins);b=validate(privacy,'privacy',version,privacy_pins)
 need(original['php']==privacy['php'])
 for key in TRUE_FIELDS|{'analytics_null','analytics_empty','analytics_string','trace_observation'}:need(a[key]==b[key])
 leak=b['trace_observation']['full_marker_present'] or b['trace_observation']['prefix15_present']
 return {'status':'SYNTHETIC_LOG_COPY_CONTRACT_MATCH','trace_gate':'BLOCKED_SENSITIVE_TRACE_OBSERVED' if leak else 'REAL_FORMATTER_AND_API_STILL_PENDING','full_privacy_accepted':False,'application_accepted':False}

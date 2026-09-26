import copy,unittest
import compare as c
PINS={'log':'a'*64,'front':'b'*64,'dispatcher':'c'*64,'formatter':'d'*64,'formatter_interface':'e'*64}
def report(variant='privacy'):
 r={k:True for k in c.TRUE_FIELDS};r.update({k:variant=='privacy' for k in c.MASK_FIELDS})
 if variant=='privacy':r.update(mapping_failure_visible=True,depth_bounded=True)
 r.update(dto_log_shape='class-tagged-visibility-field-array' if variant=='privacy' else 'original-object-print',privacy_accepted=False,trace_observation={'full_marker_present':False,'prefix15_present':True,'ignore_args_ini':'0','formatter_contains_diagnostic':True,'formatter_contains_frame':True})
 for name in ['null','empty','string']:r['analytics_'+name]={'level':5,'event_type':'LOG_TYPE_ANALYTICS','field_count':10,'request_end':'request_end','partner':'102','ks_field_expected':True,'context_unchanged':True,'unrelated_fields':['102','','0','"fixture-user"','1','','7']}
 return {'variant':variant,'php':'7.4.33','sapi':'cli','sources':PINS.copy(),'rows':r}
class CompareTests(unittest.TestCase):
 def test_expected_pair_trace_blocks_privacy(self):self.assertEqual(c.compare(report('original'),report(),'7.4',PINS,PINS)['trace_gate'],'BLOCKED_SENSITIVE_TRACE_OBSERVED')
 def test_leaking_mask_rejected(self):
  r=report();r['rows']['positional_secret_absent']=False
  with self.assertRaises(ValueError):c.validate(r,'privacy','7.4',PINS)
 def test_original_not_invented_absence(self):
  r=report('original');r['rows']['request_sensitive_fields_absent']=True
  with self.assertRaises(ValueError):c.validate(r,'original','7.4',PINS)
 def test_source_drift(self):
  r=report();r['sources']['front']='d'*64
  with self.assertRaises(ValueError):c.validate(r,'privacy','7.4',PINS)
 def test_bool_level_rejected(self):
  r=report();r['rows']['analytics_null']['level']=True
  with self.assertRaises(ValueError):c.validate(r,'privacy','7.4',PINS)
 def test_extra_field_rejected(self):
  r=report();r['rows']['raw_secret']='synthetic'
  with self.assertRaises(ValueError):c.validate(r,'privacy','7.4',PINS)
 def test_no_trace_false_fullacceptance(self):
  a=report('original');b=report()
  for r in [a,b]:r['rows']['trace_observation']['prefix15_present']=False
  result=c.compare(a,b,'7.4',PINS,PINS);self.assertFalse(result['full_privacy_accepted']);self.assertEqual(result['trace_gate'],'REAL_FORMATTER_AND_API_STILL_PENDING')
 def test_changed_unrelated_field(self):
  r=report();r['rows']['analytics_string']['unrelated_fields'][0]='103'
  with self.assertRaises(ValueError):c.validate(r,'privacy','7.4',PINS)
if __name__=='__main__':unittest.main()

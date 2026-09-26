import copy,importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('trace_validate',Path(__file__).with_name('validate.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def fixture():
 rows=[]
 for name in v.NAMES:
  neg=name in ['intrinsic-control','prerendered-control','extras-control']
  rows.append(dict(case=name,exception_state_unchanged=True,observed_same_bytes=True,structural_preserved=True,context_preserved=True,priority={'error-alert':1,'error-crit':2}.get(name,3),full_marker=neg,prefix_marker=neg,redaction_marker=not neg,writer_same_message=True,formatter_type='string',mixed_types_exact=True))
 return dict(policy=True,privacy_acceptance=False,loaded={'a':'pin'},records=rows,negative_controls_expected_to_leak=['intrinsic-control','prerendered-control','extras-control'],reject_filter=dict(empty_sink=True,observer_not_called=True,formatter_not_called=True))
class Tests(unittest.TestCase):
 def test_positive(self):self.assertFalse(v.validate(fixture(),True,{'a':'pin'})['privacy_acceptance'])
 def test_mutants(self):
  for key,value in [('exception_state_unchanged',False),('structural_preserved',False),('context_preserved',False),('priority',7),('full_marker',True),('prefix_marker',True),('redaction_marker',False),('writer_same_message',False),('formatter_type','object'),('mixed_types_exact',False)]:
   with self.subTest(key=key):
    r=fixture();r['records'][0][key]=value
    with self.assertRaises(ValueError):v.validate(r,True,{'a':'pin'})
 def test_no_missing_cases(self):
  r=fixture();r['records'].pop()
  with self.assertRaises(ValueError):v.validate(r,True,{'a':'pin'})
 def test_source_drift(self):
  with self.assertRaises(ValueError):v.validate(fixture(),True,{'a':'other'})
 def test_negative_not_waived(self):
  for row in range(7,10):
   r=fixture();r['records'][row]['prefix_marker']=False
   with self.assertRaises(ValueError):v.validate(r,True,{'a':'pin'})
 def test_legacy_error_not_policy_waiver(self):
  r=fixture();r['records'][4]['observed_same_bytes']=False
  with self.assertRaises(ValueError):v.validate(r,True,{'a':'pin'})
 def test_exact_types(self):
  for kind in ['priority','flag','reject']:
   r=fixture()
   if kind=='priority':r['records'][5]['priority']=True
   elif kind=='flag':r['records'][0]['redaction_marker']='yes'
   else:r['reject_filter']['empty_sink']=1
   with self.assertRaises(ValueError):v.validate(r,True,{'a':'pin'})
 def test_reject_filter(self):
  r=fixture();r['reject_filter']['empty_sink']=False
  with self.assertRaises(ValueError):v.validate(r,True,{'a':'pin'})
if __name__=='__main__':unittest.main()

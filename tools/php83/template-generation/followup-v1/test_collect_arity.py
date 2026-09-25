import importlib.util,json,unittest
from pathlib import Path
from unittest.mock import patch
s=importlib.util.spec_from_file_location('a',Path(__file__).with_name('collect_arity.py'));a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class ArityGuardTests(unittest.TestCase):
 def row(self):return {'runtime':'74','exit':0,'stdout':json.dumps({'runtime':'7.4.33','returned':True,'returned_type':'boolean','defined':True,'constant':1,'diagnostics':[],'exception':None})}
 def test_positive(self):self.assertTrue(a.validate_row(self.row())['defined'])
 def test_exit_exception(self):
  r=self.row();r['exit']=10
  with self.assertRaises(ValueError):a.validate_row(r)
 def test_boolean_exit(self):
  r=self.row();r['exit']=False
  with self.assertRaises(ValueError):a.validate_row(r)
 def test_native_fatal(self):
  r=self.row();r['exit']=255
  with self.assertRaises(ValueError):a.validate_row(r)
 def test_timeout(self):
  r=self.row();r['exit']=124
  with self.assertRaises(ValueError):a.validate_row(r)
 def test_schema(self):
  r=self.row();r['stdout']='{}'
  with self.assertRaises(ValueError):a.validate_row(r)
 def test_manifest_drift_before_remote(self):
  with patch.object(a,'MANIFEST_PIN','0'*64),patch.object(a.c,'remote',side_effect=AssertionError('remote prohibited')):
   with self.assertRaises(ValueError):a.identity()
 def test_main_records_all_four_after_fatal(self):
  import tempfile,sys
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/'report.json';calls=[]
   def remote(args):
    calls.append(args)
    if len(calls)==1:return {'exit':255,'stdout':'','stderr':'native fatal fixture'}
    row=self.row();body=json.loads(row['stdout']);body['runtime']='7.4.33' if len(calls)==2 else '8.3.6'
    return {'exit':0,'stdout':json.dumps(body),'stderr':''}
   with patch.object(a,'identity',return_value={'fixed':1}),patch.object(a.c,'remote',side_effect=remote),patch.object(sys,'argv',['collect_arity.py',str(output)]):self.assertEqual(a.main(),2)
   result=json.loads(output.read_text());self.assertEqual(len(result['records']),4);self.assertEqual(len(result['failures']),1);self.assertEqual(result['status'],'FAILED_OBSERVATION_VALIDATION')
if __name__=='__main__':unittest.main()

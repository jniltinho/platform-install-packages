import copy,importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('pipeline_validate',Path(__file__).with_name('validate.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Validation(unittest.TestCase):
 def fixture(self):
  pins={'source/'+str(i):'a'*64 for i in range(11)}
  rows=[]
  for n in m.CASES:
   over=n=='message-extra';string=n=='pre-rendered'
   r={k:True for k in m.BOOLS};r.update(case=n,writer_class='KalturaSerializableStream',formatter_class='Zend_Log_Formatter_Simple',write_declaring='Zend_Log_Writer_Stream',priority=3,priority_name='ERR',writer_message_type='string' if over or string else 'object',
    writer_throwable=not(over or string),writer_same_message=not over,formatter_same_message=not over,full_marker_present=n=='intrinsic',prefix15_present=not over,has_diagnostic=n not in ['intrinsic','message-extra'],has_frame=n not in ['intrinsic','message-extra'],prefix_context_present=n=='prefix-context',message_override_exact=over,sink_sha256='a'*64)
   rows.append(r)
  return {'runtime':'8.3.6','sapi':'cli','ignore_args_ini':'0','records':rows,'loaded':{str(i):'a'*64 for i in range(11)},'product_changes':0,'privacy_acceptance':False,'application_acceptance':False},{'files':pins}
 def test_expected_fixture(self):
  b,p=self.fixture();self.assertFalse(m.validate(b,p)['privacy_acceptance'])
 def test_hidden_leak(self):
  b,p=self.fixture();b['records'][0]['prefix15_present']=False
  with self.assertRaises(ValueError):m.validate(b,p)
 def test_changed_instrumentation(self):
  b,p=self.fixture();b['records'][0]['instrumented_bytes_identical']=False
  with self.assertRaises(ValueError):m.validate(b,p)
 def test_wrong_object(self):
  b,p=self.fixture();b['records'][0]['writer_same_message']=False
  with self.assertRaises(ValueError):m.validate(b,p)
 def test_override_not_detected(self):
  b,p=self.fixture();b['records'][2]['writer_throwable']=True
  with self.assertRaises(ValueError):m.validate(b,p)
 def test_duplicate_case(self):
  b,p=self.fixture();b['records'][1]=copy.deepcopy(b['records'][0])
  with self.assertRaises(ValueError):m.validate(b,p)
 def test_bool_not_int(self):
  b,p=self.fixture();b['records'][0]['priority']=True
  with self.assertRaises(ValueError):m.validate(b,p)
 def test_source_drift(self):
  b,p=self.fixture();b['loaded']['0']='b'*64
  with self.assertRaises(ValueError):m.validate(b,p)
if __name__=='__main__':unittest.main()

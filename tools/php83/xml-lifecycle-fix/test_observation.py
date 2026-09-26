import copy,importlib.util,json,pathlib,unittest
HERE=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('contract',HERE/'observation_contract.py');contract=importlib.util.module_from_spec(s);s.loader.exec_module(contract)
E=HERE.parents[2]/'doc/php83/evidence/xml-lifecycle'
def rows():
 for mode,name in [('74','private-r2-primary74.json'),('83','private-primary83.json')]:
  d=json.loads((E/name).read_text())
  for r in d['records']:yield mode,r
def validate(mode,r):
 b=r['body'];return contract.validate(b,r['variant'],r['case'],mode,b['probe_sha256'],r['stderr'])
class Tests(unittest.TestCase):
 def test_all44_actual_retained_records_new_contract(self):
  n=0
  for mode,r in rows():validate(mode,r);n+=1
  self.assertEqual(n,44)
 def target(self):return next((m,copy.deepcopy(r)) for m,r in rows() if r['case']=='nested-construct')
 def test_drop_handler_only_rejected(self):
  m,r=self.target();r['body']['diagnostics']=[d for d in r['body']['diagnostics'] if d['message'] in r['stderr']]
  with self.assertRaises(ValueError):validate(m,r)
 def test_drop_native_stderr_rejected(self):
  m,r=self.target();r['stderr']=''
  with self.assertRaises(ValueError):validate(m,r)
 def test_changed_source_line_rejected(self):
  m,r=self.target();next(d for d in r['body']['diagnostics'] if d['message'] not in r['stderr'])['line']+=1
  with self.assertRaises(ValueError):validate(m,r)
 def test_severity_bool_rejected(self):
  m,r=self.target();r['body']['diagnostics'][0]['severity']=True
  with self.assertRaises(ValueError):validate(m,r)
 def test_extra_handler_only_rejected(self):
  m,r=self.target();r['body']['diagnostics'].append(copy.deepcopy(next(d for d in r['body']['diagnostics'] if d['message'] not in r['stderr'])))
  with self.assertRaises(ValueError):validate(m,r)
 def test_different_message_rejected(self):
  m,r=self.target();next(d for d in r['body']['diagnostics'] if d['message'] not in r['stderr'])['message']='unexpected'
  with self.assertRaises(ValueError):validate(m,r)
 def test_changed_phase_rejected(self):
  m,r=self.target();next(d for d in r['body']['diagnostics'] if d['message'] not in r['stderr'])['phase']='observer:unrelated'
  with self.assertRaises(ValueError):validate(m,r)
 def test_drop_stderr_present_handler_rejected(self):
  m,r=self.target();idx=next(i for i,d in enumerate(r['body']['diagnostics']) if d['message'] in r['stderr']);r['body']['diagnostics'].pop(idx)
  with self.assertRaises(ValueError):validate(m,r)
 def test_unknown_stderr_rejected(self):
  m,r=self.target();r['stderr']+='PHP Warning: unexpected warning in unknown.php on line 1\n'
  with self.assertRaises(ValueError):validate(m,r)
 def test_duplicate_stderr_present_handler_rejected(self):
  m,r=self.target();r['body']['diagnostics'].append(copy.deepcopy(next(d for d in r['body']['diagnostics'] if d['message'] in r['stderr'])))
  with self.assertRaises(ValueError):validate(m,r)
 def test_truncated_stderr_present_handler_rejected(self):
  m,r=self.target();d=next(d for d in r['body']['diagnostics'] if d['message'] in r['stderr']);d['message']=d['message'][:5]
  with self.assertRaises(ValueError):validate(m,r)
 def test_changed_stderr_present_line_rejected(self):
  m,r=self.target();d=next(d for d in r['body']['diagnostics'] if d['message'] in r['stderr']);d['line']+=99
  with self.assertRaises(ValueError):validate(m,r)
 def test_stderr_list_rejected(self):
  m,r=self.target();r['stderr']=[d['message'] for d in r['body']['diagnostics']]
  with self.assertRaises(ValueError):validate(m,r)
 def test_changed_channel_rejected(self):
  m,r=self.target();r['stderr']+='\n'+contract.expected_handler_only(r['variant'],r['case'],m)[0]['message']
  with self.assertRaises(ValueError):validate(m,r)
if __name__=='__main__':unittest.main()

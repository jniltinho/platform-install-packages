import importlib.util,json,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('v',Path(__file__).with_name('validate_followup.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
class ContractTests(unittest.TestCase):
 def report(self,kind):return json.loads((v.E/(kind+'-primary.json')).read_text())
 def reject(self,kind,fn):
  r=self.report(kind);fn(r)
  with self.assertRaises(ValueError):(v.validate_negative if kind=='negative' else v.validate_arity)(r)
 def test_negative_primary(self):v.validate_negative(self.report('negative'))
 def test_arity_primary(self):v.validate_arity(self.report('arity'))
 def test_negative_duplicate(self):self.reject('negative',lambda r:r['records'].__setitem__(1,r['records'][0]))
 def test_negative_missing(self):self.reject('negative',lambda r:r['records'].pop())
 def test_arity_duplicate(self):self.reject('arity',lambda r:r['records'].__setitem__(1,r['records'][0]))
 def test_arity_bool_exit(self):self.reject('arity',lambda r:r['records'][0].update(exit=False))
 def test_negative_noise(self):self.reject('negative',lambda r:r['records'][0].update(stderr='noise'))
 def test_arity_noise(self):self.reject('arity',lambda r:r['records'][0].update(stderr='noise'))
 def change(self,r,field,value,index=0):
  b=json.loads(r['records'][index]['stdout']);b[field]=value;r['records'][index]['stdout']=json.dumps(b)
  if 'body' in r['records'][index]:r['records'][index]['body']=b
 def test_arity_constant_boolean(self):self.reject('arity',lambda r:self.change(r,'constant',True,1))
 def test_arity_swallowed_exception(self):self.reject('arity',lambda r:self.change(r,'exception',None,2))
 def test_negative_output_loss(self):self.reject('negative',lambda r:self.change(r,'outputs',[],4))
 def test_readonly_wrong_success(self):self.reject('negative',lambda r:self.change(r,'outputs',{'bad':{'base64':'','sha256':v.c.sha(b'')}},5))
 def test_negative_missing_lint(self):self.reject('negative',lambda r:r['records'][4]['lints'].pop())
 def test_arity_pending(self):self.reject('arity',lambda r:r.update(pending=['unfinished']))
 def test_runtime_drift(self):self.reject('negative',lambda r:r['identity_after'].update(runtime={}))
if __name__=='__main__':unittest.main()

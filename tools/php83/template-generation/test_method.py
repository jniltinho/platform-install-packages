import importlib.util,json,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('v',Path(__file__).with_name('validate_method.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
class MethodContractTests(unittest.TestCase):
 def report(self):return json.loads((v.c.ROOT/'doc/php83/evidence/template-generation/method-primary.json').read_text())
 def test_actual_records(self):v.validate(self.report())
 def reject(self,fn):
  r=self.report();fn(r)
  with self.assertRaises(ValueError):v.validate(r)
 def body(self,r,fn,index=0):
  b=json.loads(r['records'][index]['stdout']);fn(b);r['records'][index]['stdout']=json.dumps(b)
 def test_typed_zero(self):self.reject(lambda r:self.body(r,lambda b:b.update(value=[0]),6))
 def test_typed_false(self):self.reject(lambda r:self.body(r,lambda b:b.update(value=[False]),6))
 def test_missing_key(self):self.reject(lambda r:self.body(r,lambda b:b.update(value=['plain.php','nested/item.php']),3))
 def test_duplicate_case(self):self.reject(lambda r:r['records'].__setitem__(1,r['records'][0]))
 def test_duplicate_variant(self):self.reject(lambda r:r['records'].__setitem__(26,r['records'][13]))
 def test_unknown_exit(self):self.reject(lambda r:r['records'][0].update(exit=124))
 def test_extra_stderr(self):self.reject(lambda r:r['records'][0].update(stderr='noise'))
 def test_diagnostic_bool(self):self.reject(lambda r:self.body(r,lambda b:b['diagnostics'][0].update(line=True)))
 def test_loaded_omission(self):self.reject(lambda r:self.body(r,lambda b:b['loaded'].pop(next(iter(b['loaded'])))))
 def test_runtime_drift(self):self.reject(lambda r:r['identity_after'].update(runtime={}))
 def test_fixture_mutation(self):self.reject(lambda r:self.body(r,lambda b:b.update(outputs={})))
if __name__=='__main__':unittest.main()

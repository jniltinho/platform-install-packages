import importlib.util,unittest,json,base64
from pathlib import Path
s=importlib.util.spec_from_file_location('v',Path(__file__).with_name('validate.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
class OutputTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads(v.BASELINE.read_text());cls.manifest=json.loads(v.c.MANIFEST.read_text())
 def test_all_expected_deltas(self):
  changes=0
  for row in self.base['records']:
   if row['variant']!='candidate':continue
   old=json.loads(row['stdout']);new,changed=v.expected_body(row,'debug',self.manifest);changes+=changed
   for path,item in new['outputs'].items():
    data=base64.b64decode(item['base64']);before=base64.b64decode(old['outputs'][path]['base64'])
    self.assertEqual(len(data)-len(before),1 if changed else 0)
   self.assertEqual(new['exception'],old['exception'])
  self.assertEqual(changes,12)
 def test_prerequisite_unchanged(self):
  for row in self.base['records']:
   if row['variant']!='candidate':continue
   new,changed=v.expected_body(row,'prerequisite',self.manifest);self.assertFalse(changed);self.assertEqual(new,json.loads(row['stdout']))
 def test_refuse_missing_literal(self):
  row=next(r for r in self.base['records'] if r['variant']=='candidate' and r['case']=='default-false');row=dict(row);b=json.loads(row['stdout'])
  for item in b['outputs'].values():item['base64']=base64.b64encode(b'<?php echo 1;').decode()
  row['stdout']=json.dumps(b)
  with self.assertRaises(ValueError):v.expected_body(row,'debug',self.manifest)
 def synthetic(self):
  import copy
  report=copy.deepcopy(self.base);report['records']=[]
  for rt,variant in v.c.VARIANTS:
   for old in self.base['records']:
    if old['variant']!='candidate' or old['runtime']!=rt:continue
    row=copy.deepcopy(old);row['variant']=variant;row['stdout']=json.dumps(v.expected_body(old,variant,self.manifest)[0]);row['command']=f"bash {v.c.STAGE}/run.sh {rt} {variant} generate {row['case']}";report['records'].append(row)
  expected={v.c.STAGE+'/'+n:v.c.sha((v.HERE/n).read_bytes()) for n in ['probe.php','run.sh']}
  for path,pins in self.manifest['files'].items():
   for variant in ['original','exp10','prerequisite','debug']:expected[v.c.STAGE+'/'+variant+'/'+path]=pins[variant]
  report['identity_before']['stage']=expected;report['identity_after']=copy.deepcopy(report['identity_before']);report['harness_sha256']={n:v.c.sha((v.HERE/n).read_bytes()) for n in v.c.HARNESS};report['input_pins']={str(v.c.MANIFEST):v.c.sha(v.c.MANIFEST.read_bytes()),str(v.c.CASES):v.c.sha(v.c.CASES.read_bytes())};return report
 def test_synthetic_contract_not_runtime(self):self.assertEqual(v.validate(self.synthetic())['rows'],72)
 def test_duplicate_rows(self):
  r=self.synthetic();r['records'][1]=r['records'][0]
  with self.assertRaises(ValueError):v.validate(r)
 def test_native_noise(self):
  r=self.synthetic();r['records'][0]['stderr']+='noise'
  with self.assertRaises(ValueError):v.validate(r)
 def test_wrong_output(self):
  r=self.synthetic();b=json.loads(r['records'][-1]['stdout']);b['value']=42;r['records'][-1]['stdout']=json.dumps(b)
  with self.assertRaises(ValueError):v.validate(r)
 def test_runtime_drift(self):
  r=self.synthetic();r['identity_after']['runtime']={}
  with self.assertRaises(ValueError):v.validate(r)
 def test_plan_omission(self):
  import tempfile
  from unittest.mock import patch
  r=self.synthetic();r['records']=[x for x in r['records'] if x['case']!='module']
  cases=json.loads(v.c.CASES.read_text());cases['modes']['generate'].remove('module')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'cases.json';p.write_text(json.dumps(cases))
   with patch.object(v.c,'CASES',p):
    r['input_pins']={str(v.c.MANIFEST):v.c.sha(v.c.MANIFEST.read_bytes()),str(p):v.c.sha(p.read_bytes())}
    with self.assertRaises(ValueError):v.validate(r)
if __name__=='__main__':unittest.main()

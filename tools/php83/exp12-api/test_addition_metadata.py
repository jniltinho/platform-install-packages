import importlib.util,json,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('v',Path(__file__).with_name('validate-additions.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
E=v.base.REPO/'doc/php83/evidence/exp12-runtime'
class MetadataTests(unittest.TestCase):
 def report(self):return json.loads((E/'additions-primary.json').read_text())
 def check(self,r):return v.validate(r,json.loads((E/'additions-post-source.json').read_text()))
 def test_actual17_revalidation(self):self.assertEqual(len(self.check(self.report())['allowed_loaded_field_changes']),9)
 def test_unrelated_loaded_hash(self):
  r=self.report();row=next(x for x in r['records'] if x['case']=='cli-version');marker='AUTOLOAD_RESULT ';body=json.loads(row['stdout'].split(marker)[1]);key=next(k for k in body['loaded'] if 'pakeApp' not in k);pin=body['loaded'][key];row['stdout']=row['stdout'].replace(json.dumps(key)+':'+json.dumps(pin),json.dumps(key)+':'+json.dumps('0'*64),1)
  with self.assertRaises(ValueError):self.check(r)
 def test_functional_byte(self):
  r=self.report();r['records'][1]['stdout']+='unexpected'
  with self.assertRaises(ValueError):self.check(r)
 def test_stderr(self):
  r=self.report();r['records'][2]['stderr']+='warning'
  with self.assertRaises(ValueError):self.check(r)
 def test_duplicate(self):
  r=self.report();r['records'][1]=r['records'][0]
  with self.assertRaises(ValueError):self.check(r)
 def test_boolean_exit(self):
  r=self.report();r['records'][0]['exit']=False
  with self.assertRaises(ValueError):self.check(r)
 def test_missing_changed_target(self):
  r=self.report();row=next(x for x in r['records'] if x['case']=='cli-tasks-configured');row['stdout']=row['stdout'].replace('6958f51ba82e9f4922eb8a7437dc1301ffd81032dd168f9c70516dee21f9e6d9','67682683048afeaef9ed55bd95a5920792b2c6ab3b4ec11c804985ead4b347eb')
  with self.assertRaises(ValueError):self.check(r)
 def test_consistent_forged_file_count(self):
  r=self.report();r['artifact']['verified_extracted_files']+=1
  with self.assertRaises(ValueError):v.validate(r,r['artifact'])
if __name__=='__main__':unittest.main()



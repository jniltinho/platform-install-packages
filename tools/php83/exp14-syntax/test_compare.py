import copy,unittest
import scan,compare
import test_scan
class ComparatorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  Records=test_scan.Records;Records.setUpClass();cls.contract=Records.contract;cls.harness={n:scan.sha(scan.HERE/n) for n in scan.FILES}
  variants=copy.deepcopy(Records.fixture)
  for name,row in variants.items():
   row['source_after']=copy.deepcopy(row['source_before']);row['zip_sha256']=cls.contract['pins'][name];row['summary']=scan.core.summarize(row['records'])
  runtime={'command':scan.PHP,'resolved_path':scan.PHP,'sha256':'a'*64,'version':'PHP 8.3.6','modules':'Core\n','ini':'Loaded Configuration File:         (none)','linked_library_sha256':{'/lib/fake.so':'b'*64},'environment':{'LC_ALL':'C','TZ':'UTC'}}
  cls.fixture={'status':'COMPLETE_BOUNDED','application_acceptance':False,'input_contract':cls.contract,'runtime_before':runtime,'runtime_after':copy.deepcopy(runtime),'harness_before':cls.harness,'harness_after':cls.harness,'variants':variants,'comparison':scan.compare_reports(variants,cls.contract)}
 def setUp(self):self.r=copy.deepcopy(self.fixture)
 def bad(self):self.assertRaises(RuntimeError,compare.validate,self.r,self.contract,self.harness)
 def test_valid(self):self.assertTrue(compare.validate(self.r,self.contract,self.harness)['bounded_compiler_nonregression'])
 def test_source_after_drift(self):self.r['variants']['exp14']['source_after']['unknown']='0'*64;self.bad()
 def test_runtime_empty_equal(self):self.r['runtime_before']={};self.r['runtime_after']={};self.bad()
 def test_runtime_drift(self):self.r['runtime_after']['sha256']='b'*64;self.bad()
 def test_harness_drift(self):self.r['harness_after']['scan.py']='0'*64;self.bad()
 def test_missing_summary(self):self.r['variants']['exp14']['summary']={};self.bad()
 def test_only_duration_excluded(self):
  other=copy.deepcopy(self.r);other['variants']['exp14']['records'][0]['duration_ns']=99
  self.assertTrue(scan.strict_equal(compare.normalize(other),compare.normalize(self.r)))
  other['variants']['exp14']['records'][0]['stderr']='difference'
  self.assertFalse(scan.strict_equal(compare.normalize(other),compare.normalize(self.r)))
if __name__=='__main__':unittest.main()

import copy,json,pathlib,tempfile,unittest
from unittest.mock import patch
import scan
class Contract(unittest.TestCase):
 def mutate(self,fn):
  d=scan.load_contract();fn(d)
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'contract';p.write_text(json.dumps(d));self.assertRaises(RuntimeError,scan.load_contract,p)
 def test_valid(self):self.assertEqual(len(scan.load_contract()['targets']),13)
 def test_pending(self):self.mutate(lambda d:d['pins'].update(exp13=None))
 def test_wrong_counts(self):self.mutate(lambda d:d['counts'].update(exp13=11784))
 def test_duplicate(self):self.mutate(lambda d:d['targets'].__setitem__(0,d['targets'][1]))
 def test_missing(self):self.mutate(lambda d:d['targets'].pop())
 def test_bad_path(self):self.mutate(lambda d:d['targets'][0].update(path='../evil.php'))
 def test_wrong_added(self):self.mutate(lambda d:next(t for t in d['targets'] if t['exp12_sha256'] is None).update(path='wrong.php'))
 def test_boolean_count(self):self.mutate(lambda d:d['counts'].update(exp13=True))
class Records(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.contract=scan.load_contract();ts={t['path']:t for t in cls.contract['targets']};extra=cls.contract['historical_rejections'];base=[p for p,t in ts.items() if t['exp12_sha256'] is not None]+extra
  base += ['fixture/file%05d.php'%i for i in range(11784-len(base))]
  cls.original={}
  for v in scan.VARIANTS:
   paths=base+(['infra/general/kXmlEntityLoaderPolicy.php'] if v=='exp13' else []);rs=[]
   for p in paths:
    status=255 if p in extra else 0;out='' if status else 'No syntax errors detected in /audit/'+v+'/'+p+'\n';err=('Parse error in /audit/'+v+'/'+p+'\n') if status else ''
    rs.append({'path':p,'sha256':ts[p][v+'_sha256'] if p in ts else 'a'*64,'exit':status,'stdout':out,'stderr':err,'diagnostics':scan.diagnostics(out,err,pathlib.Path('/audit/'+v)),'command':[scan.PHP]+scan.FLAGS+['/audit/'+v+'/'+p],'duration_ns':1})
   cls.original[v]={'records':rs}
 def setUp(self):self.r=copy.deepcopy(self.original)
 def bad(self):self.assertRaises(RuntimeError,scan.compare_reports,self.r,self.contract)
 def test_success(self):self.assertTrue(scan.compare_reports(self.r,self.contract)['bounded_compiler_nonregression'])
 def test_truncation(self):self.r['exp13']['records'].pop();self.bad()
 def test_duplicate_record(self):self.r['exp13']['records'][-1]=self.r['exp13']['records'][0];self.bad()
 def test_timeout(self):self.r['exp13']['records'][0]['exit']=124;self.bad()
 def test_status_bool(self):self.r['exp13']['records'][0]['exit']=False;self.bad()
 def test_status_float(self):self.r['exp13']['records'][0]['exit']=0.0;self.bad()
 def test_raw_stderr_drift(self):self.r['exp13']['records'][0]['stderr']='extra';self.bad()
 def test_unapproved_hash(self):self.r['exp13']['records'][30]['sha256']='b'*64;self.bad()
 def test_added_hash(self):self.r['exp13']['records'][-1]['sha256']='b'*64;self.bad()
 def test_missing_raw(self):del self.r['exp13']['records'][0]['stdout'];self.bad()
 def test_wrong_command(self):self.r['exp13']['records'][0]['command'].append('extra');self.bad()
 def test_changed_rejection(self):self.r['exp13']['records'][0]['exit']=255;self.bad()
 def test_duration_bool(self):self.r['exp13']['records'][0]['duration_ns']=True;self.bad()
 def test_target_diagnostic_delta_recorded(self):
  row=self.r['exp13']['records'][0];row['stderr']='Deprecated: fixture\n';row['diagnostics']='Deprecated: fixture';self.assertEqual(next(d for d in scan.compare_reports(self.r,self.contract)['diagnostic_delta'] if d['path']==row['path'])['after_diagnostics'],'Deprecated: fixture')
if __name__=='__main__':unittest.main()

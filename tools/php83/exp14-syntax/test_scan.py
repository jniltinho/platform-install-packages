import copy,hashlib,io,json,pathlib,tempfile,unittest,zipfile
from unittest.mock import patch
import scan


def contract():
 d=json.loads((scan.HERE/'input-contract.json').read_text())
 d['pins']['exp14']='f'*64
 d['metadata_delta_allowlist']=[{'path':'.php83-experimental/manifest.json','exp13_sha256':'1'*64,'exp14_sha256':'2'*64},{'path':'.php83-experimental/rank.patch','exp13_sha256':None,'exp14_sha256':'3'*64}]
 return d

class ContractTests(unittest.TestCase):
 def check(self,d):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'contract';p.write_text(json.dumps(d));return scan.load_contract(p)
 def mutate(self,fn):
  d=contract();fn(d)
  with self.assertRaises(RuntimeError):self.check(d)
 def test_valid_synthetic(self):self.assertEqual(self.check(contract())['counts']['exp14'],11785)
 def test_pending_real_before_runtime(self):
  pending=scan.HERE.parents[2]/'doc/php83/evidence/exp14-syntax/pending-input-contract.json'
  with patch.object(scan.parent,'runtime_identity') as runtime,patch.object(scan.parent,'load_contract',side_effect=lambda:scan.load_contract(pending)):
   with self.assertRaises(RuntimeError):scan.run()
   runtime.assert_not_called()
 def test_candidate_pending(self):self.mutate(lambda d:d['pins'].update(exp14=None))
 def test_wrong_prior(self):self.mutate(lambda d:d['pins'].update(exp13='c'*64))
 def test_same_pin(self):self.mutate(lambda d:d['pins'].update(exp14=scan.PRIOR_PIN))
 def test_wrong_count(self):self.mutate(lambda d:d['counts'].update(exp14=11784))
 def test_bool_count(self):self.mutate(lambda d:d['counts'].update(exp14=True))
 def test_wrong_target(self):self.mutate(lambda d:d['targets'][0].update(path='other.php'))
 def test_second_target(self):self.mutate(lambda d:d['targets'].append(copy.deepcopy(d['targets'][0])))
 def test_wrong_target_pin(self):self.mutate(lambda d:d['targets'][0].update(exp14_sha256='0'*64))
 def test_wrong_rejects(self):self.mutate(lambda d:d['historical_rejections'].pop())
 def test_metadata_pending(self):self.mutate(lambda d:d.update(metadata_delta_allowlist=None))
 def test_metadata_duplicate(self):self.mutate(lambda d:d['metadata_delta_allowlist'].append(d['metadata_delta_allowlist'][0]))
 def test_metadata_source_disguised(self):self.mutate(lambda d:d['metadata_delta_allowlist'][0].update(path='api_v3/other.php'))
 def test_metadata_traversal(self):self.mutate(lambda d:d['metadata_delta_allowlist'][0].update(path='.php83-experimental/../evil.patch'))
 def test_metadata_php(self):self.mutate(lambda d:d['metadata_delta_allowlist'][0].update(path='.php83-experimental/code.php'))
 def test_metadata_removal(self):self.mutate(lambda d:d['metadata_delta_allowlist'][0].update(exp14_sha256=None))

class Records(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.contract=contract();paths=[scan.TARGET]+scan.REJECTIONS+['fixture/file%05d.php'%i for i in range(11785-8)];cls.fixture={}
  for variant in scan.VARIANTS:
   records=[];inventory={}
   for path in paths:
    status=255 if path in scan.REJECTIONS else 0
    out='' if status else 'No syntax errors detected in /audit/'+variant+'/'+path+'\n'
    err='Parse error in /audit/'+variant+'/'+path+'\n' if status else ''
    if path==scan.TARGET and variant=='exp13':err=scan.EXPECTED_DIAGNOSTIC.replace(' in '+scan.TARGET,' in /audit/exp13/'+scan.TARGET)+'\n'
    digest=scan.TARGETS[0][variant+'_sha256'] if path==scan.TARGET else 'a'*64
    inventory[path]=digest
    records.append({'path':path,'sha256':digest,'exit':status,'stdout':out,'stderr':err,'diagnostics':scan.diagnostics(out,err,pathlib.Path('/audit/'+variant)),'command':[scan.PHP]+scan.FLAGS+['/audit/'+variant+'/'+path],'duration_ns':1})
   for row in cls.contract['metadata_delta_allowlist']:
    if row[variant+'_sha256'] is not None:inventory[row['path']]=row[variant+'_sha256']
   cls.fixture[variant]={'records':records,'source_before':inventory}
 def setUp(self):self.r=copy.deepcopy(self.fixture)
 def bad(self):self.assertRaises(RuntimeError,scan.compare_reports,self.r,self.contract)
 def test_success(self):self.assertTrue(scan.compare_reports(self.r,self.contract)['bounded_compiler_nonregression'])
 def test_truncated(self):self.r['exp14']['records'].pop();self.bad()
 def test_duplicate(self):self.r['exp14']['records'][-1]=self.r['exp14']['records'][0];self.bad()
 def test_timeout(self):self.r['exp14']['records'][0]['exit']=124;self.bad()
 def test_signal(self):self.r['exp14']['records'][0]['exit']=-9;self.bad()
 def test_bool_exit(self):self.r['exp14']['records'][0]['exit']=False;self.bad()
 def test_float_exit(self):self.r['exp14']['records'][0]['exit']=0.0;self.bad()
 def test_duration_bool(self):self.r['exp14']['records'][0]['duration_ns']=True;self.bad()
 def test_raw_drift(self):self.r['exp14']['records'][0]['stderr']='new warning';self.bad()
 def test_missing_raw(self):del self.r['exp14']['records'][0]['stderr'];self.bad()
 def test_wrong_command(self):self.r['exp14']['records'][0]['command'].append('extra');self.bad()
 def test_ignored_new_warning(self):
  r=self.r['exp14']['records'][0];r['stderr']='new warning';r['diagnostics']='new warning';self.bad()
 def test_prior_notice_suppressed(self):
  r=self.r['exp13']['records'][0];r['stderr']='';r['diagnostics']='';self.bad()
 def test_second_source_delta(self):
  r=self.r['exp14']['records'][20];r['sha256']='b'*64;self.r['exp14']['source_before'][r['path']]='b'*64;self.bad()
 def test_extra_nonphp(self):self.r['exp14']['source_before']['surprise.txt']='b'*64;self.bad()
 def test_removed_metadata(self):del self.r['exp14']['source_before']['.php83-experimental/rank.patch'];self.bad()
 def test_wrong_metadata_hash(self):self.r['exp14']['source_before']['.php83-experimental/manifest.json']='c'*64;self.bad()
 def test_reject_changed(self):self.r['exp14']['records'][1]['exit']=0;self.bad()
 def test_path_added(self):self.r['exp14']['records'][20]['path']='extra.php';self.bad()

class ArchiveTests(unittest.TestCase):
 def run_archive(self,entries,files,raises=False):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);source=root/'source';source.mkdir();archive=root/'a.zip'
   with zipfile.ZipFile(archive,'w') as z:
    for name,data in entries:z.writestr(name,data)
   for name,data in files.items():(source/name).write_bytes(data)
   pin=hashlib.sha256(archive.read_bytes()).hexdigest()
   if raises:
    with self.assertRaises(RuntimeError):scan.core.archive_inventory(archive,source,pin)
   else:self.assertEqual(len(scan.core.archive_inventory(archive,source,pin)),len(files))
 def test_valid(self):self.run_archive([('server-Rigel-18.20.0/a.php',b'<?php')],{'a.php':b'<?php'})
 def test_missing(self):self.run_archive([('server-Rigel-18.20.0/a.php',b'x')],{},True)
 def test_extra(self):self.run_archive([('server-Rigel-18.20.0/a.php',b'x')],{'a.php':b'x','b.txt':b'x'},True)
 def test_duplicate(self):self.run_archive([('server-Rigel-18.20.0/a.php',b'x')]*2,{'a.php':b'x'},True)
 def test_traversal(self):self.run_archive([('server-Rigel-18.20.0/../a.php',b'x')],{'a.php':b'x'},True)
 def test_mismatch(self):self.run_archive([('server-Rigel-18.20.0/a.php',b'x')],{'a.php':b'y'},True)
 def test_symlink(self):
  info=zipfile.ZipInfo('server-Rigel-18.20.0/a.php');info.external_attr=0o120777<<16
  self.run_archive([(info,b'x')],{'a.php':b'x'},True)

if __name__=='__main__':unittest.main()

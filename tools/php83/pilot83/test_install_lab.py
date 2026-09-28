import copy,importlib.util,json,pathlib,tempfile,unittest
from unittest.mock import patch
P=pathlib.Path(__file__).with_name('install-lab.py');s=importlib.util.spec_from_file_location('install_lab',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def contract():
 c={'status':'REVIEWED_INPUTS_READY','schema':1,'target':{'hostname':m.HOST,'ip':m.IP},'packages':[{'package':n,'version':'1+php83lab1','path':'/var/lib/kaltura-php83-pilot/packages/'+n+'.deb','sha256':'a'*64} for n in sorted(m.PACKAGES)],'runtime_files':[{'path':'/usr/bin/php8.3','sha256':'b'*64}],'php_package_version':'8.3.6-0ubuntu0.24.04.11'}
 for k in ['private_deb_verification','dependency_origins','recovery_point']:c[k]={'path':'/var/lib/kaltura-php83-pilot/proofs/'+k+'.json','sha256':'c'*64}
 c['external_debs']=[dict(m.EXTERNAL,path='/var/lib/kaltura-php83-pilot/packages-external/elasticsearch.deb')]
 return c
class Tests(unittest.TestCase):
 def test_synthetic_valid_schema_not_real_proof(self):self.assertEqual(len(m.validate(contract())['packages']),17)
 def test_pending_before_commands(self):
  with patch.object(m.subprocess,'run') as r,patch.object(m.socket,'gethostname') as h:
   with self.assertRaises(ValueError):m.guest_preflight({'status':'PENDING'})
   r.assert_not_called();h.assert_not_called()
 def test_wrong_host(self):
  c=contract();c['target']['ip']='192.168.56.74'
  with self.assertRaises(ValueError):m.validate(c)
 def test_missing_package(self):
  c=contract();c['packages'].pop()
  with self.assertRaises(ValueError):m.validate(c)
 def test_duplicate(self):
  c=contract();c['packages'][1]=c['packages'][0]
  with self.assertRaises(ValueError):m.validate(c)
 def test_path_escape(self):
  c=contract();c['packages'][0]['path']='/var/lib/kaltura-php83-pilot/packages/../evil.deb'
  with self.assertRaises(ValueError):m.validate(c)
 def test_unpinned(self):
  c=contract();c['packages'][0]['sha256']='PENDING'
  with self.assertRaises(ValueError):m.validate(c)
 def test_missing_origins(self):
  c=contract();del c['dependency_origins']
  with self.assertRaises(ValueError):m.validate(c)
 def test_no_recovery(self):
  c=contract();del c['recovery_point']
  with self.assertRaises(ValueError):m.validate(c)
 def test_revision(self):
  c=contract();c['php_package_version']='7.4'
  with self.assertRaises(ValueError):m.validate(c)
 def test_regular_identity(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'input';p.write_bytes(b'x');m.checked_file(p,m.sha(b'x'))
   with self.assertRaises(ValueError):m.checked_file(p,'0'*64)
   q=p.with_name('link');q.symlink_to(p)
   with self.assertRaises(ValueError):m.checked_file(q,m.sha(b'x'))
 def test_no_installer_and_no_auth(self):
  plan=m.plan({'status':'PENDING'});self.assertFalse(plan['mutation_implemented']);self.assertFalse(plan['auth_implemented']);self.assertFalse(plan['rollback_implemented']);self.assertFalse(plan['inputs_ready'])
  self.assertIn('BEFORE any MariaDB',json.dumps(plan));self.assertIn('restore pre-install VM',json.dumps(plan))
 def test_external_required(self):
  c=contract();c['external_debs']=[]
  with self.assertRaises(ValueError):m.validate(c)
 def test_external_pin_version_arch_drift(self):
  for k in ['sha256','version','architecture','package']:
   c=contract();c['external_debs'][0][k]='wrong'
   with self.subTest(k=k),self.assertRaises(ValueError):m.validate(c)
 def test_no_zip_or_external_escape(self):
  for path in ['/var/lib/kaltura-php83-pilot/packages-external/icu.zip','/tmp/elasticsearch.deb','/var/lib/kaltura-php83-pilot/packages-external/../escape.deb']:
   c=contract();c['external_debs'][0]['path']=path
   with self.subTest(path=path),self.assertRaises(ValueError):m.validate(c)
 def test_simulation_exact18(self):
  c=contract();args=m.simulation_args(c);self.assertEqual(len(args),23);self.assertIn('--no-install-recommends',args)
  self.assertEqual(args[-1],c['external_debs'][0]['path']);self.assertEqual(set(args[5:]),{r['path'] for r in c['packages']+c['external_debs']})
 def test_no_install_subprocess(self):
  text=P.read_text();self.assertIn("['apt-get','--simulate','--no-remove','--no-install-recommends','install']",text);self.assertNotIn('apt-get update',text);self.assertNotIn("['curl'",text);self.assertNotIn("['ssh'",text)
if __name__=='__main__':unittest.main()

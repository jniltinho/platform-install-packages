import importlib.util,json,os,pathlib,stat,tempfile,types,unittest
from unittest.mock import patch
P=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('repair',P/'cache-write-config-repair-r2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def raw(self):
  value=b'host = 127.0.0.1\nport = 11211\n[write_address_list]\n1 = '+m.TOKEN+b'\n'
  return value+b';'+b'x'*(340-len(value))
 def test_authenticated_public_template(self):
  raw=(P.parents[2]/'doc/php83/evidence/cache-write-config-repair-r1/public-template.ini').read_bytes()
  self.assertEqual(m.sha(raw),'40751f37cba28413e64e2413810da0231389ba57b14b593ba86f7f5bca8fe158')
  before=raw.replace(b'@MEMACHED_PORT@',b'11211').replace(b'@MEMACHED_HOSTNAME@',b'127.0.0.1')
  self.assertEqual(m.sha(before),m.BEFORE);self.assertEqual(m.sha(m.transform(before)),m.AFTER)
 def test_exact_single_replacement(self):
  raw=self.raw();out=raw.replace(m.TOKEN,b'127.0.0.1')
  with patch.object(m,'BEFORE',m.sha(raw)),patch.object(m,'AFTER',m.sha(out)):
   self.assertEqual(m.transform(raw),out)
   for bad in (raw+b'\n',raw.replace(b'11211',b'11212'),out,b'',raw.replace(m.TOKEN,b'127.0.0.2')):
    with self.assertRaises(ValueError):m.transform(bad)
 def test_duplicate_token_even_authenticated(self):
  raw=(m.TOKEN+b'\n')*2;raw+=b';'+b'x'*(340-len(raw))
  with patch.object(m,'BEFORE',m.sha(raw)):
   with self.assertRaisesRegex(ValueError,'PREIMAGE'):m.transform(raw)
 def test_postimage_pin(self):
  raw=self.raw()
  with patch.object(m,'BEFORE',m.sha(raw)):
   with self.assertRaisesRegex(ValueError,'POSTIMAGE'):m.transform(raw)
 def contract(self):return dict(schema=1,status='LAB_CACHE_WRITE_REPAIR_AUTHORIZED',machine_id_sha256=m.MACHINE,full_acceptance=False,release_authorized=False,**{k:'a'*64 for k in ('executor_sha256','snapshot_sha256','baseline_dpkg_sha256','d1_contract_sha256','d1_terminal_sha256')})
 def test_contract(self):m.validate(self.contract())
 def test_contract_negatives(self):
  for k,v in [('schema',True),('machine_id_sha256','b'*64),('full_acceptance',True),('full_acceptance',0),('release_authorized',True),('snapshot_sha256',''),('executor_sha256',None),('status','ACCEPTED')]:
   c=self.contract();c[k]=v
   with self.subTest(key=k),self.assertRaises(ValueError):m.validate(c)
 def test_fresh_refuses_any_existing_path(self):
  with patch.object(m.os.path,'lexists',return_value=False):m.fresh()
  for existing in (m.RUN,m.TEMP,pathlib.Path('/var/lib/kaltura-php83-phase-d2'),pathlib.Path('/var/lib/kaltura-php83-phase-d2-incremental'),pathlib.Path('/usr/sbin/policy-rc.d')):
   with patch.object(m.os.path,'lexists',side_effect=lambda p:p==existing),self.assertRaisesRegex(ValueError,'NO_RESUME'):m.fresh()
 def test_private_exclusive_0600(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'backup';m.private(p,b'synthetic-private-fixture');self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
   with self.assertRaises(FileExistsError):m.private(p,b'overwrite')
   link=pathlib.Path(tmp)/'link';link.symlink_to(pathlib.Path(tmp)/'missing')
   with self.assertRaises(FileExistsError):m.private(link,b'no')
 def test_symlink_read_refused(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'link';p.symlink_to('/dev/null')
   with patch.object(m,'parents'),self.assertRaises(OSError):m.read(p)
 def test_file_metadata_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'file';p.write_bytes(b'x');p.chmod(0o666)
   with patch.object(m,'parents'),self.assertRaisesRegex(ValueError,'FILE_TRUST'):m.read(p)
 def test_stopped_states(self):
  b=types.SimpleNamespace(states=lambda f:dict(apache2='inactive',monit='inactive',mariadb='active'));m.stopped(b,None)
  for unit in ('apache2','monit','mariadb'):
   states=b.states(None);states[unit]='active' if unit!='mariadb' else 'inactive'
   with self.assertRaisesRegex(ValueError,'SERVICES'):m.stopped(types.SimpleNamespace(states=lambda f:states),None)
 def test_exact_known_root_group_parent(self):
  def status(p):return types.SimpleNamespace(st_mode=stat.S_IFDIR|(0o775 if str(p)=='/opt/kaltura/app/configurations' else 0o755),st_uid=0,st_gid=0)
  with patch.object(pathlib.Path,'lstat',status),patch.object(m.os,'listxattr',return_value=[]),patch.object(m.grp,'getgrgid',return_value=types.SimpleNamespace(gr_mem=[])),patch.object(m.pwd,'getpwall',return_value=[types.SimpleNamespace(pw_gid=0,pw_name='root')]):
   m.parents(m.TARGET)
   with patch.object(m.grp,'getgrgid',return_value=types.SimpleNamespace(gr_mem=['intruder'])),self.assertRaisesRegex(ValueError,'ROOT_GROUP'):m.parents(m.TARGET)
   with patch.object(m.pwd,'getpwall',return_value=[types.SimpleNamespace(pw_gid=0,pw_name='other')]),self.assertRaisesRegex(ValueError,'ROOT_GROUP'):m.parents(m.TARGET)
   with patch.object(m.os,'listxattr',return_value=['system.posix_acl_access']),self.assertRaisesRegex(ValueError,'PARENT_TRUST'):m.parents(m.TARGET)
 def test_parent_exception_is_exact(self):
  for location,mode,gid in [('/opt/kaltura/app/configurations',0o777,0),('/opt/kaltura/app/configurations',0o775,33),('/opt/kaltura/app',0o775,0)]:
   def status(p):return types.SimpleNamespace(st_mode=stat.S_IFDIR|(mode if str(p)==location else 0o755),st_uid=0,st_gid=gid if str(p)==location else 0)
   with patch.object(pathlib.Path,'lstat',status),patch.object(m.os,'listxattr',return_value=[]),self.assertRaisesRegex(ValueError,'PARENT_TRUST'):m.parents(m.TARGET)
 def test_parent_symlink_rejected(self):
  with patch.object(pathlib.Path,'lstat',return_value=types.SimpleNamespace(st_mode=stat.S_IFLNK|0o775,st_uid=0,st_gid=0)),patch.object(m.os,'listxattr',return_value=[]),patch.object(m.grp,'getgrgid',return_value=types.SimpleNamespace(gr_mem=[])),patch.object(m.pwd,'getpwall',return_value=[]),self.assertRaisesRegex(ValueError,'PARENT_TRUST'):m.parents(m.TARGET)
 def test_public_failure_has_no_exception_payload(self):
  source=(P/'cache-write-config-repair-r2.py').read_text();self.assertNotIn('str(error)',source);self.assertNotIn('str(exc)',source)
if __name__=='__main__':unittest.main()

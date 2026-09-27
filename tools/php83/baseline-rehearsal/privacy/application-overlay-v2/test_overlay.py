import importlib.util,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('overlay_prepare',HERE/'prepare.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
class Tests(unittest.TestCase):
 def test_real_source_preparation(self):
  with tempfile.TemporaryDirectory() as d:
   m=p.prepare(Path(d)/'fresh')
   self.assertEqual(tuple(m['before']),p.guest.TARGETS);self.assertEqual(len(m['after']),4);self.assertEqual(len(m['support_sources']),15)
   for n,h in m['files'].items():self.assertEqual(p.sha((Path(d)/'fresh'/n).read_bytes()),h)
 def test_double_output(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):p.prepare(Path(d))
 def test_support_disjoint(self):
  with tempfile.TemporaryDirectory() as d:
   m=p.prepare(Path(d)/'fresh');self.assertFalse(set(m['before'])&set(m['support_sources']))
 def test_exact_replacement_metadata(self):
  with tempfile.TemporaryDirectory() as d,patch.object(p.guest,'APP',Path(d)):
   f=Path(d)/'x';f.write_bytes(b'old');st=f.stat();p.guest.replace_file('x',b'new',dict(uid=st.st_uid,gid=st.st_gid,mode=0o640))
   self.assertEqual(f.read_bytes(),b'new');self.assertEqual(f.stat().st_mode&0o777,0o640);self.assertFalse(f.with_name('x.privacy-overlay-v2-new').exists())
 def test_refuse_existing_temporary(self):
  with tempfile.TemporaryDirectory() as d,patch.object(p.guest,'APP',Path(d)):
   f=Path(d)/'x';f.write_bytes(b'old');f.with_name('x.privacy-overlay-v2-new').write_bytes(b'foreign')
   with self.assertRaises(FileExistsError):p.guest.replace_file('x',b'new',dict(uid=0,gid=0,mode=0o644))
   self.assertEqual(f.read_bytes(),b'old')
 def test_source_drift(self):
  with tempfile.TemporaryDirectory() as d,patch.object(p.guest,'APP',Path(d)):
   (Path(d)/'x').write_bytes(b'x')
   with self.assertRaisesRegex(RuntimeError,'SOURCE_DRIFT'):p.guest.source_state({'x':'0'*64})
 def test_source_symlink(self):
  with tempfile.TemporaryDirectory() as d,patch.object(p.guest,'APP',Path(d)):
   (Path(d)/'a').write_bytes(b'a');(Path(d)/'x').symlink_to('a')
   with self.assertRaisesRegex(RuntimeError,'SOURCE_TYPE'):p.guest.source_state({'x':p.sha(b'a')})
 def test_quiescence_failclosed(self):
  with patch.object(p.guest,'app_processes',return_value={'1':{}}):
   with self.assertRaises(RuntimeError):p.guest.wait_none(limit=0)
 def test_mutation_during_start_rolls_back(self):
  for mutation in ['content','mode']:
   with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as d,patch.object(p.guest,'APP',Path(d)),patch.object(p.guest,'SYSTEM',Path(d)/'system'):
    f=Path(d)/'x';f.write_bytes(b'old');f.chmod(0o640);p.guest.SYSTEM.write_bytes(b'config')
    st=f.stat();meta={'x':dict(uid=st.st_uid,gid=st.st_gid,mode=0o640)};report={}
    def apply():
     p.guest.replace_file('x',b'new',meta['x'])
     if mutation=='content':f.write_bytes(b'tampered')
     elif mutation=='mode':f.chmod(0o600)
     else:p.guest.SYSTEM.write_bytes(b'changed')
     p.guest.final_state({'x':p.sha(b'new')},meta,b'config')
    def recover():
     p.guest.replace_file('x',b'old',meta['x']);p.guest.SYSTEM.write_bytes(b'config')
     p.guest.final_state({'x':p.sha(b'old')},meta,b'config')
    p.guest.transaction(report,apply,recover)
    self.assertEqual(report['status'],'FAILED_ROLLED_BACK_NO_AUTH');self.assertEqual(f.read_bytes(),b'old')
 def test_private_error_not_exported(self):
  def fail():raise RuntimeError('SYNTHETIC_PRIVATE_DETAIL')
  report={};private=[];p.guest.transaction(report,fail,fail,private)
  self.assertNotIn('SYNTHETIC_PRIVATE_DETAIL',str(report));self.assertEqual(len(private),2)
 def test_system_change_fails_closed(self):
  with tempfile.TemporaryDirectory() as d,patch.object(p.guest,'APP',Path(d)),patch.object(p.guest,'SYSTEM',Path(d)/'system'):
   f=Path(d)/'x';f.write_bytes(b'new');p.guest.SYSTEM.write_bytes(b'changed');st=f.stat()
   with self.assertRaisesRegex(RuntimeError,'FINAL_SYSTEM_CONFIG_DRIFT'):p.guest.final_state({'x':p.sha(b'new')},{'x':dict(uid=st.st_uid,gid=st.st_gid,mode=st.st_mode&0o777)},b'config')
 def test_recovery_failure_explicit(self):
  def fail():raise RuntimeError('synthetic')
  report={};p.guest.transaction(report,fail,fail)
  self.assertEqual(report['status'],'FAILED_RECOVERY_REQUIRED_NO_AUTH')
 def test_success_requires_final_callback(self):
  report={};p.guest.transaction(report,lambda:None,lambda:self.fail('unexpected recovery'))
  self.assertEqual(report['status'],'OVERLAY_INSTALLED_NO_AUTH_ACCEPTANCE')
 def test_no_real_auth_or_log_suppression(self):
  code=(HERE/'guest.py').read_text()
  for bad in ['session.start','curl','truncate(', 'logger.ini\').write','systemctl disable']:self.assertNotIn(bad,code)
if __name__=='__main__':unittest.main()

import copy,json,unittest
from unittest import mock
import run_r2 as r
import test_freeze
class R2Tests(unittest.TestCase):
 def report(self):
  row,_=test_freeze.Tests().inputs();row['sources_before']=row['sources_after']=r.EXPECTED_SOURCES;return row
 def test_positive_projection(self):
  row=self.report();out=r.observed_projection(row);self.assertEqual(out['fixture']['entry_version'],7);self.assertEqual(out['asset_version'],'2')
 def test_unknown_is_observed_not_faked(self):
  row=self.report();row.update(fixture=None,entry_version_status='UNRESOLVED');row['version_observations']=row['version_observations'][:2]
  out=r.observed_projection(row);self.assertIsNone(out['fixture']);self.assertEqual(out['entry_version_status'],'UNRESOLVED')
 def test_unresolved_bad_schema_rejected(self):
  for change in ('bool','match','profile','privacy'):
   row=self.report();row.update(fixture=None,entry_version_status='UNRESOLVED')
   row['version_observations'][-1]['outcome']='API_REJECTED'
   if change=='bool':row['version_observations'][1]['requested']=False
   if change=='match':row['version_observations'][-1]['outcome']='TYPED_PROJECTION_MATCH'
   if change=='profile':row['profile']['selected_profile_id']='SYNTHETIC_SECRET'
   if change=='privacy':row['media_privacy']['files']['counts']=[1,0]
   self.assertRaises(Exception,r.observed_projection,row)
 def test_reuse_program_no_creation_strict_guards(self):
  self.assertNotIn('mkdir',r.REMOTE_GUARD);self.assertIn('s.st_nlink==1',r.REMOTE_GUARD);self.assertIn('==0o444',r.REMOTE_GUARD);self.assertIn('hashlib.sha256(p.read_bytes()).hexdigest()==pin',r.REMOTE_GUARD);self.assertIn('baseline-freeze-a60d5c60.service',r.REMOTE_GUARD)
 def test_reuse_actual_file_mutations_rejected(self):
  import tempfile,pathlib,os,stat,hashlib,types
  code=r.REMOTE_GUARD[r.REMOTE_GUARD.index("pins={"):r.REMOTE_GUARD.index("old=subprocess")]
  original=pathlib.Path.lstat
  def root_metadata(path):
   st=original(path);return types.SimpleNamespace(st_mode=st.st_mode,st_uid=0,st_gid=0,st_nlink=st.st_nlink)
  for defect in (None,'bytes','mode','extra','symlink'):
   with tempfile.TemporaryDirectory() as d:
    stage=pathlib.Path(d)
    for name in r.PINS:
     (stage/name).write_bytes((r.HERE/name).read_bytes());(stage/name).chmod(0o444)
    if defect=='bytes':(stage/'guest.py').chmod(0o644);(stage/'guest.py').write_bytes(b'CHANGED');(stage/'guest.py').chmod(0o444)
    if defect=='mode':(stage/'guest.py').chmod(0o644)
    if defect=='extra':(stage/'extra').write_bytes(b'x')
    if defect=='symlink':(stage/'guest.py').unlink();(stage/'guest.py').symlink_to(stage/'observation.py')
    with mock.patch.object(pathlib.Path,'lstat',root_metadata):
     scope={'stage':stage,'stat':stat,'os':os,'hashlib':hashlib}
     if defect is None:exec(code,scope)
     else:self.assertRaises(AssertionError,exec,code,scope)
 def test_exit_retained_when_projection_rejects(self):
  import tempfile,pathlib
  with tempfile.TemporaryDirectory() as tmp,mock.patch.object(r,'check',return_value=({},{})),mock.patch.object(r,'bounded',side_effect=[(7,b'NOT_JSON',9),(0,b'',0),(3,b'inactive\n',0)]):
   p=pathlib.Path(tmp)/'out';r.main(False,str(p));v=json.loads((p/'result.json').read_text());self.assertEqual(v['guest_exit'],7);self.assertEqual(v['stdout_bytes'],8);self.assertEqual(v['failure_stage'],'PUBLIC_PROJECTION');self.assertTrue(v['unit_inactive'])
 def test_unknown_nested_private_omitted(self):
  row=self.report();row['unexpected']={'body':'SYNTHETIC_SECRET'};out=r.public_rows((json.dumps(row)+'\n').encode());self.assertNotIn('SYNTHETIC_SECRET',json.dumps(out))
if __name__=='__main__':unittest.main()

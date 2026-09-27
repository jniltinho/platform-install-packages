import hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import verify
class Tests(unittest.TestCase):
 def stage(self,d):
  root=Path(d);(root/'x.php').write_bytes(b'fixture')
  m={'files':{'x.php':verify.sha(b'fixture')},'runtime_files':{'/synthetic/runtime':'0'*64}}
  raw=json.dumps(m).encode();(root/'runner-manifest.json').write_bytes(raw);return root,verify.sha(raw)
 def test_exact_stage(self):
  with tempfile.TemporaryDirectory() as d:
   r,h=self.stage(d);self.assertEqual(verify.verify(r,h,False)['files'],{'x.php':verify.sha(b'fixture')})
 def test_drift(self):
  with tempfile.TemporaryDirectory() as d:
   r,h=self.stage(d);(r/'x.php').write_bytes(b'changed')
   with self.assertRaisesRegex(ValueError,'STAGE_DRIFT'):verify.verify(r,h,False)
 def test_extra_nested_manifest(self):
  with tempfile.TemporaryDirectory() as d:
   r,h=self.stage(d);(r/'nested').mkdir();(r/'nested/runner-manifest.json').write_bytes(b'foreign')
   with self.assertRaisesRegex(ValueError,'STAGE_DRIFT'):verify.verify(r,h,False)
 def test_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   r,h=self.stage(d);(r/'foreign').symlink_to(r/'x.php')
   with self.assertRaisesRegex(ValueError,'SYMLINK'):verify.verify(r,h,False)
 def test_manifest_pin(self):
  with tempfile.TemporaryDirectory() as d:
   r,h=self.stage(d)
   with self.assertRaisesRegex(ValueError,'MANIFEST_DRIFT'):verify.verify(r,'0'*64,False)
 def test_cohorts_and_modes(self):
  code=(HERE/'run.sh').read_text()
  for line in ['original74) src=original/original.php; engine=74; mode=before','display74) src=original/KalturaStatement.php; engine=74; mode=display','exp14statement83) src=exp14/original.php; engine=83; mode=before','display83) src=exp14/KalturaStatement.php; engine=83; mode=display']:
   self.assertIn(line,code)
  self.assertIn('"/audit/probe/$src" "$mode"',code)
 def test_lifecycle_isolated(self):
  start=(HERE/'start-db.sh').read_text();run=(HERE/'run.sh').read_text()
  for value in ['--no-defaults','--skip-networking','--auth-root-authentication-method=socket','php83-display-sql-','kaltura-display-sql.']:self.assertIn(value,start)
  for value in ['PrivateNetwork=yes','RestrictAddressFamilies=AF_UNIX','ProtectSystem=strict','-/opt/kaltura','-/run/mysqld','PHP83_PROBE_DATADIR','verify || exit 70']:self.assertIn(value,run)
 def test_collector_retains_finally_and_no_error_values(self):
  code=(HERE/'observe.py').read_text()
  for value in ['for cohort in COHORTS','finally:','post_source_error_type','runtime_after','INCOMPLETE','OBSERVED_NOT_ACCEPTED','TimeoutExpired','systemctl stop']:self.assertIn(value,code)
  self.assertNotIn("'message':str(e)",code)
if __name__=='__main__':unittest.main()

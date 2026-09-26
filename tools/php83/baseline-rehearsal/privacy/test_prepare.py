import importlib.util,unittest,tempfile,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('privacy_prepare',HERE/'prepare.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
SOURCE=Path('/home/nilton/Projetos/nilton/NOVOS/kaltura-rigel-18.20.0-source/server-Rigel-18.20.0')
class PrepareTests(unittest.TestCase):
 def test_three_known_targets(self):self.assertEqual(len(p.TARGETS),3);self.assertEqual(len(set(p.TARGETS)),3)
 def test_unknown_target(self):
  with self.assertRaises(ValueError):p.transform('wrong',b'x')
 def test_anchor_drift(self):
  with self.assertRaises(ValueError):p.transform(p.TARGETS[1],b'changed')
 def test_second_application_refused(self):
  for target in p.TARGETS:
   modified=p.transform(target,(SOURCE/target).read_bytes())
   with self.assertRaises(ValueError):p.transform(target,modified)
 def test_all_original_delta_replays_strictly(self):
  for target in p.TARGETS:
   raw=(SOURCE/target).read_bytes();after=p.transform(target,raw);p.strict_replay(target,raw,p.patch_bytes(target,raw,after),after)
 def test_front_only_log_copies_changed(self):
  raw=(SOURCE/p.TARGETS[1]).read_bytes();after=p.transform(p.TARGETS[1],raw)
  restored=after.replace(b'KalturaLog::paramsForLog($this->params)',b'$this->params').replace(b'KalturaLog::sensitiveValueForLog(kCurrentContext::$ks)',b'kCurrentContext::$ks')
  self.assertEqual(restored,raw)
 def test_dispatch_actual_arguments_not_assigned(self):
  raw=(SOURCE/p.TARGETS[2]).read_bytes();after=p.transform(p.TARGETS[2],raw)
  self.assertEqual(after.replace(b'KalturaLog::argumentsForLog($this->arguments, $actionParams)',b'$this->arguments'),raw)
 def test_no_log_level_or_exception_changes(self):
  for target in p.TARGETS:
   raw=(SOURCE/target).read_bytes();after=p.transform(target,raw)
   for marker in [b'KalturaLog::err($ex)',b'KalturaLog::crit($ex)',b'KalturaLog::alert($ex)',b'self::$_logger->log($message, self::DEBUG)']:
    self.assertEqual(after.count(marker),raw.count(marker))
 def test_bad_archive_pin_before_reading_zip(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'bad.zip';path.write_bytes(b'not a zip')
   with self.assertRaisesRegex(ValueError,'Archive drift'):p.archive(path,'0'*64)
 def test_existing_output_refused_before_archives(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(ValueError,'existing'):p.prepare('bad','bad',tmp)
 def test_wrong_replay_result_rejected(self):
  raw=b'abc\n';after=b'def\n'
  with self.assertRaises(ValueError):p.strict_replay('a.php',raw,p.patch_bytes('a.php',raw,after),b'wrong')
 def test_helper_no_clone_serialize_or_eval(self):
  code=(HERE/'log-copy-methods.php.inc').read_text()
  for token in ['clone $','serialize(','eval(','__get(']:self.assertNotIn(token,code)
 def test_actual_pinned_archives_end_to_end_composition(self):
  root=HERE.parents[3]
  original=Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip')
  exp12=root.parent/'platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip'
  with tempfile.TemporaryDirectory(prefix='privacy-prepare-test-') as tmp:
   out=Path(tmp)/'fresh';m=p.prepare(original,exp12,out)
   self.assertEqual(len(m['targets']),6)
   self.assertEqual(m['status'],'PREPARED_NOT_SELECTED_NOT_DEPLOYED')
   for path in p.TARGETS:
    baseline=(out/'baseline74-policy/source'/path).read_bytes();candidate=(out/'exp12-policy/source'/path).read_bytes()
    candidate=candidate.replace(b"strtr($value ?? '',",b"strtr($value,").replace(b"((kCurrentContext::$uid ? kCurrentContext::$uid : kCurrentContext::$ks_uid) ?? '')",b"(kCurrentContext::$uid ? kCurrentContext::$uid : kCurrentContext::$ks_uid)")
    self.assertEqual(baseline,candidate)
if __name__=='__main__':unittest.main()

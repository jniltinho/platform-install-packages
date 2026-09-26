import importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('audit',HERE/'run.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
class Tests(unittest.TestCase):
 def test_pinned_payload_local_only(self):
  with patch.object(r.subprocess,'run',side_effect=AssertionError):data=r.payload()
  self.assertEqual(len(data['sources']),16);self.assertEqual(set(data['runtime']),set(r.RUNTIME))
 def test_four_targets_present(self):
  self.assertTrue({'infra/log/KalturaLog.php','infra/log/KalturaSerializableStream.php','api_v3/lib/KalturaFrontController.php','api_v3/lib/KalturaDispatcher.php'}.issubset(r.SOURCES))
 def test_no_raw_config_export(self):
  s=(HERE/'logger.php').read_text()
  self.assertNotIn('json_encode($map)',s);self.assertNotIn('json_encode($config)',s);self.assertIn('DISK_LOGGER_RESOLUTION_ONLY_NOT_LIVE_CACHE_ATTESTATION',s)
 def test_no_factory_bootstrap_or_cache_execution(self):
  s=(HERE/'logger.php').read_text()
  for item in ['InitLogger(', 'getLogger(', 'bootstrap.php', 'kConf::', 'apc_fetch(', 'new KalturaSerializableStream']:
   self.assertNotIn(item,s)
 def test_guest_no_writes(self):
  s=(HERE/'guest.py').read_text()
  for token in ['write_text','write_bytes','mkdir','unlink','chmod','systemctl','curl']:self.assertNotIn(token,s)
 def test_guest_guards(self):
  s=(HERE/'guest.py').read_text()
  for token in ['kaltura-php74-baseline','192.168.56.20','st_nlink==1','sources_unchanged_after','runtime_unchanged_after']:self.assertIn(token,s)
if __name__=='__main__':unittest.main()

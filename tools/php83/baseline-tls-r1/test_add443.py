import json,ssl,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
import add443 as m

class Tests(unittest.TestCase):
 def test_config(self):
  c=m.config();self.assertIn(b'Listen 192.168.56.74:443 https',c);self.assertNotIn(b'8443',c);self.assertNotIn(b'LoadModule',c)
  for field in ['server.crt','server.key','error.log','access.log']:self.assertIn(field.encode(),c)
  self.assertNotIn(b'/var/log',c)
 def test_ca_wrong_rejected(self):
  with patch.object(m,'handshake',side_effect=['TLSv1.3',ssl.SSLCertVerificationError()]):m.connections([443])
 def test_ca_wrong_accepted(self):
  with patch.object(m,'handshake',return_value='TLSv1.3'):
   with self.assertRaisesRegex(m.base.Rejected,'WRONG_CA_ACCEPTED'):m.connections([443])
 def test_wrong_target(self):
  with patch.object(m.os,'geteuid',return_value=1000):
   with self.assertRaisesRegex(m.base.Rejected,'TARGET'):m.target()
 def test_preflight_no_writes(self):
  with patch.object(m,'preflight',return_value=['*:80']),patch.object(m.base,'create') as create:
   self.assertEqual(m.main(False),0);create.assert_not_called()
 def exercise(self,failure):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);state=root/'state';available=root/'conf';enabled=root/'link'
   def read(p,pin=None):return p.read_bytes()
   with patch.multiple(m,STATE=state,AVAILABLE=available,ENABLED=enabled),patch.object(m,'preflight',return_value=['*:80']),patch.object(m,'existing'),patch.object(m.base,'read_public',side_effect=read),patch.object(m.base,'command',return_value=b''),patch.object(m,'post',side_effect=[m.base.Rejected('POST_FAILURE'),None] if failure else None):
    rc=m.main(True)
   receipt=json.loads((state/'terminal.json').read_text())
   self.assertEqual(rc,1 if failure else 0);self.assertEqual(available.exists(),not failure);self.assertEqual(enabled.exists(),not failure)
   self.assertFalse(receipt['full_acceptance']);self.assertEqual(receipt['rollback_complete'],failure)
 def test_execute_modeled(self):self.exercise(False)
 def test_failed_post_rollback(self):self.exercise(True)
 def test_occupied_state(self):
  with tempfile.TemporaryDirectory() as td:
   with patch.object(m,'STATE',Path(td)),patch.object(m,'preflight',return_value=['*:80']):
    with self.assertRaises(FileExistsError):m.main(True)
if __name__=='__main__':unittest.main()

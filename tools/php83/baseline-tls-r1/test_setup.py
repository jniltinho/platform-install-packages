import importlib.util,json,ssl,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import render
spec=importlib.util.spec_from_file_location('tls_setup',Path(__file__).with_name('setup.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT=Path(__file__).resolve().parents[3]
class Tests(unittest.TestCase):
 def ports(self):return json.loads((ROOT/'doc/php83/evidence/baseline-host-context-r1/tls-ports-public.json').read_text())['public_content'].encode()
 def test_exact_ports(self):
  before=self.ports();after=render.ports_after(before);self.assertIn(b'Listen 80',after);self.assertNotIn(b'Listen 443',after);self.assertEqual(after.count(b'dedicated .74:8443'),2)
  with self.assertRaisesRegex(ValueError,'PORTS_PIN'):render.ports_after(before+b'\n')
 def test_listener_projection(self):
  self.assertEqual(s.tls_listeners(b'LISTEN 0 511 192.168.56.74:8443 0.0.0.0:*\n'),['192.168.56.74:8443'])
  self.assertEqual(s.tls_listeners(b'LISTEN 0 511 *:443 *:*\n'),['*:443'])
 def case(self,fail=False,wrong_ca=False):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);state=r/'state';ports=r/'ports.conf';av=r/'av.conf';en=r/'en.conf';ports.write_bytes(self.ports());original=ports.read_bytes();restarts=[];prints=[]
   def command(argv,timeout=30):
    if argv[:3]==['/usr/bin/systemctl','restart','apache2']:
     restarts.append(1)
     if fail and len(restarts)==1:raise s.Rejected('COMMAND_FAILED')
    if 'is-active' in argv:return b'active\n'
    if argv[0]=='/usr/bin/ss':return b'LISTEN 0 511 192.168.56.74:8443 0.0.0.0:*\n' if en.exists() else b''
    return b''
   def certs():(state/'ca.crt').write_text('public test')
   def handshake(ca):
    if ca is None and not wrong_ca:raise ssl.SSLCertVerificationError('synthetic')
    return 'TLSv1.3'
   pins={str(ports):render.PORTS_SHA}
   with patch.multiple(s,STATE=state,PORTS=ports,AVAILABLE=av,ENABLED=en,LOGS=[r/'access.log',r/'error.log'],PINS=pins),patch.object(s,'preflight',return_value={str(ports):original}),patch.object(s,'read_public',side_effect=lambda p,pin=None:p.read_bytes()),patch.object(s,'command',side_effect=command),patch.object(s,'certificates',side_effect=certs),patch.object(s,'handshake',side_effect=handshake),patch.object(s.ssl,'PEM_cert_to_DER_cert',return_value=b'public-der'),patch.object(s.signal,'signal'),patch('builtins.print',side_effect=lambda v:prints.append(v)):
    rc=s.main(True)
   report=json.loads((state/'terminal.json').read_text());self.assertFalse(report['full_acceptance']);self.assertFalse(report['keys_exported']);self.assertTrue((state/'ports.conf.before').exists())
   if fail or wrong_ca:
    self.assertEqual(rc,1);self.assertTrue(report['rollback_complete']);self.assertEqual(ports.read_bytes(),original);self.assertFalse(en.exists());self.assertFalse(av.exists())
   else:
    self.assertEqual(rc,0);self.assertTrue(en.is_symlink());self.assertEqual(ports.read_bytes(),render.ports_after(original));self.assertTrue(report['wrong_ca_rejected']);self.assertNotIn('public test',str(prints))
 def test_modeled_success(self):self.case()
 def test_modeled_restart_failure_rollback(self):self.case(fail=True)
 def test_modeled_wrong_ca_rollback(self):self.case(wrong_ca=True)
 def test_create_exclusive(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x';s.create(p,b'original',0o600)
   with self.assertRaises(FileExistsError):s.create(p,b'changed',0o600)
   self.assertEqual(p.read_bytes(),b'original')
if __name__=='__main__':unittest.main()

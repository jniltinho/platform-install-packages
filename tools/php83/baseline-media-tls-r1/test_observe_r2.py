import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import observe_r2 as m
class Tests(unittest.TestCase):
 def test_shape(self):
  x=m.shape(b'include /opt/kaltura/nginx/conf/ssl.conf;\ninclude server.conf;\nlisten 8444 ssl;\n')
  self.assertEqual(x['include_ssl_exact'],1);self.assertEqual(x['include_server_exact'],1);self.assertEqual(x['tls_listen_count'],1)
 def test_no_raw(self):
  x=m.shape(b'#secret\nproxy_set_header X secret;\ninclude /private/secret;\n')
  self.assertNotIn('secret',str(x));self.assertEqual(x['include_count'],1)
 def test_ports(self):
  x=m.listeners(b'LISTEN 0 511 0.0.0.0:88 0.0.0.0:*\nLISTEN 0 511 192.168.56.74:443 0.0.0.0:*\n')
  self.assertEqual(x['88'],['WILDCARD']);self.assertEqual(x['443'],['TARGET']);self.assertEqual(x['8444'],[])
 def test_bad_ports(self):
  with self.assertRaises(m.Rejected):m.listeners(b'secret')
 def test_read_nofollow(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x';p.write_bytes(b'abc');l=Path(t)/'l';l.symlink_to(p)
   self.assertEqual(m.read(p,3),b'abc')
   with self.assertRaises(m.Rejected):m.read(p,2)
   with self.assertRaises(OSError):m.read(l,3)
 def test_config_link(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'conf';p.mkdir();(p/'kaltura.conf').write_bytes(b'')
   (p/'server.conf').symlink_to('kaltura.conf')
   with patch.object(m,'BASE',t):
    x=m.config('server.conf');self.assertEqual(x['resolved_fixed_target'],'kaltura.conf');self.assertEqual(x['sha256'],hashlib.sha256(b'').hexdigest())
    (p/'server.conf').unlink();(p/'server.conf').symlink_to('/etc/passwd')
    with self.assertRaises(m.Rejected):m.config('server.conf')
 def test_metadata_no_read(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'key';p.write_bytes(b'synthetic-private-key')
   x=m.metadata(p);self.assertNotIn('sha',str(x));self.assertNotIn('synthetic',str(x));self.assertEqual(x['kind'],'regular')
 def test_combined_pem_rejected(self):
  cert=b'-----BEGIN CERTIFICATE-----\nYWJj\n-----END CERTIFICATE-----\n'
  self.assertEqual(m.public_cert_hash(cert),hashlib.sha256(cert).hexdigest())
  for raw in (cert+b'-----BEGIN PRIVATE KEY-----\nYWJj\n-----END PRIVATE KEY-----',b'not a cert'):
   with self.assertRaises(m.Rejected):m.public_cert_hash(raw)
 def test_key_never_read(self):
  cert=b'-----BEGIN CERTIFICATE-----\nYWJj\n-----END CERTIFICATE-----\n';seen=[]
  def reader(path,cap):
   self.assertFalse(str(path).endswith('server.key'));seen.append(str(path));return cert
  with patch.object(m,'metadata',side_effect=lambda p:{'kind':'regular'}),patch.object(m,'read',side_effect=reader):
   out=m.certificate_metadata()
  self.assertEqual(len(seen),2);self.assertNotIn('public_pem_sha256',out['server.key'])
 def test_wrong_target(self):
  with patch.object(m.socket,'gethostname',return_value='other'),patch.object(m.os,'geteuid',return_value=0),patch.object(m,'command') as c:
   with self.assertRaises(m.Rejected):m.observe()
   c.assert_not_called()
if __name__=='__main__':unittest.main()

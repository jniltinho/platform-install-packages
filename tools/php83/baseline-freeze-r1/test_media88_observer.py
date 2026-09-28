import json,unittest
from unittest.mock import patch
import media88_observer as m
class Tests(unittest.TestCase):
 def test_http_listen_shape(self):
  v=m.config_shape(b'listen 88; # SECRET\nssl_certificate /PRIVATE;\ninclude private;')
  self.assertEqual(v['listen88_count'],1);self.assertEqual(v['listen88_ssl_count'],0);self.assertNotIn('PRIVATE',json.dumps(v));self.assertFalse(v['configuration_effective_proven'])
 def test_tls_comments(self):
  v=m.config_shape(b'# listen 88 ssl;\nlisten 192.168.56.74:88 ssl; listen 888;')
  self.assertEqual(v['listen88_count'],1);self.assertEqual(v['listen88_ssl_count'],1)
 def test_status_only(self):
  self.assertEqual(m.status_line(b'HTTP/1.1 404 SECRET\r\n'),404)
  for x in [b'SECRET',b'HTTP/1.1 999 private',b'x'*1025]:self.assertIsNone(m.status_line(x))
 def test_no_transport_on_import(self):self.assertEqual(len(m.CONFIGS),4)
if __name__=='__main__':unittest.main()

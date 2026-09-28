import unittest
import render
class Tests(unittest.TestCase):
 def test_fixed_listener(self):
  self.assertIn('Listen 192.168.56.74:8443 https',render.config());self.assertNotIn('Listen 443',render.config());self.assertNotIn('<VirtualHost *',render.config())
 def test_native_include(self):self.assertIn('/opt/kaltura/app/configurations/apache/conf.d/enabled.*.conf',render.config())
 def test_modern_tls(self):
  self.assertIn('SSLProtocol -all +TLSv1.2 +TLSv1.3',render.config());self.assertNotIn('verifySSL=0',render.config())
 def test_private_keys_public_logs(self):
  self.assertIn('/var/lib/kaltura-baseline-tls-r1/server.key',render.config());self.assertIn('/var/log/apache2/baseline_tls_r1_error.log',render.config());self.assertNotIn('%r',render.config());self.assertNotIn('User-Agent',render.config())
 def test_ca_and_san(self):
  self.assertIn('pathlen:0',render.ca_extensions());self.assertIn('CA:FALSE',render.leaf_extensions());self.assertIn('subjectAltName=IP:192.168.56.74',render.leaf_extensions());self.assertIn('serverAuth',render.leaf_extensions())
if __name__=='__main__':unittest.main()

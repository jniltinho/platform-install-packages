import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import install as m
class Tests(unittest.TestCase):
 def test_render_scope(self):
  s=m.config().decode();self.assertIn('192.168.56.74:8444 ssl;',s);self.assertNotIn('listen 88',s);self.assertNotRegex(s,r'\$request(?:[^_a-zA-Z]|$)');self.assertIn('include /opt/kaltura/nginx/conf/server.conf;',s);self.assertIn('ssl_protocols TLSv1.2 TLSv1.3;',s)
 def test_frozen_closure(self):self.assertEqual(set(m.CONFIG_PINS),set(m.obs.CONFIGS));self.assertEqual(m.CONFIG_PINS['ssl.conf'],m.hashlib.sha256(b'').hexdigest())
 def test_metadata(self):
  row={'kind':'regular','uid':0,'gid':0,'mode':'0644','nlink':1,'xattrs_present':False};self.assertTrue(m.metadata_ok(row,'0644'))
  for k,v in [('uid',1),('gid',1),('mode','0664'),('nlink',2),('kind','symlink'),('xattrs_present',True)]:
   self.assertFalse(m.metadata_ok(dict(row,**{k:v}),'0644'))
 def test_preflight_only(self):
  with patch.object(m,'preflight',return_value=({},12)),patch.object(m,'create') as c:
   self.assertEqual(m.main(False)['status'],'MEDIA_TLS8444_PREFLIGHT_ONLY');c.assert_not_called()
 def test_target_failure_no_create(self):
  with patch.object(m,'preflight',side_effect=m.obs.Rejected('TARGET')),patch.object(m,'create') as c:
   with self.assertRaises(m.obs.Rejected):m.main(True)
   c.assert_not_called()
 def test_tls_context(self):
  with patch.object(m.ssl,'create_default_context') as c,patch.object(m.socket,'create_connection') as s:
   c.return_value.wrap_socket.return_value.__enter__.return_value.version.return_value='TLSv1.3';m.handshake(8444,'/publicca');c.assert_called_once_with(cafile='/publicca');self.assertEqual(s.call_args.args[0],('192.168.56.74',8444))
 def test_reload_pidfd(self):
  with patch.object(m.os,'pidfd_open',return_value=99),patch.object(m,'process',return_value=123),patch.object(m.signal,'pidfd_send_signal') as s,patch.object(m.os,'close') as c:
   m.reload_master(123);s.assert_called_once_with(99,m.signal.SIGHUP);c.assert_called_once_with(99)
 def test_reload_wrong_process(self):
  with patch.object(m.os,'pidfd_open',return_value=99),patch.object(m,'process',return_value=124),patch.object(m.signal,'pidfd_send_signal') as s,patch.object(m.os,'close'):
   with self.assertRaises(m.obs.Rejected):m.reload_master(123)
   s.assert_not_called()
 def test_failure_before_replace_preserves_state(self):
  with tempfile.TemporaryDirectory() as t:
   state=Path(t)/'state'
   with patch.object(m,'STATE',state),patch.object(m,'preflight',return_value=({},12)),patch.object(m,'metadata_ok',return_value=True),patch.object(m,'replace_ssl',side_effect=m.obs.Rejected('SSL_DRIFT')),patch.object(m.obs,'command',return_value=b''),patch.object(m,'check_ports'),patch.object(m.signal,'signal'):
    r=m.main(True);self.assertEqual(r['failure_code'],'SSL_DRIFT');self.assertTrue(r['rollback_complete']);self.assertTrue((state/'terminal.json').exists());self.assertEqual(json.loads((state/'terminal.json').read_text())['status'],'MEDIA_TLS8444_FAILED')
 def test_success_receipt_failure_rolls_back(self):
  with tempfile.TemporaryDirectory() as t:
   state=Path(t)/'state';ssl=Path(t)/'ssl.conf';ssl.write_bytes(b'');original_create=m.create;writes=[]
   def create(path,data,mode):
    if path.name=='terminal.json' and not writes:
     writes.append('failed');raise OSError('synthetic disk failure')
    return original_create(path,data,mode)
   def replace(old,new):
    self.assertEqual(ssl.read_bytes(),old);ssl.write_bytes(new);st=ssl.stat();return(st.st_dev,st.st_ino)
   with patch.object(m,'STATE',state),patch.object(m,'SSL',ssl),patch.object(m,'preflight',return_value=({},12)),patch.object(m,'metadata_ok',return_value=True),patch.object(m,'create',side_effect=create),patch.object(m,'replace_ssl',side_effect=replace),patch.object(m,'observe_check'),patch.object(m.obs,'command',return_value=b''),patch.object(m,'check_ports'),patch.object(m,'reload_master') as reload,patch.object(m,'handshake',side_effect=[None,None,None,m.ssl.SSLCertVerificationError('synthetic')]),patch.object(m.signal,'signal'):
    result=m.main(True)
   self.assertEqual(result['status'],'MEDIA_TLS8444_FAILED');self.assertTrue(result['rollback_complete']);self.assertEqual(ssl.read_bytes(),b'');self.assertEqual(reload.call_count,2)
   self.assertEqual(json.loads((state/'terminal.json').read_text())['status'],'MEDIA_TLS8444_FAILED')
 def test_log_inheritance_source(self):
  raw=(Path(__file__).resolve().parents[3]/'deb/kaltura-nginx/debian/base.conf').read_bytes();self.assertEqual(m.hashlib.sha256(raw).hexdigest(),m.CONFIG_PINS['base.conf'])
  logs=[s.strip() for s in raw.splitlines() if b'access_log' in s];self.assertEqual(logs,[b'access_log off;',b'access_log off;'])
if __name__=='__main__':unittest.main()

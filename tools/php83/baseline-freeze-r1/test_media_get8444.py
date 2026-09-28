import unittest,pathlib,sys,base64,json,types
from unittest.mock import patch
H=pathlib.Path(__file__).parent;old=list(sys.path);sys.path.insert(0,str(H.parent/'baseline-protocol'))
import media_get8444 as m
sys.path[:]=old
URL='https://192.168.56.74:8444/hls/public/index.m3u8'
class Tests(unittest.TestCase):
 def test_exact_origin_only(self):
  m.validate(URL,{'Accept-Encoding':'identity'},65536)
  for u in ('https://192.168.56.74/hls/x','https://192.168.56.74:443/x','https://192.168.56.74:8443/x','https://192.168.56.74:88/x','https://192.168.56.74:0/x','https://192.168.56.83:8444/x','http://192.168.56.74:8444/x',URL+'?',URL+'#',URL+'?ks=SYNTHETIC_SECRET',URL+'\nX'):
   with self.assertRaises(Exception):m.validate(u,{'Accept-Encoding':'identity'},1024)
  for args in (('192.168.56.83','https',8444),('192.168.56.74','http',8444),('192.168.56.74','https',443)):
   with self.assertRaises(Exception):m.MediaOrigin8444(*args)
 def test_original_origin_not_relaxed(self):
  with self.assertRaises(Exception):m.Origin('192.168.56.74','https',8444)
 def test_credentials_headers_caps(self):
  for h in ({'Accept-Encoding':'identity','Authorization':'SYNTHETIC_SECRET'},{'Accept-Encoding':'gzip'},{'Accept-Encoding':'identity','Range':'bytes=0-1\r\nX:s'}):
   with self.assertRaises(Exception):m.validate(URL,h,1024)
  for n in (True,0,m.MAX_BODY+1):
   with self.assertRaises(Exception):m.validate(URL,{'Accept-Encoding':'identity'},n)
  with self.assertRaises(Exception):m.request(b'wrongCA',URL,{'Accept-Encoding':'identity'},1024)
 def test_pairs_deadline_and_private_body(self):
  envelope={'status':200,'headers':[['X','a'],['X','b']],'body':base64.b64encode(b'ab').decode()}
  with patch.object(m,'Client'),patch.object(m.deadline,'_bounded',return_value=json.dumps(envelope).encode()) as run:
   self.assertEqual(m.request(b'fixture',URL,{'Accept-Encoding':'identity'},2),(200,envelope['headers'],b'ab'));self.assertEqual(run.call_args.kwargs,{'limit':m.IPC_LIMIT,'deadline':30})
 def test_failures_no_secret_or_redirect(self):
  state=types.SimpleNamespace(value=-1);buf=bytearray(m.IPC_LIMIT)
  with patch.object(m,'Client',side_effect=RuntimeError('SYNTHETIC_SECRET')):m._worker(b'x',URL,{'Accept-Encoding':'identity'},2,buf,state)
  self.assertEqual(state.value,-2);self.assertNotIn(b'SYNTHETIC_SECRET',buf)
  with patch.object(m,'Client'),patch.object(m.deadline,'_bounded',return_value=b'{"status":302,"headers":[],"body":""}'):
   with self.assertRaises(Exception):m.request(b'x',URL,{'Accept-Encoding':'identity'},2)
if __name__=='__main__':unittest.main()

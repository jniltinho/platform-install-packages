import base64,json,pathlib,sys,types,unittest
from unittest.mock import patch
H=pathlib.Path(__file__).parent;old=list(sys.path);sys.path.insert(0,str(H.parent/'baseline-protocol'))
import media_get as m
sys.path[:]=old
URL='https://192.168.56.74:8443/private/synthetic'
class MediaGetTests(unittest.TestCase):
 def test_fixed_origin_headers_bounds(self):
  m.validate(URL,{'Accept-Encoding':'identity','Range':'bytes=0-1023'},1024)
  for url in ('http://192.168.56.74/x','https://192.168.56.20:8443/x','https://192.168.56.74:8444/x',URL+'\nX',URL+'\\x'):
   self.assertRaises(Exception,m.validate,url,{'Accept-Encoding':'identity'},1024)
  for h in ({},{'Accept-Encoding':'gzip'},{'Accept-Encoding':'identity','Authorization':'secret'},{'Accept-Encoding':'identity','Range':'bytes=0-1\r\nX:x'}):self.assertRaises(Exception,m.validate,URL,h,1024)
  for limit in (True,0,m.MAX_BODY+1):self.assertRaises(Exception,m.validate,URL,{'Accept-Encoding':'identity'},limit)
 def test_pinned_ca_required(self):self.assertRaises(Exception,m.request,b'wrong',URL,{'Accept-Encoding':'identity'},1024)
 def test_private_envelope_preserves_pairs_deadline(self):
  envelope={'status':206,'headers':[['X-Test','a'],['X-Test','b']],'body':base64.b64encode(b'ab').decode()}
  with patch.object(m,'Client'),patch.object(m.deadline,'_bounded',return_value=json.dumps(envelope).encode()) as bounded:
   self.assertEqual(m.request(b'fixture',URL,{'Accept-Encoding':'identity'},2),(206,envelope['headers'],b'ab'));self.assertEqual(bounded.call_args.kwargs,{'limit':m.IPC_LIMIT,'deadline':30})
 def test_reject_malformed_or_oversized_ipc(self):
  for v in ({'status':302,'headers':[],'body':''},{'status':200,'headers':{},'body':''},{'status':200,'headers':[],'body':base64.b64encode(b'abc').decode()},{'status':200,'headers':[],'body':'!!!'}):
   with patch.object(m,'Client'),patch.object(m.deadline,'_bounded',return_value=json.dumps(v).encode()):self.assertRaises(Exception,m.request,b'x',URL,{'Accept-Encoding':'identity'},2)
 def test_worker_never_exports_exception(self):
  state=types.SimpleNamespace(value=-1);buffer=bytearray(m.IPC_LIMIT)
  with patch.object(m,'Client',side_effect=RuntimeError('SYNTHETIC_SECRET')):m._worker(b'x',URL,{'Accept-Encoding':'identity'},2,buffer,state)
  self.assertEqual(state.value,-2);self.assertNotIn(b'SYNTHETIC_SECRET',buffer)
if __name__=='__main__':unittest.main()

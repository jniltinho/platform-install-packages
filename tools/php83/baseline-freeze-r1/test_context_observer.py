import hashlib,pathlib,unittest
import context_urls as u
import prepare_context_observer as p
import run_context_observer as r
H=pathlib.Path(__file__).parent
class Tests(unittest.TestCase):
 def test_enroll_candidates(self):
  tokens=[];u.enroll('https://192.168.56.74/path/abcdefghijklmnop?token=qrstuvwxyz012345',tokens)
  self.assertEqual(tokens,['abcdefghijklmnop','qrstuvwxyz012345'])
 def test_shortquery_explicit_incomplete(self):
  for url in ['https://a/path?token=short','https://a/ks/short','https://user:password@a/path','https://a/path#fragment']:
   with self.assertRaisesRegex(u.Incomplete,'URL_ENROLLMENT_INCOMPLETE'):u.enroll(url,[])
 def test_limits_preserve_prior(self):
  tokens=[str(i).zfill(16) for i in range(34)]
  with self.assertRaises(u.Incomplete):u.enroll('https://a/abcdefghijklmnop',tokens)
  self.assertEqual(len(tokens),34)
 def test_decode_private_never_returns(self):
  tokens=[];self.assertIsNone(u.enroll('https://a/%61bcdefghijklmnop',tokens));self.assertEqual(tokens,['abcdefghijklmnop'])
 def test_generator_single_call_no_get(self):
  s=p.build();self.assertEqual(s,(H/'guest_context_observer.py').read_text());compile(s,'context','exec')
  self.assertEqual(s.count('context.observe('),1);self.assertNotIn("action='getUrl'",s);self.assertNotIn('delivery.progressive(',s);self.assertNotIn('media_get443.request(',s);self.assertNotIn('rehearsal.run(',s)
  self.assertIn('convergence.run(lambda:audit_once(patterns,start,jstart)',s);self.assertIn('audit_all(rehearsal.patterns(secret,ks,tracked_tokens),start,jstart)',s)
 def test_host_pins_and_projection(self):
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),pin)
  v={'case':'NATIVE_HLS_CONTEXT_NO_GET','api_calls':1,'sources':1,'original_https_hls_descriptors':1,'actions':0,'messages':0,'flavor_assets':0,'response_secret_coverage_complete':False,'delivery_authorized':False,'hls_fetched':False,'decoded':False,'full_acceptance':False}
  self.assertEqual(r.context_projection(v),v)
  for k,value in [('sources',True),('url','SECRET'),('delivery_authorized',True),('original_https_hls_descriptors',2)]:
   x=dict(v);x[k]=value;self.assertRaises(Exception,r.context_projection,x)
  self.assertIn('baseline-freeze-b1174826.service',r.REMOTE_GUARD)
 def test_exact_reviewed_module(self):self.assertEqual(hashlib.sha256((H/'playback_context_r3.py').read_bytes()).hexdigest(),'f0ec70528883e94a8d97ade697c58ff8588585c0814d06faddc948fabe436420')
if __name__=='__main__':unittest.main()

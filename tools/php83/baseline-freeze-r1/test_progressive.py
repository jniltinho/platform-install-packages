import ast,hashlib,pathlib,unittest
import run_progressive as r
import prepare_progressive as p
import url_privacy as u
H=pathlib.Path(__file__).parent
class ProgressiveTests(unittest.TestCase):
 def test_generate_pins(self):
  self.assertEqual(p.build(),(H/'guest_progressive.py').read_text())
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),pin)
 def test_no_round_and_no_upload(self):
  s=p.build();self.assertNotIn('protocol.run_round(',s);self.assertNotIn('metadata.collect(',s);self.assertIn("native_call(service='flavorasset',action='getUrl',id=delivery.ASSET)",s)
  self.assertLess(s.index('legacy.logs=lambda:tls_logs.extend(old_logs)'),s.index("report['phase']='invalid-nonce'"));self.assertLess(s.index('delivery.progressive(get,url)'),s.index("failure_stage='QUIET_SETTLE'"))
  self.assertIn('audit_all(rehearsal.patterns(secret,ks,tracked_tokens),start,jstart)',s)
 def test_native_url_no_credentials_encoded_or_query(self):
  secret='0123456789abcdef0123456789abcdef';ks='ABCDEFGHIJKLMNOPabcdefghijklmnop'
  for tail in ('/ks/'+ks,'/KS/independentTOKEN0123456789','/path?x=anything','/path#fragment','/'+secret,'/'+''.join('%%%02X'%ord(c) for c in ks),'/auth/x','/kt/x'):
   self.assertRaises(u.Rejected,u.inspect,'https://192.168.56.74:8443'+tail,secret,ks,[])
  self.assertEqual(u.inspect('https://192.168.56.74:8443/p/102/serveFlavor',secret,ks,[]),'https://192.168.56.74:8443/p/102/serveFlavor')
 def test_minted_token_enrolled_before_rejection(self):
  token='INDEPENDENT0123456789';values=[]
  self.assertRaises(u.Rejected,u.inspect,'https://192.168.56.74:8443/ks/'+token,'a'*32,'b'*32,values);self.assertIn(token,values)
 def test_closed_projection(self):
  v={'case':'ORIGINAL_PROGRESSIVE','requests':3,'bytes':1511134,'sha256':'612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473','range_checks':2,'decoded':False,'full_acceptance':False}
  self.assertEqual(r.progressive_projection(v),v)
  for key,val in [('url','SYNTHETIC_SECRET'),('decoded',True),('requests',True),('bytes',1)]:
   row=dict(v);row[key]=val;self.assertRaises(Exception,r.progressive_projection,row)
 def test_closed_url_shape_no_values(self):
  v=u.shape('http://192.168.56.74/ks/SYNTHETIC_SECRET?x=VALUE');self.assertEqual(v,{'scheme':'http','port':'80','target_host_match':True,'query_present':True,'credential_path':True});self.assertNotIn('SECRET',str(v));self.assertEqual(r.shape_projection(v),v)
  self.assertEqual(u.shape('https://192.168.56.74/path')['port'],'443')
  self.assertEqual(u.shape('https://192.168.56.74:8443/path')['port'],'8443')
  for extra in ({**v,'path':'PRIVATE'},{**v,'target_host_match':1},{**v,'scheme':'PRIVATE'}):self.assertRaises(Exception,r.shape_projection,extra)
 def test_failure_privacy_retained_without_raw_data(self):
  row={'failure_code':'DELIVERY_ORIGIN','failure_stage':'API_ROUND','native_url_shape':u.shape('http://192.168.56.74/x'),'media_failure_privacy':{'files':{'counts':[0,0],'status':'COMPLETE_FINITE_FILE_WINDOW','uncovered_tail_bytes':0},'journal':{'counts':[0,0],'status':'COMPLETE_FINITE_JOURNAL_WINDOW','cutoff_covered':True,'complete':True},'scope':'PRIVATE_WINDOW'}}
  self.assertTrue(r.failure_projection(row)['failure_privacy']['finite_scans_complete_and_zero'])
  row['media_failure_privacy']['files']['counts']=[1,0];self.assertFalse(r.failure_projection(row)['failure_privacy']['finite_scans_complete_and_zero'])
  self.assertNotIn('PRIVATE_WINDOW',str(r.failure_projection(row)))
 def test_fresh_no_webwrite_and_no_round_receipt(self):
  self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-short-progressive-r1');self.assertIn('baseline-freeze-a5549803.service',r.REMOTE_GUARD);self.assertIn('assert not os.path.lexists(stage)',r.REMOTE_GUARD)
  self.assertNotIn('api_v3/web',r.unit_command('baseline-freeze-12345678'));self.assertRaises(Exception,r.round_projection,{'untimed_round':{}})
if __name__=='__main__':unittest.main()

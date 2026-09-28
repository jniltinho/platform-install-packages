import unittest,json,hashlib,copy
from pathlib import Path
import hls_media8444 as m,hls_nested8444 as n,hls_response as response
import run_hls_media8444 as r,prepare_hls_media8444 as g,hls_context_proof as proof
import test_hls_first,test_context_capture
H=Path(__file__).parent
NESTED='https://192.168.56.74:8444/hls/p/102/sp/10200/serveFlavor/entryId/0_wzmt2sfy/v/2/flavorId/0_21p06l2j/name/a.mp4/index.m3u8'
class Tests(unittest.TestCase):
 def setUp(self):r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
 def case(self,target=NESTED):
  data=test_hls_first.Tests().data();data['sources'][0]['deliveryProfileId']=1004;data['sources'][0]['url']=data['sources'][0]['url'].replace('/deliveryProfileId/1/','/deliveryProfileId/1004/')
  asset=dict(id='0_21p06l2j',entryId='0_wzmt2sfy',partnerId=102,status=2,isOriginal=False,version=2,flavorParamsId=2,size=128,fileExt='mp4')
  gets=[];enrolled=[];diag={}
  def req1(url,h,l):gets.append(url);return 200,[],('#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=100\n'+target+'\n').encode()
  def req2(url,h,l):gets.append(url);return 200,[],b'#EXTM3U\n#EXTINF:10,\nseg-PRIVATE.ts\n#EXT-X-ENDLIST\n'
  return lambda:m.observe(lambda **kw:data,enrolled.append,req1,req2,'s'*48,'k'*80,asset,1004,lambda k,v:diag.update({k:v})),gets,enrolled,diag
 def test_exact_two_get_no_segments(self):
  run,gets,enrolled,diag=self.case();ctx,v=run();m.validate(v);self.assertEqual(len(gets),2);self.assertEqual(gets[-1],NESTED);self.assertEqual(v['segments_requested'],0);self.assertEqual(set(diag),{'MASTER','MEDIA'});self.assertNotIn('PRIVATE',json.dumps(diag));self.assertEqual(len(enrolled),2)
 def test_wrong_route_enrolled_before_no_second_get(self):
  for target in [NESTED.replace(':8444',':88'),NESTED+'?ks=syntheticprivatekey',NESTED.replace('/v/2/','/v/3/'),NESTED.replace('/name/a.mp4/','/unknown/a.mp4/')]:
   run,gets,enrolled,diag=self.case(target)
   with self.assertRaises(Exception):run()
   self.assertEqual(len(gets),1);self.assertEqual(enrolled,[target]);self.assertEqual(diag['MASTER']['status'],200)
 def test_nested_negative_and_optional(self):
  self.assertEqual(n.guard(NESTED.replace('/v/2/','/v/2/pv/4/ev/5/'),'s'*48,'k'*80),NESTED.replace('/v/2/','/v/2/pv/4/ev/5/'))
  for x in [NESTED+'#',NESTED.replace('8444','0'),NESTED.replace('/v/2/','/v/2/v/2/'),NESTED.replace('a.mp4','%61.mp4'),NESTED.replace('/v/2/','/v/2/pv/0/')]:self.assertRaises(n.Rejected,n.guard,x,'s'*48,'k'*80)
  self.assertRaises(n.Rejected,n.guard,NESTED,'0_21p06l2j/name/'+'z'*20,'k'*80)
 def test_response_validation_no_fake_url(self):
  self.assertEqual(response.validate((200,[('Content-Length','1')],b'x'))[1],b'x')
  for v in [(302,[],b'x'),(200,[('Location','PRIVATE')],b'x'),(200,[('Content-Length','1'),('Content-Length','1')],b'x')]:self.assertRaises(response.Rejected,response.validate,v)
 def row(self):
  row=test_context_capture.Tests().row();run,_,_,diag=self.case();ctx,v=run();row.update(playback_context=ctx,hls_media=v,hls_diagnostics=diag,split_receipt_sha256=r.PROOF_PIN,media_tls_logs_in_every_inventory=True);return row
 def test_full_public_success(self):
  row=self.row();row['secret_raw']='SYNTHETIC_SECRET';out=r.public_rows(json.dumps(row).encode())[0];self.assertEqual(out['hls_media']['profile_id'],1004);self.assertNotIn('SYNTHETIC_SECRET',json.dumps(out));self.assertNotIn('delivery_context_pair',out);self.assertNotIn('native_url_shape',out)
 def test_full_public_failures(self):
  for key in ('hls_media','hls_diagnostics','round_privacy','media_privacy','sources_after','media_tls_logs_in_every_inventory','split_receipt_sha256'):
   row=self.row();row.pop(key);self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
  for key,value in [('profile_id',1001),('requests',True),('full_acceptance',True),('raw','SECRET')]:
   row=self.row();row['hls_media'][key]=value;self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
 def test_failure_closed_diagnostic(self):
  run,_,_,diag=self.case();run();v={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_code':'HLS_MEDIA_REJECTED','failure_stage':'API_ROUND','hls_diagnostics':diag,'raw':'SECRET'}
  out=r.public_rows(json.dumps(v).encode())[0];self.assertEqual(set(out['hls_diagnostics']),{'MASTER','MEDIA'});self.assertNotIn('SECRET',json.dumps(out))
 def test_exact_actual_prerequisite(self):
  p=H.parents[2]/'doc/php83/evidence/baseline-freeze-r1/delivery-context-reconciliation-native-r2.json';v=json.loads(p.read_text());self.assertEqual(proof.receipt_id(v),1004);v['guest_exit']=2;self.assertRaises(proof.Rejected,proof.receipt_id,v)
 def test_generation_and_pins(self):
  self.assertEqual(g.build(),(H/'guest_hls_media8444.py').read_text())
  for name,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/name).read_bytes()).hexdigest(),pin)
  self.assertIn('baseline-freeze-7ef5461b.service',r.REMOTE_GUARD);self.assertIn('media_logs.extend(lambda:tls_logs.extend(old_logs))',g.build())
if __name__=='__main__':unittest.main()

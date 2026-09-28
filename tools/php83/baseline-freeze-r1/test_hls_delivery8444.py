import unittest,json,hashlib,ast,copy
from unittest.mock import patch
from pathlib import Path
import hls_delivery8444 as m,run_hls_delivery8444 as r,prepare_hls_delivery8444 as g
import test_hls_media8444 as base,test_hls_segments as seg,test_hls_media8444_r3 as before
H=Path(__file__).parent
DECODE={'case':'FETCHED_TS_FULL_LOCAL_DECODE','metadata':{'video_codec':'h264','audio_codec':'aac','width':640,'height':360,'video_frames':250,'fps_numerator':25,'fps_denominator':1,'duration_milliseconds':10000,'audio_sample_rate':44100,'audio_channels':2},'full_decode_verified':True,'dynamic_library_cohort_attested':False,'profile_golden_equivalence':False,'full_acceptance':False}
class Tests(unittest.TestCase):
 def setUp(self):r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
 def case(self,body=seg.BODY):
  import test_hls_first
  data=test_hls_first.Tests().data();data['sources'][0]['deliveryProfileId']=1004;data['sources'][0]['url']=data['sources'][0]['url'].replace('/deliveryProfileId/1/','/deliveryProfileId/1004/')
  asset=dict(id='0_21p06l2j',entryId='0_wzmt2sfy',partnerId=102,status=2,isOriginal=False,version=2,flavorParamsId=2,size=128,fileExt='mp4');calls=[];gets=[];diags={};segment_diags={};enrolled=[]
  def call(**form):calls.append(form);return data
  def master(url,h,l):gets.append(url);return 200,[],('#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=100\n'+base.NESTED+'\n').encode()
  def media(url,h,l):gets.append(url);return (200,[],body.encode()) if url==base.NESTED else (200,[],b'\x47'+b'\0'*187)
  run=lambda:m.observe(call,enrolled.append,master,media,'s'*48,'k'*80,asset,1004,lambda k,v:diags.update({k:v}),lambda k,v:segment_diags.update({k:v}))
  return run,calls,gets,diags,segment_diags,enrolled
 def test_one_context_seven_requests_private_decode(self):
  run,calls,gets,diags,sd,enrolled=self.case()
  with patch.object(m.decoder,'decode',return_value=copy.deepcopy(DECODE)) as decode:ctx,v=run()
  m.validate(v);self.assertEqual(len(calls),1);self.assertEqual(len(gets),7);self.assertEqual(sd['TRANSFER']['segments_received'],5);self.assertEqual(decode.call_args.args[0],(b'\x47'+b'\0'*187)*5)
 def test_bad_last_uri_rejects_before_any_segment(self):
  run,_,gets,_,sd,enrolled=self.case(seg.BODY.replace('seg-5-v1-a1.ts','seg-5-v2-a1.ts'))
  with self.assertRaises(m.Rejected):run()
  self.assertEqual(len(gets),2);self.assertFalse(sd['ROUTES']['references'][-1]['expected_sequence_tracks']);self.assertTrue(enrolled)
 def row(self):
  b=before.Tests();b.setUp();row=b.row();row.pop('hls_media');run,_,_,d,sd,_=self.case()
  with patch.object(m.decoder,'decode',return_value=copy.deepcopy(DECODE)):ctx,v=run()
  row.update(playback_context=ctx,hls_delivery=v,hls_diagnostics=d,hls_segment_diagnostics=sd);return row
 def test_full_public_success_not_media_only(self):
  row=self.row();row['private']='SECRET';out=r.public_rows(json.dumps(row).encode())[0];self.assertEqual(out['hls_delivery']['requests'],7);self.assertNotIn('SECRET',json.dumps(out));self.assertNotIn('hls_media',out)
 def test_full_public_failures(self):
  for k in ('hls_delivery','hls_segment_diagnostics','common_end_attempts','round_privacy','media_tls_logs_in_every_inventory','sources_after'):
   row=self.row();row.pop(k);self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
  row=self.row();row['hls_segment_diagnostics']['ROUTES']['references'].pop();self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
  row=self.row();row['hls_delivery']['decode']['metadata']['width']='SECRET';self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
 def test_failure_closed_routes_retained(self):
  run,_,_,d,sd,_=self.case(seg.BODY.replace('seg-5-v1-a1.ts','seg-5-v2-a1.ts'))
  try:run()
  except m.Rejected:pass
  row={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_code':'SEGMENT_ROUTE','failure_stage':'API_ROUND','hls_segment_diagnostics':sd,'hls_diagnostics':d,'private':'SECRET'}
  out=r.public_rows(json.dumps(row).encode())[0];self.assertNotIn('SECRET',json.dumps(out));self.assertEqual(len(out['hls_segment_diagnostics']['ROUTES']['references']),5)
 def test_actual_new_pin_loop_executes_before_import(self):
  tree=ast.parse(g.build());nodes=[n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Attribute) and isinstance(n.iter.func.value,ast.Dict) and any(isinstance(k,ast.Constant) and k.value=='hls_segments.py' for k in n.iter.func.value.keys)]
  self.assertEqual(len(nodes),1)
  def need(ok,code):
   if not ok:raise ValueError(code)
  exec(compile(ast.Module(body=nodes,type_ignores=[]),'real_guest_pin_loop','exec'),{'NEW_HERE':H,'hashlib':hashlib,'need':need})
 def test_regeneration_runtime_pins(self):
  self.assertEqual(g.build(),(H/'guest_hls_delivery8444.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertIn('baseline-freeze-6b33c740.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()

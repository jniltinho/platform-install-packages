import json,pathlib,hashlib,unittest
import hls_first as m
import prepare_hls_first as p
import run_hls_first as r
import test_context_capture
H=pathlib.Path(__file__).parent
URL='https://192.168.56.74/p/102/sp/102/playManifest/entryId/0_wzmt2sfy/flavorIds/0_21p06l2j/deliveryProfileId/1/protocol/https/format/applehttp/a.m3u8'
class Tests(unittest.TestCase):
 def data(self):return dict(objectType='KalturaPlaybackContext',sources=[dict(objectType='KalturaPlaybackSource',deliveryProfileId=1,format='applehttp',protocols='https',flavorIds='0_21p06l2j',url=URL)],actions=[],messages=[],flavorAssets=[])
 def run_case(self,data=None,body=None):
  calls=[];gets=[];enrolled=[];described=[]
  def call(**kw):calls.append(kw);return data if data is not None else self.data()
  def request(url,headers,limit):gets.append(url);return (200,[],body or b'#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=100\nchild.m3u8\n')
  asset=dict(id='0_21p06l2j',entryId='0_wzmt2sfy',partnerId=102,status=2,isOriginal=False,version=2,flavorParamsId=2,size=128,fileExt='mp4')
  return lambda:m.observe(call,enrolled.append,request,'s'*48,'k'*80,asset,described.append),calls,gets,enrolled,described
 def test_one_get_no_nested(self):
  run,calls,gets,enrolled,desc=self.run_case();ctx,result=run();self.assertEqual(len(calls),1);self.assertEqual(gets,[URL]);self.assertEqual(result['nested_requests'],0);self.assertEqual(len(enrolled),1);self.assertFalse(result['response_secret_coverage_complete']);self.assertTrue(desc[0]['source_bound'])
 def test_unknown_route_no_get_enrolled(self):
  d=self.data();d['sources'][0]['url']+='?token=syntheticsecretvalue'
  run,calls,gets,enrolled,desc=self.run_case(d)
  with self.assertRaises(m.Rejected):run()
  self.assertFalse(gets);self.assertEqual(enrolled,[d['sources'][0]['url']])
 def test_actions_no_get(self):
  d=self.data();d['actions']=[{}];run,_,gets,_,_=self.run_case(d)
  with self.assertRaisesRegex(m.Rejected,'HLS_ACCESS_ACTIONS'):run()
  self.assertFalse(gets)
 def test_unsupported_manifest_no_nested(self):
  run,_,gets,_,_=self.run_case(body=b'#EXTM3U\n#EXT-X-KEY:URI="PRIVATE"\n')
  with self.assertRaisesRegex(m.Rejected,'HLS_MANIFEST_REJECTED'):run()
  self.assertEqual(len(gets),1)
 def report(self):
  row=test_context_capture.Tests().row();run,_,_,_,desc=self.run_case();ctx,manifest=run();row['playback_context']=ctx;row['hls_manifest']=manifest;row['hls_route']=desc[0];return row
 def parse(self,row):return r.public_rows((json.dumps(row)+'\n').encode())[0]
 def test_full_public_rows_success(self):
  row=self.report();self.assertNotIn('native_url_shape',row);out=self.parse(row);self.assertEqual(out['hls_manifest']['requests'],1)
 def test_full_public_rows_negative(self):
  for key in ['hls_manifest','hls_route','playback_context','media_privacy','sources_before','tls_transport']:
   row=self.report();row.pop(key);self.assertRaises(Exception,self.parse,row)
  row=self.report();row['unexpected']='SYNTHETIC_SECRET';self.assertNotIn('SYNTHETIC_SECRET',json.dumps(self.parse(row)))
 def test_failure_projection_no_raw(self):
  row={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'HLS_SOURCE_GUARD','rawurl':'SYNTHETIC_SECRET'}
  self.assertNotIn('SYNTHETIC_SECRET',json.dumps(self.parse(row)))
 def test_source_pins_and_regeneration(self):
  self.assertEqual(p.build(),(H/'guest_hls_first.py').read_text());compile(p.build(),'guest','exec')
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),pin)
  self.assertIn('baseline-freeze-968111b3.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()

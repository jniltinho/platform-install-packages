import unittest,copy,json,hashlib,ast
from pathlib import Path
from unittest.mock import patch
import decode_diagnostic_r3 as diag,hls_decode_r3 as d,prepare_hls_delivery8444_r3 as g,run_hls_delivery8444_r3 as r
import test_hls_decode_diagnostic as prior
H=Path(__file__).parent
class Tests(unittest.TestCase):
 def setUp(self):r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
 def probe(self,id3=True):
  v=copy.deepcopy(prior.PROBE)
  if id3:v['streams'].append({'codec_type':'data','codec_name':'timed_id3'})
  return v
 def test_exact_optional_id3(self):
  self.assertEqual(d.projection(self.probe())['auxiliary_timed_id3_streams'],1);self.assertEqual(d.projection(self.probe(False))['auxiliary_timed_id3_streams'],0)
  v=diag.project(self.probe());diag.validate(v);self.assertEqual(v['data_count'],1);self.assertEqual(v['streams'][2]['codec'],'TIMED_ID3')
 def test_no_arbitrary_other_or_duplicate(self):
  for row in ({'codec_type':'data','codec_name':'bin_data'},{'codec_type':'attachment','codec_name':'timed_id3'},{'codec_type':'video','codec_name':'timed_id3'},{}):
   v=self.probe();v['streams'][2]=row;self.assertRaises(d.Rejected,d.projection,v)
  v=self.probe();v['streams'].append(v['streams'][2]);self.assertRaises(d.Rejected,d.projection,v)
 def test_preserve_av_predicates(self):
  for key,value in [('codec_name','mpeg2video'),('nb_read_frames','N/A'),('avg_frame_rate','0/0'),('height',0)]:
   v=self.probe();v['streams'][0][key]=value;self.assertRaises(d.Rejected,d.projection,v)
 def test_full_decode_maps_only_av(self):
  seen=[];facts=[]
  def run(fd,args,media):seen.append(args);return json.dumps(self.probe()).encode() if '-show_entries' in args else b''
  with patch.object(d.runtime,'run',side_effect=run),patch.object(d.runtime,'pinned',return_value=b'binary'):v=d.decode(b'\x47'+b'\0'*187,facts.append)
  self.assertEqual(v['decoded_stream_scope'],'ONE_VIDEO_ONE_AUDIO');self.assertFalse(v['auxiliary_metadata_payload_verified']);self.assertEqual(v['metadata']['auxiliary_timed_id3_streams'],1);self.assertEqual(seen[1][seen[1].index('-map')+1],'0:v:0')
 def row(self):
  b=prior.Tests();b.setUp();v=b.row();decoded=v['hls_delivery']['decode'];decoded['metadata']['auxiliary_timed_id3_streams']=1;decoded.update(decoded_stream_scope='ONE_VIDEO_ONE_AUDIO',auxiliary_metadata_payload_verified=False);v['hls_segment_diagnostics']['DECODE']=diag.project(self.probe());return v
 def test_full_public_success_exact_id3(self):
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual(out['hls_segment_diagnostics']['DECODE']['data_count'],1);self.assertFalse(out['hls_delivery']['decode']['auxiliary_metadata_payload_verified'])
 def test_full_public_negative(self):
  for key,value in [('auxiliary_timed_id3_streams',True),('auxiliary_timed_id3_streams',2)]:
   v=self.row();v['hls_delivery']['decode']['metadata'][key]=value;self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
  for codec in ('PRIVATE','OTHER'):
   v=self.row();v['hls_segment_diagnostics']['DECODE']['streams'][2]['codec']=codec;self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
 def test_failed_unknown_closed_not_accepted(self):
  v={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_code':'HLS_DECODE_METADATA','failure_stage':'API_ROUND','hls_segment_diagnostics':{'DECODE':diag.project({'streams':[{'codec_type':'data','codec_name':'PRIVATE'}]})}}
  out=r.public_rows(json.dumps(v).encode())[0];self.assertNotIn('PRIVATE',json.dumps(out));self.assertEqual(out['hls_segment_diagnostics']['DECODE']['streams'][0]['codec'],'OTHER')
 def test_bounded_ratio_preserved(self):
  with patch.object(diag,'Fraction',side_effect=AssertionError('unsafe')):self.assertEqual(diag.ratio('1e1000000000')['state'],'INVALID')
 def test_generated_actual_pin_loop(self):
  source=g.build();self.assertEqual(source,(H/'guest_hls_delivery8444_r3.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  node=next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Attribute) and isinstance(n.iter.func.value,ast.Dict) and any(isinstance(k,ast.Constant) and k.value=='decode_diagnostic_r3.py' for k in n.iter.func.value.keys))
  def need(ok,code):
   if not ok:raise ValueError(code)
  exec(compile(ast.Module(body=[node],type_ignores=[]),'actual_guest_id3_pins','exec'),{'NEW_HERE':H,'hashlib':hashlib,'need':need})
  self.assertIn('baseline-freeze-f137c16d.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()

import unittest,copy,json,ast,hashlib
from pathlib import Path
from unittest.mock import patch
import decode_diagnostic as d,hls_decode_r2 as decoder
import run_hls_delivery8444_r2 as r,prepare_hls_delivery8444_r2 as g
import test_hls_delivery8444 as prior
H=Path(__file__).parent
PROBE={'streams':[{'codec_type':'video','codec_name':'h264','width':640,'height':360,'nb_read_frames':'250','avg_frame_rate':'25/1'},{'codec_type':'audio','codec_name':'aac','sample_rate':'44100','channels':2}],'format':{'duration':'10'}}
class Tests(unittest.TestCase):
 def setUp(self):r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
 def test_closed_safe_numbers(self):
  out=d.project(PROBE);d.validate(out);self.assertEqual(out['streams'][0]['nb_read_frames']['value'],250);self.assertEqual(out['duration']['numerator'],10)
 def test_all_untrusted_strings_excluded(self):
  v={'streams':[{'codec_type':'SECRET','codec_name':'SECRET','width':'SECRET','avg_frame_rate':'SECRET','nb_read_frames':'SECRET','tags':{'password':'SECRET'}}],'format':{'duration':'SECRET'}}
  out=d.project(v);d.validate(out);self.assertNotIn('SECRET',json.dumps(out));self.assertEqual(out['other_count'],1)
 def test_missing_zero_cardinality_and_overflow(self):
  for value in [None,{}, {'streams':[]}, {'streams':[{}]*33}, {'streams':[{'avg_frame_rate':'0/0','nb_read_frames':'9999999999999999','width':True}]}]:d.validate(d.project(value))
  out=d.project({'streams':[{'avg_frame_rate':'0/0'}]});self.assertEqual(out['streams'][0]['avg_frame_rate']['state'],'INVALID')
 def test_diagnostic_before_same_metadata_rejection(self):
  v=copy.deepcopy(PROBE);v['streams'][0]['avg_frame_rate']='0/0';seen=[];calls=[]
  def run(fd,args,media):calls.append(args);return json.dumps(v).encode()
  with patch.object(decoder.runtime,'run',side_effect=run),patch.object(decoder.runtime,'pinned',return_value=b'binary'):
   with self.assertRaisesRegex(decoder.Rejected,'HLS_DECODE_METADATA'):decoder.decode(b'\x47'+b'\0'*187,seen.append)
  self.assertEqual(len(calls),1);self.assertEqual(seen[0]['streams'][0]['avg_frame_rate']['state'],'INVALID')
 def test_exponents_unicode_and_unsafe_fraction_never_constructed(self):
  for text in ('1e1000000000','１２/1','1_0/1',' 25/1','+25/1','1/00000000001'):
   with patch.object(d,'Fraction',side_effect=AssertionError('must not parse')):self.assertEqual(d.ratio(text)['state'],'INVALID')
  v=copy.deepcopy(PROBE);v['streams'][0]['avg_frame_rate']='1e1000000000';seen=[]
  with patch.object(decoder.runtime,'run',return_value=json.dumps(v).encode()),patch.object(decoder.runtime,'pinned',return_value=b'binary'),patch.object(decoder,'projection',side_effect=AssertionError('must not reach')):
   with self.assertRaisesRegex(decoder.Rejected,'HLS_DECODE_METADATA'):decoder.decode(b'\x47'+b'\0'*187,seen.append)
  self.assertEqual(seen[0]['streams'][0]['avg_frame_rate']['state'],'INVALID')
 def test_success_decode_unchanged(self):
  seen=[]
  def run(fd,args,media):return json.dumps(PROBE).encode() if '-show_entries' in args else b''
  with patch.object(decoder.runtime,'run',side_effect=run),patch.object(decoder.runtime,'pinned',return_value=b'binary'):result=decoder.decode(b'\x47'+b'\0'*187,seen.append)
  self.assertTrue(result['full_decode_verified']);self.assertEqual(len(seen),1)
 def row(self):
  b=prior.Tests();b.setUp();v=b.row();v['hls_segment_diagnostics']['DECODE']=d.project(PROBE);return v
 def test_full_host_projection_success(self):
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual(out['hls_segment_diagnostics']['DECODE']['video_count'],1)
 def test_full_host_failure_diagnostic_retained(self):
  v={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_code':'HLS_DECODE_METADATA','failure_stage':'API_ROUND','hls_segment_diagnostics':{'DECODE':d.project(PROBE)},'raw':'SECRET'}
  out=r.public_rows(json.dumps(v).encode())[0];self.assertEqual(out['hls_segment_diagnostics']['DECODE']['stream_count'],2);self.assertNotIn('SECRET',json.dumps(out));self.assertNotIn('hls_delivery',out)
 def test_host_invalid_or_missing_diagnostic(self):
  v=self.row();v['hls_segment_diagnostics'].pop('DECODE');self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
  v=self.row();v['hls_segment_diagnostics']['DECODE']['raw']='SECRET';self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
 def test_projection_predicates_exact_ast_unchanged(self):
  def projection(path):return next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='projection')
  self.assertEqual(ast.dump(projection(H/'hls_decode.py'),include_attributes=False),ast.dump(projection(H/'hls_decode_r2.py'),include_attributes=False))
 def test_generation_pins_and_real_pin_loop(self):
  source=g.build();self.assertEqual(source,(H/'guest_hls_delivery8444_r2.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  node=next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Attribute) and isinstance(n.iter.func.value,ast.Dict) and any(isinstance(k,ast.Constant) and k.value=='decode_diagnostic.py' for k in n.iter.func.value.keys))
  def need(ok,code):
   if not ok:raise ValueError(code)
  exec(compile(ast.Module(body=[node],type_ignores=[]),'actual_guest_new_pin_loop','exec'),{'NEW_HERE':H,'hashlib':hashlib,'need':need})
  self.assertIn('baseline-freeze-5e4900be.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()

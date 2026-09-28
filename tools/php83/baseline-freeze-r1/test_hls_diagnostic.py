import json,hashlib,pathlib,unittest
import manifest_diagnostic as d
import hls_first_r2 as m
import prepare_hls_first_r2 as p
import run_hls_first_r2 as r
import test_hls_first
H=pathlib.Path(__file__).parent
class Tests(unittest.TestCase):
 def test_closed_classification(self):
  raw=b'#EXTM3U\n#EXT-X-ALLOW-CACHE:YES\n#UNKNOWN:SECRET\nPRIVATE_URI\n'
  v=d.project((200,[('Content-Type','application/vnd.apple.mpegurl; charset=utf8')],raw),'HLS_UNSUPPORTED')
  self.assertEqual(v['content_type'],'HLS');self.assertEqual(v['tag_counts']['EXT-X-ALLOW-CACHE'],1);self.assertEqual(v['other_tags'],1);self.assertNotIn('SECRET',json.dumps(v));self.assertNotIn('PRIVATE_URI',json.dumps(v));d.validate(v)
 def test_wrong_schema_no_secrets(self):
  for k,value in [('status',True),('reason','SECRET'),('body_bytes',65537),('content_type','SECRET'),('raw','SECRET')]:
   v=d.project();v[k]=value;self.assertRaises(ValueError,d.validate,v)
 def test_before_parser_failure_once(self):
  source=test_hls_first.Tests().data();seen=[];gets=[]
  asset=dict(id='0_21p06l2j',entryId='0_wzmt2sfy',partnerId=102,status=2,isOriginal=False,version=2,flavorParamsId=2,size=128,fileExt='mp4')
  def request(*args):gets.append(1);return 200,[('Content-Type','text/html')],b'<html>PRIVATE_ERROR</html>'
  with self.assertRaisesRegex(m.Rejected,'HLS_MANIFEST_REJECTED'):m.observe(lambda **kw:source,lambda _:None,request,'s'*48,'k'*80,asset,lambda _:None,seen.append)
  self.assertEqual(gets,[1]);self.assertEqual(seen[-1]['reason'],'PLAYLIST_HEADER');self.assertEqual(seen[-1]['content_type'],'HTML');self.assertNotIn('PRIVATE_ERROR',json.dumps(seen))
 def row(self):
  row=test_hls_first.Tests().report();row['hls_diagnostic']=d.project((200,[],b'#EXTM3U\n'));return row
 def test_actual_public_rows_success(self):
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual(out['hls_diagnostic']['status'],200);self.assertNotIn('native_url_shape',out)
 def test_full_projection_failures(self):
  for key in ('hls_diagnostic','hls_route','media_privacy','sources_before'):
   row=self.row();row.pop(key);self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
  row=self.row();row['hls_diagnostic']['reason']='PRIVATE';self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
 def test_failure_diagnostic_preserved(self):
  row={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_code':'HLS_MANIFEST_REJECTED','failure_stage':'API_ROUND','hls_diagnostic':d.project(None,'TRANSPORT')}
  out=r.public_rows(json.dumps(row).encode())[0];self.assertEqual(out['hls_diagnostic']['reason'],'TRANSPORT');self.assertIsNone(out['hls_diagnostic']['status'])
 def test_pins_regeneration(self):
  self.assertEqual(p.build(),(H/'guest_hls_first_r2.py').read_text())
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),pin)
  self.assertIn('baseline-freeze-e9c1d318.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()

import json,hashlib,pathlib,unittest
import nested_descriptor as d
import hls_first_r3 as m
import prepare_hls_first_r3 as p
import run_hls_first_r3 as r
import test_hls_diagnostic,test_hls_first
H=pathlib.Path(__file__).parent
class Tests(unittest.TestCase):
 def test_closed_origins(self):
  seen=[];v=d.observe(b'#EXTM3U\nhttp://192.168.56.74:88/private\nhttps://elsewhere/private?token=secret\n',test_hls_first.URL,seen.append)
  self.assertEqual(len(seen),2);self.assertEqual(v['references'][0]['scheme'],'http');self.assertEqual(v['references'][0]['port'],'88');self.assertTrue(v['references'][0]['port_explicit']);self.assertFalse(v['references'][1]['owned_host_match']);self.assertNotIn('private',json.dumps(v));self.assertNotIn('secret',json.dumps(v));d.validate(v)
 def test_enrollment_failure_explicit(self):
  def no(url):raise Exception('PRIVATE')
  v=d.observe(b'#EXTM3U\nchild\n',test_hls_first.URL,no);self.assertFalse(v['candidate_enrollment_complete'])
 def test_source_parser_failure_preserves_descriptor(self):
  source=test_hls_first.Tests().data();seen=[];gets=[];nested=[]
  asset=dict(id='0_21p06l2j',entryId='0_wzmt2sfy',partnerId=102,status=2,isOriginal=False,version=2,flavorParamsId=2,size=128,fileExt='mp4')
  def request(*args):gets.append(1);return 200,[],b'#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=100\nhttp://192.168.56.74:88/private\n'
  with self.assertRaisesRegex(m.Rejected,'HLS_MANIFEST_REJECTED'):m.observe(lambda **kw:source,seen.append,request,'s'*48,'k'*80,asset,lambda _:None,lambda _:None,nested.append)
  self.assertEqual(gets,[1]);self.assertEqual(len(seen),1);self.assertEqual(nested[0]['references'][0]['port'],'88')
 def row(self):
  row=test_hls_diagnostic.Tests().row();row['hls_nested']=d.observe(b'#EXTM3U\nchild\n',test_hls_first.URL,lambda _:None);return row
 def test_full_public_rows(self):
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual(len(out['hls_nested']['references']),1)
  row=self.row();row['hls_nested']['raw']='PRIVATE';self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
  row=self.row();row.pop('hls_nested');self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
 def test_failed_report_retains_closed_descriptor(self):
  row={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'HLS_MANIFEST_REJECTED','hls_nested':self.row()['hls_nested']}
  self.assertIn('hls_nested',r.public_rows(json.dumps(row).encode())[0])
 def test_pins(self):
  self.assertEqual(p.build(),(H/'guest_hls_first_r3.py').read_text())
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),pin)
  self.assertIn('baseline-freeze-8dcb3711.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()

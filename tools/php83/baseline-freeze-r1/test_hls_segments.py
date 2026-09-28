import unittest,json
from unittest.mock import patch
import hls_segments as s,hls_decode as d
from test_hls_media8444 import NESTED
BODY='#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-ALLOW-CACHE:YES\n#EXT-X-PLAYLIST-TYPE:VOD\n#EXT-X-TARGETDURATION:2\n#EXT-X-MEDIA-SEQUENCE:1\n'+''.join('#EXTINF:2.000,\nseg-'+str(i)+'-v1-a1.ts\n' for i in range(1,6))+'#EXT-X-ENDLIST\n'
class Tests(unittest.TestCase):
 def test_exact_relative_absolute(self):
  for body in (BODY,BODY.replace('seg-',NESTED.rsplit('/',1)[0]+'/seg-')):
   out=[];targets=s.parse(body.encode(),NESTED,'s'*48,'k'*80,out.append);self.assertEqual(len(targets),5);self.assertTrue(all(x['expected_parent'] for x in out[-1]['references']));self.assertNotIn('seg-',json.dumps(out))
 def test_closed_route_negatives_before_fetch(self):
  for old,new in [('seg-1','seg-2'),('-v1-a1','-v2-a1'),('seg-1-v1-a1.ts','https://evil.invalid/a.ts'),('.ts\n','.ts?ks=syntheticPRIVATE\n'),('seg-1','../seg-1'),('seg-1','%73eg-1')]:
   self.assertRaises(s.Rejected,s.parse,BODY.replace(old,new).encode(),NESTED,'s'*48,'k'*80,lambda x:None)
 def test_tags_duration_cardinality(self):
  for old,new in [('TARGETDURATION:2','TARGETDURATION:1'),('VERSION:3','VERSION:7'),('SEQUENCE:1','SEQUENCE:0'),('ALLOW-CACHE:YES','ALLOW-CACHE:NO'),('VOD','EVENT'),('2.000','20.000'),('#EXT-X-ENDLIST',''),('#EXTINF:2.000,\nseg-5-v1-a1.ts\n','')]:self.assertRaises(s.Rejected,s.parse,BODY.replace(old,new).encode(),NESTED,'s'*48,'k'*80,lambda x:None)
 def test_credential_never_exempt(self):
  secret='seg-1-v1-a1.ts'+ 'x'*20;bad=BODY.replace('seg-1-v1-a1.ts',secret);self.assertRaises(s.Rejected,s.parse,bad.encode(),NESTED,secret,'k'*80,lambda x:None)
 def test_bounded_five_segment_framing(self):
  targets=s.parse(BODY.encode(),NESTED,'s'*48,'k'*80,lambda x:None);calls=[]
  def get(*args):calls.append(args);return 200,[],b'\x47'+b'\0'*187
  result,payload=s.fetch(get,targets,1000,lambda x:None);self.assertEqual(len(calls),5);self.assertEqual(len(payload),940);self.assertEqual(result['total_bytes'],1940)
  self.assertRaises(s.Rejected,s.fetch,lambda *a:(200,[],b'bad'),targets,1000,lambda x:None)
 def test_decode_projection_not_golden(self):
  value={'streams':[{'codec_type':'video','codec_name':'h264','width':320,'height':180,'nb_read_frames':'250','avg_frame_rate':'25/1'},{'codec_type':'audio','codec_name':'aac','sample_rate':'44100','channels':2}],'format':{'duration':'10.02'}}
  out=d.projection(value);self.assertEqual(out['width'],320);self.assertEqual(out['duration_milliseconds'],10020)
  value['streams'][0]['width']='SECRET';self.assertRaises(d.Rejected,d.projection,value)
 def test_decoder_fixed_memfd_no_url(self):
  value={'streams':[{'codec_type':'video','codec_name':'h264','width':320,'height':180,'nb_read_frames':'250','avg_frame_rate':'25/1'},{'codec_type':'audio','codec_name':'aac','sample_rate':'44100','channels':2}],'format':{'duration':'10'}};seen=[]
  def run(fd,args,media):seen.append(args);return json.dumps(value).encode() if '-show_entries' in args else b''
  with patch.object(d.runtime,'run',side_effect=run),patch.object(d.runtime,'pinned',return_value=b'binary'):
   out=d.decode(b'\x47'+b'\0'*187)
  self.assertTrue(out['full_decode_verified']);self.assertFalse(out['profile_golden_equivalence']);self.assertEqual(len(seen),2);self.assertTrue(all('file' in args and 'mpegts' in args and not any('://' in x for x in args) for args in seen))
if __name__=='__main__':unittest.main()

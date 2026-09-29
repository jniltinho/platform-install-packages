import unittest,hashlib,json,ast
from pathlib import Path
from unittest.mock import patch
import flavor_decode as fd,prepare_flavor_decode_r1 as g,run_flavor_decode_r1 as r
import test_thumbnail_r5 as old
H=Path(__file__).parent
def probe(fps='60/1',frames='3600',w=1920,h=1080,dur='60.010000',extra=()):
 return {'streams':[{'codec_type':'video','codec_name':'h264','width':w,'height':h,'avg_frame_rate':fps,'nb_read_frames':frames},{'codec_type':'audio','codec_name':'aac','sample_rate':'48000','channels':2},*extra],'format':{'duration':dur}}
class Tests(unittest.TestCase):
 def test_projection(self):
  m=fd.projection(probe());self.assertTrue(m['meets_1080p60']);self.assertEqual((m['video_frames'],m['fps_numerator'],m['duration_milliseconds']),(3600,60,60010))
  for p in [probe(fps='30/1'),probe(frames='3602'),probe(w=1280,h=720),probe(dur='60.100000')]:self.assertFalse(fd.projection(p)['meets_1080p60'])
  self.assertTrue(fd.projection(probe(frames='3601'))['meets_1080p60'])
  for bad in [probe(extra=({'codec_type':'data'},)),{'streams':[probe()['streams'][0]]},probe(fps='x'),probe(frames='-1'),probe(fps='0/1'),probe(fps='121/1'),probe(dur='86401'),probe(dur='0')]:self.assertRaises(fd.Rejected,fd.projection,bad)
 def test_decode_commands_and_result(self):
  seen=[]
  def run(fdx,args,media):
   seen.append(args);return json.dumps(probe()).encode() if '-show_entries' in args else b''
  with patch.object(fd,'run',side_effect=run),patch.object(fd.runtime,'pinned',return_value=b'binary'),patch.object(fd,'Path') as P:
   P.return_value.lstat.return_value=type('S',(),{'st_mode':0o100755,'st_uid':0,'st_gid':0,'st_nlink':1})()
   with patch.object(fd.os,'listxattr',return_value=[]):v=fd.decode(b'\x00'*1000)
  fd.validate(v);self.assertTrue(v['metadata']['meets_1080p60'])
  self.assertTrue(all(a[a.index('-protocol_whitelist')+1]=='file' and a[a.index('-f')+1]=='mp4' for a in seen))
  self.assertIn('-xerror',seen[1]);self.assertEqual(seen[1][-3:],['-f','null','-'])
  self.assertRaises(fd.Rejected,fd.decode,b'');self.assertRaises(fd.Rejected,fd.decode,b'x'*(fd.MAX_BYTES+1))
 def test_validate_negative(self):
  v={'case':'STORED_FLAVOR_FULL_LOCAL_DECODE','metadata':fd.projection(probe()),'full_decode_verified':True,'decoded_stream_scope':'ONE_VIDEO_ONE_AUDIO','delivery_verified':False,'dynamic_library_cohort_attested':False,'full_acceptance':False}
  fd.validate(v)
  for k,x in [('delivery_verified',True),('full_acceptance',True),('full_decode_verified',False)]:self.assertRaises(fd.Rejected,fd.validate,dict(v,**{k:x}))
  self.assertRaises(fd.Rejected,fd.validate,dict(v,metadata=dict(v['metadata'],meets_1080p60=False)))
  self.assertRaises(fd.Rejected,fd.validate,dict(v,metadata=dict(v['metadata'],fps_numerator=30,meets_1080p60=True)))
  for k,x in [('video_codec','vp9'),('audio_codec','mp3'),('fps_denominator',0),('audio_channels',0),('width',0)]:self.assertRaises(fd.Rejected,fd.validate,dict(v,metadata=dict(v['metadata'],**{k:x})))
  for dur in ('60.034332','60.034334','59.965667'):  # boundary: projection and validate must agree
   m=fd.projection(probe(dur=dur));fd.validate(dict(v,metadata=m))
 def test_derivation(self):
  s=g.build();self.assertEqual(s,(H/'guest_flavor_decode_r1.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  line=[l for l in s.splitlines() if "object_id='0_j6rfow09'" in l];self.assertEqual(len(line),1)
  sql=ast.unparse(ast.parse(line[0].strip()).body[0].value.args[0]);self.assertIn("object_id='0_j6rfow09' AND version='\" + fversion + \"'",sql)
  self.assertIn("str(fa.get('flavorParamsId'))=='118'",s);self.assertIn('before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns',s);self.assertEqual(s.count('fdec.decode('),1);self.assertEqual(s.count('newlogs.scan(files,start,patterns,legacy.logs)'),2)
  for u in ('ec2a43b0','b9e18cb6'):self.assertIn('baseline-freeze-'+u+'.service',r.REMOTE_GUARD)
  r.PROOF_PIN='a'*64;self.assertIn('/var/lib/kaltura-baseline-flavor-decode-r1/guest_flavor_decode_r1.py ',r.unit_command('baseline-freeze-00000000'))
 def row(self):
  x=old.Tests();v=x.row();v.pop('thumbnail');v.pop('thumbnail_diagnostics')
  dec={'case':'STORED_FLAVOR_FULL_LOCAL_DECODE','metadata':fd.projection(probe()),'full_decode_verified':True,'decoded_stream_scope':'ONE_VIDEO_ONE_AUDIO','delivery_verified':False,'dynamic_library_cohort_attested':False,'full_acceptance':False}
  v['flavor_decode']={'flavor_id':'0_j6rfow09','entry_id':'0_3h92ab2l','flavor_params_id':118,'flavor_version':2,'stored_bytes':31436000,'stored_sha256':'a'*64,'decode':dec};return v
 def test_public_projection(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertTrue(out['flavor_decode']['decode']['metadata']['meets_1080p60'])
  for edit in [lambda v:v['flavor_decode'].update(flavor_params_id=7),lambda v:v['flavor_decode'].update(stored_sha256='x'),lambda v:v['flavor_decode'].update(extra=1),lambda v:v.update(long_ready={})]:
   v=self.row();edit(v);self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
  f={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'FLAVOR_DECODE_LIMIT','raw':'SECRET'}
  out=r.public_rows(json.dumps(f).encode())[0];self.assertEqual(out['failure_code'],'FLAVOR_DECODE_LIMIT');self.assertNotIn('SECRET',json.dumps(out))
if __name__=='__main__':unittest.main()

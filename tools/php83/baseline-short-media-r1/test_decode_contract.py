import unittest
import decode_contract as d
class Tests(unittest.TestCase):
 def data(self):return dict(streams=[dict(codec_type='video',codec_name='h264',width=640,height=360,avg_frame_rate='25/1',nb_read_frames='250'),dict(codec_type='audio',codec_name='aac',sample_rate='44100',channels=2)],format={'duration':'10.032'})
 def test_argv(self):
  p,f=d.commands(7,'selected_hls_ts');self.assertIn('/proc/self/fd/7',p);self.assertIn('-xerror',f);self.assertEqual(f[f.index('-protocol_whitelist')+1],'file')
 def test_invalid_fd(self):
  for fd in [True,-1,'https://evil',0]:
   with self.assertRaises(d.Rejected):d.commands(fd,'selected_hls_ts')
 def test_positive(self):self.assertFalse(d.validate(self.data(),'selected_hls_ts')['full_decode_verified'])
 def test_negative(self):
  for field,val in [('width',320),('nb_read_frames','249'),('avg_frame_rate','30/1')]:
   p=self.data();p['streams'][0][field]=val
   with self.assertRaises(d.Rejected):d.validate(p,'selected_hls_ts')
 def test_duration(self):
  for val in ['NaN','Infinity','0','100']:
   p=self.data();p['format']['duration']=val
   with self.assertRaises(d.Rejected):d.validate(p,'selected_hls_ts')
if __name__=='__main__':unittest.main()

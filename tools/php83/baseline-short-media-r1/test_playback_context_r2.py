import unittest
import playback_context_r2 as p
class Tests(unittest.TestCase):
 def data(self):return dict(objectType='KalturaPlaybackContext',sources=[dict(objectType='KalturaPlaybackSource',format='applehttp',protocols='https',flavorIds=p.ASSET,url='PRIVATE')],actions=[],messages=[],flavorAssets=[])
 def test_fixed_call(self):
  calls=[];urls=[]
  def call(**kw):calls.append(kw);return self.data()
  r=p.observe(call,urls.append);self.assertEqual(len(calls),1);self.assertEqual(calls[0]['contextDataParams:flavorAssetId'],p.ASSET);self.assertEqual(urls,['PRIVATE']);self.assertNotIn('PRIVATE',str(r));self.assertFalse(r['delivery_authorized'])
 def test_empty(self):
  d=self.data();d['sources']=[];self.assertEqual(p.observe(lambda **kw:d,lambda u:None)['sources'],0)
 def test_excess(self):
  d=self.data();d['sources']*=17
  with self.assertRaises(p.Rejected):p.observe(lambda **kw:d,lambda u:None)
 def test_private_error(self):
  def fail(u):raise ValueError('PRIVATE')
  with self.assertRaisesRegex(p.Rejected,'^URL_ENROLLMENT_INCOMPLETE$'):p.observe(lambda **kw:self.data(),fail)
 def test_no_eligible(self):
  d=self.data();d['sources'][0]['protocols']='http';self.assertEqual(p.observe(lambda **kw:d,lambda u:None)['original_https_hls_descriptors'],0)
 def test_enroll_all_before_metadata_failure(self):
  d=self.data();d['sources'][0]['objectType']='BAD';d['sources'].append(dict(d['sources'][0],url='SECOND'))
  seen=[]
  with self.assertRaisesRegex(p.Rejected,'SOURCE_TYPE'):p.observe(lambda **kw:d,seen.append)
  self.assertEqual(seen,['PRIVATE','SECOND'])
 def test_bad_type(self):
  with self.assertRaises(p.Rejected):p.observe(lambda **kw:{'objectType':'KalturaAPIException'},lambda u:None)
if __name__=='__main__':unittest.main()

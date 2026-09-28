import unittest
import playback_context_r4 as p
from functools import partial
ROW=dict(id="0_21p06l2j",entryId=p.ENTRY,partnerId=102,status=2,isOriginal=False,version=2,flavorParamsId=2,fileExt="mp4",size=500)
observe=partial(p.observe,asset_row=ROW)
class Tests(unittest.TestCase):
 def data(self):return dict(objectType='KalturaPlaybackContext',sources=[dict(objectType='KalturaPlaybackSource',format='applehttp',protocols='https',flavorIds=ROW['id'],url='PRIVATE')],actions=[],messages=[],flavorAssets=[])
 def test_fixed_call(self):
  calls=[];urls=[]
  def call(**kw):calls.append(kw);return self.data()
  r=observe(call,urls.append);self.assertEqual(len(calls),1);self.assertEqual(calls[0]['contextDataParams:flavorAssetId'],ROW['id']);self.assertEqual(urls,['PRIVATE']);self.assertNotIn('PRIVATE',str(r));self.assertFalse(r['delivery_authorized'])
 def test_empty(self):
  d=self.data();d['sources']=[];self.assertEqual(observe(lambda **kw:d,lambda u:None)['sources'],0)
 def test_excess(self):
  d=self.data();d['sources']*=17
  with self.assertRaises(p.Rejected):observe(lambda **kw:d,lambda u:None)
 def test_private_error(self):
  def fail(u):raise ValueError('PRIVATE')
  with self.assertRaisesRegex(p.Rejected,'^URL_ENROLLMENT_INCOMPLETE$'):observe(lambda **kw:self.data(),fail)
 def test_no_eligible(self):
  d=self.data();d['sources'][0]['protocols']='http';self.assertEqual(observe(lambda **kw:d,lambda u:None)['selected_https_hls_descriptors'],0)
 def test_enroll_all_before_metadata_failure(self):
  d=self.data();d['sources'][0]['objectType']='BAD';d['sources'].append(dict(d['sources'][0],url='SECOND'))
  seen=[]
  with self.assertRaisesRegex(p.Rejected,'SOURCE_TYPE'):observe(lambda **kw:d,seen.append)
  self.assertEqual(seen,['PRIVATE','SECOND'])
 def test_optional_secret_carriers(self):
  for location,key in [('top','playbackCaptions'),('top','bumperData'),('row','drm')]:
   d=self.data();target=d if location=='top' else d['sources'][0];target[key]=[{'url':'UNCOVERED'}];seen=[]
   with self.assertRaisesRegex(p.Rejected,'RESPONSE_COVERAGE_INCOMPLETE'):observe(lambda **kw:d,seen.append)
   self.assertEqual(seen,['PRIVATE'])
 def test_unknown_fields(self):
  for location in ['top','row']:
   d=self.data();target=d if location=='top' else d['sources'][0];target['unknown']='PRIVATE'
   with self.assertRaisesRegex(p.Rejected,'RESPONSE_COVERAGE_INCOMPLETE'):observe(lambda **kw:d,lambda u:None)
 def test_empty_optional_fields(self):
  d=self.data();d['playbackCaptions']=[];d['bumperData']=None;d['sources'][0]['drm']=[]
  self.assertFalse(observe(lambda **kw:d,lambda u:None)['response_secret_coverage_complete'])
 def test_selected_rejected_before_call(self):
  for field,value in [('id','0_ewuu0o46'),('status',4),('partnerId',99),('version',0),('isOriginal',True),('flavorParamsId',3),('fileExt','m3u8'),('size',0)]:
   row=dict(ROW);row[field]=value;calls=[]
   with self.assertRaises(p.Rejected):p.observe(lambda **kw:calls.append(kw),lambda u:None,row)
   self.assertEqual(calls,[])
 def test_known_three(self):
  for ident,params in p.KNOWN.items():
   self.assertEqual(p.selected(dict(ROW,id=ident,flavorParamsId=params)),ident)
 def test_tag_projection(self):
  self.assertIsNone(p.tag_match(ROW))
  self.assertTrue(p.tag_match(dict(ROW,tags='SECRET,ipadnew')))
  self.assertFalse(p.tag_match(dict(ROW,tags='source')))
 def test_bad_tags(self):
  with self.assertRaises(p.Rejected):p.tag_match(dict(ROW,tags='x'*1025))
 def test_bad_type(self):
  with self.assertRaises(p.Rejected):observe(lambda **kw:{'objectType':'KalturaAPIException'},lambda u:None)
if __name__=='__main__':unittest.main()

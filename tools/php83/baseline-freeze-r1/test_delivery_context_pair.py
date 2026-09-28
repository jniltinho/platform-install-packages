import unittest
import delivery_context_pair as m
class Tests(unittest.TestCase):
 def asset(self):return {'id':'0_21p06l2j','entryId':'0_wzmt2sfy','partnerId':102,'status':2,'isOriginal':False,'version':2,'flavorParamsId':2,'fileExt':'mp4','size':100,'tags':'applembr'}
 def response(self,proto):return {'objectType':'KalturaPlaybackContext','sources':[{'objectType':'KalturaPlaybackSource','deliveryProfileId':1001 if proto=='http' else '2001','format':'applehttp','protocols':'http,https','flavorIds':'0_21p06l2j','url':proto+'://192.168.56.74/public'}],'actions':[],'messages':[],'flavorAssets':[{}]}
 def test_exact_two_calls_and_no_get(self):
  forms=[];urls=[]
  def call(**form):forms.append(form);return self.response(form['contextDataParams:mediaProtocol'])
  r=m.observe(call,urls.append,self.asset(),2001);self.assertEqual(m.validate(r),r);self.assertEqual(len(urls),2);self.assertEqual([f['contextDataParams:mediaProtocol'] for f in forms],['http','https']);self.assertEqual(r['media_gets'],0)
 def test_wrong_profile_enrolled_before_reject(self):
  urls=[]
  with self.assertRaises(m.Rejected):m.observe(lambda **f:self.response('http'),urls.append,self.asset(),2001)
  self.assertEqual(len(urls),2)
 def test_receipt_id_types(self):
  for v in (True,0,-1,1001,'2001',2147483648):
   with self.assertRaises(m.Rejected):m.observe(None,None,self.asset(),v)
 def test_uncovered_response_rejects(self):
  def call(**f):r=self.response('http');r['unknown']='SYNTHETIC_SECRET';return r
  with self.assertRaises(m.Rejected):m.observe(call,lambda u:None,self.asset(),2001)
 def test_output_unknown_rejected(self):
  r=m.observe(lambda **f:self.response(f['contextDataParams:mediaProtocol']),lambda u:None,self.asset(),2001);r['private']='SYNTHETIC_SECRET'
  with self.assertRaises(m.Rejected):m.validate(r)
if __name__=='__main__':unittest.main()

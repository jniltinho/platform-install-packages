import unittest
import hls_source_r2 as h
S='a'*48;K='b'*40
class Tests(unittest.TestCase):
 def row(self):return dict(objectType='KalturaPlaybackSource',format='applehttp',protocols='https',flavorIds=h.ASSET,deliveryProfileId='1001',url=f'https://192.168.56.74/p/102/sp/102/playManifest/entryId/{h.ENTRY}/flavorIds/{h.ASSET}/deliveryProfileId/1001/protocol/https/format/applehttp/a.m3u8')
 def test_valid(self):
  for host in ('192.168.56.74','192.168.56.74:443'):
   r=self.row();r['url']=r['url'].replace('192.168.56.74',host);self.assertEqual(h.guard(r,S,K),r['url'])
 def test_route_mismatch(self):
  for old,new in [('/sp/102/','/sp/10200/'),('flavorIds/'+h.ASSET,'flavorIds/0_other000'),('/1001/','/1002/'),('/a.m3u8','/token/signature/a.m3u8')]:
   r=self.row();r['url']=r['url'].replace(old,new)
   with self.assertRaises(h.Rejected):h.guard(r,S,K)
 def test_auth_and_origin(self):
  for change in [lambda u:u+'?',lambda u:u+'#',lambda u:u+'?ks='+K,lambda u:u+'#x',lambda u:u.replace('https:','http:'),lambda u:u.replace('.74/','.74:8443/'),lambda u:u.replace('/p/','/%70/'),lambda u:u.replace('.74/','.83/')]:
   r=self.row();r['url']=change(r['url'])
   with self.assertRaises(h.Rejected):h.guard(r,S,K)
 def test_descriptors(self):
  for key,value in [('drm',[{}]),('deliveryProfileId',True),('deliveryProfileId','01001'),('flavorIds','0_other000'),('format','http'),('unknown','private')]:
   r=self.row();r[key]=value
   with self.assertRaises(h.Rejected):h.guard(r,S,K)
 def test_no_credential_values_error(self):
  r=self.row();r['url']+='?x='+K
  try:h.guard(r,S,K)
  except h.Rejected as e:self.assertNotIn(K,str(e));self.assertNotIn(r['url'],str(e))
  else:self.fail('accepted')
if __name__=='__main__':unittest.main()

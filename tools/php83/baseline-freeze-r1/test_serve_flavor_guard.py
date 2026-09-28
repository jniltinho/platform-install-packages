import importlib.util,itertools,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('closed_serve',Path(__file__).with_name('serve_flavor_guard.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
BASE='https://192.168.56.74/p/102/sp/10200/serveFlavor/'
PAIRS=['entryId/0_wzmt2sfy','flavorId/0_ewuu0o46','v/2','fileName/owned_public_long_name.mp4']
class Tests(unittest.TestCase):
 def check(self,u):return m.check(u,expected_filename='owned_public_long_name.mp4',secret='s'*48,ks='k'*80)
 def test_all_pair_orders(self):
  for p in itertools.permutations(PAIRS):
   u=BASE+'/'.join(p);self.assertEqual(self.check(u),u)
 def test_optional(self):self.check(BASE+'/'.join(PAIRS+['name/a.mp4','ev/12','pv/3']))
 def test_closed_failures(self):
  cases=[('other/1','SOURCE_ROUTE_UNKNOWN_KEY'),('v/2','SOURCE_ROUTE_DUPLICATE_KEY'),('name/evil.mp4','SOURCE_ROUTE_EXPECTED_VALUE')]
  for suffix,code in cases:
   with self.assertRaisesRegex(m.Rejected,code):self.check(BASE+'/'.join(PAIRS)+'/'+suffix)
 def test_omission_empty_encoding_auth(self):
  for u in [BASE+'/'.join(PAIRS[:-1]),BASE+'/'.join(PAIRS)+'/',BASE+'/'.join(PAIRS).replace('entryId','%65ntryId'),BASE+'/'.join(PAIRS)+'?ks=x',BASE+'/'.join(PAIRS)+'#x',BASE+'/'.join(PAIRS)+'//']:
   with self.assertRaises(m.Rejected):self.check(u)
 def test_wrong_values_origin(self):
  u=BASE+'/'.join(PAIRS)
  for bad in [u.replace('0_ewuu0o46','0_wrong'),u.replace('/102/','/103/'),u.replace('https:','http:'),u.replace('.74/','.74:8443/'),u.replace('.74/','.74:0/'),u.replace('v/2','v/3'),u.replace('owned_public_long_name','different')]:
   with self.assertRaises(m.Rejected):self.check(bad)
 def test_credentials_checked_even_filename(self):
  for needle in ['s'*48,'s'*15,'k'*80,'k'*15,'%73'*15]:
   with self.assertRaisesRegex(m.Rejected,'SOURCE_ROUTE_CREDENTIAL'):self.check(BASE+'/'.join(PAIRS)+needle)
 def test_no_raw_failures(self):
  with self.assertRaises(m.Rejected) as c:self.check(BASE+'/'.join(PAIRS)+'/SYNTHETIC_SECRET/1')
  self.assertEqual(str(c.exception),'SOURCE_ROUTE_UNKNOWN_KEY')
if __name__=='__main__':unittest.main()

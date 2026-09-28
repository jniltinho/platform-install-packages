import copy,json,unittest
import join_supplements as s
class Tests(unittest.TestCase):
 def data(self):
  source={'source_archive_sha256':'a','source_members':[{'path':'vendor/x','sha256':'b','bytes':1}],'packaged_php':[], 'packaged_entrypoint_candidates':[{'path':'hook','sha256':'c','owners':[{'package_file':'p'}]}]}
  notices={'archive_sha256':'a','files':[{'path':'vendor/x','sha256':'b','bytes':1}]}
  routes={'routes':[{'id':'declared'}],'archive_candidates':[{'path':'hook','sha256':'c','owners':[{'package_file':'p'}]}]}
  return source,notices,routes
 def test_join(self):self.assertEqual(s.join(*self.data())['vendor_file_identities'],1)
 def test_missing_or_mutated_notice(self):
  for mutation in ('missing','hash'):
   a,b,c=self.data()
   if mutation=='missing':b['files']=[]
   else:b['files'][0]['sha256']='wrong'
   with self.assertRaises(ValueError):s.join(a,b,c)
 def test_owner_or_route_duplicate(self):
  for mutation in ('owner','duplicate'):
   a,b,c=self.data()
   if mutation=='owner':c['archive_candidates'][0]['owners']=[]
   else:c['routes']*=2
   with self.assertRaises(ValueError):s.join(a,b,c)
if __name__=='__main__':unittest.main()

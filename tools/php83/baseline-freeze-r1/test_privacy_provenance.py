import copy,json,unittest
import privacy_provenance as p
class ProvenanceTests(unittest.TestCase):
 def make(self,counts):
  return {'counts':counts,'status':'COMPLETE_FINITE_FILE_WINDOW','uncovered_tail_bytes':0},{'counts':[0]*len(counts),'status':'COMPLETE_FINITE_JOURNAL_WINDOW','cutoff_covered':True,'complete':True}
 def test_every_secret_and_url_category_without_values(self):
  secret=b'SYNTHETIC_SECRET_PRIVATE';ks=b'SYNTHETIC_CURRENT_KS_PRIVATE';url=b'SYNTHETIC_PUBLIC_OR_PRIVATE_URL'
  patterns=[secret,secret[:15],ks,ks[:15],url,url[:15]];f,j=self.make([0,0,0,0,2,3]);r=p.receipt(4,'files_and_journal',patterns,f,j,secret=secret,ks=ks,candidates=[url])
  self.assertEqual([x['categories'] for x in r['patterns']],[['CURRENT_SECRET_FULL'],['CURRENT_SECRET_PREFIX'],['CURRENT_KS_FULL'],['CURRENT_KS_PREFIX'],['URL_CANDIDATE_FULL'],['URL_CANDIDATE_PREFIX']]);self.assertTrue(r['any_match']);self.assertFalse(r['final_privacy_acceptance'])
  for value in patterns:self.assertNotIn(value.decode(),json.dumps(r))
 def test_collision_preserves_both_roles(self):
  value=b'SYNTHETIC_COLLISION';f,j=self.make([0,1]);r=p.receipt(2,'files_after_journal',[value,value[:15]],f,j,secret=value,candidates=[value]);self.assertEqual(r['patterns'][0]['categories'],['CURRENT_SECRET_FULL','URL_CANDIDATE_FULL'])
 def test_unknown_is_not_dropped(self):
  f,j=self.make([1,0]);r=p.receipt(1,'files_and_journal',[b'UNKNOWN_PATTERN_FULL',b'UNKNOWN_PREFIX_'],f,j);self.assertEqual(r['patterns'][0]['categories'],['UNATTRIBUTED_PATTERN']);self.assertTrue(r['any_match'])
 def test_closed_shapes_and_bounds(self):
  f,j=self.make([0,0]);args=(1,'files_and_journal',[b'a'*16,b'b'*16],f,j)
  for counts in ([True,0],[-1,0],[0],[2**63,0]):
   broken=dict(f,counts=counts);self.assertRaises(p.Rejected,p.receipt,*args[:3],broken,j)
  self.assertRaises(p.Rejected,p.receipt,1,'SYNTHETIC_SECRET',*args[2:]);self.assertRaises(p.Rejected,p.receipt,*args,candidates=[b'a'*16]*35)
 def test_no_mutation_or_incomplete_pass(self):
  f,j=self.make([0,0]);f['status']='PRIVATE_UNEXPECTED_STATUS';before=copy.deepcopy((f,j));r=p.receipt(1,'files_and_journal',[b'a'*16,b'b'*16],f,j)
  self.assertFalse(r['file_window_complete']);self.assertNotIn('PRIVATE_UNEXPECTED_STATUS',json.dumps(r));self.assertEqual((f,j),before);self.assertFalse(r['final_privacy_acceptance'])
if __name__=='__main__':unittest.main()

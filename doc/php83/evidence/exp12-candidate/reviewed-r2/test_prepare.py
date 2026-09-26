import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('p',Path(__file__).with_name('prepare.py'));p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
class ProposalTests(unittest.TestCase):
 def test_exact65(self):self.assertEqual(len(p.proposal(p.documents())['patches']),65)
 def test_prior62_exact(self):
  d=p.documents();m=p.proposal(d)
  for i,row in enumerate(d['prior']['patches']):
   if row['path']!=p.CRITERIA:self.assertEqual(row,m['patches'][i])
 def reject(self,fn):
  d=p.documents();fn(d)
  with self.assertRaises(ValueError):p.proposal(d)
 def test_prior_omission(self):self.reject(lambda d:d['prior']['patches'].pop())
 def test_old_prepared_not_selected(self):self.reject(lambda d:d['prior'].update(status='PREPARED_NOT_SELECTED'))
 def test_criteria_prior_drift(self):self.reject(lambda d:d['criteria'].update(prior_sha256='0'*64))
 def test_criteria_promoted(self):self.reject(lambda d:d['criteria'].update(next_zip_selected=True))
 def test_debug_wrong_prerequisite(self):self.reject(lambda d:d['debug']['prerequisite'].update(after_sha256='0'*64))
 def test_new_target_collision(self):self.reject(lambda d:d['pake'].update(target=p.CRITERIA))
 def test_real_strict65(self):
  m,r=p.prepare('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip');self.assertEqual(len(r['strict_replays']),65);self.assertFalse(m['selection_approved'])
if __name__=='__main__':unittest.main()

"""Historical exp13 receipts are fixtures, NOT exp14 runtime observations."""
import copy,importlib.util,json,unittest
from pathlib import Path
from unittest.mock import patch
s=importlib.util.spec_from_file_location('ledger14',Path(__file__).with_name('ledger.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Ledger(unittest.TestCase):
 def fixture(self):
  root=m.REPO/'doc/php83/evidence/exp13-runtime'
  return root,[json.loads(x) for x in (root/'primary74-execution-ledger.jsonl').read_text().splitlines()]
 def test_actual_historical_fixture(self):
  root,e=self.fixture()
  with patch.object(m,'RUN',root):m.ledger_validate(e,'74','primary')
 def reject(self,edit):
  root,e=self.fixture();edit(e)
  with patch.object(m,'RUN',root):
   with self.assertRaises(ValueError):m.ledger_validate(e,'74','primary')
 def test_null_productive_output(self):
  def edit(e):
   r=next(x for x in e if x['phase']=='api-primary');r['output_sha256']=None;r['output']='/outside'
  self.reject(edit)
 def test_missing_phase(self):
  self.reject(lambda e:e.pop(next(i for i,x in enumerate(e) if x['phase']=='api-primary')))
 def test_orchestrator_drift(self):
  self.reject(lambda e:e[0].update(orchestrator_sha256='a'*64))
 def test_path_escape(self):
  self.reject(lambda e:next(x for x in e if 'command' in x).update(stdout_path='/outside'))
if __name__=='__main__':unittest.main()

import copy,importlib.util,json,sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import common as c
import collect as adapter
from unittest.mock import patch
class Adapter(unittest.TestCase):
 def setUp(self):self.rows=copy.deepcopy(c.expected())
 def test_historical88_replay_only(self):
  r=c.compare(self.rows);self.assertEqual(r['new_native83_processes'],88);self.assertEqual(r['historical74_rows_NOT_RERUN'],38);self.assertFalse(r['rollback_compatible'])
 def test_oracle_oserror_retains_rows(self):
  result={'records':self.rows,'failures':[]}
  with patch.object(c,'compare',side_effect=OSError('synthetic missing oracle input')):adapter.adjudicate(result,{})
  self.assertEqual(result['status'],'FAIL_RETAINED_OBSERVATIONS');self.assertEqual(len(result['records']),88);self.assertEqual(result['contract_error']['type'],'OSError')
 def test_wrong_cwd_before_native(self):
  with patch.object(adapter.Path,'cwd',return_value=Path('/')):
   with self.assertRaises(ValueError):adapter.run(Path('never-created-native-report.json'))
 def test_inventory(self):
  self.assertEqual(len(self.rows),88);self.assertEqual(sum(r['variant']=='candidate' for r in self.rows),44);self.assertFalse(any(r['variant']=='cachefix' for r in self.rows))
 def test_exit_bool(self):
  self.rows[0]['exit']=False
  with self.assertRaises(ValueError):c.compare(self.rows)
 def test_missing(self):
  self.rows.pop()
  with self.assertRaises(ValueError):c.compare(self.rows)
 def test_diagnostic_change(self):
  self.rows[0]['stderr']=''
  with self.assertRaises(ValueError):c.compare(self.rows)
 def test_artifact_sources(self):
  p=c.preparation();m=json.loads((c.ROOT/p['local']/'identities.json').read_bytes());self.assertEqual(len(m['source_joins']),44);self.assertEqual(len(m['files']),48)
 def test_no74_wrapper(self):
  p=c.preparation();s=(c.ROOT/p['local']/'run.sh').read_text();self.assertNotIn('kaltura-php74-baseline)',s);self.assertNotIn('original|cachefix|candidate',s)
if __name__=='__main__':unittest.main()

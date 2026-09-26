"""Local-only exp14 adapter proof; pending pin must stop before remote access."""
import ast,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
def load(name,leaf):
 s=importlib.util.spec_from_file_location(name,HERE/leaf);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class Adaptation(unittest.TestCase):
 def test_parent_frozen(self):
  pins=json.loads((ROOT/'doc/php83/evidence/exp14-runtime/adaptation-parent-pins.json').read_text())
  for path,pin in pins.items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),pin,path)
 def test_verified_default_pin(self):
  self.assertEqual(load('p14','artifact.py').read_pin(),'459feaf9caf2abe55963dce0cac51b8b593e4ff1b46d2eaf9cb7d5c3f13f62a1')
 def test_pending_collector_before_ssh(self):
  m=load('c14','collect.py')
  with tempfile.TemporaryDirectory() as d,patch.object(m,'read_pin',side_effect=RuntimeError('pending fixture')),patch.object(m,'remote') as remote,patch('sys.argv',['collect.py',d+'/out.json']):
   with self.assertRaises(RuntimeError):m.main()
   remote.assert_not_called()
 def test_pending_original_before_ssh(self):
  import sys
  m=load('original14','original-source-identity.py')
  a=load('ap14','artifact.py')
  with patch.object(a,'read_pin',side_effect=RuntimeError('pending fixture')),patch.dict(sys.modules,{'artifact':a}),patch('subprocess.run') as remote:
   with self.assertRaises(RuntimeError):m.main()
   remote.assert_not_called()
 def test_pending_native_snapshot_before_ssh(self):
  import sys,runpy
  a=load('ar14','artifact.py')
  with patch.object(a,'read_pin',side_effect=RuntimeError('pending fixture')),patch.dict(sys.modules,{'artifact':a}),patch('subprocess.run') as remote,patch('sys.argv',['runtime83-identity.py','unused']):
   with self.assertRaises(RuntimeError):runpy.run_path(str(HERE/'runtime83-identity.py'),run_name='__main__')
   remote.assert_not_called()
 def test_no_exp12_seams(self):
  for p in list(HERE.glob('*'))+list((HERE.parent/'exp14-regression').glob('*')):
   if p.is_file() and not p.name.startswith('test_') and p.name!='README.md':self.assertNotIn('exp12',p.read_text(),str(p))
 def test_prior_verifier_and_pin(self):
  for p in [HERE/'collect.py',HERE.parent/'exp14-regression/batch.py']:
   s=p.read_text();self.assertIn('/home/vagrant/php-exp13-regression/api/verify-source.py',s)
   self.assertIn('6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944',s)
 def test_stage_pin_check_before_ssh(self):
  s=(HERE/'stage.sh').read_text();self.assertLess(s.index('pin=$(python3'),s.index('ssh -T'))
 def test_ledger_functions_exact_r3(self):
  info=json.loads((ROOT/'doc/php83/evidence/exp14-runtime/ledger-parent.json').read_text())
  p=ROOT/info['path'];old=p.read_text();new=(HERE/'ledger.py').read_text()
  self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),info['sha256'])
  def funcs(text):
   return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
  a,b=funcs(old),funcs(new)
  for name in info['functions']:self.assertEqual(a[name],b[name])
if __name__=='__main__':unittest.main()

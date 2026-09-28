import ast,unittest,hashlib,json,copy
from pathlib import Path
import prepare_hls_media8444_r2 as g,run_hls_media8444_r2 as r
import test_hls_media8444 as base
H=Path(__file__).parent
def pin_node(source):
 tree=ast.parse(source)
 return next(n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and any(isinstance(k,ast.Constant) and k.value=='hls_context_proof.py' for k in (n.iter.keys if isinstance(n.iter,ast.Dict) else n.iter.func.value.keys if isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Attribute) and isinstance(n.iter.func.value,ast.Dict) else [])))
def execute_pin_node(source,root=H):
 node=pin_node(source);code=compile(ast.Module(body=[node],type_ignores=[]),'actual_guest_pin_loop','exec')
 def need(ok,code):
  if not ok:raise ValueError(code)
 exec(code,{'NEW_HERE':root,'hashlib':hashlib,'need':need})
class Tests(unittest.TestCase):
 def setUp(self):r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
 def test_real_old_loop_reproduces_failure(self):
  with self.assertRaises(ValueError):execute_pin_node((H/'guest_hls_media8444.py').read_text())
 def test_real_fixed_loop_validates_all_files(self):execute_pin_node(g.build())
 def test_real_fixed_loop_rejects_drift(self):
  class Bad:
   def __truediv__(self,k):return self
   def read_bytes(self):return b'drift'
  with self.assertRaisesRegex(ValueError,'HLS_PIN'):execute_pin_node(g.build(),Bad())
 def test_only_one_semantic_delta(self):
  old=ast.parse((H/'guest_hls_media8444.py').read_text());new=ast.parse(g.build());n=pin_node((H/'guest_hls_media8444.py').read_text());n.iter=ast.Call(func=ast.Attribute(value=n.iter,attr='items',ctx=ast.Load()),args=[],keywords=[])
  # Match the separately parsed original after exact intended AST transformation.
  target=next(x for x in ast.walk(old) if isinstance(x,ast.For) and x.lineno==n.lineno);target.iter=n.iter
  self.assertEqual(ast.dump(old,include_attributes=False),ast.dump(new,include_attributes=False))
 def test_full_projection_still_success_and_negatives(self):
  b=base.Tests();b.setUp();row=b.row();out=r.public_rows(json.dumps(row).encode())[0];self.assertEqual(out['hls_media']['requests'],2)
  for k in ('round_privacy','media_tls_logs_in_every_inventory','split_receipt_sha256','hls_media'):
   bad=copy.deepcopy(row);bad.pop(k);self.assertRaises(Exception,r.public_rows,json.dumps(bad).encode())
 def test_regeneration_pins_prior_unit(self):
  self.assertEqual(g.build(),(H/'guest_hls_media8444_r2.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertIn('baseline-freeze-fc9b70f1.service',r.REMOTE_GUARD);self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-hls-media8444-r2')
if __name__=='__main__':unittest.main()

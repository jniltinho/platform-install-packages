import importlib.util,hashlib,sys,unittest
from pathlib import Path
H=Path(__file__).parent
sys.path.insert(0,str(H))
def module(n):
 s=importlib.util.spec_from_file_location(n,H/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
p=module('prepare_serve_progressive');r=module('run_serve_progressive')
class Tests(unittest.TestCase):
 def test_regeneration(self):self.assertEqual(p.build(),(H/'guest_serve_progressive.py').read_text())
 def test_pins(self):
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),pin)
 def test_newstage_and_prior(self):
  self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-serve-progressive-r1');self.assertIn('baseline-freeze-a1776f1a.service',r.REMOTE_GUARD)
 def test_private_semantics(self):
  s=p.build();self.assertEqual(s.count("raw_url=call(service='flavorasset',action='getUrl'"),1)
  self.assertIn('serve.check(raw_url,expected_filename=expected_filename,secret=secret,ks=ks)',s)
  self.assertIn('serve.check(url,expected_filename=expected_filename,secret=secret,ks=ks)',s)
  self.assertNotIn("private_json(private_dir/'route-descriptor.json'",s)
  self.assertEqual(s.count('serve_source_guard()'),3)
  self.assertIn('report[\'round_privacy\']=audit_all(rehearsal.patterns(secret,ks,tracked_tokens),start,jstart)',s)
 def test_projection(self):
  with self.assertRaises(Exception):r.join_projection({'url':'SYNTHETIC_SECRET'})
  with self.assertRaises(Exception):r.progressive_projection({'body':'SYNTHETIC_SECRET'})
 def test_no_extra_workload(self):
  s=p.build();self.assertNotIn('rehearsal.run(',s);self.assertNotIn('delivery.native_url(',s);compile(s,'guest','exec')
if __name__=='__main__':unittest.main()

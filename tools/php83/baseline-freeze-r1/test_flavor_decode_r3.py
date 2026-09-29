import unittest,hashlib,ast
from pathlib import Path
import prepare_flavor_decode_r2 as g,run_flavor_decode_r2 as r2,run_flavor_decode_r3 as r
H=Path(__file__).parent
class Tests(unittest.TestCase):
 def test_guest_only_binding_changed(self):
  s=g.build();self.assertEqual(s,(H/'guest_flavor_decode_r2.py').read_text())
  a=(H/'guest_flavor_decode_r1.py').read_text().splitlines();b=s.splitlines()
  self.assertEqual([x for x in a if x not in b],['\"\"\"Stored 1080p60 flavor (params 118) full local decode after finite privacy gates; read-only, no upload.\"\"\"',"  fa=call(service='flavorasset',action='get',ks=ks,id='0_j6rfow09')"])
  self.assertEqual(len([x for x in b if x not in a]),4);self.assertNotIn("service='flavorasset',action='get'",s);self.assertIn("str(fa.get('flavorParamsId'))=='118'",s)
 def test_binding_selects_exact_row(self):
  s=g.build();lines=[l.strip() for l in s.splitlines() if l.strip().startswith(('listed=','need(type(listed)','matches='))]
  ns={'need':lambda ok,code:(_ for _ in ()).throw(ValueError(code)) if not ok else None}
  def run(listed):
   env=dict(ns,call=lambda **k:listed,ks='k');exec(compile('\n'.join(lines),'b','exec'),env);return env['fa']
  row={'id':'0_j6rfow09','entryId':'0_3h92ab2l'}
  self.assertEqual(run([{'id':'0_other000'},row]),row)
  for bad in ([],[{'id':'0_other000'}],[row,row],{'id':'x'},['x']):self.assertRaises(ValueError,run,bad)
 def test_runner(self):
  self.assertEqual({k:v for k,v in r.PINS.items() if k!='guest_flavor_decode_r2.py'},{k:v for k,v in r2.PINS.items() if k!='guest_flavor_decode_r1.py'})
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertIn('/var/lib/kaltura-baseline-flavor-decode-r3',r.REMOTE_GUARD+r.STAGE);self.assertIn('baseline-freeze-8372955c.service',r.REMOTE_GUARD)
  r.PROOF_PIN='a'*64;self.assertIn('/var/lib/kaltura-baseline-flavor-decode-r3/guest_flavor_decode_r2.py ',r.unit_command('baseline-freeze-00000000'))
if __name__=='__main__':unittest.main()

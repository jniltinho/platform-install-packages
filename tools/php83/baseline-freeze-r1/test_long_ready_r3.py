import unittest,hashlib,json
from pathlib import Path
import long_ready as a,long_ready_r2 as b,prepare_long_ready_r3 as g,run_long_ready_r3 as r
import test_long_ready_r1 as t1
H=Path(__file__).parent
class Tests(unittest.TestCase):
 def test_module_diff_only_constants(self):
  x=Path('long_ready.py').read_text().splitlines();y=Path('long_ready_r2.py').read_text().splitlines()
  self.assertEqual([l for l in y if l not in x],['"""R2: long_ready.py for the profile-15 upload (entry 0_3h92ab2l, params 118 = 1080p60 replaces 7); otherwise identical.','Phase B of the FullHD60 fixture: read-only observation of the phase-A entry (0_wzlsbwmy) until READY,',"ENTRY='0_3h92ab2l';PARTNER=102;PROFILE=15",'PROFILE_PARAMS={0,2,3,4,5,6,118}'])
 def test_hd60_detection(self):
  assets=[t1.asset(0,orig=True,i='0_orig0000'),t1.asset(2,w=640,h=360,fps=25,i='0_flav0002'),t1.asset(118,i='0_flav0118')]
  for x in assets:x['entryId']=b.ENTRY
  f=t1.Fake(assets=assets);f.entry={'id':b.ENTRY,'conversionProfileId':15}
  v=b.observe(f.call,'k'*40,sleep=lambda s:None);v['stored_original_sha256_match']=True;b.validate(v)
  self.assertTrue(v['delivered_1080p60_flavor_present']);self.assertEqual(v['ready_flavor_params'],[0,2,118])
  bad=[dict(x) for x in assets];bad[2]['flavorParamsId']=7
  f=t1.Fake(assets=bad);f.entry={'id':b.ENTRY,'conversionProfileId':15};self.assertRaises(b.Rejected,b.observe,f.call,'k'*40,sleep=lambda s:None)
 def test_derivation(self):
  s=g.build();self.assertEqual(s,(H/'guest_long_ready_r3.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertIn("load('long_ready_r2'",s);self.assertNotIn("load('long_ready',",s);self.assertEqual(s.count('newlogs.scan(files,start,patterns,legacy.logs)'),2)
  for u in ('2e9f8e2c','ec2a43b0'):self.assertIn('baseline-freeze-'+u+'.service',r.REMOTE_GUARD)
  r.PROOF_PIN='a'*64;self.assertIn('/var/lib/kaltura-baseline-long-ready-r3/guest_long_ready_r3.py ',r.unit_command('baseline-freeze-00000000'))
if __name__=='__main__':unittest.main()

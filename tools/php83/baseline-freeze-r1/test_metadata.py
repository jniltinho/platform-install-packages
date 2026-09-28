import ast,copy,hashlib,pathlib,unittest
import run_metadata as r
import prepare_metadata as p
H=pathlib.Path(__file__).parent
class MetadataTests(unittest.TestCase):
 def sample(self):
  return {'case':'EXISTING_SHORT_FLAVOR_METADATA','api_calls':1,'assets':[dict(id='0_ewuu0o46',entryId='0_wzmt2sfy',partnerId=102,status=2,isOriginal=True,version=2,flavorParamsId=0,size=1475,fileExt='mp4')],'playback_tested':False,'full_acceptance':False,'size_unit':'API_KBytes'}
 def test_projection(self):self.assertEqual(r.metadata_projection(self.sample()),self.sample())
 def test_no_secret_or_extra_fields(self):
  for level in ('outer','inner'):
   row=self.sample();(row if level=='outer' else row['assets'][0])['unexpected']='SYNTHETIC_SECRET';self.assertRaises(Exception,r.metadata_projection,row)
 def test_identity_cardinality_units_and_claims(self):
  for key,value in [('size_unit','bytes'),('api_calls',True),('playback_tested',True),('full_acceptance',True)]:
   row=self.sample();row[key]=value;self.assertRaises(Exception,r.metadata_projection,row)
  for key,value in [('partnerId',20),('entryId','0_aaaaaaaa'),('version',3),('id','0_aaaaaaaa')]:
   row=self.sample();row['assets'][0][key]=value;self.assertRaises(Exception,r.metadata_projection,row)
  row=self.sample();row['assets']*=2;self.assertRaises(Exception,r.metadata_projection,row)
 def test_derivation_and_pins(self):
  self.assertEqual(p.build(),(H/'guest_metadata.py').read_text())
  for name,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/name).read_bytes()).hexdigest(),pin)
 def test_only_one_new_call_no_round_or_session_repeat(self):
  s=p.build();self.assertNotIn('protocol.run_round(',s);self.assertNotIn('TrackedTransport(',s);self.assertEqual(s.count('metadata.collect('),1)
  self.assertIn('metadata.collect(lambda **form:call(ks=ks,**form))',s)
  self.assertLess(s.index('legacy.logs=lambda:tls_logs.extend(old_logs)'),s.index("report['phase']='invalid-nonce'"))
  self.assertLess(s.index('metadata.collect('),s.index("failure_stage='QUIET_SETTLE'"));self.assertIn('audit_all(rehearsal.patterns(secret,ks,tracked_tokens),start,jstart)',s)
  calls=[n for n in ast.walk(ast.parse(s)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='PostTransport'];self.assertEqual(len(calls),1)
  self.assertEqual([ast.literal_eval(v) for v in calls[0].args[0].args],['192.168.56.74','https',8443])
 def test_fresh_stage_and_prior_unit(self):
  self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-short-metadata-r1');self.assertIn('baseline-freeze-3b21eb13.service',r.REMOTE_GUARD);self.assertIn('assert not os.path.lexists(stage)',r.REMOTE_GUARD)
  self.assertNotIn('api_v3/web',r.unit_command('baseline-freeze-12345678'))
 def test_round_claim_rejected(self):
  self.assertRaises(Exception,r.round_projection,{'untimed_round':{},'flavor_metadata':self.sample()})
if __name__=='__main__':unittest.main()

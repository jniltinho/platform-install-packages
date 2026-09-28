import hashlib,json,pathlib,subprocess,sys,tempfile,unittest
import observation_v2 as o
import assemble_v2 as a
import run_v3 as r
import test_freeze
HERE=pathlib.Path(__file__).parent
class V2Tests(unittest.TestCase):
 def inputs(self,observed=0):
  row,env=test_freeze.Tests().inputs();entry=row['fixture']['entry'];row['fixture']=o.fixture(entry,{'objectType':'KalturaMediaListResponse','objects':[entry],'totalCount':'1'},observed)
  row['version_observations']=[{'requested':n,'outcome':'TYPED_PROJECTION_MATCH'} for n in sorted({-1,0}|({observed} if observed is not None else set()))]
  row['entry_version_status']='UNRESOLVED' if observed is None else 'OBSERVED_FROM_ENTRY_DATA';row['sources_before']=row['sources_after']=r.EXPECTED_SOURCES
  row['profile']=o.profile({'objectType':'KalturaConversionProfile','id':14,'partnerId':102,'status':2,'flavorParamsIds':'0,1'},14)
  return row,env
 def test_native_zero_and_explicit_current(self):
  row,env=self.inputs();out=a.assemble(row,env);self.assertEqual(out['protocol_fixture']['media_get_version'],-1);self.assertEqual(out['protocol_fixture']['observed_entry_data_version'],0);self.assertEqual(out['protocol_fixture']['source_asset']['version'],'2');self.assertFalse(out['approved_freeze'])
 def test_unknown_stays_unknown_and_current_observed(self):
  row,env=self.inputs(None);out=a.assemble(row,env);self.assertIsNone(out['protocol_fixture']['observed_entry_data_version']);self.assertEqual(out['protocol_fixture']['media_get_version'],-1)
 def test_old_protocol_untouched_and_new_does_not_accept_v1(self):
  row,_=test_freeze.Tests().inputs();self.assertRaises(Exception,a.fixture,row['fixture']);self.assertEqual(hashlib.sha256((HERE.parent/'baseline-api/protocol.py').read_bytes()).hexdigest(),'4587eab6222c2cacc381b6ef100dc557f1afb814250dcc5ba92b3b2ee7eeca34')
 def test_native_data_zero(self):
  for value in ('','0','0.mp4','0^other'):self.assertEqual(o.entry_version(value),0)
  self.assertIsNone(o.entry_version('unknown'));self.assertEqual(o.entry_version('7.mp4'),7)
 def test_native_profile_class_empty_configured_and_owner(self):
  p={'objectType':'KalturaConversionProfile','id':14,'partnerId':0,'status':2,'flavorParamsIds':''};self.assertEqual(o.profile(p,14)['configured_flavor_ids'],[])
  p['partnerId']=999;self.assertRaises(Exception,o.profile,p,14)
  p['objectType']='KalturaConversionProfile2';self.assertEqual(o.profile(p,14)['status'],'UNRESOLVED_API_PROFILE')
 def test_selection_bool_and_wrong_profile_reject(self):
  for value in (0,False,1):
   row,env=self.inputs();row['fixture']['media_get_version']=value;self.assertRaises(Exception,a.assemble,row,env)
  row,env=self.inputs();row['profile']['selected_profile_id']=15;self.assertRaises(Exception,a.assemble,row,env)
 def test_public_projection_retains_typed_count_without_positive_version(self):
  row,_=self.inputs();row['unrecognized']='SYNTHETIC_SECRET';out=r.public_rows((json.dumps(row)+'\n').encode())[0]
  self.assertEqual(out['fixture']['list_total_count'],'1');self.assertEqual(out['fixture']['entry']['status'],2);self.assertNotIn('SYNTHETIC_SECRET',json.dumps(out))
 def test_top_level_asset_version_cannot_export_arbitrary_value(self):
  for value in ('SYNTHETIC_SECRET',2,True):
   row,_=self.inputs();row['asset_version']=value;self.assertRaises(Exception,r.public_rows,(json.dumps(row)+'\n').encode())
 def test_fresh_stage_and_guest_pins(self):
  self.assertIn('assert not os.path.lexists(stage)',r.REMOTE_GUARD);self.assertIn('baseline-freeze-fe117e92',r.REMOTE_GUARD)
  for name,pin in r.PINS.items():self.assertEqual(hashlib.sha256((HERE/name).read_bytes()).hexdigest(),pin)
  self.assertIn('/guest_v2.py',r.unit_command('baseline-freeze-12345678'))
 def test_protocol_same100_mix_and_current_get(self):
  sys.path.insert(0,str(HERE.parent/'baseline-api'))
  import protocol_v2 as protocol
  from transport import Reply
  row,_=self.inputs();fixture=row['fixture'];calls=[]
  class Fake:
   def request(self,params):
    calls.append(params)
    if params['service']=='session':value='synthetic-session-token-123456789'
    elif params['action']=='list':value={'objectType':'KalturaMediaListResponse','totalCount':'1','objects':[fixture['entry']]}
    else:value=fixture['entry']
    return Reply(value,100,200)
  result=protocol.run_round(Fake(),protocol.Credentials(102,'synthetic','SYNTHETIC_SECRET'),fixture)
  self.assertTrue(result['functional_round_pass']);self.assertEqual(len(calls),100);self.assertEqual([x['operation'] for x in result['records']],protocol.OPERATIONS)
  self.assertTrue(all(x['version']==-1 for x in calls[67:]));self.assertNotIn('SYNTHETIC_SECRET',json.dumps(result))
 def test_exact_generated_derivative(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'guest.py';p=subprocess.run([sys.executable,'-B',str(HERE/'prepare_v2.py'),'--output',str(path)],capture_output=True)
   self.assertEqual(p.returncode,0);self.assertEqual(path.read_bytes(),(HERE/'guest_v2.py').read_bytes())
if __name__=='__main__':unittest.main()

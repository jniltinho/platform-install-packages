import copy,json,unittest
import assemble_readiness as a
import test_v2
class ReadinessTests(unittest.TestCase):
 def inputs(self):
  row,env=test_v2.V2Tests().inputs();env.update(vm_uuid=a.UUID,cpus=4,memory_mib=8192)
  o={'status':'OBSERVATION_CAPTURED_NOT_APPROVED','guest_exit':0,'unit_inactive':True,'files':a.OBS_FILES,'phase_receipts':[row]}
  p={'source_sha256':a.PROFILE_SOURCE,'exit_status':0,'stderr_bytes':0,'observation':{'schema':1,'status':'READ_ONLY_STORED_PROFILE_OBSERVED','entry_id':'0_wzmt2sfy','entry_partner_id':102,'selected_profile_id':14,'profile_partner_id':102,'profile_status':2,'profile_type':1,'profile_not_deleted':True,'configured_flavor_ids':[0,2,3,4,5,6,7,19],'select_count':5,'db_identity_verified':True,'api_authorization_verified':False,'full_acceptance':False}}
  w={'status':'CURRENT_WEB_OBSERVATION_CAPTURED','guest_exit':0,'unit_inactive':True,'host_unchanged':True,'runner_sha256':a.WEB_RUNNER,'source_pins':{'tools/php83/baseline-web-runtime-r1/guest.py':a.WEB_GUEST},'host':{'UUID':a.UUID,'name':'kaltura-php74-noble-baseline','VMState':'running','cpus':'4','memory':'8192'},'provider':{'status':'CURRENT_APACHE_PHP74_OBSERVED_OWN_PROBE_REMOVED','probe_removed':True,'nonce_verified':True,'app_credentials_read':False,'sql_executed':False,'version':'7.4.33','sapi':'apache2handler','ini_file':'/etc/php/7.4/apache2/php.ini','modules':sorted(a.WEB_MODULES)}}
  return o,{'environment':env},p,w
 def test_join_not_acceptance(self):
  v=a.assemble(*self.inputs());self.assertFalse(v['approved_freeze']);self.assertFalse(v['performance_measurement_ready']);self.assertEqual(v['protocol_plan']['calls_per_round'],100);self.assertIsNone(v['environment']['snapshot_id'])
 def test_wrong_receipt_pins(self):
  for index,key in [(0,'files'),(2,'source_sha256'),(3,'runner_sha256')]:
   x=list(self.inputs());x[index][key]='BAD';self.assertRaises(Exception,a.assemble,*x)
 def test_web_cleanup_and_ownership(self):
  x=list(self.inputs());x[3]['provider']['probe_removed']=False;self.assertRaises(Exception,a.assemble,*x)
  x=list(self.inputs());x[2]['observation']['profile_partner_id']=999;self.assertRaises(Exception,a.assemble,*x)
 def test_extra_secret_not_copied(self):
  x=list(self.inputs());x[3]['unknown']='SYNTHETIC_SECRET';self.assertNotIn('SYNTHETIC_SECRET',json.dumps(a.assemble(*x)))
 def test_unknown_module_no_raw_field_pass(self):
  x=list(self.inputs());x[3]['provider']['modules'][0]='SYNTHETIC_SECRET';self.assertRaises(Exception,a.assemble,*x)
if __name__=='__main__':unittest.main()

import ast,copy,hashlib,importlib.util,json,pathlib,subprocess,sys,tempfile,unittest
import observation as o
import assemble as a
HERE=pathlib.Path(__file__).parent
class Tests(unittest.TestCase):
 def entry(self):return {'objectType':'KalturaMediaEntry','id':o.ENTRY,'partnerId':102,'status':2,'mediaType':1}
 def fixture(self):return o.fixture(self.entry(),{'objectType':'KalturaMediaListResponse','objects':[self.entry()],'totalCount':'1'},7)
 def inputs(self):
  privacy={'files':{'counts':[0,0],'status':'COMPLETE_FINITE_FILE_WINDOW','uncovered_tail_bytes':0},'journal':{'counts':[0,0],'status':'COMPLETE_FINITE_JOURNAL_WINDOW','cutoff_covered':True,'complete':True},'scope':'finite'}
  r={'status':'EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE','baseline_label':a.LABEL,'upload_attempted':False,'wrong_secret_rejected':True,'admin_escalation_rejected':True,'fixture':self.fixture(),'source_sha256':o.SOURCE,'stored_source_sha256':o.SOURCE,'original_asset_id':'0_ewuu0o46','asset_version':'2','file_sync_id':315,'version_observations':[{'requested':n,'outcome':'TYPED_PROJECTION_MATCH'} for n in (-1,0,7)],'entry_version_status':'OBSERVED_FROM_ENTRY_DATA','overlay_manifest_sha256':a.OVERLAY,'runtime_pins_verified':True,'sources_before':dict.fromkeys('abcde','p'),'sources_after':dict.fromkeys('abcde','p'),'profile':{'status':'UNRESOLVED_SELECTED_PROFILE','selected_profile_id':None}}
  for k in ('invalid_nonce','user_privacy','media_privacy'):r[k]=copy.deepcopy(privacy)
  e=dict.fromkeys(a.ENV_KEYS);e.update(vm_uuid='9e954729-16f3-4eda-9db5-b94e5ada9e44',cpus=4,memory_mib=8192,observed_readonly=True)
  return r,e
 def test_exact8_keys_and_typed_total(self):
  f=self.fixture();self.assertEqual(len(f),8);self.assertEqual(type(f['list_total_count']),str);a.fixture(f)
  f['extra']='no';self.assertRaises(o.Invalid,a.fixture,f)
 def test_entry_version_not_asset(self):
  r,e=self.inputs();out=a.assemble(r,e);self.assertEqual(out['protocol_fixture']['entry_version'],7);self.assertNotEqual(out['protocol_fixture']['entry_version'],int(r['asset_version']))
  self.assertFalse(out['approved_freeze']);self.assertIsNone(out['environment']['snapshot_id'])
 def test_version_source_grammar(self):
  self.assertEqual(o.entry_version('7.mp4^extra'),7);self.assertEqual(o.entry_version('7&extra'),7)
  for data in ('','NULL','../7.mp4','0','SYNTHETIC_PRIVATE'):self.assertIsNone(o.entry_version(data))
 def test_typed_projection_difference(self):
  listing={'objectType':'KalturaMediaListResponse','objects':[self.entry()],'totalCount':1};listing['objects'][0]['status']='2'
  self.assertRaises(o.Invalid,o.fixture,self.entry(),listing,7)
 def test_boolean_or_extra_version(self):
  for row in ({'requested':False,'outcome':'TYPED_PROJECTION_MATCH'},{'requested':0,'outcome':'arbitrary'},{'requested':0,'outcome':'API_REJECTED','raw':'secret'}):
   r,e=self.inputs();r['version_observations'][1]=row;self.assertRaises(o.Invalid,a.assemble,r,e)
 def test_incomplete_or_hit_privacy(self):
  for key,value in [('counts',[0,1]),('uncovered_tail_bytes',1)]:
   r,e=self.inputs();r['media_privacy']['files'][key]=value;self.assertRaises(o.Invalid,a.assemble,r,e)
 def test_source_runtime_target_drift(self):
  for key,value in [('overlay_manifest_sha256','x'),('runtime_pins_verified',False),('stored_source_sha256','x')]:
   r,e=self.inputs();r[key]=value;self.assertRaises(o.Invalid,a.assemble,r,e)
  v=self.entry();v['partnerId']=103;self.assertRaises(o.Invalid,o.projection,v)
 def test_secret_public_field_rejected(self):
  r,e=self.inputs();r['secret']='SYNTHETIC';self.assertRaises(o.Invalid,a.assemble,r,e)
 def test_profile_binding_and_closed_projection(self):
  p={'objectType':'KalturaConversionProfile2','id':'1','partnerId':102,'status':2,'flavorParamsIds':'0,1','name':'SYNTHETIC_NOT_EXPORTED'}
  out=o.profile(p,'1');self.assertNotIn('name',out);p['partnerId']=999;self.assertRaises(o.Invalid,o.profile,p,1)
 def test_asset_bound_and_owner(self):
  self.assertRaises(o.Invalid,o.assets_projection,[])
  self.assertRaises(o.Invalid,o.assets_projection,[{}]*65)
 def test_guest_derivative_reproducible_no_write_apis(self):
  with tempfile.TemporaryDirectory() as d:
   target=pathlib.Path(d)/'guest.py';p=subprocess.run([sys.executable,'-B',str(HERE/'prepare.py'),'--output',str(target)],capture_output=True)
   self.assertEqual(p.returncode,0);self.assertEqual(target.read_bytes(),(HERE/'guest.py').read_bytes())
  tree=ast.parse((HERE/'guest.py').read_text());calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
  for call in calls:
   if isinstance(call.func,ast.Attribute):self.assertNotIn(call.func.attr,('_upload_worker','probe','replace_file'))
  text=(HERE/'guest.py').read_text();self.assertNotIn("value('media','add'",text);self.assertNotIn("value('uploadtoken'",text)
 def test_fixed_failure_code(self):self.assertIn("media_privacy_failure_class']='FINITE_SCAN_INCOMPLETE'",(HERE/'guest.py').read_text())
if __name__=='__main__':unittest.main()

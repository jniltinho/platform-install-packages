import json,hashlib,pathlib,unittest
import test_v2
import privacy_provenance
import run_context_observer_r3 as r
class Tests(unittest.TestCase):
 def row(self):
  row,_=test_v2.V2Tests().inputs();row['tls_transport']={'scheme':'https','port':8443,'ca_sha256':'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef','tls_logs_in_every_inventory':True}
  q={'status':'QUIET_WINDOW_OBSERVED','samples':9,'quiet_seconds':2,'maximum_seconds':30};row['quiet_window']=q;row['last_audit_quiet']=dict(q,audit=3,stage='MEDIA_PRIVACY')
  audit=row['media_privacy'];row['round_privacy']={'common_end_verified':True,'pattern_count':len(audit['files']['counts']),'batches':[audit]}
  row['match_provenance']=[privacy_provenance.receipt(1,'files_and_journal',[b'a'*16,b'b'*16],audit['files'],audit['journal'])]
  row['playback_context']={'case':'NATIVE_HLS_CONTEXT_NO_GET','api_calls':1,'sources':1,'selected_hls_tag_match':True,'selected_https_hls_descriptors':1,'actions':0,'messages':0,'flavor_assets':1,'response_secret_coverage_complete':False,'delivery_authorized':False,'hls_fetched':False,'decoded':False,'full_acceptance':False}
  return row
 def parse(self,row):return r.public_rows((json.dumps(row)+'\n').encode())[0]
 def test_actual_public_rows_success_no_urlshape(self):
  row=self.row();self.assertNotIn('native_url_shape',row);result=self.parse(row);self.assertEqual(result['playback_context'],row['playback_context']);self.assertNotIn('native_url_shape',result)
 def test_extra_private_field_not_exported(self):
  row=self.row();row['unexpected']={'private':'SYNTHETIC_PRIVATE_VALUE'};result=self.parse(row);self.assertNotIn('SYNTHETIC_PRIVATE_VALUE',json.dumps(result))
 def test_source_privacy_context_rejections(self):
  for key in ['sources_before','media_privacy','round_privacy','playback_context','tls_transport','match_provenance']:
   row=self.row();row.pop(key);self.assertRaises(Exception,self.parse,row)
  row=self.row();row['media_privacy']['files']['counts'][0]=1;self.assertRaises(Exception,self.parse,row)
 def test_failure_path_fixed_privacy_code(self):
  row={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_code':'SOURCE_ROUTE_UNKNOWN_KEY','failure_stage':'API_ROUND','media_privacy_failure_class':'FINITE_SCAN_INCOMPLETE','media_privacy_failure_code':'COMMON_AUDIT_END_DRIFT'}
  result=self.parse(row);self.assertFalse(result['failure_privacy']['finite_scans_complete_and_zero']);self.assertEqual(result['failure_privacy']['code'],'COMMON_AUDIT_END_DRIFT')
 def test_pins_and_fresh_stage(self):
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((pathlib.Path(__file__).parent/n).read_bytes()).hexdigest(),pin)
  self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-context-observer-r3');self.assertIn('baseline-freeze-28018daf.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()

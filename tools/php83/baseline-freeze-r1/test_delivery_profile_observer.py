import json,hashlib,pathlib,unittest
import delivery_profile_observation as d
import prepare_delivery_profile_observer as p
import run_delivery_profile_observer as r
import test_context_capture
H=pathlib.Path(__file__).parent
class Tests(unittest.TestCase):
 def stored(self):return [['1001','0','61','0','1','0','applehttp','NULL',b'192.168.56.74:88/hls'.hex().upper()]]
 def test_selected_id_not_guessed(self):
  response={'objectType':'KalturaPlaybackContext','sources':[{'objectType':'KalturaPlaybackSource','format':'applehttp','flavorIds':'0_21p06l2j','deliveryProfileId':1234}]}
  self.assertEqual(d.selected(response),1234);self.assertIn('WHERE id=1234 LIMIT 2',d.query(1234))
 def test_closed_stored_shape(self):
  v=d.parse(self.stored(),1001);d.validate(v);self.assertEqual(v['port'],88);self.assertTrue(v['path_hls']);self.assertNotIn('192.168.56.74:88/hls',json.dumps(v))
 def test_reject_identity_or_sql_injection(self):
  for value in [True,'1001 OR 1=1',-1]:self.assertRaises(d.Rejected,d.query,value)
  self.assertRaises(d.Rejected,d.parse,self.stored(),1234)
  rows=self.stored();rows[0][1]='99';self.assertRaises(d.Rejected,d.parse,rows,1001)
 def row(self):
  row=test_context_capture.Tests().row();row['delivery_profile']=d.parse(self.stored(),1001);return row
 def test_full_success_capture(self):
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual(out['delivery_profile']['profile_id'],1001);self.assertNotIn('native_url_shape',out)
 def test_full_negative_capture(self):
  for key in ['delivery_profile','media_privacy','sources_before','playback_context']:
   row=self.row();row.pop(key);self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
  row=self.row();row['delivery_profile']['rawurl']='SECRET';self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
 def test_failed_projection(self):
  row={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'DELIVERY_PROFILE_OBSERVATION','delivery_profile':d.parse(self.stored(),1001)}
  self.assertIn('delivery_profile',r.public_rows(json.dumps(row).encode())[0])
 def test_pins_and_no_get(self):
  s=p.build();self.assertEqual(s,(H/'guest_delivery_profile_observer.py').read_text());self.assertNotIn('media_get443.request(',s);self.assertIn('captured_context[0]',s)
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),pin)
  self.assertIn('baseline-freeze-f101d171.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()

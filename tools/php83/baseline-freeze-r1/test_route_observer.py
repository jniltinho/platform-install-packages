import ast,copy,hashlib,json,pathlib,unittest
import route_descriptor as d
import prepare_route_observer as p
import run_route_observer as r
H=pathlib.Path(__file__).parent
class RouteTests(unittest.TestCase):
 def args(self):return dict(stored_path='/content/entry/data//0/1/0_wzmt2sfy_0_ewuu0o46_2.mp4',expected_filename=d.filename('private source name','Source','mp4'),secret='s'*32,ks='k'*32,candidates=[])
 def test_source_filename_byte_sanitizer(self):
  self.assertEqual(d.filename('entry name','Source','mp4'),'entry_name_(Source).mp4');self.assertEqual(d.filename('entry','0','mp4'),'entry.mp4');self.assertEqual(d.filename('é','', 'mp4'),'__.mp4')
 def test_serveflavor_descriptor_keeps_candidates(self):
  a=self.args();url='https://192.168.56.74/p/102/sp/10200/serveFlavor/entryId/0_wzmt2sfy/v/2/flavorId/0_ewuu0o46/fileName/'+a['expected_filename']+'/name/a.mp4';v=d.describe(url,**a)
  self.assertEqual(v['route_kind'],'SERVE_FLAVOR');self.assertTrue(v['source_serve_flavor_grammar']);self.assertTrue(v['filename_equal_expected']);self.assertFalse(v['direct_file_sync_path_equal']);self.assertIn('FILENAME',v['long_segment_roles']);self.assertEqual(a['candidates'],[a['expected_filename']]);self.assertNotIn(a['expected_filename'],json.dumps(d.validate(v)))
 def test_direct_and_other_not_guessed(self):
  a=self.args();v=d.describe('https://192.168.56.74'+a['stored_path'],**a);self.assertEqual(v['route_kind'],'DIRECT_CONTENT');self.assertTrue(v['direct_file_sync_path_equal'])
  v=d.describe('https://192.168.56.74/other/LONG_UNKNOWN_CANDIDATE',**self.args());self.assertEqual(v['route_kind'],'OTHER');self.assertFalse(v['source_serve_flavor_grammar']);self.assertEqual(v['get_requests'],0)
 def test_signed_or_wrong_identity_reported_not_exempted(self):
  a=self.args();v=d.describe('https://192.168.56.74/p/20/sp/2000/serveFlavor/entryId/0_aaaaaaaa/v/1/flavorId/0_bbbbbbbb/ks/'+a['ks']+'?sig=LONG_SIGNATURE_VALUE',**a)
  self.assertFalse(v['partner_equal']);self.assertFalse(v['owned_entry_equal']);self.assertTrue(v['credential_marker_present']);self.assertTrue(v['current_credential_present']);self.assertTrue(v['query_present']);self.assertFalse(v['candidate_patterns_exempted']);self.assertIn(a['ks'],a['candidates'])
 def test_closed_public_schema_no_values(self):
  v=d.describe('https://192.168.56.74/other',**self.args())
  for key,value in [('url','PRIVATE'),('route_kind','PRIVATE'),('long_segment_roles',['PRIVATE']),('get_requests',True)]:
   row=copy.deepcopy(v);row[key]=value;self.assertRaises(d.Rejected,d.validate,row)
 def test_frozen_sources_and_stage(self):
  self.assertEqual(p.build(),(H/'guest_route_observer.py').read_text())
  for name,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/name).read_bytes()).hexdigest(),pin)
  self.assertNotIn('media_get443.py',r.PINS);self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-route-observer-r1');self.assertIn('baseline-freeze-fb70dd4c.service',r.REMOTE_GUARD)
 def test_no_get_no_raw_url_persistence(self):
  s=p.build();tree=ast.parse(s)
  self.assertNotIn('media_get',s);self.assertNotIn('delivery.progressive',s);self.assertNotIn('protocol.run_round',s)
  private_calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='private_json']
  for call in private_calls:self.assertNotIn('raw_url',ast.unparse(call))
  self.assertIn("private_json(private_dir/'route-descriptor.json',report['route_observation'])",s);self.assertIn('rehearsal.patterns(secret,ks,tracked_tokens)',s)
 def test_fixed_join_schema_sql_and_sourcepins(self):
  self.assertTrue(p.QUERY.startswith('SELECT '));self.assertIn('FROM flavor_asset a LEFT JOIN flavor_params p ON p.id=a.flavor_params_id',p.QUERY);self.assertIn("a.id='0_ewuu0o46' AND a.partner_id=102 AND a.entry_id='0_wzmt2sfy' LIMIT 2",p.QUERY)
  self.assertIn('HEX(COALESCE(p.name',p.QUERY);self.assertIn('route_source_guard()',p.build());self.assertNotIn('save(',p.build())
if __name__=='__main__':unittest.main()

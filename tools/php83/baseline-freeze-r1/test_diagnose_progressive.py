import ast,json,pathlib,unittest
import diagnose_progressive as d
class DiagnosisTests(unittest.TestCase):
 def test_public_filename_shape_no_values(self):
  counts=d.blank();name='privacy-media-'+'a'*32+'-short360.mp4';d.classify(('/p/102/serveFlavor/entryId/0_wzmt2sfy/flavorId/0_ewuu0o46/fileName/'+name).encode(),counts)
  self.assertEqual(counts['owned_route_candidates'],1);self.assertEqual(counts['filename_long_segments'],1);self.assertEqual(counts['synthetic_filename_shape'],1);self.assertEqual(counts['other_long_segments'],0);self.assertNotIn(name,json.dumps(counts))
 def test_unknown_long_field_and_credentials_not_called_public(self):
  counts=d.blank();d.classify(b'/flavorId/0_ewuu0o46/ks/SYNTHETIC_PRIVATE_TOKEN?token=PRIVATE',counts)
  self.assertEqual(counts['credential_marker_candidates'],1);self.assertEqual(counts['query_candidates'],1);self.assertEqual(counts['other_long_segments'],1);self.assertEqual(counts['synthetic_filename_shape'],0);self.assertNotIn('PRIVATE',json.dumps(counts))
 def test_unrelated_logs_ignored_and_encoding(self):
  counts=d.blank();d.classify(b'/not-owned/ks/SYNTHETIC_PRIVATE_TOKEN',counts);self.assertEqual(counts['owned_route_candidates'],0)
  d.classify(b'/flavorId/0_ewuu0o46/%6b%73/SYNTHETIC_PRIVATE_TOKEN',counts);self.assertEqual(counts['credential_marker_candidates'],1)
 def test_sink_closed_allowlist(self):
  self.assertEqual(d.category('/var/lib/kaltura-baseline-tls-logs-r2/access.log'),'tls');self.assertEqual(d.category('/opt/kaltura/log/x'),'application')
  for name in ('/root/secret','/var/log/other','/opt/kaltura/log/../secret','relative'):self.assertRaises(d.Rejected,d.category,name)
 def test_bounded_and_no_network_or_credential_source(self):
  self.assertRaises(d.Rejected,d.classify,b'x'*65537,d.blank())
  text=pathlib.Path(d.__file__).read_text();tree=ast.parse(text)
  self.assertNotIn('mysql',text);self.assertNotIn('PostTransport',text);self.assertNotIn('urllib.request',text)
  self.assertIn('read_boundary(3)',text);self.assertIn('read_boundary(4)',text);self.assertIn('64*1024*1024',text);self.assertIn('time.monotonic()+10',text)
if __name__=='__main__':unittest.main()

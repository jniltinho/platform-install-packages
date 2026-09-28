import hashlib,json,pathlib,unittest
import diagnose_progressive_r2 as d
class RoleTests(unittest.TestCase):
 def observe(self,value):
  c=d.blank();d.classify(value,c);return c
 def test_owned_basename_hypothesis_only(self):
  c=self.observe(b'path=/opt/kaltura/web/content/entry/data/0_ewuu0o46_2.mp4')
  for key in ('filesystem_root_hint','content_path_hint','long_terminal','long_owned_asset_basename','long_contains_asset_id','other_long_segments'):self.assertEqual(c[key],1,key)
  self.assertEqual(c['filename_long_segments'],0);self.assertNotIn('0_ewuu0o46',json.dumps(c))
 def test_punctuation_not_silently_normalized(self):
  c=self.observe(b'path=/opt/kaltura/web/content/0_ewuu0o46_2.mp4);')
  self.assertEqual(c['long_owned_asset_basename'],0);self.assertEqual(c['long_owned_asset_basename_with_punctuation'],1);self.assertEqual(c['long_trailing_punctuation'],1)
 def test_source_filename_key_role(self):
  c=self.observe(b'https://192.168.56.74/p/102/serveFlavor/flavorId/0_ewuu0o46/fileName/privacy-media-'+b'a'*32+b'-short360.mp4')
  self.assertEqual(c['absolute_url_candidates'],1);self.assertEqual(c['serveflavor_hint'],1);self.assertEqual(c['filename_long_segments'],1);self.assertEqual(c['synthetic_filename_shape'],1);self.assertEqual(c['long_owned_asset_basename'],0)
 def test_unknown_value_stays_other(self):
  c=self.observe(b'/flavorId/0_ewuu0o46/other/SYNTHETIC_PRIVATE_UNKNOWN')
  self.assertEqual(c['long_after_other'],1);self.assertEqual(c['long_owned_asset_basename'],0);self.assertNotIn('PRIVATE',json.dumps(c))
 def test_fixed_predecessor_name_not_filename(self):
  c=self.observe(b'/flavorId/0_ewuu0o46/name/SYNTHETIC_FILENAME.mp4')
  self.assertEqual(c['long_after_name'],1);self.assertEqual(c['filename_long_segments'],0)
 def test_credential_marker_no_exemption(self):
  c=self.observe(b'/flavorId/0_ewuu0o46/ks/SYNTHETIC_PRIVATE_TOKEN?x=1')
  self.assertEqual(c['credential_marker_candidates'],1);self.assertEqual(c['query_candidates'],1);self.assertEqual(c['long_owned_asset_basename'],0)
 def test_reader_and_bounds_unchanged(self):
  h=pathlib.Path(d.__file__).parent;old=(h/'diagnose_progressive.py').read_text();new=pathlib.Path(d.__file__).read_text()
  self.assertEqual(hashlib.sha256(old.encode()).hexdigest(),'0d9f5a95a79938ecd5b146e8c35a42d0666a9be833d20b4ec0e50c0bb987729a')
  self.assertEqual(old[old.index('def read_boundary('):].replace('SAVED_START_FILE_WINDOW_SHAPES_OBSERVED','SAVED_START_FILE_WINDOW_ROLES_OBSERVED'),new[new.index('def read_boundary('):])
if __name__=='__main__':unittest.main()

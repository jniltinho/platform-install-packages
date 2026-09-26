import hashlib,importlib.util,json,pathlib,shutil,subprocess,tempfile,unittest
HERE=pathlib.Path(__file__).resolve().parent;REPO=HERE.parents[2]
s=importlib.util.spec_from_file_location('build',HERE/'build-held.py');build=importlib.util.module_from_spec(s);s.loader.exec_module(build)
class HeldTests(unittest.TestCase):
 def test_patch_applies_exactly(self):
  m=build.build()
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d)
   for x in m['changes']:
    target=root/x['path'];target.parent.mkdir(parents=True,exist_ok=True)
    if x['operation']=='modify':target.write_bytes((build.SOURCE/x['path']).read_bytes())
    r=subprocess.run(['patch','--batch','--forward','-p1','-i',str(REPO/x['patch'])],cwd=root,capture_output=True)
    self.assertEqual(r.returncode,0,(r.stdout,r.stderr));self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),x['after_sha256'])
 def test_no_application_selection(self):
  m=build.build();self.assertFalse(m['selected_in_artifact']);self.assertEqual([x['operation'] for x in m['changes']],['modify','modify','add'])
 def test_explicit_helper_require_and_startup_security(self):
  s=(HERE/'candidate-tree/alpha/config/kConf.php').read_text()
  self.assertIn("require_once __DIR__ . '/../../infra/general/kXmlEntityLoaderPolicy.php';",s)
  self.assertIn("stream_wrapper_unregister ('http');",s);self.assertIn("stream_wrapper_unregister ('https');",s)
  self.assertNotIn('libxml_disable_entity_loader',s)
 def test_finally_every_soap_entry(self):
  s=(HERE/'candidate-tree/infra/general/kSoapClient.php').read_text();self.assertEqual(s.count('finally {'),3);self.assertEqual(s.count('endSoapScope($scope, $error)'),3)
  self.assertIn('parent::__soapCall($function_name, $arguments)',s)
 def test_no_broad_null_override(self):
  s=(HERE/'candidate/kXmlEntityLoaderPolicy.php').read_text();self.assertNotIn('libxml_set_external_entity_loader(null)',s);self.assertIn('$previous === self::denyLoader()',s)
 def test_opaque_scope_state(self):
  s=(HERE/'candidate/kXmlEntityLoaderPolicy.php').read_text();self.assertIn('private static $scopes',s);self.assertIn('$token = new stdClass()',s);self.assertIn("['token'] !== $token",s)
 def test_native_warnings_not_suppressed(self):
  s=(HERE/'candidate/kXmlEntityLoaderPolicy.php').read_text();self.assertNotIn('@stream',s);self.assertNotIn('error_reporting(',s);self.assertNotIn('set_error_handler',s)
if __name__=='__main__':unittest.main()

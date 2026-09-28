import ast,hashlib,pathlib,subprocess,sys,tempfile,types,unittest
HERE=pathlib.Path(__file__).parent;original_path=list(sys.path);sys.path.insert(0,str(HERE.parent/'baseline-api'))
import run_https as r
from transport import Origin,PostTransport,BoundaryError
from guarded_http import trusted_context
sys.path[:]=original_path
class HTTPSTests(unittest.TestCase):
 def test_origin_exact8443_no_plain_or_foreign_fallback(self):
  origin=Origin('192.168.56.74','https',8443);self.assertEqual(origin.validate('https://192.168.56.74:8443/api_v3/index.php'),'https://192.168.56.74:8443/api_v3/index.php')
  for url in ('http://192.168.56.74/api_v3/index.php','https://192.168.56.20:8443/','https://192.168.56.74:8444/'):
   self.assertRaises(BoundaryError,origin.validate,url)
  self.assertRaises(BoundaryError,Origin,'192.168.56.20','https',8443);self.assertRaises(BoundaryError,Origin,'192.168.56.74','https',8444)
 def test_ca_required_and_exact(self):
  self.assertRaises(BoundaryError,PostTransport,Origin('192.168.56.74','https',8443))
  self.assertRaises(BoundaryError,trusted_context,b'WRONG_CA','5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef')
 def test_both_native_post_sites_are_tls_with_ca(self):
  tree=ast.parse((HERE/'guest_https.py').read_text());calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='PostTransport'];self.assertEqual(len(calls),2)
  for call in calls:
   self.assertEqual([ast.literal_eval(n) for n in call.args[0].args],['192.168.56.74','https',8443]);self.assertEqual(call.args[1].id,'tls_ca');self.assertEqual(ast.literal_eval(call.args[2]),'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef')
 def test_adapter_wrap_precedes_any_request_every_inventory(self):
  text=(HERE/'guest_https.py').read_text();self.assertLess(text.index('legacy.logs=lambda:tls_logs.extend(old_logs)'),text.index("report['phase']='invalid-nonce'"));self.assertLess(text.index('legacy.logs() # Mandatory'),text.index("Path('/root/kaltura-sanity.rc')"))
  tree=ast.parse(text);node=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='logs' for t in n.targets));calls=[];legacy=types.SimpleNamespace()
  scope={'legacy':legacy,'tls_logs':types.SimpleNamespace(extend=lambda f:calls.append(1) or f()+['TLS_PRIVATE']),'old_logs':lambda:['BASE']}
  exec(compile(ast.Module(body=[node],type_ignores=[]),'fixture','exec'),scope)
  for _ in range(3):self.assertEqual(legacy.logs(),['BASE','TLS_PRIVATE'])
  self.assertEqual(len(calls),3)
 def test_exact_adapter_and_guest_derivative(self):
  self.assertEqual(hashlib.sha256((HERE/'privacy_logs_r2.py').read_bytes()).hexdigest(),'d67eb65900c3134c91efaf94b18ba482b59261c81b0084de0cea3bcd37d5246c')
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'guest.py';v=subprocess.run([sys.executable,'-B',str(HERE/'prepare_https.py'),'--output',str(p)],capture_output=True);self.assertEqual(v.returncode,0);self.assertEqual(p.read_bytes(),(HERE/'guest_https.py').read_bytes())
  for name,pin in r.PINS.items():self.assertEqual(hashlib.sha256((HERE/name).read_bytes()).hexdigest(),pin)
 def test_fresh_stage_and_no_webwrite(self):
  self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-https100-r1');self.assertIn('assert not os.path.lexists(stage)',r.REMOTE_GUARD);self.assertNotIn('api_v3/web',r.unit_command('baseline-freeze-12345678'))
if __name__=='__main__':unittest.main()

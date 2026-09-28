import ast,hashlib,pathlib,sys,unittest
H=pathlib.Path(__file__).parent;old=list(sys.path);sys.path.insert(0,str(H.parent/'baseline-protocol'))
import media_get443 as get
import short_delivery443 as delivery
import run_progressive443 as runner
import prepare_progressive443 as prepare
sys.path[:]=old
class Port443Tests(unittest.TestCase):
 def test_exact_derivatives_and_all_pins(self):
  for name,value in prepare.sources().items():self.assertEqual((H/name).read_text(),value)
  for name,pin in runner.PINS.items():self.assertEqual(hashlib.sha256((H/name).read_bytes()).hexdigest(),pin)
 def test_native443_and_no_rewrite(self):
  for url in ('https://192.168.56.74/x','https://192.168.56.74:443/x'):
   self.assertEqual(delivery.target(url),url);self.assertEqual(get.validate(url,{'Accept-Encoding':'identity'},10).port,443)
  for url in ('https://192.168.56.74:8443/x','http://192.168.56.74/x','https://192.168.56.20/x','https://192.168.56.83/x','https://192.168.56.74:444/x'):
   self.assertRaises(Exception,delivery.target,url);self.assertRaises(Exception,get.validate,url,{'Accept-Encoding':'identity'},10)
 def test_api_still8443_same_ca(self):
  s=(H/'guest_progressive443.py').read_text();calls=[n for n in ast.walk(ast.parse(s)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='PostTransport'];self.assertEqual(len(calls),1)
  self.assertEqual([ast.literal_eval(v) for v in calls[0].args[0].args],['192.168.56.74','https',8443]);self.assertIn("native=native_call(service='flavorasset',action='getUrl',id=delivery.ASSET)",s);self.assertIn('url=delivery.target(native)',s)
  self.assertEqual(get.CA_PIN,'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef')
 def test_tls_inventory_privacy_and_absence_guard(self):
  s=(H/'guest_progressive443.py').read_text();self.assertIn('legacy.logs=lambda:tls_logs.extend(old_logs)',s);self.assertIn('audit_all(rehearsal.patterns(secret,ks,tracked_tokens),start,jstart)',s)
  self.assertEqual(runner.STAGE,'/var/lib/kaltura-baseline-short-progressive443-r1');self.assertIn('baseline-freeze-1dbf90f3.service',runner.REMOTE_GUARD);self.assertIn('assert not os.path.lexists(stage)',runner.REMOTE_GUARD)
 def test_wrong_ca_stays_rejected(self):self.assertRaises(Exception,get.request,b'wrong','https://192.168.56.74/x',{'Accept-Encoding':'identity'},10)
if __name__=='__main__':unittest.main()

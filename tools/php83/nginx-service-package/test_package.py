import pathlib,unittest
import prepare,build
E=pathlib.Path(__file__).resolve().parents[3]/'doc/php83/evidence/nginx-service-package-r1'
class Tests(unittest.TestCase):
 def sources(self):return (E/'postinst.before').read_bytes(),(E/'control.before').read_bytes()
 def test_exact_only_post_and_version(self):
  old,control=self.sources();helper=b'raise SystemExit(0)\n';hook,new=prepare.transform(old,control,helper,prepare.sha(helper))
  start=old.index(prepare.ANCHOR);self.assertEqual(hook[:start],old[:start]);self.assertTrue(hook.endswith(b'PILOT83_NGINX_DEPLOY_LAB3\ninvoke-rc.d kaltura-nginx restart\n'))
  self.assertEqual(new,control.replace(b'php83lab2',b'php83lab3'));self.assertEqual(hook.count(helper),1)
 def test_source_drift(self):
  h,c=self.sources();x=b'pass\n'
  for a,b in ((h+b'\n',c),(h,c+b'\n')):
   with self.assertRaises(ValueError):prepare.transform(a,b,x,prepare.sha(x))
 def test_helper_pin_and_framing(self):
  h,c=self.sources()
  for x,p in ((b'pass\n','a'*64),(b'pass',prepare.sha(b'pass')),(prepare.TAG+b'\n',prepare.sha(prepare.TAG+b'\n')),(b'\x00\n',prepare.sha(b'\x00\n'))):
   with self.assertRaises(ValueError):prepare.transform(h,c,x,p)
 def test_syntax_no_execution(self):
  h,c=self.sources();x=b'raise RuntimeError("must not run")\n';prepare.transform(h,c,x,prepare.sha(x))
  with self.assertRaises(SyntaxError):prepare.transform(h,c,b'if\n',prepare.sha(b'if\n'))
 def test_builder_rejects_wrong_package(self):
  with self.assertRaises(ValueError):build.derive(b'wrong',b'pass\n',prepare.sha(b'pass\n'))
if __name__=='__main__':unittest.main()

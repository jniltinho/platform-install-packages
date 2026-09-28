"""Local synthetic executors only: never execute an installer, MySQL or PHP app."""
import importlib.util,json,os,subprocess,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('hooks',HERE/'transform-hooks.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
class Tests(unittest.TestCase):
 def test_published_hook_pin(self):
  b=(h.ROOT/'deb/kaltura-db/debian/postinst').read_bytes();a,m=h.transform('kaltura-db','postinst',b)
  self.assertIn(b'pilot83_private_mysql',a);self.assertNotIn(b'rm -f $APP_DIR/log/kaltura-*.log',a)
  self.assertNotIn(b'# mysql -h$MYSQL_HOST',a);self.assertIn(b'pilot83_private_php',a)
  self.assertNotIn(b'\n\tphp ',a);self.assertTrue(m['changed_lines'])
 def test_mysql_database_argument_preserved(self):
  b=(h.ROOT/'deb/kaltura-base/debian/postinst').read_bytes();a,_=h.transform('kaltura-base','postinst',b)
  old=next(x for x in b.splitlines() if b"update mysql.user set password=PASSWORD(" in x)
  new=next(x for x in a.splitlines() if b"update mysql.user set password=PASSWORD(" in x)
  self.assertEqual(new,old.replace(b'| mysql ',b'| pilot83_private_mysql ',1));self.assertTrue(new.endswith(b' mysql'))
 def test_drop_branches_fail_closed(self):
  a,_=h.transform('kaltura-db','postinst',(h.ROOT/'deb/kaltura-db/debian/postinst').read_bytes())
  self.assertNotIn(b'kaltura-drop-db.sh',a);self.assertEqual(a.count(b'PRIVATE_PILOT_FRESH_DATABASE_REQUIRED'),2)
  for line in a.splitlines():
   if b'PRIVATE_PILOT_FRESH_DATABASE_REQUIRED' in line:
    p=subprocess.run(['bash','-c',line.decode()],capture_output=True);self.assertEqual(p.returncode,94)
 def test_source_failure_fails_closed(self):
  a,_=h.transform('kaltura-base','postinst',(h.ROOT/'deb/kaltura-base/debian/postinst').read_bytes())
  lines=[x for x in a.splitlines() if x.strip().startswith((b'. $KALTURA_FUNCTIONS_RC',b'. $KALTURA_PREFIX/bin/kaltura-functions.rc'))]
  self.assertEqual(len(lines),2)
  for line in lines:self.assertTrue(line.endswith(b' || exit 92'))
 def test_drift(self):
  with self.assertRaises(ValueError):h.transform('kaltura-db','postinst',b'changed')
 def test_unknown(self):
  with self.assertRaises(ValueError):h.transform('unknown','postinst',b'')
 def test_base_sensitive_sed_and_native_pin(self):
  a,_=h.transform('kaltura-base','postinst',(h.ROOT/'deb/kaltura-base/debian/postinst').read_bytes())
  self.assertIn(b's#@PHP_BIN@#/usr/bin/php8.3#g',a)
  for line in a.splitlines():
   if b'sed ' in line and any(x in line for x in [b'$DB1_PASS',b'$ADMIN_SECRET',b'${NEW_SECRETS']):self.assertIn(b'pilot83_private_sed ',line)
 def execute(self,invocation,status=0):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);capture=root/'capture.json';child=root/'child'
   child.write_text('#!/usr/bin/python3\nimport sys,pathlib,json,os\na=sys.argv[1:];p=next((x.split("=",1)[1] for x in a if x.startswith("--defaults-extra-file=")),None)\nif p is None:p=a[1] if a[0]=="-f" else a[-1]\nr={"argv":a,"content":pathlib.Path(p).read_text(),"mode":os.stat(p).st_mode&511,"path":p}\npathlib.Path('+repr(str(capture))+').write_text(json.dumps(r))\nprint("synthetic native failure",file=sys.stderr)\nsys.exit('+str(status)+')\n');child.chmod(0o700)
   source=(HERE/'private-hook-functions.sh').read_text().replace('/run/kaltura-pilot83-',d+'/private-').replace('/usr/bin/mysql',str(child)).replace('/usr/bin/sed',str(child)).replace('/usr/bin/php8.3',str(child))
   helper=root/'helper.sh';helper.write_text(source)
   p=subprocess.run(['bash','-c','set -e; source "$1"; '+invocation,'fixture',str(helper)],capture_output=True)
   row=json.loads(capture.read_text()) if capture.exists() else None
   self.assertFalse(list(root.glob('private-*')))
   return p,row
 def test_mysql_no_secret_argv_private_content(self):
  p,r=self.execute('pilot83_private_mysql -u fixture -pSynthetic_Secret -hlocalhost')
  self.assertEqual(p.returncode,0);self.assertNotIn('Synthetic_Secret',' '.join(r['argv']));self.assertIn('password="Synthetic_Secret"',r['content']);self.assertEqual(r['mode'],0o600)
 def test_mysql_failure_preserved_and_cleanup(self):
  p,r=self.execute('pilot83_private_mysql -pSynthetic_Secret',17);self.assertEqual(p.returncode,17);self.assertIn(b'synthetic native failure',p.stderr)
 def test_mysql_unsafe_password_rejected(self):
  p,r=self.execute("pilot83_private_mysql '-pbad\\secret'");self.assertEqual(p.returncode,92);self.assertIsNone(r)
 def test_mysql_defaults_injection_rejected(self):
  p,r=self.execute('pilot83_private_mysql --defaults-file=/tmp/other');self.assertEqual(p.returncode,92);self.assertIsNone(r)
 def test_mysql_duplicate_password_rejected(self):
  p,r=self.execute('pilot83_private_mysql -pOne -pTwo');self.assertEqual(p.returncode,92);self.assertIsNone(r)
 def test_sed_private_program_and_failure(self):
  p,r=self.execute("pilot83_private_sed -e 's#MARK#Synthetic_Secret#g' -i fixture",9)
  self.assertEqual(p.returncode,9);self.assertNotIn('Synthetic_Secret',' '.join(r['argv']));self.assertEqual(r['content'],'s#MARK#Synthetic_Secret#g\n');self.assertEqual(r['mode'],0o600)
 def test_php_nul_argv_transport_only(self):
  p,r=self.execute("pilot83_private_php /opt/kaltura/apps/create_playkit_uiconf.php 0 'Synthetic Secret' ''",12)
  self.assertEqual(p.returncode,12);self.assertNotIn('Synthetic Secret',' '.join(r['argv']));self.assertEqual(r['content'],'/opt/kaltura/apps/create_playkit_uiconf.php\x000\x00Synthetic Secret\x00\x00');self.assertEqual(r['mode'],0o600)
 def test_payload_helper_pin_and_message(self):
  p=h.ROOT/'doc/php83/evidence/pilot83/hooks-inputs/kaltura-postinst/opt/kaltura/bin/kaltura-functions.rc'
  a,m=h.transform_payload(h.PAYLOAD_PATH,p.read_bytes());self.assertEqual(len(m['changed_lines']),7)
  self.assertNotIn(b'connect with mysql -u$DB_USER -p$DB_PASSWD',a)
  self.assertIn(b'| pilot83_private_mysql -u$DB_USER',a)
  with self.assertRaises(ValueError):h.transform_payload(h.PAYLOAD_PATH,p.read_bytes()+b' ')
 def test_secret_only_sed(self):
  a,_=h.transform('kaltura-base','postinst',(h.ROOT/'deb/kaltura-base/debian/postinst').read_bytes())
  line=next(x for x in a.splitlines() if b's#@ADMIN_CONSOLE_PARTNER_ADMIN_SECRET@#$MINUS_2_PARTNER_ADMIN_SECRET' in x)
  self.assertIn(b'pilot83_private_sed',line)
 def test_sed_real_byte_semantics(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);helper=root/'helper';helper.write_text((HERE/'private-hook-functions.sh').read_text().replace('/run/kaltura-pilot83-',d+'/private-'))
   a=root/'before';a.write_text('MARK\nother\n')
   p=subprocess.run(['bash','-c','source "$1"; pilot83_private_sed -e "s#MARK#Synthetic_Secret#g" -i "$2"','fixture',str(helper),str(a)],capture_output=True)
   self.assertEqual(p.returncode,0);self.assertEqual(a.read_text(),'Synthetic_Secret\nother\n');self.assertFalse(list(root.glob('private-*')))
 def test_php_bridge_guards_static_not_native(self):
  source=(HERE/'private-argv.php').read_text()
  for value in ['fstat(',"['ino']", "['dev']",'unlink($privateArgumentPath)',"basename($argv[0]) !== 'create_playkit_uiconf.php'",'$_SERVER[\'argv\'] = $argv']:
   self.assertIn(value,source)
 def test_helper_syntax(self):
  p=subprocess.run(['bash','-n',str(HERE/'private-hook-functions.sh')],capture_output=True);self.assertEqual(p.returncode,0)
if __name__=='__main__':unittest.main()

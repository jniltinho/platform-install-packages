import io,json,pathlib,subprocess,tarfile,unittest
import execute_e as e

class Tests(unittest.TestCase):
 def contract(self):return {'schema':1,'phase':'E','status':'LAB_INCREMENTAL_AUTHORIZED','package':e.ROW.copy(),'full_acceptance':False,'release_authorized':False,'workers_policy':'HELD','pending':e.PENDING,'machine_id_sha256':e.MACHINE,'baseline_dpkg_sha256':e.BASELINE,'d3_terminal_sha256':e.D3_TERMINAL,'executor_sha256':'a'*64,'snapshot_sha256':'b'*64,'audit_since':'2026-09-28T04:30:00Z'}
 def test_contract(self):e.validate(self.contract())
 def test_wrong_cohort(self):
  for field,value in (('baseline_dpkg_sha256','c'*64),('release_authorized',True),('schema',True)):
   c=self.contract();c[field]=value
   with self.assertRaises(e.Failure):e.validate(c)
 def test_delta(self):
  before=b'a\t1\tall\tii \n';after=before+b'kaltura-server\t18.20.0-1+php83lab1\tall\tii \n';e.delta(before,after)
  with self.assertRaises(e.Failure):e.delta(before,after.replace(b'a\t1',b'a\t2'))
 def test_actual_pinned_hookless_package(self):
  package=pathlib.Path(__file__).resolve().parents[4]/'platform-install-packages-php83-artifacts/pilot83-private-r2/packages/kaltura-server_18.20.0-1+php83lab1_all.deb'
  self.assertEqual(e.sha(package.read_bytes()),e.ROW['sha256'])
  control=subprocess.check_output(['dpkg-deb','--ctrl-tarfile',str(package)]);data=subprocess.check_output(['dpkg-deb','--fsys-tarfile',str(package)]);self.assertTrue(e.hookless(control,data))
  with self.assertRaises(e.Failure):e.hookless(control,control)
 def test_hook_member_rejected(self):
  buffer=io.BytesIO()
  with tarfile.open(fileobj=buffer,mode='w') as archive:
   for name in ('.','./control','./md5sums','./postinst'):
    m=tarfile.TarInfo(name);m.type=tarfile.DIRTYPE if name=='.' else tarfile.REGTYPE;archive.addfile(m,io.BytesIO())
  with self.assertRaises(e.Failure):e.hookless(buffer.getvalue(),buffer.getvalue())
 def test_no_service_mutation_command(self):
  text=pathlib.Path(e.__file__).read_text()
  for verb in ("'start'","'restart'","'stop'","'reload'","'--force'"):self.assertNotIn(verb,text)
  self.assertIn("parser.add_argument('--check',action='store_true')",text)
if __name__=='__main__':unittest.main()

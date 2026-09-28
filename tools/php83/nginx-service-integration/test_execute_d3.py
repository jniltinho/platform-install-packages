import json,pathlib,tempfile,types,unittest
from unittest import mock
import execute_d3 as e

class Tests(unittest.TestCase):
 def contract(self):
  pins=json.loads((pathlib.Path(__file__).resolve().parents[3]/'doc/php83/evidence/nginx-service-package-r1/expected-installed-pins.json').read_text())
  return {'schema':1,'phase':'D3','status':'LAB_INCREMENTAL_AUTHORIZED','full_acceptance':False,'release_authorized':False,'workers_policy':'HELD','pending':e.PENDING,'package':dict(e.PACKAGE,sha256='c52b28cd2aa081a8254089cb5d32ab72b177975a95f5b23b021600cce375bc19'),'machine_id_sha256':e.MACHINE,'baseline_dpkg_sha256':e.BASELINE,'d2_terminal_sha256':e.D2_TERMINAL,'executor_sha256':'a'*64,'snapshot_sha256':'b'*64,'audit_since':'2026-09-28T04:30:00Z','installed_pins':pins}
 def test_actual43pins_contract(self):e.validate(self.contract())
 def test_wrong_package_pin(self):
  c=self.contract();c['package']['sha256']='c'*64
  with self.assertRaises(e.Failure):e.validate(c)
 def test_forbidden_release(self):
  c=self.contract();c['release_authorized']=True
  with self.assertRaises(e.Failure):e.validate(c)
 def test_exact_delta(self):
  before=b'other\t1\tall\tii \n';after=before+b'kaltura-nginx\t1.23.0-1+php83lab3\tamd64\tii \n'
  e.delta(before,after)
  with self.assertRaises(e.Failure):e.delta(before,after.replace(b'other\t1',b'other\t2'))
 def test_probe_retains_external_token_on_failure(self):
  token=b'SYNTHETIC_ONLY';client=mock.MagicMock();client.getresponse.return_value.status=500;client.getresponse.return_value.read.return_value=b''
  with mock.patch.object(e.http.client,'HTTPConnection',return_value=client):
   with self.assertRaises(e.Failure):e.probe(token)
  self.assertEqual(token,b'SYNTHETIC_ONLY');client.close.assert_called()
 def test_failure_logs_still_copied_and_later_files_scanned(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=pathlib.Path(tmp);sink=base/'kaltura-php83-nginx-log-sink';access=base/'kaltura-php83-nginx-access';sink.mkdir();access.mkdir();run=base/'receipt';run.mkdir()
   (sink/'events-0001.jsonl').write_bytes(b'UNSAFE_SYNTHETIC\n');(sink/'terminal.json').write_text('{"status":"FAILED","child_reaped":true}\n');(access/'access.log').write_bytes(b'404 123 0.001 45 1 GET\n')
   def path(value):return base/pathlib.Path(value).name
   def private(target,raw):target.write_bytes(raw)
   def reject(raw,canaries):
    if any(c in raw for c in canaries):raise ValueError('CANARY')
   d=types.SimpleNamespace(read_log=lambda p:p.read_bytes(),reject_canaries=reject)
   with mock.patch.object(e,'Path',side_effect=path),mock.patch.object(e,'RUN',run):
    paths,report=e.private_scans([b'UNSAFE_SYNTHETIC'],b'',None,types.SimpleNamespace(new_private=private),d,require_observed=False)
   self.assertEqual(len(paths),3);self.assertEqual(report['access_events'],1);self.assertFalse(report['checks_passed']);self.assertFalse(report['synthetic_probe_executed'])
 def test_source_contains_readonly_switch_and_fixed_error(self):
  raw=pathlib.Path(e.__file__).read_text();self.assertIn("parser.add_argument('--check',action='store_true')",raw);self.assertIn('failure_code',raw);self.assertNotIn('print(exc)',raw)
if __name__=='__main__':unittest.main()

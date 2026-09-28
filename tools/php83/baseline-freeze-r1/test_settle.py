import ast,hashlib,json,pathlib,subprocess,sys,tempfile,unittest
import settle
import run_untimed_r2 as r
HERE=pathlib.Path(__file__).parent
class SettleTests(unittest.TestCase):
 def clock(self):
  values=[0.0];return values,lambda:values[0],lambda n:values.__setitem__(0,values[0]+n)
 def test_two_seconds_quiet(self):
  v,clock,sleep=self.clock();result=settle.wait_quiet(lambda:'same',clock=clock,sleep=sleep);self.assertEqual(v[0],2);self.assertEqual(result['samples'],9)
 def test_async_growth_then_quiet_keeps_original_start(self):
  v,clock,sleep=self.clock();start={'fixed':'ORIGINAL_BOUNDARY'};saved=start.copy()
  result=settle.wait_quiet(lambda:int(v[0]) if v[0]<3 else 3,clock=clock,sleep=sleep);self.assertEqual(v[0],5);self.assertEqual(start,saved)
 def test_continuous_writer_rejected_at30(self):
  v,clock,sleep=self.clock();self.assertRaises(settle.Unsettled,settle.wait_quiet,lambda:v[0],clock=clock,sleep=sleep);self.assertEqual(v[0],30)
 def test_late_append_still_guarded_no_scanner_start_reset(self):
  text=(HERE/'guest_untimed_r2.py').read_text();self.assertIn("results=[audit(batch,start,jstart) for batch in batches]",text);self.assertIn("files.snapshot(legacy.logs())==cutoff and journal.snapshot()==jcut",text)
  between=text.split("failure_stage='QUIET_SETTLE'",1)[1].split("report['media_privacy']",1)[0];self.assertNotIn('start=',between);self.assertNotIn('jstart=',between)
 def test_late_append_new_guest_function_rejects(self):
  import types
  tree=ast.parse((HERE/'guest_untimed_r2.py').read_text());fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='audit_all')
  for journal_drift in (False,True):
   marks={'fixed':types.SimpleNamespace(size=4)};later={'fixed':types.SimpleNamespace(size=5)}
   files=iter([marks,marks if journal_drift else later]);journal=iter(['SYNTHETIC_CURSOR','CHANGED' if journal_drift else 'SYNTHETIC_CURSOR'])
   scope={'files':types.SimpleNamespace(snapshot=lambda x:next(files)),'journal':types.SimpleNamespace(snapshot=lambda:next(journal)),'legacy':types.SimpleNamespace(logs=lambda:[]),'audit':lambda *args:{'files':{'end_offsets':{'fixed':4}}},'need':lambda value,code:None if value else (_ for _ in ()).throw(ValueError(code))}
   exec(compile(ast.Module(body=[fn],type_ignores=[]),'fixture','exec'),scope);self.assertRaises(ValueError,scope['audit_all'],[[b'a'*16,b'b'*16]],{},None)
 def test_fixed_failure_projection(self):
  row={'failure_code':'FILES_UNDRAINED_TAIL','failure_stage':'MEDIA_PRIVACY','privacy_errors':[{'phase':'files_initial','code':'UNDRAINED_TAIL','audit':3}]};self.assertEqual(r.failure_projection(row)['failure_stage'],'MEDIA_PRIVACY')
  row['failure_code']='SYNTHETIC_SECRET';self.assertRaises(Exception,r.failure_projection,row)
 def test_reproducible_newstage_pins(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'guest.py';result=subprocess.run([sys.executable,'-B',str(HERE/'prepare_untimed_r2.py'),'--output',str(p)],capture_output=True);self.assertEqual(result.returncode,0);self.assertEqual(p.read_bytes(),(HERE/'guest_untimed_r2.py').read_bytes())
  for name,pin in r.PINS.items():self.assertEqual(hashlib.sha256((HERE/name).read_bytes()).hexdigest(),pin)
  self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-untimed100-r2')
if __name__=='__main__':unittest.main()

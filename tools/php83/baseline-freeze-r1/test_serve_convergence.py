import ast,hashlib,pathlib,types,unittest
import convergence as c
import prepare_serve_progressive_r2 as p
import run_serve_progressive_r2 as r
from test_progressive_join_r2 import QuietAuditTests,Rejected,need
H=pathlib.Path(__file__).parent
class Tests(unittest.TestCase):
 def context(self,counts=None,always=False):
  _,scope,events,start,jstart=QuietAuditTests().context()
  n=[0];saved=[]
  def scan(s,patterns,**kw):
   self.assertIs(s,start);n[0]+=1;size=n[0] if always else (1 if n[0]==1 else 2)
   return {'counts':counts if counts and n[0]==2 else [0,0],'status':'COMPLETE_FINITE_FILE_WINDOW','uncovered_tail_bytes':0,'end_offsets':{'x':size}}
  scope['files'].scan_window=scan;scope['convergence']=c;scope['record_match']=lambda *args:saved.append(args)
  tree=ast.parse(p.build());accepted=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='accepted');main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main');funcs=[next(x for x in ast.walk(main) if isinstance(x,ast.FunctionDef) and x.name==name) for name in ('audit_once','audit')]
  factory=ast.parse('def factory():\n audit_number=0\n return None').body[0];factory.body=[factory.body[0]]+funcs+[ast.Return(ast.Name('audit',ast.Load()))]
  exec(compile(ast.fix_missing_locations(ast.Module([accepted,factory],[])),'actual-convergence','exec'),scope)
  return scope['factory'](),scope,start,jstart,n,saved
 def test_actual_retry_same_starts(self):
  f,s,a,b,n,saved=self.context();f([b'a'*16,b'b'*16],a,b);self.assertEqual(n[0],4);self.assertEqual(a['original'].size,0);self.assertEqual([v[-1] for v in saved],[1,1,2,2])
 def test_late_positive_before_tail_retry(self):
  f,s,a,b,n,saved=self.context([1,0])
  with self.assertRaisesRegex(Rejected,'PRIVATE_MARKER_LOGGED'):f([b'a'*16,b'b'*16],a,b)
  self.assertEqual(n[0],2);self.assertEqual(saved[-1][2]['counts'],[1,0])
 def test_continuous_append_max_three(self):
  f,s,a,b,n,saved=self.context(always=True)
  with self.assertRaisesRegex(Rejected,'AUDIT_CONVERGENCE_EXHAUSTED'):f([b'a'*16,b'b'*16],a,b)
  self.assertEqual(n[0],6)
 def test_other_errors_never_retry(self):
  for code in ['FILES_UNDRAINED_TAIL','FILES_IDENTITY_CHANGED','FILES_TRUNCATED','COMMON_AUDIT_END_DRIFT','PRIVATE_MARKER_LOGGED']:
   calls=[]
   def operation():calls.append(1);raise Rejected(code)
   with self.assertRaisesRegex(Rejected,code):c.run(operation,Rejected)
   self.assertEqual(len(calls),1)
 def test_deadline(self):
  times=iter([0,0,211]);calls=[]
  with self.assertRaisesRegex(c.Exhausted,'DEADLINE'):c.run(lambda:calls.append(1),Rejected,clock=lambda:next(times))
  self.assertEqual(calls,[1])
 def test_early_positive_retained_no_journal(self):
  f,s,a,b,n,saved=self.context();s['files'].scan_window=lambda *a,**k:{'counts':[1,0]}
  s['journal'].scan_window=lambda *a: self.fail('journal should not run')
  with self.assertRaisesRegex(Rejected,'PRIVATE_MARKER_LOGGED'):f([b'a'*16,b'b'*16],a,b)
  self.assertEqual(saved[0][2]['counts'],[1,0]);self.assertNotIn('complete',saved[0][3])
 def test_regeneration_pins_and_common_end(self):
  self.assertEqual(p.build(),(H/'guest_serve_progressive_r2.py').read_text())
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),pin)
  self.assertIn('files.snapshot(legacy.logs())==cutoff and journal.snapshot()==jcut',p.build())
  self.assertIn('baseline-freeze-041e9c7b.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()

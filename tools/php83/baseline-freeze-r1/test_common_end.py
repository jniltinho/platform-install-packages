import unittest,dataclasses,copy,ast,json,hashlib
from pathlib import Path
import common_end as c
@dataclasses.dataclass(frozen=True)
class Mark:device:int=1;inode:int=2;size:int=3;mtime_ns:int=4
@dataclasses.dataclass(frozen=True)
class Journal:boot:str='boot';token:str='cursor'
def snap(size=3,mtime=None,token='cursor',inode=2):return {'/private/log':Mark(size=size,mtime_ns=size+1 if mtime is None else mtime,inode=inode)},Journal(token=token)
def result(size=3,count=2):return {'files':{'counts':[0]*count,'status':'COMPLETE_FINITE_FILE_WINDOW','uncovered_tail_bytes':0,'end_offsets':{'/private/log':size}},'journal':{'counts':[0]*count,'status':'COMPLETE_FINITE_JOURNAL_WINDOW','complete':True,'cutoff_covered':True}}
class Tests(unittest.TestCase):
 def run_case(self,snapshots,results,batches=None):
  snapshots=iter(snapshots);results=iter(results);calls=[];diags=[];start,jstart=object(),object()
  def audit(b,s,j):self.assertIs(s,start);self.assertIs(j,jstart);calls.append(b);v=next(results);(None if not isinstance(v,Exception) else self.throw(v));return v
  run=lambda:c.run(batches or [[b'a',b'b']],start,jstart,snapshot=lambda:next(snapshots),quiet=lambda:None,audit_once=audit,emit=diags.append,clock=lambda:0)
  return run,calls,diags
 def throw(self,e):raise e
 def test_stable_one_sweep(self):
  run,calls,d=self.run_case([snap(),snap()],[result()]);self.assertTrue(run()['common_end_verified']);self.assertEqual(len(calls),1);self.assertEqual(d[-1]['classification'],'STABLE')
 def test_append_repeats_all_batches_same_originals(self):
  batches=[[b'a',b'b'],[b'c',b'd']];run,calls,d=self.run_case([snap(),snap(4),snap(4),snap(4)],[result(),result(4),result(4),result(4)],batches);run();self.assertEqual(calls,batches+batches);self.assertEqual([x['classification'] for x in d],['APPEND_ONLY','STABLE'])
 def test_journal_advance_repeated(self):
  run,calls,d=self.run_case([snap(),snap(token='next'),snap(token='next'),snap(token='next')],[result(),result()]);run();self.assertTrue(d[0]['journal_advanced'])
 def test_continuous_append_exhaustion(self):
  run,calls,d=self.run_case([snap(3),snap(4),snap(4),snap(5),snap(5),snap(6)],[result(3),result(4),result(5)])
  with self.assertRaisesRegex(c.Rejected,'EXHAUSTED'):run()
  self.assertEqual(len(calls),3)
 def test_positive_sticky_no_snapshot_retry(self):
  v=result();v['files']['counts'][0]=1;run,calls,d=self.run_case([snap()],[v])
  with self.assertRaisesRegex(c.Rejected,'POSITIVE'):run()
  self.assertEqual(len(calls),1)
  v=result();v['journal']['counts'][0]=1;run,calls,d=self.run_case([snap()],[v]);self.assertRaises(c.Rejected,run)
 def test_opaque_incomplete_no_retry(self):
  run,calls,d=self.run_case([snap()],[RuntimeError('UNDRAINED_TAIL')]);self.assertRaises(RuntimeError,run);self.assertEqual(len(calls),1)
 def test_unsafe_identity_truncate_rewrite_boot(self):
  for end in [snap(inode=9),snap(2),snap(mtime=20),({'/private/log':Mark()},Journal(boot='different'))]:
   run,calls,d=self.run_case([snap(),end],[result()]);self.assertRaises(c.Rejected,run);self.assertEqual(len(calls),1);self.assertEqual(d[-1]['classification'],'UNSAFE')
 def test_offset_outside_current_window_rejected(self):
  for size in (2,10):
   run,_,_=self.run_case([snap(),snap(4)],[result(size)]);self.assertRaises(c.Rejected,run)
 def test_deadline_finite(self):
  clock=iter([0,701]);self.assertRaises(c.Rejected,c.run,[[b'a',b'b']],None,None,snapshot=lambda:None,quiet=lambda:None,audit_once=lambda *a:None,emit=lambda x:None,clock=lambda:next(clock))
 def test_closed_diagnostics(self):
  v={'attempt':1,'classification':'STABLE','file_appends':0,'journal_advanced':False,'offset_batches_changed':0};self.assertEqual(c.validate_diagnostic(v),v);v['path']='PRIVATE';self.assertRaises(c.Rejected,c.validate_diagnostic,v)

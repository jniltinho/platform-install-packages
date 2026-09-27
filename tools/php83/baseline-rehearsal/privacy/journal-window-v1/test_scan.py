import importlib.util,json,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
s=importlib.util.spec_from_file_location('journal_scan',Path(__file__).with_name('scan.py'));m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
P=b'SYNTHETIC_TRACE_ARGUMENT_4F83_ONLY'
def row(c,message='safe',boot='boot'):
 return {'__CURSOR':c,'_BOOT_ID':boot,'MESSAGE':message}
def raw(*rows):return b''.join(json.dumps(r).encode()+b'\n' for r in rows)
class Tests(unittest.TestCase):
 def scan(self,outputs,**kwargs):
  iterator=iter(outputs)
  def fetch(args,budget):
   data=next(iterator);budget.bytes+=len(data);m.need(budget.bytes<=budget.limits.bytes,'BYTE_LIMIT');return data
  with patch.object(m,'_fetch',side_effect=fetch):
   return m.scan_window(m.Cursor('a','boot'),[P,P[:15]],limits=m.Limits(**kwargs))
 def test_private_snapshot(self):
  with patch.object(m,'_fetch',return_value=raw(row('private-cursor'))):c=m.snapshot()
  self.assertEqual(c.token,'private-cursor');self.assertNotIn('private',repr(c))
 def test_cutoff_decode_and_exclude_start(self):
  report=self.scan([raw(row('b')),raw(row('a',P.decode()),row('b',[list(P),P.decode()])),raw(row('b'))])
  self.assertEqual(report['counts'],[2,2]);self.assertEqual(report['records'],1)
  self.assertNotIn('cursor',json.dumps(report));self.assertFalse(report['privacy_acceptance'])
 def test_missing_anchor(self):
  with self.assertRaisesRegex(m.Incomplete,'START_CURSOR_MISSING'):
   self.scan([raw(row('b')),raw(row('x'),row('b'))])
 def test_missing_end(self):
  with self.assertRaisesRegex(m.Incomplete,'END_CURSOR_MISSING'):
   self.scan([raw(row('c')),raw(row('a'),row('b'))])
 def test_drain_not_double_count(self):
  r=self.scan([raw(row('b')),raw(row('a'),row('b',P.decode()),row('c',P.decode())),raw(row('c')),raw(row('c')),raw(row('b',P.decode()),row('c',P.decode())),raw(row('c'))])
  self.assertEqual(r['counts'],[2,2]);self.assertEqual(r['rounds'],2)
 def test_observed_tail_disappeared(self):
  with self.assertRaisesRegex(m.Incomplete,'TAIL_REGRESSED'):
   self.scan([raw(row('b')),raw(row('a'),row('b'),row('c',P.decode())),raw(row('b'))])
 def test_observed_suffix_missing_next_round(self):
  with self.assertRaisesRegex(m.Incomplete,'OBSERVED_TAIL_MISSING'):
   self.scan([raw(row('b')),raw(row('a'),row('b'),row('c',P.decode()),row('d')),raw(row('d')),raw(row('d')),raw(row('b'),row('d'))])
 def test_suffix_boot_duplicate_invalid(self):
  for suffix in [[row('c',boot='other')],[row('c'),row('c')]]:
   with self.assertRaisesRegex(m.Incomplete,'CURSOR_CONTINUITY'):
    self.scan([raw(row('b')),raw(row('a'),row('b'),*suffix)])
 def test_latest_snapshot_highwater_not_discarded(self):
  with self.assertRaisesRegex(m.Incomplete,'OBSERVED_CURSOR_MISSING'):
   self.scan([raw(row('b')),raw(row('a'),row('b')),raw(row('c',P.decode())),raw(row('b')),raw(row('b')),raw(row('b'))])
 def test_snapshot_highwater_normal_drain(self):
  r=self.scan([raw(row('b')),raw(row('a'),row('b')),raw(row('c',P.decode())),raw(row('c')),raw(row('b'),row('c',P.decode())),raw(row('c'))])
  self.assertEqual(r['counts'],[1,1]);self.assertEqual(r['records'],2)
 def test_tail_incomplete(self):
  with self.assertRaisesRegex(m.Incomplete,'UNDRAINED_JOURNAL_TAIL'):
   self.scan([raw(row('b')),raw(row('a'),row('b')),raw(row('c'))],rounds=1)
 def test_boot_change(self):
  with self.assertRaisesRegex(m.Incomplete,'BOOT_CHANGED'):self.scan([raw(row('b',boot='other'))])
 def test_duplicate_sequence(self):
  with self.assertRaisesRegex(m.Incomplete,'CURSOR_CONTINUITY'):
   self.scan([raw(row('c')),raw(row('a'),row('b'),row('b'),row('c'))])
 def test_null_truncation_and_bad_encoding(self):
  for value in [None,[],[256],True]:
   with self.subTest(value=value),self.assertRaises(m.Incomplete):
    self.scan([raw(row('b')),raw(row('a'),row('b',value)),raw(row('b'))])
 def test_bytes_and_records(self):
  with self.assertRaisesRegex(m.Incomplete,'BYTE_LIMIT'):self.scan([raw(row('b'))],bytes=1)
  with self.assertRaisesRegex(m.Incomplete,'RECORD_LIMIT'):self.scan([raw(row('b')),raw(row('a'),row('b'))],records=1)
 def test_empty_malformed_duplicate_fields(self):
  for data in [b'',b'{bad}\n',b'{"__CURSOR":"a","__CURSOR":"b","_BOOT_ID":"boot"}\n']:
   with patch.object(m,'_fetch',return_value=data),self.assertRaises(m.Incomplete):m.snapshot()
 def test_private_process_error(self):
  with patch.object(m.subprocess,'run',side_effect=ValueError(P.decode())):
   with self.assertRaises(m.Incomplete) as e:m.snapshot()
  self.assertEqual(str(e.exception),'SNAPSHOT_FAILED');self.assertNotIn(P.decode(),str(e.exception))
 def test_runner_exit_stderr_timeout(self):
  for mode in ['exit','stderr','timeout']:
   def run(args,**kw):
    if mode=='timeout':raise subprocess.TimeoutExpired(args,1)
    if mode=='stderr':kw['stderr'].write(P)
    return SimpleNamespace(returncode=2 if mode=='exit' else 0)
   with patch.object(m.subprocess,'run',side_effect=run),self.assertRaises(m.Incomplete):m.snapshot()
 def test_runner_private_output_and_switches(self):
  def run(args,**kw):
   self.assertIn('--all',args);self.assertIn('--lines=1',args)
   self.assertEqual(__import__('os').fstat(kw['stdout'].fileno()).st_mode & 0o777,0o600)
   self.assertTrue(callable(kw['preexec_fn']));kw['stdout'].write(raw(row('a')))
   return SimpleNamespace(returncode=0)
  with patch.object(m.subprocess,'run',side_effect=run):self.assertEqual(m.snapshot().token,'a')
 def test_deadline(self):
  with patch.object(m.time,'monotonic',side_effect=[0,100]),self.assertRaisesRegex(m.Incomplete,'DEADLINE'):m.snapshot()
if __name__=='__main__':unittest.main()

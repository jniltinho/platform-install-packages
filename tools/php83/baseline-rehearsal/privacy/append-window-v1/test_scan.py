import importlib.util
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

s = importlib.util.spec_from_file_location('append_scan', Path(__file__).with_name('scan.py'))
a = importlib.util.module_from_spec(s);sys.modules[s.name] = a;s.loader.exec_module(a)
P = b'SYNTHETIC_TRACE_ARGUMENT_4F83_ONLY'

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.file=self.root/'log';self.file.write_bytes(b'historical '+P+b'\n')
        self.start=a.snapshot([self.file]);self.inventory=lambda: sorted(self.root.iterdir())
    def tearDown(self):self.tmp.cleanup()
    def append(self,data):
        with self.file.open('ab') as f:f.write(data)
    def scan(self,**kw):return a.scan_window(self.start,[P,P[:15]],inventory=self.inventory,limits=a.Limits(chunk=7,quiet_seconds=0,**kw))
    def test_historical_excluded_new_overlap_counted(self):
        self.append(b'xx'+P+b'yy'+P)
        r=self.scan();self.assertEqual(r['counts'],[2,2]);self.assertEqual(r['scanned_bytes'],len(b'xx'+P+b'yy'+P))
        self.assertFalse(r['privacy_acceptance']);self.assertFalse(r['future_writes_covered'])
    def test_reusable_snapshot(self):
        self.append(P);self.assertEqual(self.scan()['counts'],[1,1]);self.append(P)
        self.assertEqual(self.scan()['counts'],[2,2]);self.assertEqual(self.start[str(self.file)].size,len(b'historical '+P+b'\n'))
    def test_empty_window(self):self.assertEqual(self.scan()['counts'],[0,0])
    def test_overlap_across_drain_round(self):
        self.append(P[:13]);calls=0
        def inventory():
            nonlocal calls
            calls+=1
            if calls==2:self.append(P[13:])
            return [self.file]
        self.inventory=inventory
        r=self.scan();self.assertEqual(r['counts'],[1,1]);self.assertEqual(r['rounds'],2)
    def test_append_during_quiet(self):
        with patch.object(a.time,'sleep',side_effect=lambda _:self.append(b'x')):
            with self.assertRaisesRegex(a.Incomplete,'UNDRAINED_TAIL'):self.scan(rounds=2)
    def test_truncate(self):
        self.file.write_bytes(b'')
        with self.assertRaisesRegex(a.Incomplete,'TRUNCATED'):self.scan()
    def test_rotation(self):
        self.file.rename(self.root/'rotated');self.file.write_bytes(b'new')
        with self.assertRaises(a.Incomplete):self.scan()
    def test_path_swap_same_size(self):
        size=self.file.stat().st_size;self.file.rename(self.root/'old');self.file.write_bytes(b'x'*size)
        self.inventory=lambda:[self.file]
        with self.assertRaisesRegex(a.Incomplete,'IDENTITY_CHANGED'):self.scan()
    def test_same_size_rewrite(self):
        size=self.file.stat().st_size;self.file.write_bytes(b'x'*size)
        os.utime(self.file,ns=(1,self.start[str(self.file)].mtime_ns+1))
        with self.assertRaisesRegex(a.Incomplete,'REWRITTEN'):self.scan()
    def test_new_sink(self):
        (self.root/'new').write_bytes(b'')
        with self.assertRaisesRegex(a.Incomplete,'INVENTORY_CHANGED'):self.scan()
    def test_symlink(self):
        self.file.unlink();self.file.symlink_to('/dev/null')
        with self.assertRaisesRegex(a.Incomplete,'SYMLINK'):self.scan()
    def test_hardlink(self):
        os.link(self.file,self.root/'other')
        with self.assertRaisesRegex(a.Incomplete,'UNSAFE_FILE'):self.scan()
    def test_fifo_nonblocking(self):
        self.file.unlink();os.mkfifo(self.file)
        with self.assertRaisesRegex(a.Incomplete,'UNSAFE_FILE'):self.scan()
    def test_byte_limit(self):
        self.append(P)
        with self.assertRaisesRegex(a.Incomplete,'BYTE_LIMIT'):self.scan(bytes=8)
    def test_deadline(self):
        with patch.object(a.time,'monotonic',side_effect=[0,20]):
            with self.assertRaisesRegex(a.Incomplete,'DEADLINE'):self.scan(seconds=1)
    def test_no_secret_in_errors(self):
        def inventory():raise ValueError(P.decode())
        with self.assertRaises(a.Incomplete) as e:a.scan_window(self.start,[P],inventory=inventory)
        self.assertEqual(str(e.exception),'SCAN_FAILED')
    def test_invalid_limits(self):
        for bad in [a.Limits(bytes=True),a.Limits(seconds=float('inf')),a.Limits(rounds=0)]:
            with self.assertRaises(a.Incomplete):a.scan_window(self.start,[P],inventory=self.inventory,limits=bad)
    def test_empty_patterns_inventory_and_closure(self):
        for patterns in [[],[b'short'],['not bytes']]:
            with self.assertRaises(a.Incomplete):a.scan_window(self.start,patterns,inventory=self.inventory)
        with self.assertRaises(a.Incomplete):a.snapshot([])
        with self.assertRaises(a.Incomplete):a.snapshot([self.file,self.file])
    def test_swap_while_reading_detected(self):
        self.append(P);calls=0
        def inventory():
            nonlocal calls
            calls+=1
            if calls==2:
                self.file.rename(self.root/'old');self.file.write_bytes(b'x'*100)
            return [self.file]
        self.inventory=inventory
        with self.assertRaisesRegex(a.Incomplete,'IDENTITY_CHANGED'):self.scan()
    def test_growth_after_cutoff_is_drained_not_hidden(self):
        self.append(b'a');calls=0
        def inventory():
            nonlocal calls
            calls+=1
            if calls==2:self.append(P)
            return [self.file]
        self.inventory=inventory
        r=self.scan();self.assertEqual(r['counts'],[1,1]);self.assertEqual(r['uncovered_tail_bytes'],0)
    def test_observed_growth_then_shrink_above_cutoff(self):
        self.append(b'x');calls=0;opened=False;native_open=a.os.open
        def open_with_growth(*args,**kwargs):
            nonlocal opened
            if not opened:
                opened=True;self.append(P)
            return native_open(*args,**kwargs)
        def inventory():
            nonlocal calls
            calls+=1
            if calls==2:
                with self.file.open('r+b') as f:f.truncate(self.start[str(self.file)].size+2)
            return [self.file]
        self.inventory=inventory
        with patch.object(a.os,'open',side_effect=open_with_growth):
            with self.assertRaisesRegex(a.Incomplete,'TRUNCATED'):self.scan()
    def test_dense_matches_check_deadline_inside_loop(self):
        self.append(b'a'*20000)
        ticks=[]
        def clock():
            ticks.append(1)
            return 0 if len(ticks)<10 else 100
        with patch.object(a.time,'monotonic',side_effect=clock):
            with self.assertRaisesRegex(a.Incomplete,'DEADLINE'):
                a.scan_window(self.start,[b'a'*8],inventory=self.inventory,
                              limits=a.Limits(chunk=20000,seconds=1,quiet_seconds=0))
        self.assertEqual(len(ticks),10)
    def test_missing_file(self):
        self.file.unlink()
        with self.assertRaises(a.Incomplete):self.scan()

if __name__=='__main__':unittest.main()

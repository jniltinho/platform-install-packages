from contextlib import nullcontext
import fcntl
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import offline_decode as d

class Tests(unittest.TestCase):
    def test_wrong_size(self):
        for v in (b'', 'url', bytearray(d.SIZE)):
            with self.assertRaises(d.Rejected): d.decode(v)
    def test_wrong_hash(self):
        with self.assertRaisesRegex(d.Rejected, 'MEDIA_PIN'): d.decode(b'x'*d.SIZE)
    def test_sealed(self):
        fd=d.sealed(b'abc','test')
        try:
            self.assertEqual(os.read(fd,3),b'abc')
            with self.assertRaises(OSError): os.write(fd,b'x')
            self.assertTrue(fcntl.fcntl(fd,fcntl.F_GET_SEALS)&fcntl.F_SEAL_WRITE)
        finally: os.close(fd)
    def test_pin(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x';p.write_bytes(b'abc')
            self.assertEqual(d.pinned(str(p),hashlib.sha256(b'abc').hexdigest(),4),b'abc')
            with self.assertRaises(d.Rejected): d.pinned(str(p),'0'*64,4)
            with self.assertRaises(d.Rejected): d.pinned(str(p),'0'*64,2)
            q=Path(t)/'link';q.symlink_to(p)
            with self.assertRaises(OSError): d.pinned(str(q),'0'*64,4)
    def child(self, script, **patches):
        # Synthetic shell exercises runner lifecycle, not public decoder API.
        exe=d.sealed(Path('/usr/bin/dash').read_bytes(),'test-shell');media=d.sealed(b'x','test-media')
        try:
            with (patch.multiple(d,**patches) if patches else nullcontext()): return d.run(exe,['-c',script],media)
        finally: os.close(exe);os.close(media)
    def test_child_success(self): self.assertEqual(self.child('printf ok'),b'ok')
    def test_leader_unreaped_at_group_cleanup(self):
        original = os.killpg
        observed = []
        def check(pid, sig):
            row = os.waitid(os.P_PID, pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            observed.append(row is not None and row.si_pid == pid)
            return original(pid, sig)
        with patch.object(d.os, 'killpg', side_effect=check):
            self.assertEqual(self.child('printf ok'), b'ok')
        self.assertEqual(observed, [True])
    def test_child_exit(self):
        with self.assertRaisesRegex(d.Rejected,'DECODER_EXIT'): self.child('exit 2')
    def test_child_stderr(self):
        with self.assertRaisesRegex(d.Rejected,'DECODER_STDERR'): self.child('printf error >&2')
    def test_output_limit(self):
        with self.assertRaisesRegex(d.Rejected,'OUTPUT_LIMIT'): self.child('while :; do printf 123456789; done', CAP=20)
    def test_timeout(self):
        with self.assertRaisesRegex(d.Rejected,'TIME_LIMIT'): self.child('sleep 10',WALL=.05)

if __name__=='__main__': unittest.main()

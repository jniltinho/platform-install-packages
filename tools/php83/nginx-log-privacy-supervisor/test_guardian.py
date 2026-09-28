import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest import mock
import guardian as g

path=Path(__file__).resolve().parents[1]/'nginx-log-privacy/sanitizer.py'
spec=importlib.util.spec_from_file_location('privacy_sanitizer',path)
san=importlib.util.module_from_spec(spec);spec.loader.exec_module(san)
CANARY=b'PRIVATE_SYNTHETIC_SUPERVISOR_CANARY'

class Tests(unittest.TestCase):
    def fixture(self,root,body,**kw):
        binary=root/'fake-nginx';config=root/'nginx.conf'
        binary.write_text('#!/usr/bin/python3\n'+body);binary.chmod(0o700);config.write_text('fixture');config.chmod(0o600)
        pins=tuple((str(p),hashlib.sha256(p.read_bytes()).hexdigest()) for p in (binary,config))
        return g.Spec(str(binary),str(config),str(root),pins,require_root=False,seconds=.25,**kw)
    def test_closed_schema(self):
        for event in ({'severity':'err','reason':CANARY.decode(),'count':1},{'severity':'err','reason':'timeout','count':True},{'severity':'err','reason':'timeout','count':1,'raw':'x'}):
            with self.assertRaises(g.Rejected):g.encode(event)
    def test_pins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s=self.fixture(root,'pass\n');Path(s.config).write_text('drift')
            self.assertEqual(g.run(s,san)['status'],'FAILED');self.assertFalse((root/'syslog').exists())
    def test_pipes_and_datagrams_never_persist_canary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            body="import os,socket,sys,time\nr=sys.argv[sys.argv.index('-p')+1]\ns=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)\ns.sendto(b'<3>fixture PRIVATE_SYNTHETIC_SUPERVISOR_CANARY',(r+'syslog'))\nos.write(2,b'PRIVATE_SYNTHETIC_SUPERVISOR_CANARY\\n')\nos.write(1,b'PRIVATE_SYNTHETIC_SUPERVISOR_CANARY\\n')\ntime.sleep(10)\n"
            report=g.run(self.fixture(root,body),san)
            self.assertEqual(report['status'],'TIMEOUT');self.assertTrue(report['child_reaped'])
            files=list(root.glob('events-*'));self.assertTrue(files)
            self.assertGreaterEqual(sum(len(p.read_bytes().splitlines()) for p in files),3)
            for p in files:self.assertNotIn(CANARY,p.read_bytes());self.assertEqual(p.stat().st_mode&0o777,0o600)
    def test_parser_failure_reaps(self):
        class Bad:
            class LineFeed:
                def __init__(self,**kw):pass
                def feed(self,raw):raise RuntimeError(CANARY.decode())
        with tempfile.TemporaryDirectory() as tmp:
            s=self.fixture(Path(tmp),"import os,time\nos.write(2,b'bad\\n');time.sleep(10)\n")
            report=g.run(s,Bad);self.assertEqual(report['status'],'FAILED');self.assertTrue(report['child_reaped'])
    def test_socket_loss_reaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s=self.fixture(root,"import os,sys,time\nos.unlink(sys.argv[sys.argv.index('-p')+1]+'syslog');time.sleep(10)\n")
            report=g.run(s,san);self.assertEqual(report['status'],'FAILED');self.assertTrue(report['child_reaped'])
    def test_output_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);sink=g.Sink(root,g.Spec('','','',(),output_limit=256,segment_limit=128))
            try:
                with self.assertRaises(g.Rejected):
                    for _ in range(20):sink.write({'severity':'err','reason':'timeout','count':1})
            finally:sink.close()
            files=list(root.glob('events-*'));self.assertGreater(len(files),1)
            self.assertLessEqual(sum(p.stat().st_size for p in files),256)
            self.assertTrue(all(p.stat().st_size<=128 for p in files))
    def test_stop_reaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            stop=threading.Event();stop.set()
            report=g.run(self.fixture(Path(tmp),'import time\ntime.sleep(10)\n'),san,stop)
            self.assertEqual(report['status'],'STOPPED');self.assertTrue(report['child_reaped'])
    def test_signal_reaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.fixture(Path(tmp),"import os,signal,time\nos.kill(os.getppid(),signal.SIGTERM);time.sleep(10)\n")
            report=g.run(s,san);self.assertEqual(report['status'],'STOPPED');self.assertTrue(report['child_reaped'])
    def test_output_io_failure_reaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.fixture(Path(tmp),"import os,time\nos.write(2,b'bad\\n');time.sleep(10)\n")
            with mock.patch.object(g.Sink,'write',side_effect=OSError(CANARY.decode())):
                report=g.run(s,san)
            self.assertEqual(report['status'],'FAILED');self.assertTrue(report['child_reaped'])
    def test_input_limit_reaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=self.fixture(Path(tmp),"import os,time\nos.write(2,b'x'*512);time.sleep(10)\n",input_limit=128)
            report=g.run(s,san);self.assertEqual(report['status'],'FAILED');self.assertTrue(report['child_reaped'])
    def test_root_default(self):
        self.assertTrue(g.Spec('','','',()).require_root)

if __name__=='__main__':unittest.main()

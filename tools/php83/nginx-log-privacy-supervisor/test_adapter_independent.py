"""Author-independent disposable tests; no nginx, VM, service or package actions."""
import hashlib,importlib.util,json,os,pathlib,shutil,socket,stat,tempfile,unittest
from unittest.mock import patch
import lab_adapter as a
P=pathlib.Path(__file__).resolve().parent
SOURCE=P.parent/'nginx-log-privacy/sanitizer.py'
PIN='090c5e8faaf9a0fc468ad31994b2077cc8b50858b3577a0d1c7e327433be1af5'
class Independent(unittest.TestCase):
 def setup(self,base,body,**kwargs):
  root=base/'root';sock=base/'socket';sink=base/'sink'
  for p in (root,sock,sink):p.mkdir(mode=0o700)
  binary=root/'child';binary.write_text('#!/usr/bin/python3\n'+body);binary.chmod(0o700)
  config=root/'nginx.conf';config.write_text('SYNTHETIC_FIXTURE_ONLY');config.chmod(0o600)
  source=base/'sanitizer.py';shutil.copyfile(SOURCE,source);source.chmod(0o600)
  spec=importlib.util.spec_from_file_location('private_sanitizer',source);san=importlib.util.module_from_spec(spec);spec.loader.exec_module(san)
  allow=tuple((str(p),hashlib.sha256(p.read_bytes()).hexdigest()) for p in (binary,config,source))
  s=a.Spec(str(binary),str(config),str(root),str(sock),str(sink),allow,fixture_roots=(str(base),),seconds=3,**kwargs)
  return s,san,sink,sock
 def test_frozen_source(self):self.assertEqual(hashlib.sha256((P/'lab_adapter.py').read_bytes()).hexdigest(),PIN)
 def test_2000_event_exit_and_partial(self):
  with tempfile.TemporaryDirectory() as temp:
   body='import os\nraw=b"nginx: [error] connect() failed (111: Connection refused) while connecting to upstream\\n"*2000+b"nginx: [error] open() \\"/SYNTHETIC_SECRET\\" failed (2: No such file or directory)"\nwhile raw:\n n=os.write(2,raw);raw=raw[n:]\n'
   # The source is synthetic code; quote construction is validated before launching.
   compile(body,'fixture','exec')
   s,san,sink,sock=self.setup(pathlib.Path(temp),body)
   result=a.run(s,san);self.assertEqual(result['status'],'CHILD_EXIT');self.assertTrue(result['child_reaped'])
   raw=b''.join(p.read_bytes() for p in sorted(sink.glob('events-*')));events=[json.loads(x) for x in raw.splitlines()]
   self.assertEqual(len(events),2001);self.assertEqual(sum(e['reason']=='connect_failure' for e in events),2000);self.assertEqual(events[-1]['reason'],'file_missing');self.assertNotIn(b'SYNTHETIC_SECRET',raw)
   self.assertTrue(all(stat.S_IMODE(p.stat().st_mode)==0o600 for p in sink.glob('events-*')));self.assertNotEqual(s.socket_dir,s.sink_dir)
 def test_unsafe_parent_rejected_before_child(self):
  with tempfile.TemporaryDirectory() as temp:
   s,san,sink,sock=self.setup(pathlib.Path(temp),'raise SystemExit(0)\n');pathlib.Path(s.root).chmod(0o777)
   self.assertEqual(a.run(s,san)['status'],'FAILED');self.assertFalse((sock/'syslog').exists());self.assertFalse(list(sink.iterdir()))
 def test_symlink_and_hardlink_pin_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   s,san,sink,sock=self.setup(pathlib.Path(temp),'pass\n');config=pathlib.Path(s.config);link=config.with_name('alias');link.symlink_to(config)
   with self.assertRaises(a.Rejected):a.pinned(link,dict(s.allowlist)[s.config],s)
   link.unlink();os.link(config,link)
   with self.assertRaises(a.Rejected):a.pinned(config,dict(s.allowlist)[s.config],s)
 def test_permission_and_acl_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   s,san,sink,sock=self.setup(pathlib.Path(temp),'pass\n');p=pathlib.Path(s.config);p.chmod(0o666)
   with self.assertRaises(a.Rejected):a.trust(p,s)
   p.chmod(0o600)
   with patch.object(a.os,'listxattr',return_value=['system.posix_acl_access']),self.assertRaises(a.Rejected):a.trust(p,s)
 def test_no_implicit_fixture_boundary(self):
  with tempfile.TemporaryDirectory() as temp:
   s,san,sink,sock=self.setup(pathlib.Path(temp),'pass\n');s=a.dataclasses.replace(s,fixture_roots=())
   self.assertEqual(a.run(s,san)['status'],'FAILED');self.assertFalse((sock/'syslog').exists())
 def test_sanitizer_must_be_pinned(self):
  with tempfile.TemporaryDirectory() as temp:
   s,san,sink,sock=self.setup(pathlib.Path(temp),'pass\n');s=a.dataclasses.replace(s,allowlist=s.allowlist[:2])
   self.assertEqual(a.run(s,san)['status'],'FAILED');self.assertFalse((sock/'syslog').exists())
 def test_datagram_and_both_pipes_exit_tail(self):
  with tempfile.TemporaryDirectory() as temp:
   base=pathlib.Path(temp);body='import os,socket\ns=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)\ns.sendto(b"<187>Sep 28 12:00:00 kaltura_nginx: open() \\"/SYNTHETIC_SECRET\\" failed (2: No such file or directory)",'+repr(str(base/'socket/syslog'))+')\nos.write(1,b"nginx: [error] connect() failed (111: Connection refused) while connecting to upstream")\nos.write(2,b"nginx: [error] connect() failed (111: Connection refused) while connecting to upstream")\n'
   compile(body,'fixture','exec');s,san,sink,sock=self.setup(base,body);result=a.run(s,san);self.assertEqual(result['status'],'CHILD_EXIT')
   data=b''.join(p.read_bytes() for p in sink.glob('events-*'));self.assertNotIn(b'SYNTHETIC_SECRET',data);self.assertEqual(len(data.splitlines()),3)
 def test_descendant_tail_timeout_fails_without_early_flush(self):
  with tempfile.TemporaryDirectory() as temp:
   body='import os,time\nif os.fork()==0:\n os.write(2,b"nginx: [error] open() ")\n time.sleep(2)\n os.write(2,b"UNEXPECTED_LATE_TAIL")\n os._exit(0)\nos._exit(0)\n'
   s,san,sink,sock=self.setup(pathlib.Path(temp),body,drain_seconds=.05)
   result=a.run(s,san);self.assertEqual(result['status'],'FAILED');self.assertTrue(result['child_reaped'])
   data=b''.join(p.read_bytes() for p in sink.glob('events-*'));self.assertNotIn(b'UNEXPECTED_LATE_TAIL',data)
   events=[json.loads(line) for line in data.splitlines()];self.assertEqual(len(events),1);self.assertEqual(events[0]['reason'],'unclassified')
if __name__=='__main__':unittest.main()

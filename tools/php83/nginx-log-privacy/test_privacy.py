import json,os,pathlib,socket,stat,subprocess,sys,tempfile,time,unittest
from unittest.mock import patch
from sanitizer import sanitize,event,MAX_DATAGRAM,REASONS,SEVERITIES,LineFeed
import collector
P=pathlib.Path(__file__).parent.resolve()
SECRET=b'SYNTHETIC_KS_password_CANARY_DO_NOT_PERSIST'
class Pure(unittest.TestCase):
 def test_error_metadata_not_values(self):
  examples=((b'open() "/private" failed (13: Permission denied)','permission_denied'),(b'open() "/missing" failed (2: No such file or directory)','file_missing'),(b'connect() failed (111: Connection refused) while connecting to upstream','connect_failure'),(b'upstream timed out (110: Connection timed out) while reading response header from upstream','timeout'),(b'upstream prematurely closed connection while reading response header from upstream','upstream_failure'))
  for message,expected in examples:
   raw=b'<131>Sep 28 12:00:00 nginx_error: '+message+b', client: 127.0.0.1, request: GET /ks/'+SECRET+b'?password='+SECRET
   result=sanitize(raw);self.assertEqual(result,event('err',expected));self.assertNotIn(SECRET.decode(),json.dumps(result))
 def test_spoof_in_path_and_stderr_rejected(self):
  raw=b'<131>Sep 28 12:00:00 nginx_error: open() "/(13: Permission denied)/[emerg]" failed (2: No such file or directory), client: x'
  self.assertEqual(sanitize(raw),event('err','file_missing'))
  self.assertEqual(sanitize(b'untrusted /[emerg]/'+SECRET,source='stderr'),event('warning','unclassified'))
  self.assertEqual(sanitize(b'<131>Sep 28 12:00:00 nginx_error: usertext Permission denied'),event('err','unclassified'))
  self.assertEqual(sanitize(b'<131>Sep 28 12:00:00 nginx_error: open() "/bad\"suffix" failed (13: Permission denied)'),event('err','unclassified'))
 def test_closed_schema_only(self):
  for pri in range(192):
   result=sanitize(b'<'+str(pri).encode()+b'>Sep 28 12:00:00 nginx_error: '+SECRET);self.assertEqual(set(result),{'severity','reason','count'});self.assertIn(result['severity'],SEVERITIES);self.assertIn(result['reason'],REASONS);self.assertEqual(result['count'],1)
 def test_malformed_truncation(self):
  for raw in (b'',b'raw'+SECRET,b'<999>x',b'<3>x\n'+SECRET,b'<3>x\r',b'<3>x\x00',SECRET.decode()):self.assertEqual(sanitize(raw)['reason'],'malformed')
  self.assertEqual(sanitize(b'<3>'+SECRET,True)['reason'],'truncated');self.assertEqual(sanitize(b'x'*(MAX_DATAGRAM+1))['reason'],'truncated')
 def test_access_class_only(self):
  for status,reason in ((100,'access_informational'),(200,'access_success'),(302,'access_redirect'),(404,'access_client_error'),(503,'access_server_error')):
   self.assertEqual(sanitize(f'<134>Sep 28 12:00:00 nginx_access: v1 {status} 123 0.001 456 789'.encode())['reason'],reason)
  self.assertEqual(sanitize(b'<134>nginx_access: v1 200 '+SECRET)['reason'],'malformed')
 def test_enum_does_not_accept_free_text(self):
  for args in (('err',SECRET.decode()),(SECRET.decode(),'unclassified'),('err','unclassified',True),('err','unclassified',0),('err','unclassified',1000001)):
   with self.assertRaises(ValueError):event(*args)
 def test_stderr_split_line_and_flush(self):
  feed=LineFeed();self.assertEqual(feed.feed(b'2026/09/28 12:00:00 [err'),[])
  out=feed.feed(b'or] 123#123: *1 open() "/ks/'+SECRET+b'" failed (13: Permission denied)\n')
  self.assertEqual(out,[event('err','permission_denied')]);self.assertNotIn(SECRET.decode(),json.dumps(out))
  self.assertEqual(feed.feed(b'nginx: [warn] upstream timed out (110: Connection timed out) while reading response header from upstream, client: '+SECRET),[]);self.assertEqual(feed.flush(),[event('warning','timeout')]);self.assertEqual(feed.flush(),[])
 def test_stderr_long_line_and_bounded_buffer(self):
  feed=LineFeed();out=[]
  for _ in range(10):out+=feed.feed(SECRET*100);self.assertLessEqual(len(feed.buffer),MAX_DATAGRAM)
  out+=feed.feed(b'\nnginx: [error] connect() failed (111: Connection refused) while connecting to upstream\n');self.assertEqual(out,[event('warning','truncated'),event('err','connect_failure')])
  self.assertEqual(feed.feed(b'x'*65537),[event('warning','truncated')]);self.assertEqual(feed.flush(),[])
 def test_output_budget_and_no_raw(self):
  with tempfile.TemporaryDirectory(dir=pathlib.Path.home()) as tmp:
   path=pathlib.Path(tmp)/'events';fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
   try:
    with patch.object(collector,'MAX_OUTPUT',512):
     used=0
     while True:
      n=collector.append(fd,event('err','unclassified'),used)
      if n is None:break
      used=n
     self.assertLessEqual(used,256)
   finally:os.close(fd)
   self.assertNotIn(SECRET,path.read_bytes())
class Isolated(unittest.TestCase):
 def test_real_socket_truncation_and_exclusive_output(self):
  with tempfile.TemporaryDirectory(dir=pathlib.Path.home()) as tmp:
   root=pathlib.Path(tmp);root.chmod(0o700)
   process=subprocess.Popen([sys.executable,'-B',str(P/'collector.py'),'--directory',str(root),'--seconds','5','--events','3','--isolated-prototype'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   address=root/'input.sock';deadline=time.monotonic()+3
   try:
    while not address.exists() and process.poll() is None and time.monotonic()<deadline:time.sleep(.02)
    self.assertTrue(address.exists())
    with socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM) as sender:
     for raw in (b'<131>Sep 28 12:00:00 nginx_error: open() "/'+SECRET+b'" failed (13: Permission denied)',b'<131>'+b'x'*(MAX_DATAGRAM+1)+SECRET,b'<131>bad\n'+SECRET):sender.sendto(raw,str(address))
    stdout,stderr=process.communicate(timeout=6);self.assertEqual(process.returncode,0);self.assertEqual(stderr,b'');self.assertNotIn(SECRET,stdout)
    output=root/'events.jsonl';raw=output.read_bytes();self.assertNotIn(SECRET,raw);self.assertEqual(stat.S_IMODE(output.stat().st_mode),0o600)
    events=[json.loads(line) for line in raw.splitlines()];self.assertEqual([e['reason'] for e in events],['collector_started','permission_denied','truncated','malformed','collector_stopped']);self.assertFalse(address.exists())
    with self.assertRaises(ValueError):collector.run(root,1,1,True)
   finally:
    if process.poll() is None:process.kill();process.communicate()
 def test_symlink_directory_and_unsafe_mode_rejected(self):
  with tempfile.TemporaryDirectory(dir=pathlib.Path.home()) as tmp:
   root=pathlib.Path(tmp);link=root/'link';link.symlink_to(root)
   with self.assertRaises(ValueError):collector.directory(link,os.geteuid())
   root.chmod(0o777)
   with self.assertRaises(ValueError):collector.directory(root,os.geteuid())
 def test_runtime_bounds(self):
  for seconds,events in ((0,1),(301,1),(1,0),(1,10001)):
   with self.assertRaises(ValueError):collector.run(P,seconds,events,True)
if __name__=='__main__':unittest.main()

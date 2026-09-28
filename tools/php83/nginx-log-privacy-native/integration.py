"""Synthetic exact binary guardian integration; private local loopback only."""
import hashlib,importlib.util,json,os,pathlib,signal,socket,tempfile,threading,time
P=pathlib.Path(__file__).resolve().parent.parent
BIN=pathlib.Path('/tmp/php83-nginx-native-fixture-bin/nginx');BP='1a995dddd470f013258b1890cfc7c9e3b10c344461eb085de6b2ef8f991faec0'
CAN='SYNTHETIC_GUARDIAN_CANARY_91'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
 import sys
 sys.modules[name]=m;s.loader.exec_module(m);return m
def run():
 gpath=P/'nginx-log-privacy-supervisor/guardian.py';spath=P/'nginx-log-privacy/sanitizer.py';g=load('guardian_native',gpath);san=load('san_native',spath)
 assert hashlib.sha256(BIN.read_bytes()).hexdigest()==BP
 report={'binary_sha256':BP,'guardian_sha256':hashlib.sha256(gpath.read_bytes()).hexdigest(),'sanitizer_sha256':hashlib.sha256(spath.read_bytes()).hexdigest(),'cases':[]}
 for case in ('reload_reopen','collector_lost','startup_error','invalid_reload'):
  with tempfile.TemporaryDirectory(prefix='nginx-guardian-native-') as td:
   root=pathlib.Path(td);root.chmod(0o700);cfg=root/'nginx.conf';access=root/'access'
   with socket.socket() as reserve:reserve.bind(('127.0.0.1',0));port=reserve.getsockname()[1]
   text=f'''daemon off; master_process on; pid {root}/pid;
error_log syslog:server=unix:{root}/syslog,nohostname,tag=kaltura_nginx error;
events {{ worker_connections 32; }}
http {{ log_format scalar 'v1 $status $bytes_sent $request_time $request_length $connection'; access_log {access} scalar;
client_body_temp_path {root}/body; proxy_temp_path {root}/proxy; fastcgi_temp_path {root}/fastcgi; uwsgi_temp_path {root}/uwsgi; scgi_temp_path {root}/scgi;
server {{ listen 127.0.0.1:{port}; root {root}/missing; location /upstream {{ proxy_pass http://127.0.0.1:1; }} }} }}\n'''
   cfg.write_text(text+(CAN+';\n' if case=='startup_error' else ''));cfg.chmod(0o600)
   spec=g.Spec(str(BIN),str(cfg),str(root),((str(BIN),BP),(str(cfg),hashlib.sha256(cfg.read_bytes()).hexdigest())),seconds=5,require_root=False)
   stop=threading.Event();obs={'statuses':[],'errors':[]}
   def request(uri):
    with socket.create_connection(('127.0.0.1',port),.5) as s:
     s.settimeout(.5);s.sendall(('GET '+uri+' HTTP/1.1\r\nHost: '+CAN+'\r\nConnection: close\r\n\r\n').encode());raw=s.recv(4096);obs['statuses'].append(raw.split(b' ',2)[1].decode())
   def exercise():
    try:
     if case=='startup_error':return
     for _ in range(100):
      if (root/'pid').exists():
       try:request('/missing?secret='+CAN);break
       except OSError:pass
      time.sleep(.02)
     else:raise RuntimeError('START_TIMEOUT')
     pid=int((root/'pid').read_text());request('/upstream?secret='+CAN);request('/'+CAN+'x'*12000)
     if case=='collector_lost':(root/'syslog').unlink();time.sleep(.2);return
     if case=='reload_reopen':
      access.rename(root/'access.old');os.kill(pid,signal.SIGUSR1)
      for _ in range(50):
       if access.exists():break
       time.sleep(.02)
      assert access.exists();request('/post_reopen?secret='+CAN)
      os.kill(pid,signal.SIGHUP);time.sleep(.3);request('/post_reload?secret='+CAN)
      obs['reopen_new_file']=True
     if case=='invalid_reload':
      cfg.write_text(text+CAN+';\n');os.kill(pid,signal.SIGHUP);time.sleep(.3);request('/after_failed_reload?secret='+CAN)
     time.sleep(.15);stop.set()
    except BaseException:obs['errors'].append('FIXTURE_FAILURE');stop.set()
   thread=threading.Thread(target=exercise);thread.start();result=g.run(spec,san,stop);thread.join(timeout=3);assert not thread.is_alive()
   files=list(root.glob('events-*.jsonl'));raw=b''.join(p.read_bytes() for p in files);events=[json.loads(x) for x in raw.splitlines()]
   logs=raw+b''.join(p.read_bytes() for p in root.glob('access*'))
   assert CAN.encode() not in logs
   assert all(set(e)=={'severity','reason','count'} for e in events)
   try:
    with socket.create_connection(('127.0.0.1',port),.1):closed=False
   except OSError:closed=True
   assert not obs['errors'] and result['child_reaped'] and closed
   assert result['status']=={'reload_reopen':'STOPPED','collector_lost':'FAILED','startup_error':'CHILD_EXIT','invalid_reload':'STOPPED'}[case]
   assert events
   if case!='startup_error':assert obs['statuses'][:3]==['404','502','414']
   if case=='reload_reopen':assert len(obs['statuses'])==5 and obs['reopen_new_file']
   if case=='invalid_reload':assert len(obs['statuses'])==4 and 'unclassified' in {e['reason'] for e in events}
   report['cases'].append(dict(case=case,result=result,observed=obs,event_count=len(events),reasons=sorted({e['reason'] for e in events}),canary_absent=True,listener_closed=closed))
 return report
if __name__=='__main__':print(json.dumps(run(),indent=2))

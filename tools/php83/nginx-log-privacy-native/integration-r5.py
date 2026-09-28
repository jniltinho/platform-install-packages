"""Synthetic exact binary guardian integration; private local loopback only."""
import hashlib,importlib.util,json,os,pathlib,signal,socket,tempfile,threading,time
P=pathlib.Path(__file__).resolve().parent.parent
BIN=pathlib.Path('/tmp/php83-nginx-native-fixture-bin/nginx');BP='1a995dddd470f013258b1890cfc7c9e3b10c344461eb085de6b2ef8f991faec0'
CAN='SYNTHETIC_GUARDIAN_CANARY_91'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
 import sys
 sys.modules[name]=m;s.loader.exec_module(m);return m
def children(master):
 # Read only our nginx master's kernel child list, not global process discovery.
 ids=pathlib.Path(f'/proc/{master}/task/{master}/children').read_text().split()
 if not ids or len(ids)>16 or any(not x.isdecimal() for x in ids):raise RuntimeError('WORKER_SET')
 result=set()
 for pid in ids:
  raw=pathlib.Path(f'/proc/{pid}/stat').read_text();fields=raw.rsplit(')',1)[1].split()
  if fields[0] in ('Z','X') or int(fields[1])!=master:raise RuntimeError('WORKER_STATE')
  result.add((int(pid),int(fields[19]))) # Linux stat field22: starttime.
 return result

def run():
 gpath=P/'nginx-log-privacy-supervisor/lab_adapter.py';spath=P/'nginx-log-privacy/sanitizer.py';g=load('guardian_native',gpath);san=load('san_native',spath)
 assert hashlib.sha256(BIN.read_bytes()).hexdigest()==BP
 transform_path=P/'nginx-log-privacy-config/transform.py';transform=load('native_transform',transform_path)
 report={'transform_sha256':hashlib.sha256(transform_path.read_bytes()).hexdigest(),'binary_sha256':BP,'guardian_sha256':hashlib.sha256(gpath.read_bytes()).hexdigest(),'sanitizer_sha256':hashlib.sha256(spath.read_bytes()).hexdigest(),'cases':[]}
 for case in ('reload_reopen','collector_lost','startup_error','invalid_reload'):
  with tempfile.TemporaryDirectory(prefix='nginx-guardian-native-') as td:
   boundary=pathlib.Path(td);boundary.chmod(0o700)
   root=boundary/'runtime';socketdir=boundary/'socket';sinkdir=boundary/'sink'
   for directory in (root,socketdir,sinkdir):directory.mkdir(mode=0o700)
   binary=boundary/'nginx';binary.write_bytes(BIN.read_bytes());binary.chmod(0o700)
   sanitizer_copy=boundary/'sanitizer.py';sanitizer_copy.write_bytes(spath.read_bytes());sanitizer_copy.chmod(0o600)
   san=load('san_fixture_'+case,sanitizer_copy)
   cfg=root/'nginx.conf';access=root/'access'
   with socket.socket() as reserve:reserve.bind(('127.0.0.1',0));port=reserve.getsockname()[1]
   text=f'''daemon off; master_process on; pid {root}/pid;
error_log syslog:server=unix:{socketdir}/syslog,nohostname,tag=kaltura_nginx error;
events {{ worker_connections 32; }}
http {{ {transform.ACCESS} access_log {access} main;
client_body_temp_path {root}/body; proxy_temp_path {root}/proxy; fastcgi_temp_path {root}/fastcgi; uwsgi_temp_path {root}/uwsgi; scgi_temp_path {root}/scgi;
server {{ listen 127.0.0.1:{port}; root {root}/missing; location /upstream {{ proxy_pass http://127.0.0.1:1; }} }} }}\n'''
   cfg.write_text(text+(CAN+';\n' if case=='startup_error' else ''));cfg.chmod(0o600)
   spec=g.Spec(binary=str(binary),config=str(cfg),root=str(root),socket_dir=str(socketdir),sink_dir=str(sinkdir),allowlist=((str(binary),BP),(str(cfg),hashlib.sha256(cfg.read_bytes()).hexdigest()),(str(sanitizer_copy),hashlib.sha256(sanitizer_copy.read_bytes()).hexdigest())),seconds=5,fixture_roots=(str(boundary),))
   stop=threading.Event();obs={'statuses':[],'errors':[]}
   def request(uri,method="GET"):
    with socket.create_connection(('127.0.0.1',port),.5) as s:
     s.settimeout(.5);s.sendall((method+' '+uri+' HTTP/1.1\r\nHost: '+CAN+'\r\nConnection: close\r\n\r\n').encode());raw=s.recv(4096);obs['statuses'].append(raw.split(b' ',2)[1].decode())
   def exercise():
    try:
     if case=='startup_error':return
     for _ in range(100):
      if (root/'pid').exists():
       try:request('/missing?secret='+CAN);break
       except OSError:pass
      time.sleep(.02)
     else:raise RuntimeError('START_TIMEOUT')
     pid=int((root/'pid').read_text());request('/upstream?secret='+CAN);request('/'+CAN+'x'*12000);request('/custom?secret='+CAN,method=CAN)
     if case=='collector_lost':(socketdir/'syslog').unlink();time.sleep(.2);return
     if case=='reload_reopen':
      access.rename(root/'access.old');os.kill(pid,signal.SIGUSR1)
      for _ in range(50):
       if access.exists():break
       time.sleep(.02)
      assert access.exists();request('/post_reopen?secret='+CAN)
      before=children(pid);os.kill(pid,signal.SIGHUP)
      deadline=time.monotonic()+2
      while True:
       after=children(pid)
       if after and after.isdisjoint(before):break
       if time.monotonic()>=deadline:raise RuntimeError('RELOAD_WORKERS_UNCHANGED')
       time.sleep(.02)
      request('/post_reload?secret='+CAN)
      assert children(pid)==after
      obs['replacement_worker_transition']=True
      obs['old_worker_count']=len(before);obs['new_worker_count']=len(after)
      obs['reopen_new_file']=True
     if case=='invalid_reload':
      cfg.write_text(text+CAN+';\n');os.kill(pid,signal.SIGHUP);time.sleep(.3);request('/after_failed_reload?secret='+CAN)
     time.sleep(.15);stop.set()
    except BaseException:obs['errors'].append('FIXTURE_FAILURE');stop.set()
   thread=threading.Thread(target=exercise);thread.start();result=g.run(spec,san,stop);thread.join(timeout=3);assert not thread.is_alive()
   files=list(sinkdir.glob('events-*.jsonl'));raw=b''.join(p.read_bytes() for p in files);events=[json.loads(x) for x in raw.splitlines()]
   logs=raw+b''.join(p.read_bytes() for p in root.glob('access*'))
   assert CAN.encode() not in logs
   if case!='startup_error':
    access_raw=b''.join(p.read_bytes() for p in root.glob('access*'))
    assert any(line.endswith(b' OTHER') for line in access_raw.splitlines())
    obs['custom_method_OTHER']=True
   assert all(p.stat().st_mode&0o777==0o600 for p in files)
   assert all(set(e)=={'severity','reason','count'} for e in events)
   try:
    with socket.create_connection(('127.0.0.1',port),.1):closed=False
   except OSError:closed=True
   assert not obs['errors'] and result['child_reaped'] and closed
   assert result['status']=={'reload_reopen':'STOPPED','collector_lost':'FAILED','startup_error':'CHILD_EXIT','invalid_reload':'STOPPED'}[case]
   assert events
   if case!='startup_error':assert obs['statuses'][:3]==['404','502','414']
   if case=='reload_reopen':assert len(obs['statuses'])==6 and obs['reopen_new_file'] and obs['replacement_worker_transition']
   if case=='invalid_reload':assert len(obs['statuses'])==5 and 'unclassified' in {e['reason'] for e in events}
   report['cases'].append(dict(case=case,result=result,observed=obs,event_count=len(events),reasons=sorted({e['reason'] for e in events}),canary_absent=True,listener_closed=closed))
 return report
if __name__=='__main__':print(json.dumps(run(),indent=2))

"""Exact packaged binary, disposable loopback-only synthetic log probe. No host install."""
import argparse,hashlib,json,os,pathlib,signal,socket,subprocess,tempfile,time
PIN='1a995dddd470f013258b1890cfc7c9e3b10c344461eb085de6b2ef8f991faec0'
CANARY='SYNTHETIC_NGINX_PRIVATE_CANARY_72'
def main(binary,output):
 binary=pathlib.Path(binary).resolve();assert hashlib.sha256(binary.read_bytes()).hexdigest()==PIN
 output=pathlib.Path(output);output.mkdir(exist_ok=False)
 results=[]
 for available in (True,False):
  with tempfile.TemporaryDirectory(prefix='nginx-private-') as tmp:
   root=pathlib.Path(tmp);sockpath=root/'syslog';receiver=None
   if available:
    receiver=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM);receiver.bind(str(sockpath));receiver.settimeout(.1)
   reserve=socket.socket();reserve.bind(('127.0.0.1',0));port=reserve.getsockname()[1];reserve.close()
   config=root/'nginx.conf';access=root/'access';stderr=root/'stderr'
   config.write_text(f'''daemon off;
master_process on;
pid {root}/pid;
error_log syslog:server=unix:{sockpath},nohostname,tag=kaltura_nginx error;
events {{ worker_connections 32; }}
http {{
 map $request_method $safe_method {{ default OTHER; GET GET; POST POST; HEAD HEAD; OPTIONS OPTIONS; }}
 log_format scalar 'v1 $status $bytes_sent $request_time $request_length $connection $safe_method';
 access_log {access} scalar;
 client_body_temp_path {root}/body;
 proxy_temp_path {root}/proxy;
 fastcgi_temp_path {root}/fastcgi;
 uwsgi_temp_path {root}/uwsgi;
 scgi_temp_path {root}/scgi;
 server {{ listen 127.0.0.1:{port}; root {root}/missing;
  location /upstream {{ proxy_pass http://127.0.0.1:1; }}
 }}
}}
''')
   raw=[];responses=[]
   with stderr.open('wb') as err:
    proc=subprocess.Popen([str(binary),'-p',str(root)+'/', '-c',str(config),'-e','stderr'],stdout=subprocess.DEVNULL,stderr=err,start_new_session=True)
    try:
     for _ in range(100):
      if proc.poll() is not None:raise RuntimeError('START_FAILED')
      try:
       s=socket.create_connection(('127.0.0.1',port),.1);s.close();break
      except OSError:time.sleep(.02)
     def drain():
      if receiver:
       while True:
        try:raw.append(receiver.recv(65536))
        except socket.timeout:break
     for uri in ('/missing?token='+CANARY,'/upstream?token='+CANARY,'/'+CANARY+'x'*12000):
      with socket.create_connection(('127.0.0.1',port),1) as s:
       s.settimeout(1);s.sendall(('GET '+uri+' HTTP/1.1\r\nHost: '+CANARY+'\r\nAuthorization: Bearer '+CANARY+'\r\nConnection: close\r\n\r\n').encode());data=b''
       try:
        while len(data)<65536:
         chunk=s.recv(4096)
         if not chunk:break
         data+=chunk
       except (TimeoutError,ConnectionResetError):pass
       responses.append(data.split(b'\r\n',1)[0].decode('ascii','replace'));drain()
     proc.send_signal(signal.SIGUSR1);time.sleep(.1);drain()
     proc.send_signal(signal.SIGHUP);time.sleep(.1);drain()
    finally:
     if proc.poll() is None:proc.send_signal(signal.SIGQUIT)
     try:proc.wait(timeout=4)
     except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=2)
     if receiver:drain();receiver.close()
   er=stderr.read_bytes();ac=access.read_bytes() if access.exists() else b'';wire=b'\n'.join(raw)
   assert len(er)+len(ac)+len(wire)<1024*1024
   name='available' if available else 'unavailable'
   for suffix,data in [('stderr',er),('access',ac),('datagrams',wire)]: (output/(name+'.'+suffix)).write_bytes(data)
   results.append(dict(collector_available=available,exit=proc.returncode,responses=responses,datagrams=len(raw),max_datagram=max(map(len,raw),default=0),access_canary=CANARY.encode() in ac,stderr_canary=CANARY.encode() in er,datagram_canary=CANARY.encode() in wire,stderr_bytes=len(er),access_bytes=len(ac)))
 report=dict(binary_sha256=PIN,scope='SYNTHETIC_HOST_LOOPBACK_FIXTURE_NOT_GUEST',cases=results)
 (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',required=True);a=p.parse_args();main(a.binary,a.output)

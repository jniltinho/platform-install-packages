"""Fixed .74 synthetic profile SELECT observation; no API/bootstrap/session mutation."""
import hashlib,json,os,re,selectors,signal,socket,stat,subprocess,time
from pathlib import Path
SOCKET='/run/mysqld/mysqld.sock'
DATADIR='/var/lib/mysql/'
PINS={
 'alpha/lib/model/om/BaseconversionProfile2Peer.php':'f19f06093fa6238603a45a0031b251d62dc17f5b9071518a3f870b9a4a7b275e',
 'alpha/lib/model/om/BaseflavorParamsConversionProfilePeer.php':'4b27213108fc0a516d8f9a6d7223a68a27b59415cf74924e791f04de8961ce89',
}
SQL="""SET SESSION max_statement_time=3;
START TRANSACTION READ ONLY;
SELECT 'IDENTITY',@@hostname,@@socket,@@datadir,CURRENT_USER(),DATABASE();
SELECT 'ENTRY',id,partner_id,conversion_profile_id FROM entry WHERE id='0_wzmt2sfy' AND partner_id=102 LIMIT 2;
SELECT 'PROFILE',id,partner_id,status,type,deleted_at IS NULL FROM conversion_profile_2 WHERE id=14 LIMIT 2;
SELECT 'FLAVOR',conversion_profile_id,flavor_params_id FROM flavor_params_conversion_profile WHERE conversion_profile_id=14 ORDER BY id LIMIT 129;
COMMIT;
"""
class Rejected(ValueError):pass
def need(v):
 if not v:raise Rejected('PROFILE_OBSERVATION_REJECTED')
def integer(v):
 need(type(v) is str and re.fullmatch('-?[0-9]{1,10}',v) is not None);return int(v)
def identity(rows):
 need(len(rows)==1 and len(rows[0])==5)
 host,sock,data,user,db=rows[0]
 need(host=='kaltura-php74-baseline' and sock in (SOCKET,'/var/run/mysqld/mysqld.sock') and data==DATADIR and user=='root@localhost' and db=='kaltura')
def parse(raw):
 need(type(raw) is bytes and len(raw)<=32768)
 rows=[line.split('\t') for line in raw.decode('ascii').splitlines()]
 groups={k:[] for k in ('IDENTITY','ENTRY','PROFILE','FLAVOR')}
 for row in rows:need(row and row[0] in groups);groups[row[0]].append(row[1:])
 identity(groups['IDENTITY'])
 need(groups['ENTRY']==[['0_wzmt2sfy','102','14']])
 p=groups['PROFILE'];need(len(p)==1 and len(p[0])==5);p=[integer(v) for v in p[0]]
 need(p[0]==14 and p[1] in (0,102) and p[4] in (0,1))
 flavors=groups['FLAVOR'];need(len(flavors)<=128 and all(len(row)==2 for row in flavors))
 ids=[]
 for row in flavors:need(integer(row[0])==14);ids.append(integer(row[1]))
 need(len(ids)==len(set(ids)))
 return {'schema':1,'status':'READ_ONLY_STORED_PROFILE_OBSERVED','entry_id':'0_wzmt2sfy','entry_partner_id':102,'selected_profile_id':14,'profile_partner_id':p[1],'profile_status':p[2],'profile_type':p[3],'profile_not_deleted':bool(p[4]),'configured_flavor_ids':ids,'select_count':5,'db_identity_verified':True,'api_authorization_verified':False,'full_acceptance':False}
def secret_read():
 fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
 try:
  for name in ('root','kaltura-baseline-private'):
   new=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=new
   st=os.fstat(fd);need(st.st_uid==0 and not st.st_mode&0o077)
  child=os.open('mysql-password',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
  try:
   st=os.fstat(child);need(stat.S_ISREG(st.st_mode) and st.st_uid==0 and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1 and st.st_size<=256)
   value=os.read(child,257).decode().strip();need(re.fullmatch('[a-f0-9]{48}',value) is not None);return value
  finally:os.close(child)
 finally:os.close(fd)
def guard():
 need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline')
 info=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={v.get('local') for row in info for v in row.get('addr_info',[])}
 need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}))
 for name,pin in PINS.items():
  p=Path('/opt/kaltura/app')/name;s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==pin)
 st=Path(SOCKET).lstat();need(stat.S_ISSOCK(st.st_mode) and st.st_uid==111 and st.st_gid==110 and stat.S_IMODE(st.st_mode)==0o777)
 need(Path(SOCKET).parent.resolve()==Path('/run/mysqld'))
 st=Path(DATADIR).lstat();need(stat.S_ISDIR(st.st_mode) and st.st_uid==111 and st.st_gid==110 and stat.S_IMODE(st.st_mode)==0o755)
def query(password,identity_only=False):
 fd=os.memfd_create('baseline-profile-options',os.MFD_CLOEXEC)
 try:
  os.fchmod(fd,0o600);os.write(fd,('[client]\nuser=root\npassword='+password+'\n').encode());os.lseek(fd,0,0)
  argv=['/usr/bin/mysql','--defaults-file=/proc/self/fd/'+str(fd),'--protocol=SOCKET','--socket='+SOCKET,'--connect-timeout=5','--batch','--raw','--skip-column-names','kaltura']
  p=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,pass_fds=(fd,),start_new_session=True)
  sel=selectors.DefaultSelector();raw=bytearray();err=0;sent=0;data=("SELECT 'IDENTITY',@@hostname,@@socket,@@datadir,CURRENT_USER(),DATABASE();" if identity_only else SQL).encode();until=time.monotonic()+20;complete=False
  try:
   for stream,event,kind in ((p.stdin,selectors.EVENT_WRITE,'in'),(p.stdout,selectors.EVENT_READ,'out'),(p.stderr,selectors.EVENT_READ,'err')):
    os.set_blocking(stream.fileno(),False);sel.register(stream,event,kind)
   while sel.get_map():
    need(time.monotonic()<until)
    for key,_ in sel.select(.1):
     if key.data=='in':
      sent+=os.write(key.fileobj.fileno(),data[sent:sent+4096])
      if sent==len(data):sel.unregister(key.fileobj);key.fileobj.close()
      continue
     block=os.read(key.fileobj.fileno(),4096)
     if not block:sel.unregister(key.fileobj);continue
     if key.data=='out':raw.extend(block)
     else:err+=len(block)
     need(len(raw)+err<=32768)
   need(p.wait(timeout=max(.1,until-time.monotonic()))==0);complete=True;return bytes(raw)
  finally:
   if not complete:
    try:os.killpg(p.pid,signal.SIGKILL)
    except ProcessLookupError:pass
   if p.poll() is None:p.wait(timeout=5)
   sel.close()
   for stream in (p.stdin,p.stdout,p.stderr):
    if not stream.closed:stream.close()
 finally:os.close(fd)
def main():
 phase='TARGET_SOURCE_GUARD'
 try:
  guard();phase='PRIVATE_OPTION_READ';password=secret_read();phase='DB_IDENTITY';first=query(password,True).decode('ascii').splitlines();need(len(first)==1 and first[0].startswith('IDENTITY\t'));identity([first[0].split('\t')[1:]]);phase='BOUNDED_READ_ONLY_SQL';raw=query(password);phase='PUBLIC_PROJECTION';result=parse(raw)
 except Exception:result={'status':'FAILED_CLOSED','failure_stage':phase,'full_acceptance':False}
 print(json.dumps(result,sort_keys=True));return 0 if result['status']=='READ_ONLY_STORED_PROFILE_OBSERVED' else 2
if __name__=='__main__':raise SystemExit(main())

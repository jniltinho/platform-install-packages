#!/usr/bin/env python3
"""One owned 10s fixture, native74 untimed only; never print private API bodies."""
import base64,hashlib,json,os,re,socket,stat,subprocess,sys,time,gzip,tempfile,resource
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'baseline-api'))
from transport import PostTransport,Origin,Client,deadline,read_bounded,strict_json,_pack_post
from protocol import read_file
SOURCE_PIN='612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473'
LOG_ROOTS=[Path('/opt/kaltura/log'),Path('/var/log/apache2'),Path('/var/log/nginx')]
LOG_EXTRA=[Path('/var/log/syslog'),Path('/var/log/messages')]
JOURNAL_SINCE=None
ID=re.compile(r'[0-9]_[a-z0-9]{8}\Z')
class Failed(RuntimeError):pass
def need(ok,code):
    if not ok:raise Failed(code)
def checksum(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def api_value(value):
    if type(value) is dict and value.get('objectType')=='KalturaAPIException':
        code=value.get('code')
        raise Failed('API_'+code if type(code) is str and re.fullmatch('[A-Z0-9_]{1,64}',code) else 'API_REJECTED')
    return value
def media_projection(value):
    keys=['objectType','id','partnerId','status','mediaType']
    need(type(value) is dict and all(k in value for k in keys),'MEDIA_SHAPE')
    need(value['objectType']=='KalturaMediaEntry' and type(value['id']) is str and ID.fullmatch(value['id']),'MEDIA_ID')
    for k in ['partnerId','status','mediaType']:
        need(type(value[k]) in {int,str} and re.fullmatch(r'-?[0-9]+',str(value[k])) is not None,'MEDIA_TYPES')
    return {k:value[k] for k in keys}
def typed_equal(left,right):
    return type(left) is type(right) and left.keys()==right.keys() and all(type(left[k]) is type(right[k]) and left[k]==right[k] for k in left)
def sql(query):
    need(query.startswith('SELECT ') and ';' not in query,'READ_ONLY_SQL')
    password=read_file(Path('/root/kaltura-baseline-private/mysql-password'),256,private=True).decode().strip()
    need(re.fullmatch('[0-9a-f]{48}',password) is not None,'PRIVATE_DB_FORMAT')
    fd=os.memfd_create('baseline-db-option',os.MFD_CLOEXEC)
    try:
        os.fchmod(fd,0o600);os.write(fd,('[client]\nuser=root\npassword='+password+'\n').encode());os.lseek(fd,0,0)
        p=subprocess.run(['mysql','--defaults-extra-file=/proc/self/fd/'+str(fd),'--protocol=socket','--batch','--raw','--skip-column-names','kaltura'],input=query.encode(),capture_output=True,pass_fds=(fd,),timeout=20)
        need(p.returncode==0,'DB_READ_FAILED')
        return [line.split('\t') for line in p.stdout.decode().splitlines()]
    finally:os.close(fd)
def logs():
    result=[]
    for root in LOG_ROOTS:
        if not root.exists():continue
        for p in root.rglob('*'):
            if p.is_symlink():raise Failed('LOG_SYMLINK_UNREVIEWED')
            if p.is_file():
                need(p.stat().st_size<=64*1024*1024,'LOG_SIZE_UNREVIEWED')
                result.append(p)
    for p in LOG_EXTRA:
        if p.exists():
            need(p.is_file() and not p.is_symlink() and p.stat().st_size<=64*1024*1024,'EXTRA_LOG_UNREVIEWED');result.append(p)
    need(bool(result),'LOG_INVENTORY_EMPTY')
    return sorted(result)
def privacy(patterns):
    need(patterns and all(type(p) is bytes and len(p)>=16 for p in patterns),'PRIVATE_SCAN_PATTERNS')
    hits=[0]*len(patterns);paths=logs()
    for p in paths:
        with (gzip.open(p,'rb') if p.suffix=='.gz' else p.open('rb')) as f:
            tail=b'';total=0
            while True:
                b=f.read(1024*1024)
                if not b:break
                total+=len(b);need(total<=64*1024*1024,'LOG_GROWTH_UNREVIEWED')
                data=tail+b
                for i,pattern in enumerate(patterns):
                    if pattern in data:hits[i]+=1
                tail=data[-max(len(x) for x in patterns):]
    need(JOURNAL_SINCE is not None,'JOURNAL_BOUNDARY')
    with tempfile.TemporaryFile() as journal:
        def limit_output():resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024*1024,64*1024*1024))
        proc=subprocess.run(['journalctl','--since',JOURNAL_SINCE,'--no-pager','--output=cat'],stdout=journal,stderr=subprocess.DEVNULL,timeout=20,preexec_fn=limit_output)
        need(proc.returncode==0,'JOURNAL_SCAN_FAILED');journal.seek(0);data=journal.read(64*1024*1024+1)
        need(len(data)<=64*1024*1024,'JOURNAL_SIZE')
        for i,pattern in enumerate(patterns):
            if pattern in data:hits[i]+=1
    return {'journal_since_start_scanned':True,'reviewed_files':len(paths),'inventory_sha256':hashlib.sha256('\n'.join(str(p) for p in paths).encode()).hexdigest(),'hits':hits}
def logging_preflight():
    paths=[]
    for root in ['/etc/apache2','/etc/nginx','/etc/rsyslog.d']:
        r=Path(root)
        if r.exists():paths.extend(p for p in r.rglob('*') if p.is_file())
    paths.extend(p for p in [Path('/etc/rsyslog.conf'),Path('/opt/kaltura/app/configurations/logger.ini')] if p.is_file())
    need(any(p.name=='logger.ini' for p in paths),'APP_LOG_CONFIG_MISSING')
    snapshot={}
    for p in paths:
        raw=p.read_bytes();need(len(raw)<=2*1024*1024,'LOG_CONFIG_SIZE')
        snapshot[str(p)]=hashlib.sha256(raw).hexdigest() # guest-private only, never export values
        active='\n'.join(x.strip() for x in raw.decode().splitlines() if x.strip() and not x.lstrip().startswith(('#',';')))
        low=active.lower()
        if 'rsyslog' in str(p):
            need(not any(x in low for x in ['@@','omfwd','omrelp','omhttp','omprog']) and re.search(r'(^|\s)@[^\s]',active) is None,'REMOTE_LOG_FORWARDER')
        if '/apache2/' in str(p):
            need(not any(x in low for x in ['security2_module','dumpio_module']) and re.search(r'(?im)^\s*(customlog|errorlog)\s+["\']?\|',active) is None,'APACHE_BODY_OR_PIPE_LOG')
        if '/nginx/' in str(p):
            need('syslog:' not in low and '$request_body' not in low,'NGINX_BODY_OR_REMOTE_LOG')
        if p.name=='logger.ini':
            for line in active.splitlines():
                if re.match(r'writers\.[^.]+\.name\s*=',line):need(line.split('=',1)[1].strip().strip('"')=='Zend_Log_Writer_Stream','APP_LOG_WRITER')
                if re.match(r'writers\.[^.]+\.stream\s*=',line):
                    sink=line.split('=',1)[1].strip().strip('"')
                    need(sink.startswith('/opt/kaltura/log/') or sink in ['php://output','php://stderr'],'APP_LOG_SINK')
    services=subprocess.check_output(['systemctl','list-units','--type=service','--state=running','--no-legend','--plain'],timeout=10).decode().lower()
    need(not any(x in services for x in ['filebeat','fluent','logstash','vector.service','promtail']),'UNREVIEWED_LOG_AGENT')
    return snapshot
def _probe_worker(nonce,buffer,state):
    try:
        need(re.fullmatch('[0-9a-f]{32}',nonce) is not None,'NONCE')
        client=Client(Origin('192.168.56.74','http',80))
        _pack_post(client,'http://192.168.56.74/api_v3/baseline_provider_'+nonce+'.php',{'nonce':nonce},buffer,state)
    except Exception:state.value=-2
def probe(nonce):
    p=Path('/opt/kaltura/app/api_v3/web')/('baseline_provider_'+nonce+'.php')
    code=('<?php if ($_SERVER["REQUEST_METHOD"]!=="POST" || $_SERVER["REMOTE_ADDR"]!=="192.168.56.74" || ($_POST["nonce"]??"")!=="'+nonce+'") {http_response_code(403);exit;} header("Content-Type: application/json"); echo json_encode(["nonce"=>"'+nonce+'","version"=>PHP_VERSION,"sapi"=>PHP_SAPI,"modules"=>get_loaded_extensions(),"ini_file"=>php_ini_loaded_file()]);').encode()
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644)
    try:
        os.write(fd,code);os.close(fd);fd=None
        packed=deadline._bounded(_probe_worker,(nonce,),limit=64*1024,deadline=30)
        data=strict_json(base64.b64decode(strict_json(packed)['response'],validate=True))
        need(data.get('nonce')==nonce and data.get('version','').startswith('7.4.') and data.get('sapi') in ['apache2handler','fpm-fcgi'],'WEB_PROVIDER')
        return data
    finally:
        if fd is not None:os.close(fd)
        need(checksum(p)==hashlib.sha256(code).hexdigest(),'PROBE_DRIFT')
        p.unlink();need(not p.exists(),'PROBE_REMOVAL')
def multipart(params,content,nonce):
    boundary='baseline-'+nonce
    need(boundary.encode() not in content,'MULTIPART_BOUNDARY')
    chunks=[]
    for key,value in params.items():
        need(re.fullmatch('[A-Za-z0-9_:]+',key) is not None,'PARAMETER_NAME')
        chunks.extend([('--'+boundary+'\r\nContent-Disposition: form-data; name="'+key+'"\r\n\r\n').encode(),str(value).encode(),b'\r\n'])
    chunks.extend([('--'+boundary+'\r\nContent-Disposition: form-data; name="fileData"; filename="short360.mp4"\r\nContent-Type: video/mp4\r\n\r\n').encode(),content,b'\r\n',('--'+boundary+'--\r\n').encode()])
    return b''.join(chunks),'multipart/form-data; boundary='+boundary
def _upload_worker(params,content,nonce,buffer,state):
    try:
        payload,ctype=multipart(params,content,nonce)
        client=Client(Origin('192.168.56.74','http',80))
        request=Request('http://192.168.56.74/api_v3/index.php',data=payload,method='POST',headers={'Content-Type':ctype,'Accept':'application/json'})
        with client.opener.open(request,timeout=30) as response:
            need(response.status==200 and response.headers.get_content_type()=='application/json','UPLOAD_HTTP')
            client.origin.validate(response.geturl());raw=read_bounded(response,1024*1024)
        memoryview(buffer).cast('B')[:len(raw)]=raw;state.value=len(raw)
    except Exception:state.value=-2
def owned_storage(row,partner,asset,version):
    need(len(row)==7,'FILESYNC_SCHEMA')
    sync_id,partner_id,object_id,stored_version,root,path,status=row
    need(sync_id.isdigit() and int(partner_id)==partner and object_id==asset and stored_version==version and status=='2','FILESYNC_BINDING')
    resolved=(Path(root)/path).resolve()
    allowed=Path('/opt/kaltura/web/content').resolve()
    need(resolved.is_relative_to(allowed) and resolved.is_file(),'SOURCE_STORAGE_SCOPE')
    return resolved,int(sync_id)
def main(nonce,unit,source):
    global JOURNAL_SINCE
    JOURNAL_SINCE=time.strftime('%Y-%m-%d %H:%M:%S UTC',time.gmtime())
    need(re.fullmatch('[0-9a-f]{32}',nonce) is not None,'NONCE')
    need(socket.gethostname()=='kaltura-php74-baseline','HOSTNAME')
    ips=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10))
    addresses={a.get('local') for x in ips for a in x.get('addr_info',[])}
    need('192.168.56.74' in addresses and not addresses.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'HOST_IP')
    need(re.fullmatch('baseline-untimed-[0-9a-f]{8}',unit) is not None,'UNIT_NAME')
    policy=subprocess.check_output(['systemctl','show',unit+'.service','-p','IPAddressDeny','-p','IPAddressAllow','-p','NoNewPrivileges'],timeout=10).decode()
    need('NoNewPrivileges=yes' in policy and '0.0.0.0/0' in policy and '::/0' in policy and '192.168.56.74' in policy and '127.' in policy,'UNIT_NETWORK_POLICY')
    raw=read_file(Path(source),2*1024*1024)
    need(hashlib.sha256(raw).hexdigest()==SOURCE_PIN,'SOURCE_PIN')
    report={'status':'INCOMPLETE','phase':'provider','nonce':nonce,'source_sha256':SOURCE_PIN,'baseline_acceptance':False,'benchmark_executed':False,'owned_entry_id':None}
    def call(service,action,**params):
        return api_value(PostTransport(Origin('192.168.56.74','http',80)).request(dict(service=service,action=action,format=1,**params)).value)
    def checkpoint():print(json.dumps(report,sort_keys=True),flush=True)
    try:
        report['provider']=probe(nonce);report['provider_probe_removed']=True;checkpoint()
        report['phase']='logging-preflight'
        config_snapshot=logging_preflight();report['logging_preflight']={'status':'LOCAL_CONFIG_AND_SINKS_REVIEWED','file_count':len(config_snapshot),'remote_forwarding_detected':False,'scope':'installed rsyslog/apache/nginx/Kaltura logger config plus local sinks and journal; not complete host security attestation'};checkpoint()
        report['phase']='synthetic-partner'
        state=read_file(Path('/root/kaltura-sanity.rc'),256).decode()
        match=re.fullmatch(r'PARTNER_ID=([1-9][0-9]*)\s*',state);need(match is not None,'SYNTHETIC_PARTNER_STATE')
        partner=int(match.group(1));rows=sql('SELECT id,admin_email,secret FROM partner WHERE id='+str(partner))
        need(len(rows)==1 and len(rows[0])==3 and rows[0][0]==str(partner) and rows[0][1]=='sanity@kaltura.local','SYNTHETIC_PARTNER_PROVENANCE')
        secret=rows[0][2];need(re.fullmatch(r'[A-Za-z0-9_+/=-]{16,4096}',secret) is not None,'PRIVATE_USER_SECRET_FORMAT')
        user='baseline-'+nonce
        report.update(partner_id=partner,partner_origin='existing_published_smoke_synthetic',user_id=user)
        report['phase']='invalid-canary-privacy'
        canary='invalid-'+nonce+'-secret-marker'
        rejected=False
        try:call('session','start',partnerId=partner,userId=user,type=0,expiry=3600,secret=canary)
        except Failed as exc:rejected=str(exc)=='API_START_SESSION_ERROR'
        need(rejected,'WRONG_SECRET_CONTROL');time.sleep(.5)
        audit=privacy([canary.encode()]);report['invalid_canary_privacy']=audit
        need(audit['hits']==[0],'INVALID_CANARY_LOGGED');checkpoint()
        report['phase']='user-session'
        ks=call('session','start',partnerId=partner,userId=user,type=0,expiry=3600,secret=secret)
        need(type(ks) is str and 20<=len(ks)<=8192,'USER_KS')
        escalation=False
        try:call('session','start',partnerId=partner,userId=user,type=2,expiry=60,secret=secret)
        except Failed as exc:escalation=str(exc)=='API_START_SESSION_ERROR'
        need(escalation,'ADMIN_ESCALATION_CONTROL');time.sleep(.5)
        audit=privacy([secret.encode(),ks.encode()]);report['valid_auth_privacy']=audit
        need(audit['hits']==[0,0],'VALID_AUTH_LOGGED')
        private=Path('/root/kaltura-baseline-private')/('rehearsal-'+nonce)
        private.mkdir(mode=0o700)
        fd=os.open(private/'credentials.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        try:os.write(fd,json.dumps({'partner_id':partner,'user_id':user,'secret':secret}).encode())
        finally:os.close(fd)
        report['credential_file']=str(private/'credentials.json');checkpoint()
        report['phase']='upload'
        token=call('uploadtoken','add',ks=ks)
        token_id=token.get('id') if type(token) is dict else None
        need(type(token_id) is str and re.fullmatch('[A-Za-z0-9_-]{1,128}',token_id),'UPLOAD_TOKEN')
        reply=deadline._bounded(_upload_worker,({'service':'uploadtoken','action':'upload','format':1,'ks':ks,'uploadTokenId':token_id,'resume':0,'finalChunk':1,'resumeAt':-1},raw,nonce),limit=1024*1024,deadline=30)
        api_value(strict_json(reply))
        entry=call('media','add',ks=ks,**{'entry:objectType':'KalturaMediaEntry','entry:name':'baseline-'+nonce+'-short360','entry:tags':'baseline-'+nonce,'entry:referenceId':'baseline-'+nonce,'entry:mediaType':1})
        projected=media_projection(entry);entry_id=projected['id'];report['owned_entry_id']=entry_id;checkpoint()
        entry=call('media','addContent',ks=ks,entryId=entry_id,**{'resource:objectType':'KalturaUploadedFileTokenResource','resource:token':token_id})
        report['phase']='ready-poll';until=time.monotonic()+600;polls=0
        while True:
            entry=call('media','get',ks=ks,entryId=entry_id,version=-1);polls+=1
            if str(entry.get('status'))=='2':break
            need(time.monotonic()<until and str(entry.get('status')) not in ['-1','-2','3'],'READY_NOT_REACHED')
            time.sleep(2)
        report['ready_poll_count']=polls;report['media_projection']=media_projection(entry);report['conversion_profile_id']=entry.get('conversionProfileId')
        report['phase']='source-binding'
        assets=call('flavorasset','getByEntryId',ks=ks,entryId=entry_id)
        need(type(assets) is list and all(type(a) is dict for a in assets),'ASSET_LIST')
        originals=[a for a in assets if a.get('isOriginal') in [True,1,'1']]
        need(len(originals)==1,'ORIGINAL_ASSET_COUNT')
        asset=originals[0];asset_id=asset.get('id');version=str(asset.get('version'))
        need(type(asset_id) is str and ID.fullmatch(asset_id) and version.isdigit(),'ASSET_VERSION')
        rows=sql("SELECT id,partner_id,object_id,version,file_root,file_path,status FROM file_sync WHERE object_type=4 AND object_sub_type=1 AND status=2 AND partner_id="+str(partner)+" AND object_id='"+asset_id+"' AND version='"+version+"'")
        candidates=[]
        for row in rows:
            try:candidates.append(owned_storage(row,partner,asset_id,version))
            except Failed:continue
        need(len(candidates)==1,'LOCAL_SOURCE_BINDING')
        stored,sync_id=candidates[0];stored_hash=checksum(stored);need(stored_hash==SOURCE_PIN,'STORED_SOURCE_BYTES')
        report.update(original_asset_id=asset_id,asset_version=version,file_sync_id=sync_id,stored_source_sha256=stored_hash)
        data=sql("SELECT partner_id,data FROM entry WHERE id='"+entry_id+"'")
        need(len(data)==1 and len(data[0])==2 and int(data[0][0])==partner,'ENTRY_DB_BINDING')
        first=data[0][1].split('^' if '^' in data[0][1] else '&')[0]
        current=0 if first in ['', 'NULL'] else Path(first).stem
        need(str(current).isdigit(),'ENTRY_CURRENT_VERSION')
        current=int(current);report['entry_current_version']=current
        report['phase']='untimed-api-versions'
        versions=[];base_url=entry.get('dataUrl')
        for request_version in sorted(set([-1,0,current])):
            value=call('media','get',ks=ks,entryId=entry_id,version=request_version)
            need(typed_equal(media_projection(value),report['media_projection']),'VERSION_MEDIA_PROJECTION')
            versions.append({'requested_version':request_version,'accepted':True,'same_data_url_as_current':value.get('dataUrl')==base_url,'entry_current_version':current,'source_asset_version':version})
        listing=call('media','list',ks=ks,**{'filter:objectType':'KalturaMediaEntryFilter','filter:idEqual':entry_id,'filter:orderBy':'+createdAt','pager:objectType':'KalturaFilterPager','pager:pageSize':1,'pager:pageIndex':1})
        need(type(listing) is dict and listing.get('objectType')=='KalturaMediaListResponse' and type(listing.get('objects')) is list and len(listing['objects'])==1,'LIST_FIXTURE')
        need(typed_equal(media_projection(listing['objects'][0]),report['media_projection']) and type(listing.get('totalCount')) in {str,int} and str(listing.get('totalCount'))=='1','LIST_BINDING')
        report['version_observations']=versions;report['list_total_count']=listing['totalCount']
        need(checksum(stored)==SOURCE_PIN and checksum(source)==SOURCE_PIN,'SOURCE_CHANGED')
        need(logging_preflight()==config_snapshot,'LOG_CONFIG_CHANGED')
        report['logging_config_unchanged']=True
        audit=privacy([secret.encode(),ks.encode()]);report['final_auth_privacy']=audit;need(audit['hits']==[0,0],'FINAL_AUTH_LOGGED')
        report.update(status='UNTIMED_OWNED_SHORT_MEDIA_AND_API_OBSERVED',phase='complete',source_after_sha256=SOURCE_PIN,stored_source_after_sha256=SOURCE_PIN,full_tls_workload=False,full_media_matrix=False)
    except Exception as exc:
        report['status']='UNTIMED_REHEARSAL_FAILED'
        report['failure_code']=str(exc) if type(exc) is Failed and re.fullmatch('[A-Z0-9_]{1,100}',str(exc)) else 'CONTROLLED_OPERATION_FAILED'
    finally:checkpoint()
    return 0 if report['status']=='UNTIMED_OWNED_SHORT_MEDIA_AND_API_OBSERVED' else 1
if __name__=='__main__':
    try:result=main(sys.argv[1],sys.argv[2],sys.argv[3])
    except Exception:
        print('Untimed rehearsal rejected',file=sys.stderr);result=1
    raise SystemExit(result)

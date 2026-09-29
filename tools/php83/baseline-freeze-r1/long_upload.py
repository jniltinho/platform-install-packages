"""Phase A of the FullHD60 baseline fixture: one sequential chunked uploadToken upload over pinned HTTPS8443,
then media.add + addContent. No retry of any request; any ambiguous or unexpected acknowledgement stops.
Semantics from pinned Rigel-18.20.0 (UploadTokenService.php:70-97, kUploadTokenMgr.php:118-215,406-461):
part 1 resume=0/finalChunk=0 -> PARTIAL(1); part n resume=1,resumeAt=offset appends when resumeAt equals the
current size and returns uploadedFileSize=offset+length; last part finalChunk=1 -> FULL_UPLOAD(2).
autoFinalize is never requested. READY/flavor verification is a separate read-only phase (B).
Exports sizes/counts/status only; the KS travels in the POST body only."""
import hashlib,json,os,re,stat,time
from pathlib import Path
SOURCE=Path('/var/lib/kaltura-baseline-long-media-r1/fullhd60.mp4')
SIZE=117210794
SHA256='611e3644fb56fc1f12ddccd1d889258d249e36a4eca445451c16d13f5c5f5b07'
CHUNK=1024*1024
REQUEST_LIMIT=CHUNK+64*1024 # below Apache php upload_max_filesize=2M on Baseline74
UPLOAD_BUDGET=600
TOKEN=re.compile(r'[0-9]_[a-z0-9]{8,64}')
ENTRY=re.compile(r'[01]_[a-z0-9]{8}')
CODES=('LONG_SOURCE','LONG_TOKEN_ADD','LONG_PART_TRANSPORT','LONG_PART_ACK','LONG_BUDGET','LONG_MEDIA_ADD','LONG_ADD_CONTENT','LONG_SCHEMA')
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)

def plan():
 return [(i+1,off,min(CHUNK,SIZE-off),i!=0,off+CHUNK>=SIZE) for i,off in enumerate(range(0,SIZE,CHUNK))]

def read_source(path=SOURCE):
 """Root-owned immutable staged copy; exact size and hash before any API call."""
 for p in (path.parent.parent,path.parent):
  s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and not s.st_mode&0o022,'LONG_SOURCE')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  s=os.fstat(f.fileno());need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o444 and s.st_size==SIZE,'LONG_SOURCE')
  data=f.read(SIZE+1)
 need(len(data)==SIZE and hashlib.sha256(data).hexdigest()==SHA256,'LONG_SOURCE');return data

def multipart(params,content,boundary):
 need(re.fullmatch('[a-z0-9-]{16,70}',boundary) is not None and boundary.encode() not in content,'LONG_PART_TRANSPORT')
 out=[]
 for k,v in params.items():
  need(re.fullmatch('[A-Za-z0-9_:]+',k) is not None,'LONG_PART_TRANSPORT')
  out+=[('--'+boundary+'\r\nContent-Disposition: form-data; name="'+k+'"\r\n\r\n').encode(),str(v).encode(),b'\r\n']
 out+=[('--'+boundary+'\r\nContent-Disposition: form-data; name="fileData"; filename="fullhd60.mp4"\r\nContent-Type: video/mp4\r\n\r\n').encode(),content,b'\r\n',('--'+boundary+'--\r\n').encode()]
 body=b''.join(out);need(len(content)<=CHUNK and len(body)<=REQUEST_LIMIT,'LONG_PART_TRANSPORT') # request-body bound
 return body,'multipart/form-data; boundary='+boundary

def _part_worker(fields,ca,pin,params,content,boundary,buffer,state):
 # Spawned child: fixed origin, pinned CA, no redirect/proxy (guarded_http.Client); never marshals error text.
 try:
  from urllib.request import Request
  from guarded_http import Client,Origin,read_bounded
  origin=Origin(*fields)
  if origin.ip!='192.168.56.74' or origin.scheme!='https' or origin.port!=8443:raise ValueError
  client=Client(origin,ca,pin);body,ctype=multipart(params,content,boundary)
  req=Request('https://192.168.56.74:8443/api_v3/index.php',data=body,method='POST',headers={'Content-Type':ctype,'Accept':'application/json'})
  with client.opener.open(req,timeout=30) as r:
   if r.status!=200 or r.headers.get_content_type()!='application/json':raise ValueError
   client.origin.validate(r.geturl());raw=read_bounded(r,1024*1024)
  memoryview(buffer).cast('B')[:len(raw)]=raw;state.value=len(raw)
 except Exception:state.value=-2

def strict_json(raw):
 def pairs(items):
  out={}
  for k,v in items:
   if k in out:raise ValueError
   out[k]=v
  return out
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError()))

def whole(v):
 return v if type(v) is int else int(v) if type(v) is float and v.is_integer() else int(v) if type(v) is str and re.fullmatch('[0-9]{1,12}',v) else None

def ack(value,token_id,expected_size,final):
 """Exact acknowledgement for one part; anything else is ambiguous and stops the upload."""
 need(type(value) is dict and value.get('objectType')=='KalturaUploadToken' and value.get('id')==token_id,'LONG_PART_ACK')
 need(whole(value.get('uploadedFileSize'))==expected_size,'LONG_PART_ACK')
 need(whole(value.get('status'))==(2 if final else 1),'LONG_PART_ACK')

def upload(call,post_part,ks,data,boundary,clock=time.monotonic,progress=lambda value:None):
 """call(service,action,**form)->decoded API value; post_part(params,content)->raw JSON bytes (bounded worker)."""
 need(type(data) is bytes and len(data)==SIZE and hashlib.sha256(data).hexdigest()==SHA256,'LONG_SOURCE')
 started=clock()
 try:token=call('uploadtoken','add',ks=ks)
 except Exception:raise Rejected('LONG_TOKEN_ADD') from None
 need(type(token) is dict and token.get('objectType')=='KalturaUploadToken' and type(token.get('id')) is str and TOKEN.fullmatch(token['id']) is not None and whole(token.get('status'))==0,'LONG_TOKEN_ADD')
 token_id=token['id'];acked=0;done=0
 progress({'token_created':True,'acked_parts':0,'acked_bytes':0,'entry_created':False,'entry_id':None})
 for number,offset,length,resume,final in plan():
  need(clock()-started<=UPLOAD_BUDGET,'LONG_BUDGET');need(offset==acked,'LONG_PART_ACK')
  params={'service':'uploadtoken','action':'upload','format':1,'ks':ks,'uploadTokenId':token_id,'resume':int(resume),'finalChunk':int(final),'resumeAt':offset if resume else -1}
  try:value=strict_json(post_part(params,data[offset:offset+length]))
  except Exception:raise Rejected('LONG_PART_TRANSPORT') from None
  ack(value,token_id,offset+length,final);acked=offset+length;done=number
  progress({'token_created':True,'acked_parts':done,'acked_bytes':acked,'entry_created':False,'entry_id':None})
 need(acked==SIZE,'LONG_PART_ACK');upload_seconds=clock()-started
 try:entry=call('media','add',ks=ks,**{'entry:objectType':'KalturaMediaEntry','entry:name':'baseline-long-fullhd60-'+boundary[-12:],'entry:mediaType':1})
 except Exception:raise Rejected('LONG_MEDIA_ADD') from None
 need(type(entry) is dict and entry.get('objectType')=='KalturaMediaEntry' and type(entry.get('id')) is str and ENTRY.fullmatch(entry['id']) is not None,'LONG_MEDIA_ADD')
 entry_id=entry['id'];progress({'token_created':True,'acked_parts':done,'acked_bytes':acked,'entry_created':True,'entry_id':entry_id})
 try:added=call('media','addContent',ks=ks,entryId=entry_id,**{'resource:objectType':'KalturaUploadedFileTokenResource','resource:token':token_id})
 except Exception:raise Rejected('LONG_ADD_CONTENT') from None
 need(type(added) is dict and added.get('id')==entry_id and whole(added.get('status')) is not None,'LONG_ADD_CONTENT')
 return {'case':'FULLHD60_CHUNKED_UPLOAD_PHASE_A','parts':len(plan()),'bytes':SIZE,'source_sha256':SHA256,'acknowledged_bytes':acked,
  'token_final_status':2,'auto_finalize_requested':False,'retries':0,'upload_seconds':round(upload_seconds,3),'owned_entry_id':entry_id,
  'entry_status_after_add_content':whole(added.get('status')),'ready_verified':False,'full_acceptance':False}

def validate(v):
 need(type(v) is dict and set(v)=={'case','parts','bytes','source_sha256','acknowledged_bytes','token_final_status','auto_finalize_requested','retries','upload_seconds','owned_entry_id','entry_status_after_add_content','ready_verified','full_acceptance'},'LONG_SCHEMA')
 need(v['case']=='FULLHD60_CHUNKED_UPLOAD_PHASE_A' and v['parts']==len(plan()) and v['bytes']==v['acknowledged_bytes']==SIZE and v['source_sha256']==SHA256 and v['token_final_status']==2,'LONG_SCHEMA')
 need(v['auto_finalize_requested'] is False and v['retries']==0 and v['ready_verified'] is False and v['full_acceptance'] is False,'LONG_SCHEMA')
 need(type(v['upload_seconds']) in (int,float) and 0<v['upload_seconds']<=UPLOAD_BUDGET and type(v['owned_entry_id']) is str and ENTRY.fullmatch(v['owned_entry_id']) is not None,'LONG_SCHEMA')
 need(type(v['entry_status_after_add_content']) is int and -2<=v['entry_status_after_add_content']<=7,'LONG_SCHEMA')
 return dict(v)

def validate_progress(v):
 need(type(v) is dict and set(v)=={'token_created','acked_parts','acked_bytes','entry_created','entry_id'} and type(v['token_created']) is bool and type(v['entry_created']) is bool,'LONG_SCHEMA')
 need(type(v['acked_parts']) is int and type(v['acked_bytes']) is int and 0<=v['acked_parts']<=len(plan()) and 0<=v['acked_bytes']<=SIZE,'LONG_SCHEMA')
 need(v['acked_bytes']==(0 if v['acked_parts']==0 else min(SIZE,v['acked_parts']*CHUNK)) and (not v['entry_created'] or v['acked_bytes']==SIZE),'LONG_SCHEMA')
 need(v['entry_id'] is None if not v['entry_created'] else type(v['entry_id']) is str and ENTRY.fullmatch(v['entry_id']) is not None,'LONG_SCHEMA')
 return dict(v)

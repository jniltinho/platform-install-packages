"""R3: r2 plus closed ROUTE_CHECKS before THUMB_ROUTE (r2 native run failed THUMB_ROUTE with HTTPS/443/owned/no query).
Pinned asset.php may append /ks/<download KS> or /relocate/, and edge nodes may rewrite paths; only key names are recorded.
R2 of thumbnail.py: one owned READY thumbnail list/getUrl/download; no URL rewriting or credentials in GET.
R1 failed THUMB_ROW natively. Pinned source stores thumbAsset.size via filesize() (bytes: myEntryUtils,
kBusinessPreConvertDL, kFlowHelper), not the KBytes the API doc claims, so r1's 1024 bound rejected real JPEGs.
R2 bounds size in bytes and records closed per-field booleans (ROW_CHECKS) before any row rejection."""
import re
from urllib.parse import urlsplit,unquote
import hls_response
class Rejected(ValueError):pass
ENTRY='0_wzmt2sfy';PARTNER=102
CODES=('THUMB_API','THUMB_LIST','THUMB_ROW','THUMB_SELECTION','THUMB_URL','THUMB_ORIGIN','THUMB_CREDENTIAL','THUMB_ROUTE','THUMB_ENROLLMENT','THUMB_RESPONSE','THUMB_IMAGE','THUMB_SCHEMA')
def need(ok,code):
 if not ok:raise Rejected(code)
def integer(v,maximum=2147483647):
 need(type(v) is int or type(v) is str and re.fullmatch('0|[1-9][0-9]{0,9}',v) is not None,'THUMB_ROW');n=int(v);need(0<=n<=maximum,'THUMB_ROW');return n

INT=re.compile('0|[1-9][0-9]{0,9}')
def is_int(v,maximum=2147483647):
 return (type(v) is int or type(v) is str and INT.fullmatch(v) is not None) and 0<=int(v)<=maximum
ROW_CHECK_KEYS=('dict','objectType','entryId','partnerId','id_format','id_unique','status','version','thumbParamsId','width','height','size','fileExt')
FILE_EXTS=('jpg','jpeg','png','gif','bif')
def row_checks(row,seen):
 """Closed booleans plus one bounded enum; never copies values other than fixed extension names."""
 d=type(row) is dict;g=row.get if d else (lambda k:None);ident=g('id');raw=g('status');ext=g('fileExt')
 out={'dict':d,'objectType':g('objectType')=='KalturaThumbAsset','entryId':g('entryId')==ENTRY,'partnerId':is_int(g('partnerId')) and int(g('partnerId'))==PARTNER,
  'id_format':type(ident) is str and re.fullmatch('[01]_[a-z0-9]{8}',ident) is not None,'id_unique':type(ident) is str and ident not in seen,
  'status':type(raw) in (int,str) and raw in (-1,'-1') or is_int(raw,9),'version':is_int(g('version')),'thumbParamsId':is_int(g('thumbParamsId')),
  'width':is_int(g('width'),4096),'height':is_int(g('height'),4096),'size':is_int(g('size'),1024*1024),'fileExt':ext in ('jpg','jpeg')}
 out['fileExt_class']=ext if ext in FILE_EXTS else 'ABSENT' if ext is None else 'OTHER'
 return out

def collect(call,describe=None):
 try:v=call(service='thumbasset',action='list',**{'filter:objectType':'KalturaThumbAssetFilter','filter:entryIdEqual':ENTRY,'pager:pageSize':'21','pager:pageIndex':'1'})
 except Exception:raise Rejected('THUMB_API') from None
 need(type(v) is dict and v.get('objectType')=='KalturaThumbAssetListResponse','THUMB_LIST');total=integer(v.get('totalCount'),20)
 rows=v.get('objects');need(type(rows) is list and len(rows)==total and total>0,'THUMB_LIST');safe=[];seen=set()
 for row in rows:
  if describe is not None:
   checks=row_checks(row,seen)
   if not all(checks[k] for k in ROW_CHECK_KEYS):describe('ROW_CHECKS',{'row_index':len(safe),'rows':total,'checks':checks})
  need(type(row) is dict and row.get('objectType')=='KalturaThumbAsset' and row.get('entryId')==ENTRY and integer(row.get('partnerId'))==PARTNER,'THUMB_ROW')
  ident=row.get('id');need(type(ident) is str and re.fullmatch('[01]_[a-z0-9]{8}',ident) is not None and ident not in seen,'THUMB_ROW');seen.add(ident)
  raw=row.get('status');status=-1 if type(raw) in (int,str) and raw in (-1,'-1') else integer(raw,9)
  value={'id':ident,'entryId':ENTRY,'partnerId':PARTNER,'status':status,'version':integer(row.get('version')),'thumbParamsId':integer(row.get('thumbParamsId')),'width':integer(row.get('width'),4096),'height':integer(row.get('height'),4096),'size_API_bytes':integer(row.get('size'),1024*1024),'fileExt':row.get('fileExt')}
  need(value['fileExt'] in ('jpg','jpeg'),'THUMB_ROW');safe.append(value)
 ready=[r for r in safe if r['status']==2];need(len(ready)==1,'THUMB_SELECTION');chosen=ready[0]
 need(chosen['version']>=1 and chosen['width']>0 and chosen['height']>0 and chosen['width']*chosen['height']<=4*1024*1024,'THUMB_SELECTION')
 return sorted(safe,key=lambda r:r['id']),chosen

def shape(url):
 out={'scheme':'OTHER','owned_host':False,'port':'OTHER','query':False,'fragment':False,'userinfo':False}
 if type(url) is not str or len(url)>8192:return out
 try:
  p=urlsplit(url);out.update(scheme=p.scheme.upper() if p.scheme in ('http','https') else 'OTHER',owned_host=p.hostname=='192.168.56.74',port=str(p.port if p.port is not None else 443 if p.scheme=='https' else 80) if p.port in (None,80,443,8443,8444,88) else 'OTHER',query='?' in url,fragment='#' in url,userinfo=p.username is not None or p.password is not None)
 except ValueError:pass
 return out

ROUTE_KEYS=('pv','ev','ks','relocate','file_name','v','thumbAssetId')
def route_checks(path,prefix):
 """Closed shape of the path: prefix match plus key names (enum) of /key/value pairs after the service/action base; no values."""
 base='/api_v3/index.php/service/thumbAsset/action/serve'
 out={'base':path.startswith(base+'/'),'prefix':path.startswith(prefix),'pairs_even':False,'keys':[]}
 if out['base']:
  parts=path[len(base)+1:].split('/');out['pairs_even']=len(parts)%2==0
  out['keys']=[k if k in ROUTE_KEYS else 'OTHER' for k in parts[0::2]][:8]
 return out

def guard(url,row,secret,ks,describe=None):
 need(type(url) is str and 0<len(url)<=8192,'THUMB_URL')
 decoded=unquote(unquote(url));need(all(type(v) is str and len(v)>=16 for v in (secret,ks)),'THUMB_CREDENTIAL')
 need(not any(t in decoded for v in (secret,ks) for t in (v,v[:15])),'THUMB_CREDENTIAL')
 need(url.isascii() and not any(ord(c)<=32 or ord(c)==127 for c in url) and not any(c in url for c in ('%','?','#','\\')),'THUMB_URL')
 try:p=urlsplit(url)
 except ValueError:raise Rejected('THUMB_ORIGIN') from None
 need(p.scheme=='https' and p.netloc in ('192.168.56.74','192.168.56.74:443'),'THUMB_ORIGIN')
 prefix='/api_v3/index.php/service/thumbAsset/action/serve/thumbAssetId/'+row['id']
 if row['version']>1:prefix+='/v/'+str(row['version'])
 ok=p.path.startswith(prefix) and re.fullmatch(r'(?:/pv/[1-9][0-9]{0,9})?(?:/ev/[1-9][0-9]{0,9})?',p.path[len(prefix):]) is not None
 if not ok and describe is not None:describe('ROUTE_CHECKS',route_checks(p.path,prefix))
 need(ok,'THUMB_ROUTE')
 return url

def observe(call,enroll,get,decode,secret,ks,describe):
 rows,row=collect(call,describe);describe('METADATA',{'assets':rows,'selected_id':row['id']})
 try:url=call(service='thumbasset',action='getUrl',id=row['id'])
 except Exception:raise Rejected('THUMB_API') from None
 describe('URL',shape(url))
 try:enroll(url)
 except Exception:raise Rejected('THUMB_ENROLLMENT') from None
 url=guard(url,row,secret,ks,describe)
 try:
  response=get(url,{'Accept-Encoding':'identity'},1024*1024)
  _,body=hls_response.validate(response,1024*1024)
 except Exception:raise Rejected('THUMB_RESPONSE') from None
 types=[v.split(';',1)[0].strip().lower() for k,v in response[1] if k.lower()=='content-type']
 describe('IMAGE',{'status':200,'body_bytes':len(body),'content_type':'JPEG' if len(types)==1 and types[0] in ('image/jpeg','image/jpg') else 'OTHER'})
 need(len(types)==1 and types[0] in ('image/jpeg','image/jpg') and body.startswith(b'\xff\xd8') and body.endswith(b'\xff\xd9'),'THUMB_IMAGE')
 decoded=decode(body,row['width'],row['height'])
 return {'case':'OWNED_READY_THUMBNAIL_JPEG','api_calls':2,'gets':1,'assets':rows,'selected_id':row['id'],'jpeg_bytes':len(body),'decode':decoded,'response_secret_coverage_complete':False,'full_acceptance':False}

def metadata(v):
 need(type(v) is dict and set(v)=={'assets','selected_id'},'THUMB_SCHEMA')
 need(type(v['assets']) is list,'THUMB_SCHEMA')
 raw=[]
 for r in v['assets']:
  need(type(r) is dict and set(r)=={'id','entryId','partnerId','status','version','thumbParamsId','width','height','size_API_bytes','fileExt'},'THUMB_SCHEMA')
  raw.append(dict(r,objectType='KalturaThumbAsset',size=r['size_API_bytes']))
 rows,selected=collect(lambda **kw:{'objectType':'KalturaThumbAssetListResponse','objects':raw,'totalCount':len(raw)})
 need(rows==v['assets'] and selected['id']==v['selected_id'],'THUMB_SCHEMA');return v

def diagnostics(v):
 need(type(v) is dict and set(v)<={'METADATA','URL','IMAGE','ROW_CHECKS','ROUTE_CHECKS'},'THUMB_SCHEMA')
 for k,r in v.items():
  if k=='METADATA':metadata(r)
  elif k=='ROUTE_CHECKS':
   need(type(r) is dict and set(r)=={'base','prefix','pairs_even','keys'} and all(type(r[n]) is bool for n in ('base','prefix','pairs_even')) and type(r['keys']) is list and len(r['keys'])<=8 and all(x in ROUTE_KEYS+('OTHER',) for x in r['keys']) and (r['base'] or not r['keys']),'THUMB_SCHEMA')
  elif k=='ROW_CHECKS':
   need(type(r) is dict and set(r)=={'row_index','rows','checks'} and all(type(r[n]) is int for n in ('row_index','rows')) and 0<=r['row_index']<r['rows']<=20,'THUMB_SCHEMA')
   c=r['checks'];need(type(c) is dict and set(c)==set(ROW_CHECK_KEYS)|{'fileExt_class'} and all(type(c[n]) is bool for n in ROW_CHECK_KEYS) and c['fileExt_class'] in FILE_EXTS+('ABSENT','OTHER') and not all(c[n] for n in ROW_CHECK_KEYS),'THUMB_SCHEMA')
  elif k=='URL':
   need(type(r) is dict and set(r)=={'scheme','owned_host','port','query','fragment','userinfo'} and r['scheme'] in ('HTTP','HTTPS','OTHER') and r['port'] in ('80','88','443','8443','8444','OTHER') and all(type(r[n]) is bool for n in ('owned_host','query','fragment','userinfo')),'THUMB_SCHEMA')
  else:need(type(r) is dict and set(r)=={'status','body_bytes','content_type'} and type(r['status']) is int and r['status']==200 and type(r['body_bytes']) is int and 0<r['body_bytes']<=1024*1024 and r['content_type'] in ('JPEG','OTHER'),'THUMB_SCHEMA')
 return v

def validate(v):
 need(type(v) is dict and set(v)=={'case','api_calls','gets','assets','selected_id','jpeg_bytes','decode','response_secret_coverage_complete','full_acceptance'},'THUMB_SCHEMA')
 need(v['case']=='OWNED_READY_THUMBNAIL_JPEG' and type(v['api_calls']) is int and v['api_calls']==2 and type(v['gets']) is int and v['gets']==1 and v['response_secret_coverage_complete'] is False and v['full_acceptance'] is False,'THUMB_SCHEMA')
 metadata({k:v[k] for k in ('assets','selected_id')});row=next(r for r in v['assets'] if r['id']==v['selected_id']);d=v['decode']
 need(type(v['jpeg_bytes']) is int and 0<v['jpeg_bytes']<=1024*1024,'THUMB_SCHEMA')
 need(type(d) is dict and set(d)=={'codec','width','height','frames','full_image_decode','api_dimensions_match','dynamic_library_cohort_attested','full_acceptance'},'THUMB_SCHEMA')
 need(d['codec']=='mjpeg' and all(type(d[k]) is int for k in ('width','height','frames')) and d['width']==row['width'] and d['height']==row['height'] and d['frames']==1 and d['full_image_decode'] is True and d['api_dimensions_match'] is True and d['dynamic_library_cohort_attested'] is False and d['full_acceptance'] is False,'THUMB_SCHEMA');return v

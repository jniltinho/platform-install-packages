"""Step 2 of the 1080p60 delivered-stream verification: fetch the delivered progressive bytes of flavor 0_j6rfow09
(params 118, entry 0_3h92ab2l) over the pinned HTTPS443 client in exact 1 MiB Range requests and require the
SHA256 of the concatenation to equal the stored file already fully decoded natively (c14cbe84...; step 1). Equal
bytes transfer that decode result to the delivered stream. URL from flavorasset.getUrl (pinned FlavorAssetService:
media clips return getServeFlavorUrl); its tokens are enrolled for privacy scanning BEFORE any guard or GET. The
route must match the serveFlavor grammar observed for the short fixture; no URL rewriting, no retry, no redirects.
The claim is byte equality only (Content-Type is not exposed by the pinned fetch). Credentials: any '%' rejects the URL, and
the raw secret/KS (+15-char prefixes) are searched after two unquote passes, so an encoded form cannot pass unseen.
API errors are exported only as a closed Kaltura error code. Exports sizes/hashes/booleans only."""
import hashlib,re
from urllib.parse import urlsplit,unquote
ENTRY='0_3h92ab2l';FLAVOR='0_j6rfow09';SIZE=31441393;SHA256='c14cbe84aa6f401c813200a12b427518cd3f0c7dd68fb5b7f4d4bd7f8c9ccf7a'
CHUNK=1024*1024;BUDGET=600
GRAMMAR=re.compile(r'/p/102/sp/10200/serveFlavor/entryId/0_3h92ab2l/v/[1-9][0-9]{0,5}(?:/pv/[0-9]{1,10})?(?:/ev/[0-9]{1,10})?/flavorId/0_j6rfow09/fileName/[A-Za-z0-9\-._~!$()*+,;=:@]{1,300}(?:/name/a[.]mp4)?')
API_ERRORS=('FLAVOR_ASSET_ID_NOT_FOUND','ASSET_ID_NOT_FOUND','FLAVOR_ASSET_IS_NOT_READY','ENTRY_ID_NOT_FOUND','ASSET_NOT_ALLOWED','SERVICE_FORBIDDEN','INVALID_KS','ACCESS_CONTROL_RESTRICTED','INVALID_ENTRY_ID')
CODES=('PROG_API','PROG_URL','PROG_ENROLLMENT','PROG_CREDENTIAL','PROG_ORIGIN','PROG_ROUTE','PROG_RESPONSE','PROG_RANGE','PROG_BUDGET','PROG_HASH','PROG_SCHEMA')
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def shape(url):
 out={'scheme':'OTHER','owned_host':False,'port':'OTHER','query':False,'fragment':False,'userinfo':False,'grammar':False}
 if type(url) is not str or len(url)>8192:return out
 try:
  p=urlsplit(url);port=p.port if p.port is not None else 443 if p.scheme=='https' else 80 if p.scheme=='http' else None
  out.update(scheme=p.scheme.upper() if p.scheme in ('http','https') else 'OTHER',owned_host=p.hostname=='192.168.56.74',port=str(port) if port in (80,443,8443,8444) else 'OTHER',
   query=bool(p.query),fragment=bool(p.fragment),userinfo=p.username is not None or p.password is not None,grammar=GRAMMAR.fullmatch(p.path) is not None)
 except ValueError:pass
 return out
def guard(url,secret,ks):
 need(type(url) is str and 0<len(url)<=8192,'PROG_URL')
 decoded=unquote(unquote(url));need(all(type(v) is str and len(v)>=16 for v in (secret,ks)),'PROG_CREDENTIAL')
 need(not any(t in decoded for v in (secret,ks) for t in (v,v[:15])),'PROG_CREDENTIAL')
 need(url.isascii() and not any(ord(c)<=32 or ord(c)==127 for c in url) and not any(c in url for c in ('%','?','#','\\')),'PROG_URL')
 try:p=urlsplit(url)
 except ValueError:raise Rejected('PROG_ORIGIN') from None
 need(p.scheme=='https' and p.netloc in ('192.168.56.74','192.168.56.74:443') and p.username is None and p.password is None,'PROG_ORIGIN')
 need(GRAMMAR.fullmatch(p.path) is not None,'PROG_ROUTE')
 return url
def observe(call,enroll,fetch,secret,ks,describe,clock):
 """fetch(url,headers,limit,status)->(selected_headers,body): short_delivery443.fetch bound to the pinned HTTPS443 GET."""
 try:url=call(service='flavorasset',action='getUrl',id=FLAVOR)
 except Exception:raise Rejected('PROG_API') from None
 if type(url) is dict:
  code=url.get('code') if url.get('objectType')=='KalturaAPIException' else None
  describe('API_ERROR',{'code':code if code in API_ERRORS else 'OTHER'});raise Rejected('PROG_API')
 describe('URL',shape(url))
 try:enroll(url)
 except Exception:raise Rejected('PROG_ENROLLMENT') from None
 url=guard(url,secret,ks)
 digest=hashlib.sha256();started=clock();requests=0;types=set()
 for offset in range(0,SIZE,CHUNK):
  end=min(offset+CHUNK,SIZE)-1;need(clock()-started<=BUDGET,'PROG_BUDGET')
  try:headers,body=fetch(url,{'Accept-Encoding':'identity','Range':'bytes=%d-%d'%(offset,end)},CHUNK,206)
  except Exception:raise Rejected('PROG_RESPONSE') from None
  requests+=1
  need(headers.get('content-range')=='bytes %d-%d/%d'%(offset,end,SIZE) and headers.get('content-length')==str(end-offset+1) and len(body)==end-offset+1,'PROG_RANGE')
  digest.update(body)
 need(clock()-started<=BUDGET+30,'PROG_BUDGET') # each GET is bounded to 30 s by the pinned transport
 need(digest.hexdigest()==SHA256,'PROG_HASH')
 describe('TRANSFER',{'range_requests':requests,'bytes':SIZE})
 return {'case':'DELIVERED_PROGRESSIVE_1080P60','flavor_id':FLAVOR,'entry_id':ENTRY,'range_requests':requests,'bytes':SIZE,'sha256':SHA256,
  'delivered_equals_stored_decoded':True,'full_body_single_request':False,'full_acceptance':False}
def validate(v):
 need(type(v) is dict and set(v)=={'case','flavor_id','entry_id','range_requests','bytes','sha256','delivered_equals_stored_decoded','full_body_single_request','full_acceptance'},'PROG_SCHEMA')
 need(v['case']=='DELIVERED_PROGRESSIVE_1080P60' and v['flavor_id']==FLAVOR and v['entry_id']==ENTRY and v['bytes']==SIZE and v['sha256']==SHA256,'PROG_SCHEMA')
 need(type(v['range_requests']) is int and v['range_requests']==-(-SIZE//CHUNK) and v['delivered_equals_stored_decoded'] is True and v['full_body_single_request'] is False and v['full_acceptance'] is False,'PROG_SCHEMA')
 return dict(v)
def diagnostics(v):
 need(type(v) is dict and set(v)<={'API_ERROR','URL','TRANSFER'},'PROG_SCHEMA')
 for k,r in v.items():
  if k=='API_ERROR':need(type(r) is dict and set(r)=={'code'} and r['code'] in API_ERRORS+('OTHER',),'PROG_SCHEMA')
  elif k=='URL':need(type(r) is dict and set(r)=={'scheme','owned_host','port','query','fragment','userinfo','grammar'} and r['scheme'] in ('HTTP','HTTPS','OTHER') and r['port'] in ('80','443','8443','8444','OTHER') and all(type(r[n]) is bool for n in ('owned_host','query','fragment','userinfo','grammar')),'PROG_SCHEMA')
  else:need(type(r) is dict and set(r)=={'range_requests','bytes'} and r['range_requests']==-(-SIZE//CHUNK) and r['bytes']==SIZE,'PROG_SCHEMA')
 return v

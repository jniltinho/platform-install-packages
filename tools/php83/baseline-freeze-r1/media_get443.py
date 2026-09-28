"""Fixed .74 pinned-TLS GET with private bounded IPC and overall 30s deadline."""
import base64,json,re
from urllib.request import Request
import deadline_transport as deadline
from guarded_http import BoundaryError,Client,Origin,read_bounded
CA_PIN='5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef'
MAX_BODY=2*1024*1024
IPC_LIMIT=3*1024*1024

def validate(url,headers,limit):
 origin=Origin('192.168.56.74','https',443);origin.validate(url)
 if type(url) is not str or len(url)>8192 or any(ord(c)<=32 or ord(c)==127 for c in url) or '\\' in url:raise BoundaryError('GET_URL')
 if type(limit) is not int or not 0<limit<=MAX_BODY:raise BoundaryError('GET_LIMIT')
 if type(headers) is not dict or set(headers) not in ({'Accept-Encoding'},{'Accept-Encoding','Range'}) or headers.get('Accept-Encoding')!='identity':raise BoundaryError('GET_HEADERS')
 if 'Range' in headers and (type(headers['Range']) is not str or re.fullmatch(r'bytes=[0-9]{1,10}-[0-9]{1,10}',headers['Range']) is None):raise BoundaryError('GET_RANGE')
 return origin

def _worker(ca,url,headers,limit,buffer,state):
 try:
  origin=validate(url,headers,limit);client=Client(origin,ca,CA_PIN)
  with client.opener.open(Request(url,headers=headers,method='GET'),timeout=30) as response:
   origin.validate(response.geturl())
   if response.status not in (200,206):raise BoundaryError('GET_STATUS')
   pairs=list(response.headers.items())
   if len(pairs)>100 or sum(len(k)+len(v) for k,v in pairs)>16384:raise BoundaryError('GET_HEADERS')
   body=read_bounded(response,limit)
   packed=json.dumps({'status':response.status,'headers':pairs,'body':base64.b64encode(body).decode('ascii')},separators=(',',':')).encode()
  if len(packed)>IPC_LIMIT:raise BoundaryError('GET_IPC')
  memoryview(buffer).cast('B')[:len(packed)]=packed;state.value=len(packed)
 except Exception:state.value=-2

def request(ca,url,headers,limit):
 origin=validate(url,headers,limit);Client(origin,ca,CA_PIN)
 raw=deadline._bounded(_worker,(ca,url,headers,limit),limit=IPC_LIMIT,deadline=30)
 try:
  value=json.loads(raw)
  if type(value) is not dict or set(value)!={'status','headers','body'} or type(value['status']) is not int or value['status'] not in (200,206):raise ValueError()
  pairs=value['headers']
  if type(pairs) is not list or len(pairs)>100 or any(type(p) is not list or len(p)!=2 or any(type(v) is not str for v in p) for p in pairs):raise ValueError()
  if sum(len(k)+len(v) for k,v in pairs)>16384:raise ValueError()
  body=base64.b64decode(value['body'],validate=True)
  if len(body)>limit:raise ValueError()
  return value['status'],pairs,body
 except Exception:raise BoundaryError('GET_RESPONSE') from None

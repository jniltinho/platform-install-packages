"""Reject credential-bearing URL before GET; enroll returned token candidates privately."""
import re
from urllib.parse import urlsplit,unquote,parse_qsl
class Rejected(ValueError):pass
MARKERS={'ks','kt','token','access_token','auth','authorization','session','sessionid','password','secret','signature','sig'}
def inspect(value,secret,ks,tokens):
 if type(value) is not str or not 0<len(value)<=8192:raise Rejected('URL_SHAPE')
 # No decoding bypass: two canonical levels are inspected, leftover encoding rejected.
 decoded=value
 for _ in range(2):decoded=unquote(decoded)
 try:p=urlsplit(decoded)
 except ValueError:raise Rejected('URL_SHAPE') from None
 segments=p.path.split('/');query=parse_qsl(p.query,keep_blank_values=True,max_num_fields=32)
 candidates=[v for v in segments if len(v)>=16]+[v for _,v in query if len(v)>=16]
 for v in candidates:
  if 16<=len(v)<=8192 and v not in tokens:
   if len(tokens)>=34:raise Rejected('URL_PATTERN_LIMIT')
   tokens.append(v)
 if any(v and v in decoded for v in (secret,ks,secret[:15],ks[:15])):raise Rejected('URL_CREDENTIAL')
 if p.query or p.fragment or p.username is not None or p.password is not None or '%' in decoded or any(s.lower() in MARKERS for s in segments):raise Rejected('URL_AUTH_SHAPE')
 return value

def shape(value):
 # Descriptor never copies any URL component into its closed output.
 out={'scheme':'other','port':'other','target_host_match':False,'query_present':False,'credential_path':False}
 if type(value) is not str or len(value)>8192:return out
 try:
  p=urlsplit(value);scheme=p.scheme;port=p.port
  if port is None:port={'http':80,'https':443}.get(scheme)
  decoded=unquote(unquote(p.path))
  out.update(scheme=scheme if scheme in ('http','https') else 'other',port=str(port) if port in (80,443,8443) else 'other',target_host_match=p.hostname=='192.168.56.74',query_present=bool(p.query),credential_path=any(s.lower() in MARKERS for s in decoded.split('/')))
 except ValueError:pass
 return out

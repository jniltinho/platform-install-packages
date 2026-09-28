"""No transmission: conservative bounded candidate enrollment, never URL output."""
from urllib.parse import urlsplit,unquote,parse_qsl
class Incomplete(ValueError):pass
def enroll(value,tokens):
 if type(value) is not str or not 0<len(value)<=8192 or type(tokens) is not list:raise Incomplete('URL_ENROLLMENT_INCOMPLETE')
 try:
  p=urlsplit(unquote(unquote(value)));parts=p.path.split('/');query=parse_qsl(p.query,keep_blank_values=True,max_num_fields=32)
 except ValueError:raise Incomplete('URL_ENROLLMENT_INCOMPLETE') from None
 candidates=[v for v in parts if len(v)>=16]+[v for _,v in query if len(v)>=16]
 for v in candidates:
  if v not in tokens:
   if len(tokens)>=34 or len(v)>8192:raise Incomplete('URL_ENROLLMENT_INCOMPLETE')
   tokens.append(v)
 # Short signed values cannot use the vetted >=16 byte scanner protocol.
 auth={'ks','kt','token','access_token','auth','authorization','session','sessionid','password','secret','signature','sig'}
 short=any(0<len(v)<16 for _,v in query)
 short=short or any(k.lower() in auth and (i+1==len(parts) or len(parts[i+1])<16) for i,k in enumerate(parts))
 if short or p.username is not None or p.password is not None or p.fragment or not p.scheme or not p.netloc:raise Incomplete('URL_ENROLLMENT_INCOMPLETE')
 return None

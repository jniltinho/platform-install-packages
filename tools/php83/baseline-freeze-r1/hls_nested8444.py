"""Exact native selected asset playlist route; no arbitrary same-host permission."""
import re
from urllib.parse import urlsplit,quote,quote_plus
class Rejected(ValueError):pass
CODES=('NESTED_URL_SHAPE','NESTED_CREDENTIAL','NESTED_ORIGIN','NESTED_ROUTE_PREFIX','NESTED_ROUTE_KEY','NESTED_ROUTE_VALUE','NESTED_ROUTE_DUPLICATE')
def need(ok,code):
 if not ok:raise Rejected(code)
def guard(url,secret,ks):
 need(type(url) is str and 0<len(url)<=8192 and url.isascii() and not any(ord(c)<=32 or ord(c)==127 for c in url) and not any(c in url for c in ('\\','%','?','#')),'NESTED_URL_SHAPE')
 for value in (secret,ks):
  need(type(value) is str and len(value)>=16,'NESTED_CREDENTIAL')
  for token in (value,value[:15]):need(not any(x in url for x in (token,quote(token,safe=''),quote_plus(token,safe=''))),'NESTED_CREDENTIAL')
 try:p=urlsplit(url)
 except ValueError:raise Rejected('NESTED_ORIGIN') from None
 need(p.scheme=='https' and p.netloc=='192.168.56.74:8444','NESTED_ORIGIN')
 prefix='/hls/p/102/sp/10200/serveFlavor/';suffix='/index.m3u8'
 need(p.path.startswith(prefix) and p.path.endswith(suffix),'NESTED_ROUTE_PREFIX')
 parts=p.path[len(prefix):-len(suffix)].split('/');need(len(parts)%2==0 and 8<=len(parts)<=12,'NESTED_ROUTE_KEY')
 values={}
 for k,v in zip(parts[::2],parts[1::2]):
  need(k in ('entryId','v','pv','ev','flavorId','name'),'NESTED_ROUTE_KEY');need(k not in values,'NESTED_ROUTE_DUPLICATE');values[k]=v
 need(all(values.get(k)==v for k,v in {'entryId':'0_wzmt2sfy','v':'2','flavorId':'0_21p06l2j','name':'a.mp4'}.items()),'NESTED_ROUTE_VALUE')
 for k in ('pv','ev'):
  if k in values:need(re.fullmatch('[1-9][0-9]{0,9}',values[k]) is not None,'NESTED_ROUTE_VALUE')
 # Native emitter order, optional version-cache components exactly in place.
 need(parts[::2]==['entryId','v']+([k for k in ('pv','ev') if k in values])+['flavorId','name'],'NESTED_ROUTE_KEY')
 return url

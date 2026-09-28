"""Exact private FileSync315 route join; no arbitrary filename exemption."""
import re
from pathlib import PurePosixPath
from urllib.parse import urlsplit,unquote,parse_qsl
NAME='0_wzmt2sfy_0_ewuu0o46_2.mp4'
MARKERS={'ks','kt','token','access_token','auth','authorization','session','sessionid','password','secret','signature','sig'}
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def mapping(root,path,stored):
 need(type(root) is str and root in ('/opt/kaltura/web','/opt/kaltura/web/'),'DIRECT_STORAGE_ROOT')
 need(type(path) is str and len(path)<=1024,'DIRECT_STORAGE_PATH')
 match=re.fullmatch(r'/content/entry/data//?(0|[1-9][0-9]{0,9})/(0|[1-9][0-9]{0,2})/'+re.escape(NAME),path)
 need(match is not None and int(match[2])<1000,'DIRECT_STORAGE_PATH')
 need(str(PurePosixPath(root+path))==str(stored),'DIRECT_STORAGE_JOIN')
 return path

def check(value,secret,ks,candidates,*,root,path,stored):
 expected=mapping(root,path,stored)
 need(type(value) is str and 0<len(value)<=8192,'DIRECT_URL_SHAPE')
 need(not any(ord(c)<=32 or ord(c)==127 for c in value) and '\\' not in value,'DIRECT_URL_SHAPE')
 decoded=unquote(unquote(value))
 try:p=urlsplit(decoded)
 except ValueError:raise Rejected('DIRECT_URL_SHAPE') from None
 parts=p.path.split('/')
 # Existing full/current-secret and KS prefixes are never exempt, even in a
 # FileSync-matching path. Callers retain the original credential scan patterns.
 need(type(secret) is str and type(ks) is str and len(secret)>=16 and len(ks)>=20,'DIRECT_CREDENTIAL_SHAPE')
 credential=any(v in decoded for v in (secret,secret[:15],ks,ks[:15]))
 auth=p.query or p.fragment or p.username is not None or p.password is not None or any(v.lower() in MARKERS for v in parts)
 exact=False
 try:exact=p.scheme=='https' and p.hostname=='192.168.56.74' and p.port in (None,443) and p.path==expected and '%' not in value
 except ValueError:pass
 if not exact or credential or auth:
  # Rejected candidates remain privately available for the failure audit.
  try:values=[v for v in parts if len(v)>=16]+[v for _,v in parse_qsl(p.query,keep_blank_values=True,max_num_fields=32) if len(v)>=16]
  except ValueError:raise Rejected('DIRECT_URL_SHAPE') from None
  for v in values:
   if v not in candidates:
    need(len(candidates)<34 and len(v)<=8192,'DIRECT_PATTERN_LIMIT');candidates.append(v)
  need(not credential,'DIRECT_URL_CREDENTIAL');need(not auth,'DIRECT_URL_AUTH');raise Rejected('DIRECT_URL_MISMATCH')
 # Exactly the stored public resource path, not arbitrary length-based values.
 return value

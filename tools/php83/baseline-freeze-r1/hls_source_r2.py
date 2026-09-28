"""Source-bound FIRST manifest URL only. Never authorizes nested GETs."""
import re
from urllib.parse import urlsplit,quote,quote_plus
ENTRY='0_wzmt2sfy'
ASSET='0_21p06l2j'
class Rejected(ValueError):pass

def need(ok,code):
 if not ok:raise Rejected(code)

def guard(row,secret,ks):
 need(type(row) is dict and row.get('objectType')=='KalturaPlaybackSource','SOURCE_TYPE')
 need(set(row)<= {'objectType','deliveryProfileId','format','protocols','flavorIds','url','drm'},'SOURCE_SCHEMA')
 need(row.get('format')=='applehttp' and row.get('flavorIds')==ASSET,'SOURCE_IDENTITY')
 protocols=row.get('protocols');need(type(protocols) is str and protocols in ('https','http,https','https,http'),'SOURCE_PROTOCOL')
 need(row.get('drm') is None or row['drm']==[],'DRM_UNSUPPORTED')
 profile=row.get('deliveryProfileId')
 need(type(profile) in (int,str) and re.fullmatch(r'[1-9][0-9]{0,9}',str(profile)) is not None,'PROFILE_ID')
 url=row.get('url')
 need(type(url) is str and 0<len(url)<=8192 and url.isascii() and not any(ord(c)<=32 or ord(c)==127 for c in url) and '\\' not in url and '%' not in url and '?' not in url and '#' not in url,'URL_SHAPE')
 # Exact full route makes tokens/arbitrary suffixes impossible; still explicitly
 # prohibit any known current credential/prefix in raw or encoded spelling.
 for value in (secret,ks):
  need(type(value) is str and len(value)>=16,'CREDENTIAL_INPUT')
  for token in (value,value[:15]):
   need(not any(v in url for v in (token,quote(token,safe=''),quote_plus(token,safe=''))),'URL_CREDENTIAL')
 try:p=urlsplit(url);port=p.port
 except ValueError:raise Rejected('URL_SHAPE') from None
 need(p.scheme=='https' and p.hostname=='192.168.56.74' and p.netloc in ('192.168.56.74','192.168.56.74:443') and port in (None,443) and not p.query and not p.fragment,'URL_ORIGIN_AUTH')
 expected=f'/p/102/sp/102/playManifest/entryId/{ENTRY}/flavorIds/{ASSET}/deliveryProfileId/{profile}/protocol/https/format/applehttp/a.m3u8'
 need(p.path==expected,'MANIFEST_ROUTE')
 return url  # Private value, unchanged. Never publish/hash it.

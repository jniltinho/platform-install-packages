"""Closed no-GET route observation; unknown candidates remain privacy scan inputs."""
import re
from urllib.parse import urlsplit,unquote,parse_qsl
ENTRY='0_wzmt2sfy';ASSET='0_ewuu0o46'
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def filename(entry_name,params_name,extension):
 # Native keepOnlyValidUrlChars is byte-oriented preg_replace without /u.
 need(type(entry_name) is str and 0<len(entry_name)<=256 and type(params_name) is str and len(params_name)<=256 and extension=='mp4','ROUTE_FILENAME_INPUT')
 raw=(entry_name+(' ('+params_name+')' if params_name not in ('','0') else '')).replace('\n',' ').encode('utf-8')
 return re.sub(rb'[^A-Za-z0-9\-._~!$()*+,;=:@]',b'_',raw).decode('ascii')+'.mp4'
def describe(value,*,stored_path,expected_filename,secret,ks,candidates):
 need(type(value) is str and 0<len(value)<=8192 and not any(ord(c)<=32 or ord(c)==127 for c in value) and '\\' not in value,'ROUTE_URL_SHAPE')
 decoded=unquote(unquote(value))
 try:p=urlsplit(decoded);port=p.port if p.port is not None else (443 if p.scheme=='https' else 80 if p.scheme=='http' else None);query=parse_qsl(p.query,keep_blank_values=True,max_num_fields=32)
 except ValueError:raise Rejected('ROUTE_URL_SHAPE') from None
 parts=p.path.split('/');roles=[]
 keys={'fileName':'FILENAME','name':'NAME_SUFFIX','entryId':'ENTRY','flavorId':'ASSET','v':'VERSION','pv':'PARTNER_VERSION','ev':'ENTRY_VERSION','p':'PARTNER','sp':'SUBPARTNER'}
 for index,v in enumerate(parts):
  if len(v)<16:continue
  role=keys.get(parts[index-1] if index else '', 'OTHER')
  if role not in roles:roles.append(role)
 for v in [v for v in parts if len(v)>=16]+[v for _,v in query if len(v)>=16]:
  if v not in candidates:
   need(type(candidates) is list and len(candidates)<34 and len(v)<=8192,'ROUTE_PATTERN_LIMIT');candidates.append(v)
 def matches(key,expected):
  positions=[i for i,v in enumerate(parts) if v==key]
  return len(positions)==1 and positions[0]+1<len(parts) and parts[positions[0]+1]==expected
 serve=len(parts)>5 and parts[0]=='' and parts[1]=='p' and parts[3]=='sp' and parts[5]=='serveFlavor'
 kind='SERVE_FLAVOR' if serve else 'DIRECT_CONTENT' if p.path.startswith('/content/') else 'OTHER'
 # Explicit known observed grammar; this is a descriptor, not a request allowlist.
 grammar=re.fullmatch(r'/p/102/sp/10200/serveFlavor/entryId/0_wzmt2sfy/v/2(?:/pv/[0-9]+)?(?:/ev/[0-9]+)?/flavorId/0_ewuu0o46/fileName/[^/]+(?:/name/a[.]mp4)?',p.path) is not None
 auth_markers={'ks','kt','token','access_token','auth','authorization','session','sessionid','password','secret','signature','sig'}
 return {'route_kind':kind,'source_serve_flavor_grammar':grammar,'origin_https443':p.scheme=='https' and p.hostname=='192.168.56.74' and port==443,'direct_file_sync_path_equal':p.path==stored_path,'owned_entry_equal':matches('entryId',ENTRY),'owned_asset_equal':matches('flavorId',ASSET),'version_equal':matches('v','2'),'partner_equal':matches('p','102'),'subpartner_equal':matches('sp','10200'),'expected_filename_known':expected_filename is not None,'filename_equal_expected':expected_filename is not None and matches('fileName',expected_filename),'query_present':bool(p.query),'credential_marker_present':any(v.lower() in auth_markers for v in parts) or p.username is not None or p.password is not None,'current_credential_present':any(v and v in decoded for v in (secret,secret[:15],ks,ks[:15])),'long_segment_roles':roles,'candidate_count':len(candidates),'get_requests':0,'raw_url_persisted':False,'candidate_patterns_exempted':False,'full_acceptance':False}
def validate(value):
 keys={'route_kind','source_serve_flavor_grammar','origin_https443','direct_file_sync_path_equal','owned_entry_equal','owned_asset_equal','version_equal','partner_equal','subpartner_equal','expected_filename_known','filename_equal_expected','query_present','credential_marker_present','current_credential_present','long_segment_roles','candidate_count','get_requests','raw_url_persisted','candidate_patterns_exempted','full_acceptance'}
 need(type(value) is dict and set(value)==keys,'ROUTE_PUBLIC_SCHEMA')
 need(value['route_kind'] in ('SERVE_FLAVOR','DIRECT_CONTENT','OTHER'),'ROUTE_PUBLIC_SCHEMA')
 for k in keys-{'route_kind','long_segment_roles','candidate_count','get_requests'}:need(type(value[k]) is bool,'ROUTE_PUBLIC_SCHEMA')
 roles=value['long_segment_roles'];need(type(roles) is list and len(roles)<=10 and all(type(v) is str and v in {'FILENAME','NAME_SUFFIX','ENTRY','ASSET','VERSION','PARTNER_VERSION','ENTRY_VERSION','PARTNER','SUBPARTNER','OTHER'} for v in roles) and len(set(roles))==len(roles),'ROUTE_PUBLIC_SCHEMA')
 need(type(value['candidate_count']) is int and 0<=value['candidate_count']<=34 and type(value['get_requests']) is int and value['get_requests']==0 and value['raw_url_persisted'] is False and value['candidate_patterns_exempted'] is False and value['full_acceptance'] is False,'ROUTE_PUBLIC_SCHEMA')
 return value

"""One exact context-selected stored row, fixed SQL, no raw URL output."""
import re
from urllib.parse import urlsplit
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('DELIVERY_PROFILE_OBSERVATION')
def number(v):
 need(type(v) in (str,int) and re.fullmatch(r'0|[1-9][0-9]{0,9}',str(v)) is not None);return int(v)
def selected(response):
 need(type(response) is dict and response.get('objectType')=='KalturaPlaybackContext')
 rows=response.get('sources');need(type(rows) is list and len(rows)==1)
 row=rows[0];need(type(row) is dict and row.get('objectType')=='KalturaPlaybackSource' and row.get('format')=='applehttp' and row.get('flavorIds')=='0_21p06l2j')
 ident=number(row.get('deliveryProfileId'));need(ident>0);return ident
def query(ident):
 need(type(ident) is int and 0<ident<=9999999999)
 return 'SELECT id,partner_id,type,status,is_default,parent_id,streamer_type,COALESCE(media_protocols,\'NULL\'),HEX(url) FROM delivery_profile WHERE id='+str(ident)+' LIMIT 2'
def parse(rows,ident):
 need(type(rows) is list and len(rows)==1 and type(rows[0]) is list and len(rows[0])==9)
 r=rows[0];values=[number(v) for v in r[:6]];need(values[0]==ident and values[1] in (0,102) and values[4] in (0,1) and r[6]=='applehttp')
 need(r[7] in ('NULL','http','https','http,https','https,http'))
 need(type(r[8]) is str and re.fullmatch(r'[0-9A-F]{0,16384}',r[8]) is not None)
 try:
  url=bytes.fromhex(r[8]).decode('ascii');need(len(url)<=8192 and not any(ord(c)<=32 or ord(c)==127 for c in url))
  p=urlsplit(url if '://' in url else '//'+url);port=p.port
 except (ValueError,UnicodeError):raise Rejected('DELIVERY_PROFILE_OBSERVATION') from None
 return {'profile_id':values[0],'partner_id':values[1],'profile_type':values[2],'status':values[3],'is_default':bool(values[4]),'parent_id':values[5],'streamer_type':'applehttp','media_protocols':r[7], 'url_scheme':p.scheme if p.scheme in ('http','https') else 'absent' if not p.scheme else 'other','owned_host_match':p.hostname=='192.168.56.74','port':port if port in (80,88,443,8443,8444) else None,'port_explicit':port is not None,'path_hls':p.path=='/hls','userinfo':p.username is not None or p.password is not None,'query':bool(p.query),'fragment':bool(p.fragment),'selected_descriptor_id_joined':True,'sql_selects':1,'configuration_changed':False,'full_acceptance':False}
def validate(v):
 keys={'profile_id','partner_id','profile_type','status','is_default','parent_id','streamer_type','media_protocols','url_scheme','owned_host_match','port','port_explicit','path_hls','userinfo','query','fragment','selected_descriptor_id_joined','sql_selects','configuration_changed','full_acceptance'}
 need(type(v) is dict and set(v)==keys)
 for k in ('profile_id','partner_id','profile_type','status','parent_id','sql_selects'):need(type(v[k]) is int and 0<=v[k]<=9999999999)
 need(v['profile_id']>0 and v['partner_id'] in (0,102) and v['sql_selects']==1 and v['streamer_type']=='applehttp' and v['media_protocols'] in ('NULL','http','https','http,https','https,http') and v['url_scheme'] in ('http','https','absent','other') and (v['port'] is None or type(v['port']) is int and v['port'] in (80,88,443,8443,8444)))
 for k in ('is_default','owned_host_match','port_explicit','path_hls','userinfo','query','fragment','selected_descriptor_id_joined','configuration_changed','full_acceptance'):need(type(v[k]) is bool)
 need(v['selected_descriptor_id_joined'] is True and v['configuration_changed'] is False and v['full_acceptance'] is False);return v

"""Closed native Symfony key/value route; no URL rewriting or credential exemptions."""
import re
from urllib.parse import urlsplit,unquote
CODES=('SOURCE_ROUTE_SHAPE','SOURCE_ROUTE_CREDENTIAL','SOURCE_ROUTE_ENCODING','SOURCE_ROUTE_ORIGIN','SOURCE_ROUTE_AUTH','SOURCE_ROUTE_ORDER','SOURCE_ROUTE_EMPTY_SEGMENT','SOURCE_ROUTE_UNKNOWN_KEY','SOURCE_ROUTE_DUPLICATE_KEY','SOURCE_ROUTE_EXPECTED_VALUE')
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def check(value,*,expected_filename,secret,ks):
 need(type(value) is str and 0<len(value)<=8192,'SOURCE_ROUTE_SHAPE')
 decoded=unquote(unquote(value))
 need(type(secret) is str and len(secret)>=15 and type(ks) is str and len(ks)>=15,'SOURCE_ROUTE_CREDENTIAL')
 need(not any(v in decoded for v in (secret,secret[:15],ks,ks[:15])),'SOURCE_ROUTE_CREDENTIAL')
 need('%' not in value and '\\' not in value and value.isascii() and not any(ord(c)<=32 or ord(c)==127 for c in value),'SOURCE_ROUTE_ENCODING')
 try:p=urlsplit(value);port=p.port if p.port is not None else 443
 except ValueError:raise Rejected('SOURCE_ROUTE_SHAPE') from None
 need(p.scheme=='https' and p.hostname=='192.168.56.74' and port==443,'SOURCE_ROUTE_ORIGIN')
 need(not p.query and not p.fragment and p.username is None and p.password is None and '?' not in value and '#' not in value,'SOURCE_ROUTE_AUTH')
 parts=p.path.split('/')
 need(all(parts[1:]),'SOURCE_ROUTE_EMPTY_SEGMENT')
 need(parts[:6]==['','p','102','sp','10200','serveFlavor'],'SOURCE_ROUTE_ORDER')
 tail=parts[6:];need(len(tail)%2==0 and 8<=len(tail)<=16,'SOURCE_ROUTE_ORDER')
 values={};allowed={'entryId','flavorId','v','fileName','pv','ev','name','forceproxy'}
 for key,val in zip(tail[::2],tail[1::2]):
  need(key in allowed,'SOURCE_ROUTE_UNKNOWN_KEY');need(key not in values,'SOURCE_ROUTE_DUPLICATE_KEY');values[key]=val
 need(type(expected_filename) is str and 0<len(expected_filename)<=1024 and re.fullmatch(r'[A-Za-z0-9\-._~!$()*+,;=:@]+[.]mp4',expected_filename) is not None,'SOURCE_ROUTE_EXPECTED_VALUE')
 # parse_str decodes + to space, and & splits fields. Refuse those even in source-derived names.
 need('+' not in expected_filename and '&' not in expected_filename,'SOURCE_ROUTE_ENCODING')
 need(all(values.get(k)==v for k,v in {'entryId':'0_wzmt2sfy','flavorId':'0_ewuu0o46','v':'2','fileName':expected_filename}.items()),'SOURCE_ROUTE_EXPECTED_VALUE')
 need(all(re.fullmatch(r'[0-9]{1,10}',values[k]) is not None for k in ('pv','ev') if k in values) and ('name' not in values or values['name']=='a.mp4'),'SOURCE_ROUTE_EXPECTED_VALUE')
 need('forceproxy' not in values or values['forceproxy']=='true','SOURCE_ROUTE_EXPECTED_VALUE')
 return value

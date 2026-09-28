"""Fixed native DB credential field only, bytes remain private/in-memory.
Not a generic INI credential search and not whole-bootstrap secret coverage.
"""
import re
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('NATIVE_DB_CREDENTIAL_SHAPE')
def native_password(raw):
 need(type(raw) is bytes and len(raw)<=131072 and b'\x00' not in raw)
 need(all(v>=32 or v in (9,10,13) for v in raw) and b'\r' not in raw.replace(b'\r\n',b'\n'))
 try:lines=raw.decode('ascii').splitlines()
 except UnicodeError:raise Rejected('NATIVE_DB_CREDENTIAL_SHAPE') from None
 section=None;values={};sections=set()
 for line in lines:
  line=line.strip()
  if not line or line.startswith((';','#')):continue
  if line.startswith('['):
   need(re.fullmatch(r'\[[A-Za-z0-9_]+\]',line) is not None);section=line[1:-1];need(section not in sections);sections.add(section);continue
  if section!='datasources':continue
  need('=' in line);key,value=map(str.strip,line.split('=',1));need(key not in values);values[key]=value
 need(values.get('default')=='propel')
 def value(key):
  v=values.get('propel.connection.'+key);need(type(v) is str)
  if v.startswith('"') or v.endswith('"'):need(len(v)>=2 and v[0]==v[-1]=='"');v=v[1:-1]
  need('"' not in v and '\\' not in v);return v
 need(value('database')=='kaltura' and value('hostspec') in ('localhost','127.0.0.1'))
 need(values.get('propel.connection.dsn','').startswith('"') and values.get('propel.connection.dsn','').endswith('"'))
 need(value('dsn') in ('mysql:host=localhost;port=3306;dbname=kaltura;','mysql:host=127.0.0.1;port=3306;dbname=kaltura;'))
 secret=value('password')
 # Native template substitutes an unquoted password, not a base64 token.
 # Keep the scanner's 15-byte minimum; do not interpret INI escapes/comments.
 need(15<=len(secret)<=256 and all(33<=ord(ch)<=126 for ch in secret))
 need(not any(ch in secret for ch in ";#'$|&~!()^{}=[]") and re.search(r'@[A-Za-z0-9_]+@',secret) is None)
 return secret.encode('ascii')
def patterns(dbraw,rootraw):
 app=native_password(dbraw);need(type(rootraw) is bytes and re.fullmatch(rb'[0-9a-f]{48}\n?',rootraw) is not None);root=rootraw.removesuffix(b'\n')
 result=[]
 for secret in (app,root):
  for part in (secret,secret[:15]):
   if part not in result:result.append(part)
 return result

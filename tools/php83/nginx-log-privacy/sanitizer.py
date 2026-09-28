"""Finite diagnostic events only: no input text, captures, or hashes are returned."""
import re
MAX_DATAGRAM=8192
SEVERITIES=('emerg','alert','crit','err','warning','notice','info','debug')
REASONS=('permission_denied','file_missing','connect_failure','timeout','upstream_failure','invalid_request','unclassified','malformed','truncated','collector_failure','collector_started','collector_stopped','output_limit','access_success','access_redirect','access_client_error','access_server_error','access_informational')
# Anchored, closed diagnostic grammars; ambiguous/user-context content is unclassified.
HEADER=rb'(?:[0-9]{4}/[0-9]{2}/[0-9]{2} [0-9:]{8} )?\[(emerg|alert|crit|error|warn|notice|info|debug)\] [0-9]{1,12}#[0-9]{1,12}: (?:\*[0-9]{1,12} )?'
SYSLOG=rb'<([0-9]{1,3})>[A-Z][a-z]{2} [ 0-9][0-9] [0-9:]{8} (?:[A-Za-z0-9._-]{1,255} )?(nginx_error|kaltura_nginx|nginx_access): '
def reason(message):
 # Stop before appended request/client context. An embedded delimiter makes file grammar fail closed.
 body=message.split(b', client:',1)[0]
 for prefix,value in ((b'connect() failed (111: Connection refused) while connecting to upstream','connect_failure'),(b'upstream timed out (110: Connection timed out) while reading response header from upstream','timeout'),(b'upstream prematurely closed connection while reading response header from upstream','upstream_failure')):
  if body==prefix:return value
 match=re.fullmatch(rb'open\(\) "[^"\\\r\n]*" failed \((2: No such file or directory|13: Permission denied)\)',body)
 if match:return 'file_missing' if match[1].startswith(b'2:') else 'permission_denied'
 return 'unclassified'
def event(severity,reason,count=1):
 if severity not in SEVERITIES or reason not in REASONS or type(count) is not int or not 1<=count<=1000000:raise ValueError('EVENT_SCHEMA')
 return {'severity':severity,'reason':reason,'count':count}
def sanitize(raw,truncated=False,source="syslog"):
 if type(raw) is not bytes: return event('warning','malformed')
 if truncated or len(raw)>MAX_DATAGRAM:return event('warning','truncated')
 if not raw or b'\x00' in raw or b'\r' in raw or b'\n' in raw:return event('warning','malformed')
 # Severity must come from PRI or an anchored native stderr header, never path text.
 if source=='syslog':
  match=re.match(SYSLOG,raw)
  if match is None or int(match[1])>191:return event('warning','malformed')
  severity=SEVERITIES[int(match[1])%8];message=raw[match.end():]
  if match[2]==b'nginx_access':
   access=re.fullmatch(rb'v1 ([1-5][0-9]{2}) [0-9]{1,20} [0-9]{1,10}\.[0-9]{3} [0-9]{1,20} [0-9]{1,20}',message)
   if access is None:return event('warning','malformed')
   return event('info',('access_informational','access_success','access_redirect','access_client_error','access_server_error')[int(access[1])//100-1])
  header=re.match(HEADER,message)
  if header:message=message[header.end():]
  else:
   header=re.match(rb'[0-9]{1,12}#[0-9]{1,12}: (?:\*[0-9]{1,12} )?',message)
   if header:message=message[header.end():]
 elif source=='stderr':
  match=re.match(HEADER,raw)
  if match is None:
   match=re.match(rb'nginx: \[(emerg|alert|crit|error|warn|notice|info|debug)\] ',raw)
  if match is None:return event('warning','unclassified')
  severity={b'error':'err',b'warn':'warning'}.get(match[1],match[1].decode('ascii'));message=raw[match.end():]
 else:return event('warning','malformed')
 return event(severity,reason(message))

class LineFeed:
 """Bounded in-memory stderr framing. Never stores a complete overlong line."""
 def __init__(self,source='stderr'):
  if source not in ('syslog','stderr'):raise ValueError('SOURCE_SCHEMA')
  self.source=source;self.buffer=bytearray();self.discard=False
 def feed(self,chunk):
  if type(chunk) is not bytes:
   self.buffer.clear();self.discard=False;return [event('warning','malformed')]
  if len(chunk)>65536:
   self.buffer.clear();self.discard=True;return [event('warning','truncated')]
  out=[];start=0
  while start<len(chunk):
   end=chunk.find(b'\n',start);complete=end!=-1
   if not complete:end=len(chunk)
   if not self.discard:
    if len(self.buffer)+end-start>MAX_DATAGRAM:
     self.buffer.clear();self.discard=True;out.append(event('warning','truncated'))
    else:self.buffer.extend(chunk[start:end])
   if complete:
    if not self.discard:out.append(sanitize(bytes(self.buffer),source=self.source))
    self.buffer.clear();self.discard=False
   start=end+1
  return out
 def flush(self):
  if self.discard:self.buffer.clear();self.discard=False;return []
  if not self.buffer:return []
  out=[sanitize(bytes(self.buffer),source=self.source)];self.buffer.clear();return out

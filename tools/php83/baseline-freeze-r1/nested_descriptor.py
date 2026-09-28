"""No-fetch reference observation before origin-enforcing HLS parser."""
from urllib.parse import urlsplit,urljoin
class Incomplete(ValueError):pass
def observe(body,parent,enroll):
 if type(body) is not bytes or len(body)>65536:raise Incomplete('NESTED_DESCRIPTOR')
 try:text=body.decode('utf-8')
 except UnicodeError:raise Incomplete('NESTED_DESCRIPTOR') from None
 lines=text.split('\n')
 if len(lines)>512:raise Incomplete('NESTED_DESCRIPTOR')
 rows=[];complete=True
 for raw in lines:
  line=raw[:-1] if raw.endswith('\r') else raw
  if not line or line.startswith('#'):continue
  if len(rows)>=32:raise Incomplete('NESTED_DESCRIPTOR')
  if len(line)>8192 or any(ord(c)<=32 or ord(c)==127 for c in line) or '\\' in line:raise Incomplete('NESTED_DESCRIPTOR')
  value=urljoin(parent,line)
  try:
   p=urlsplit(value);port=p.port if p.port is not None else 443 if p.scheme=='https' else 80 if p.scheme=='http' else None
  except ValueError:raise Incomplete('NESTED_DESCRIPTOR') from None
  rows.append({'scheme':p.scheme if p.scheme in ('http','https') else 'other','owned_host_match':p.hostname=='192.168.56.74','port':str(port) if port in (80,88,443,8443) else 'other','port_explicit':p.port is not None,'userinfo':p.username is not None or p.password is not None,'fragment':bool(p.fragment),'query':bool(p.query),'nested_requested':False})
  try:enroll(value)
  except Exception:complete=False
 return {'references':rows,'candidate_enrollment_complete':complete,'nested_get_authorized':False,'raw_values_exported':False}
def validate(v):
 if type(v) is not dict or set(v)!={'references','candidate_enrollment_complete','nested_get_authorized','raw_values_exported'} or type(v['candidate_enrollment_complete']) is not bool or v['nested_get_authorized'] is not False or v['raw_values_exported'] is not False:raise ValueError('NESTED_DESCRIPTOR')
 if type(v['references']) is not list or len(v['references'])>32:raise ValueError('NESTED_DESCRIPTOR')
 for r in v['references']:
  if type(r) is not dict or set(r)!={'scheme','owned_host_match','port','port_explicit','userinfo','fragment','query','nested_requested'} or r['scheme'] not in ('http','https','other') or r['port'] not in ('80','88','443','8443','other') or any(type(r[k]) is not bool for k in ('owned_host_match','port_explicit','userinfo','fragment','query','nested_requested')) or r['nested_requested'] is not False:raise ValueError('NESTED_DESCRIPTOR')
 return v

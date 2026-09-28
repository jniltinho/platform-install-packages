"""Pure one-round tracking and bounded private-pattern batches; never logs values."""
import protocol_v2 as protocol

def patterns(secret,initial,tokens):
 if type(secret) is not str or type(initial) is not str or type(tokens) is not list or len(tokens)>34:raise ValueError('PATTERNS')
 values=[]
 for value in [secret,initial]+tokens:
  if not value:continue
  if type(value) is not str or not 16<=len(value)<=8192:raise ValueError('PATTERNS')
  for item in (value.encode(),value[:15].encode()):
   if item not in values:values.append(item)
 if not 2<=len(values)<=72:raise ValueError('PATTERNS')
 batches=[values[i:i+32] for i in range(0,len(values),32)]
 if len(batches[-1])==1:batches[-1].insert(0,batches[-2].pop())
 return batches

class TrackedTransport:
 def __init__(self,inner,tokens):self.inner=inner;self.tokens=tokens
 def request(self,params):
  reply=self.inner.request(params)
  if params.get('service')=='session' and params.get('action')=='start' and type(reply.value) is str and protocol.TOKEN.fullmatch(reply.value):
   if len(self.tokens)>=34:raise ValueError('TOKEN_LIMIT')
   self.tokens.append(reply.value)
  return reply

def validate_round(row):
 if type(row) is not dict or row.get('protocol_version')!=2 or row.get('planned')!=100:raise ValueError('ROUND_SCHEMA')
 records=row.get('records')
 if type(records) is not list or len(records)!=100:raise ValueError('ROUND_RECORDS')
 allowed={'index','operation','status','child_http_ns','parent_ns','parent_overhead_ns','attempt_wall_ns','failure_kind'}
 for i,item in enumerate(records):
  if type(item) is not dict or not set(item)<=allowed or item.get('index')!=i+1 or type(item.get('index')) is not int or item.get('operation')!=protocol.OPERATIONS[i] or item.get('status') not in ('PASS','FAIL','NOT_EXECUTED_DEPENDENCY','NOT_EXECUTED_ABORT'):raise ValueError('ROUND_ROW')
  for key in ('child_http_ns','parent_ns','parent_overhead_ns','attempt_wall_ns'):
   value=item.get(key)
   if value is not None and (type(value) is not int or not 0<=value<=10**15):raise ValueError('ROUND_TIMING')
  if item['status']=='PASS' and (type(item.get('child_http_ns')) is not int or type(item.get('parent_ns')) is not int or not 0<item['child_http_ns']<=item['parent_ns'] or item.get('parent_overhead_ns')!=item['parent_ns']-item['child_http_ns']):raise ValueError('ROUND_TIMING')
  if 'failure_kind' in item and item['failure_kind']!='WORKER_CLEANUP':raise ValueError('ROUND_FAILURE')
 for key in ('attempted','passed','failed','not_executed'):
  if type(row.get(key)) is not int or not 0<=row[key]<=100:raise ValueError('ROUND_COUNT')
 if row['passed']!=sum(x['status']=='PASS' for x in records) or row['failed']!=sum(x['status']=='FAIL' for x in records) or row['not_executed']!=sum(x['status'].startswith('NOT_EXECUTED') for x in records) or row['attempted']!=100-row['not_executed']:raise ValueError('ROUND_COUNT')
 if type(row.get('functional_round_pass')) is not bool or row['functional_round_pass']!=(row['passed']==100) or type(row.get('aborted')) is not bool:raise ValueError('ROUND_OUTCOME')
 return {'protocol_version':2,'planned':100,'attempted':row['attempted'],'passed':row['passed'],'failed':row['failed'],'not_executed':row['not_executed'],'aborted':row['aborted'],'functional_round_pass':row['functional_round_pass'],'records':records,'diagnostic_timings_only':True,'performance_acceptance':False}

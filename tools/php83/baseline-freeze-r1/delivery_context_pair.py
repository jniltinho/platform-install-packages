"""Two native playback context calls, no GET; caller supplies committed receipt ID."""
import playback_context_r4 as context
from urllib.parse import urlsplit
class Rejected(ValueError):pass
def need(v,code):
 if not v:raise Rejected(code)
def number(v):
 need(type(v) in (str,int) and str(v).isdigit() and str(int(v))==str(v) and 0<int(v)<2147483648,'PROFILE_SELECTION_ID');return int(v)
def observe(call,enroll,asset,expected_https_id):
 need(type(expected_https_id) is int and 0<expected_https_id<2147483648 and expected_https_id!=1001,'PROFILE_SELECTION_ID')
 rows=[]
 for protocol,expected in (('http',1001),('https',expected_https_id)):
  captured=[]
  def request(**form):
   need(form.get('contextDataParams:mediaProtocol')=='https','CONTEXT_REQUEST_SHAPE')
   form['contextDataParams:mediaProtocol']=protocol
   value=call(**form);captured.append(value);return value
  try:summary=context.observe(request,enroll,asset)
  except context.Rejected as e:
   code=str(e);raise Rejected(code if code in ('URL_ENROLLMENT_INCOMPLETE','RESPONSE_COVERAGE_INCOMPLETE') else 'CONTEXT_RESPONSE_REJECTED') from None
  need(summary['sources']==1 and summary['actions']==summary['messages']==0 and summary['flavor_assets']==1,'CONTEXT_SELECTION_CARDINALITY')
  source=captured[0]['sources'][0]
  need(source['format']=='applehttp' and source['flavorIds']=='0_21p06l2j' and protocol in source['protocols'].split(','),'CONTEXT_SELECTION_FIELDS')
  actual=number(source.get('deliveryProfileId'));need(actual==expected,'PROFILE_SELECTION_MISMATCH')
  # No URL is fetched/approved. Keep only a closed scheme observation; enrollment
  # has already seen the entire bounded source list, even on metadata failures.
  try:p=urlsplit(source['url']);scheme=p.scheme if p.scheme in ('http','https') else 'other'
  except ValueError:scheme='other'
  rows.append({'requested_protocol':protocol,'profile_id':actual,'selected_expected_profile':True,'source_url_scheme':scheme})
 return {'case':'NATIVE_HTTP_HTTPS_PROFILE_SELECTION_NO_GET','api_calls':2,'selections':rows,'source_urls_enrolled':True,'response_secret_coverage_complete':False,'media_gets':0,'full_acceptance':False}
def validate(v):
 need(type(v) is dict and set(v)=={'case','api_calls','selections','source_urls_enrolled','response_secret_coverage_complete','media_gets','full_acceptance'},'CONTEXT_PAIR_SCHEMA')
 need(v['case']=='NATIVE_HTTP_HTTPS_PROFILE_SELECTION_NO_GET' and type(v['api_calls']) is int and v['api_calls']==2 and type(v['media_gets']) is int and v['media_gets']==0,'CONTEXT_PAIR_SCHEMA')
 need(v['source_urls_enrolled'] is True and v['response_secret_coverage_complete'] is False and v['full_acceptance'] is False,'CONTEXT_PAIR_SCHEMA')
 need(type(v['selections']) is list and len(v['selections'])==2,'CONTEXT_PAIR_SCHEMA')
 for i,r in enumerate(v['selections']):
  need(type(r) is dict and set(r)=={'requested_protocol','profile_id','selected_expected_profile','source_url_scheme'},'CONTEXT_PAIR_SCHEMA')
  need(r['requested_protocol']==('http','https')[i] and type(r['profile_id']) is int and 0<r['profile_id']<2147483648 and r['selected_expected_profile'] is True and r['source_url_scheme'] in ('http','https','other'),'CONTEXT_PAIR_SCHEMA')
 need(v['selections'][0]['profile_id']==1001 and v['selections'][1]['profile_id']!=1001,'CONTEXT_PAIR_SCHEMA');return v
def receipt_id(v):
 need(type(v) is dict and v.get('status')=='NATIVE_PROFILE_SPLIT_COMMITTED_FINITE_PRIVACY' and v.get('privacy_passed') is True and v.get('full_acceptance') is False,'SPLIT_RECEIPT')
 p=v.get('profile_result');need(type(p) is dict and p.get('status')=='NATIVE_PROFILE_SPLIT_COMMITTED' and type(p.get('original_profile_id')) is int and p['original_profile_id']==1001 and p.get('http_preserved') is True and p.get('native_model_save_used') is True and p.get('full_acceptance') is False,'SPLIT_RECEIPT')
 ident=p.get('https_profile_id');need(type(ident) is int and 0<ident<2147483648 and ident!=1001,'SPLIT_RECEIPT');return ident

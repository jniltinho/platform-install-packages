"""Observation of unchanged real classes; no patch acceptance or live backend."""
import argparse,hashlib,itertools,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
CHANNELS=json.loads((HERE/'baseline-channels.json').read_text())['cases']
PINS=json.loads((HERE.parent/'xml-lifecycle/source-pins.json').read_text())
CASES=('bootstrap','construct-good','construct-malformed','construct-missing','explicit-ok','magic-ok','explicit-fault','callback-existing','nested-construct','nested-call-ok','nested-call-fault')
FAIL_CASES={'construct-malformed','construct-missing','explicit-fault'}
CALLBACK_CASES={'callback-existing','nested-construct'}
POSITIVE={'explicit-ok','magic-ok','nested-call-ok','nested-call-fault'}
def require(condition,message):
 if not condition:raise ValueError(message)
def exception(x):
 require(x is None or (type(x) is dict and set(x)=={'class','message'} and all(type(v) is str and v for v in x.values())),'exception shape')
def wrapper(x):
 require(type(x) is dict and set(x)=={'http','https','all'},'wrapper shape')
 require(type(x['all']) is list and all(type(v) is str for v in x['all']),'wrapper list')
 require(x['all']==sorted(set(x['all'])),'wrapper sorted unique')
 for k in ('http','https'):require(type(x[k]) is bool and x[k]==(k in x['all']),'wrapper bool consistency')
def expected_handler_only(variant,case,runtime):
 file=variant+'/infra/general/kSoapClient.php'
 if case=='construct-missing':
  method='SoapClient' if runtime=='74' else '__construct'
  return [{'phase':'operation:construct','severity':2,'message':'SoapClient::'+method+'(): I/O warning : failed to load external entity "file:///audit/probe/fixtures/missing.wsdl"','file':file,'line':8}]
 if case=='nested-construct':
  return [{'phase':'nested-resolver:construct','severity':8,'message':'stream_wrapper_restore(): '+scheme+':// was never changed, nothing to restore','file':file,'line':line} for scheme,line in [('http',27),('https',28)]]
 return []
def typed_equal(a,b):
 return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))
def validate(b,variant,case,runtime,probe,stderr):
 require(type(b) is dict,'body object')
 require(type(stderr) is str,'native stderr string')
 key='/'.join([runtime,variant,case]);require(key in CHANNELS,'known baseline diagnostic case')
 recorded=CHANNELS[key]
 require(typed_equal(b.get('diagnostics'),recorded['handler']),'complete exact handler diagnostic inventory')
 require(stderr==recorded['native_stderr'],'complete exact native stderr inventory')
 require(typed_equal(b.get('runtime'),recorded['runtime']),'baseline diagnostic runtime identity')
 require(b.get('probe_sha256')==recorded['probe_sha256'],'baseline diagnostic probe identity')
 require(type(b.get('schema')) is int and b['schema']==1,'schema')
 require(b.get('variant')==variant and b.get('case')==case,'case identity')
 for k in ('real_transport_coverage','full_application_bootstrap','application_patch_selected'):
  require(b.get(k) is False,'scope flags')
 require(b.get('loaded')==PINS[variant]['files'],'loaded actual five classes')
 require(b.get('probe_sha256')==probe,'probe identity')
 require(b.get('classes')=={'config':'kEnvironment','soap':'SoapClient','transport':'kSoapClient'},'real class chain')
 r=b.get('runtime');require(type(r) is dict,'runtime shape');pid=r.get('php_id')
 require(type(pid) is int and ((70400<=pid<70500) if runtime=='74' else (80300<=pid<80400)),'runtime family')
 require(type(r.get('error_reporting')) is int and r['error_reporting']==32767,'E_ALL')
 require(type(r.get('modules')) is list and {'soap','dom','libxml'}.issubset(r['modules']),'runtime modules')
 require(b.get('environment_keys')==['cache_root_path','general_cache_dir','response_cache_dir','syndication_core_xsd_path'],'real environment map')
 ds=b.get('diagnostics');require(type(ds) is list,'diagnostic list')
 for d in ds:
  require(type(d) is dict and set(d)=={'phase','severity','message','file','line'},'diagnostic fields')
  require(type(d['severity']) is int and d['severity']>0 and type(d['line']) is int and d['line']>0,'diagnostic integers')
  require(all(type(d[k]) is str and d[k] for k in ('phase','message','file')),'diagnostic strings')
  # Preserve two native observation channels; no invented stderr or dropped diagnostics.
  require(d['message'] in stderr or any(typed_equal(d,x) for x in expected_handler_only(variant,case,runtime)),'unexpected handler-only diagnostic')
 missing=[d for d in ds if d['message'] not in stderr]
 require(typed_equal(missing,expected_handler_only(variant,case,runtime)),'exact handler-only diagnostic inventory')
 ev=b.get('events');require(type(ev) is list and len(ev)>=3,'state events')
 phases=[x.get('phase') for x in ev if type(x) is dict]
 require(len(phases)==len(ev) and len(set(phases))==len(phases),'state phase identity')
 require(phases[:2]==['before-kConf','after-kConf'] and phases[-1]=='after-operation','state order')
 for x in ev:
  wrapper(x['wrappers'])
  require(type(x.get('value')) is str and type(x.get('parse_return')) is bool,'state value')
  require(type(x.get('marker_seen')) is bool and x['marker_seen']==(x['value']=='SYNTHETIC_LIFECYCLE_MARKER'),'marker consistency')
  require(type(x.get('callback_identity_available')) is bool,'callback availability')
  require(type(x.get('callback_same')) is bool if x['callback_identity_available'] else x.get('callback_same') is None,'callback identity type')
 require(ev[0]['marker_seen'] and ev[0]['wrappers']['http'] and ev[0]['wrappers']['https'],'native enabled positive canary')
 require(not ev[1]['wrappers']['http'] and not ev[1]['wrappers']['https'],'real kConf wrappers')
 if case not in CALLBACK_CASES:require(not ev[1]['marker_seen'],'real kConf block without preexisting callback')
 exception(b.get('exception'))
 require(type(b.get('functions')) is list and all(type(f) is str for f in b['functions']),'SOAP function list')
 for k in ('resolver_events','transport_events','nested_results'):require(type(b.get(k)) is list,'trace list')
 for x in b['resolver_events']:
  require(type(x) is dict and set(x)=={'phase','public','system','wrappers'},'resolver trace')
  require(type(x['phase']) is str and x['phase'],'resolver phase')
  require(x['public'] is None or type(x['public']) is str,'resolver public')
  require(type(x['system']) is str and x['system'],'resolver system');wrapper(x['wrappers'])
 for x in b['transport_events']:
  require(type(x) is dict and set(x)=={'depth','location','action','version','request_sha256','wrappers'},'transport trace')
  require(type(x['depth']) is int and x['depth'] in (0,1),'transport depth')
  require(x['location']=='urn:xml-lifecycle:transport' and x['action']=='urn:xml-lifecycle:ping','synthetic transport endpoint')
  require(type(x['version']) is int and x['version']==1,'SOAP1.1')
  require(type(x['request_sha256']) is str and len(x['request_sha256'])==64,'request hash');wrapper(x['wrappers'])
 for x in b['nested_results']:
  require(type(x) is dict and type(x.get('site')) is str,'nested trace');exception(x.get('exception'))
 if case in FAIL_CASES:
  require(b['exception'] is not None and b['exception']['class']=='SoapFault','expected native SoapFault')
  require(ev[-1]['marker_seen'] and ev[-1]['wrappers']['http'] and ev[-1]['wrappers']['https'],'preserve existing exception cleanup flaw')
 elif case!='nested-construct':
  require(b['exception'] is None,'positive operation failed')
  require(not ev[-1]['wrappers']['http'] and not ev[-1]['wrappers']['https'],'successful operation closes wrappers')
  if case not in CALLBACK_CASES:require(not ev[-1]['marker_seen'],'successful legacy operation closes window without callback')
 if case in POSITIVE:
  require(b['result']=={'value':'SYNTHETIC_RESPONSE'},'native decoded synthetic envelope')
  require(bool(b['transport_events']),'actual transport seam reached')
 elif case!='nested-construct':require(b['result'] is None,'constructor-only result')
 if case in ('callback-existing','nested-construct'):
  soap_ids={'file:///audit/probe/fixtures/good.wsdl','file:///audit/probe/fixtures/inner.wsdl','file:///audit/probe/fixtures/types.xsd','/audit/probe/fixtures/good.wsdl','/audit/probe/fixtures/inner.wsdl','/audit/probe/fixtures/types.xsd'}
  require(any(x['system'] in soap_ids and not x['phase'].startswith('observer:') for x in b['resolver_events']),'SOAP resolver reached outside canary observer')
  for x in ev:
   if x['callback_identity_available']:require(x['callback_same'] is True,'original external callback retained')
 if case.startswith('nested-'):
  require(len(b['nested_results'])==1,'nested operation actually reached')
 if case not in {'bootstrap','construct-malformed','construct-missing','nested-construct'}:
  require(any('ping(' in f for f in b['functions']),'actual WSDL operation discovered')
 return {'callback_policy_relation_unadjudicated':case in CALLBACK_CASES,
    'callback_observer_marker_after_kConf':ev[1]['marker_seen'] if case in CALLBACK_CASES else None,
    'existing_exception_cleanup_flaw_observed':case in FAIL_CASES,
    'nested_outcome_not_security_approval':case.startswith('nested-'),
    'diagnostic_channels':{'handler_count':len(ds),'handler_only':missing,'native_stderr_preserved':True},'diagnostics':len(ds),'real_transport_coverage':False,'application_patch_selected':False}

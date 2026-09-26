"""Bounded actual held observation collection; functional checks are not release acceptance."""
import argparse,hashlib,itertools,json,subprocess
from pathlib import Path
BEHAVIOR=('bootstrap','construct-good','construct-malformed','construct-missing','explicit-ok','magic-ok','explicit-fault','callback-existing','nested-construct','nested-call-ok','nested-call-fault','callback-deny','callback-throw')
SCOPE=('default','custom-allow','custom-deny','custom-throw','nested','custom-wrapper','foreign-mutation','non-lifo','invalid-token','primary-exception-chain','idempotent-init','standalone')
def require(ok,msg):
 if not ok:raise ValueError(msg)
def validate(body,kind,variant,case,manifest):
 require(kind in ('behavior','scope') and variant in ('baseline','candidate'),'known process kind/variant')
 require(case in (BEHAVIOR if kind=='behavior' else SCOPE),'known case')
 require(kind!='scope' or variant=='candidate','helper candidate only')
 require(type(body) is dict and type(body.get('schema')) is int and body['schema']==1,'body schema')
 require(body.get('case')==case and body.get('application_patch_selected') is False,'case/scope identity')
 require(body.get('probe_sha256')==manifest['files']['behavior.php' if kind=='behavior' else 'scope-probe.php'],'probe identity')
 if kind=='behavior':
  require(body.get('variant')==variant,'variant identity')
  expected={p[len(variant)+1:]:h for p,h in manifest['files'].items() if p.startswith(variant+'/')}
  require(body.get('loaded')==expected,'actual complete included source identities')
  require(type(body.get('runtime',{}).get('php_id')) is int and body['runtime']['php_id']==80306 and body['runtime']['error_reporting']==32767,'native runtime')
  require(body.get('real_transport_coverage') is False and body.get('full_application_bootstrap') is False,'transport scope')
  events=body['events'];phases={x['phase']:x for x in events};require('after-kConf' in phases and 'after-operation' in phases,'event inventory')
  if variant=='candidate':
   for name in ['after-kConf','after-operation']:
    x=phases[name];require(x['marker_seen'] is False and x['wrappers']['http'] is False and x['wrappers']['https'] is False,'candidate outside policy restored')
   if case in ('nested-call-ok','nested-call-fault'):
    x=phases['transport-after-inner'];require(x['marker_seen'] is True and x['wrappers']['http'] is True and x['wrappers']['https'] is True,'inner preserves outer active policy')
   if case=='nested-construct':require(body['nested_results'][0]['wrappers_after']['http'] is True,'nested constructor preserves outer wrappers')
  expected_error='SoapFault' if case in ('construct-malformed','construct-missing','explicit-fault','callback-deny','callback-throw') else None
  require((body['exception']['class'] if body['exception'] else None)==expected_error,'expected actual SOAP outcome')
  if case in ('explicit-ok','magic-ok','nested-call-ok','nested-call-fault'):require(body['result']=={'value':'SYNTHETIC_RESPONSE'},'real response decode')
 else:
  require(body.get('helper_sha256')==manifest['files']['candidate/infra/general/kXmlEntityLoaderPolicy.php'],'actual helper identity')
  require(body.get('php')=='8.3.6' and body.get('native_error_reporting')==32767,'helper runtime')
  states={x['phase']:x for x in body['states']};require('outside-before' in states and 'outside-after' in states,'helper states')
  if case!='standalone':
   require(states['outside-before']['marker'] is False and states['outside-after']['marker'] is False,'helper deny outside')
   if case!='custom-wrapper':require(states['outside-after']['http'] is False and states['outside-after']['https'] is False,'owned wrapper cleanup')
  if case in ('foreign-mutation','non-lifo','invalid-token','primary-exception-chain'):
   require(body['error'] is not None and body['error']['class']=='RuntimeException','failclosed visible exception')
  else:require(body['error'] is None,'unexpected helper error')
  if case=='primary-exception-chain':require(body['error']['previous_class']=='SoapFault' and body['error']['previous_message']=='SYNTHETIC_PRIMARY_SOAPFAULT','original primary cause preserved')
  if case=='custom-wrapper':require(type(body.get('custom_wrapper_hits')) is int and body['custom_wrapper_hits']==1 and states['outside-after']['http'] is True,'preexisting custom wrapper preserved')
  if case=='nested':require(states['after-inner']['marker'] is True and states['after-inner']['http'] is True,'helper nested outer lifetime')
  if case=='custom-deny':require(states['outer']['marker'] is False and states['outer']['prior_callback_active'] is True,'foreign restrictive callback remains active')
  if case=='custom-allow':require(states['outer']['marker'] is True and states['outer']['prior_callback_active'] is True,'foreign allow callback remains active')
  if case=='custom-throw':require(states['outer']['error']['class']=='RuntimeException' and states['outer']['prior_callback_active'] is True,'foreign throwing callback remains active')
  if case=='standalone':require(all(x['prior_callback_active'] is True for x in states.values()),'standalone foreign callback unchanged')
 require(type(body.get('diagnostics')) is list,'diagnostic capture')
 for d in body['diagnostics']:
  require(type(d) is dict and type(d.get('severity')) is int and type(d.get('line')) is int and type(d.get('message')) is str,'typed diagnostic')
 return {'functional_checks':'PASS_BOUNDED_REVISED_CAUSAL_CONTRACT','diagnostic_inventory':'VALIDATED_SEPARATELY'}

"""Candidate diagnostic expectations derive from deny observers and native SOAP boundaries.
This compares expected strings to raw evidence; it never rewrites observed stderr.
"""
import json
DOM='DOMDocument::loadXML(): Failed to load external entity because the resolver function returned null'
def same(a,b):return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))
def expected(kind,case):
 if kind=='behavior':
  def dom(phase):return {'phase':'observer:'+phase,'severity':2,'message':DOM,'file':'behavior.php','line':28}
  handler=[]
  if case=='callback-deny':handler.append(dom('before-kConf'))
  handler.append(dom('after-kConf'))
  if case not in ('bootstrap','construct-malformed','construct-missing','callback-deny','callback-throw'):handler.append(dom('after-constructor'))
  if case in ('construct-missing','callback-deny'):
   message=('SoapClient::__construct(): I/O warning : failed to load external entity "file:///audit/probe/fixtures/missing.wsdl"' if case=='construct-missing' else 'SoapClient::__construct(): Failed to load external entity because the resolver function returned null')
   handler.append({'phase':'operation:construct','severity':2,'message':message,'file':'candidate/infra/general/kSoapClient.php','line':11})
  handler.append(dom('after-operation'))
  printed=[d for d in handler if d['file']=='behavior.php']
 else:
  dom={'severity':2,'message':DOM,'file':'scope-probe.php','line':42}
  if case=='standalone':handler=[]
  elif case=='custom-wrapper':handler=[dom,{'severity':2,'message':'fopen(http://synthetic-wrapper-control): Failed to open stream: "XmlLifecycleCustomHttp::stream_open" call failed','file':'scope-probe.php','line':93},dom]
  else:handler=[dom]*(3 if case=='custom-deny' else 2)
  printed=handler
 stderr=''.join('Warning: '+d['message']+' in /audit/probe/'+d['file']+' on line '+str(d['line'])+'\n' for d in printed)
 return handler,stderr
def validate_candidate(row):
 handler,stderr=expected(row['kind'],row['case'])
 if not same(row['body']['diagnostics'],handler):raise ValueError('Candidate complete diagnostic inventory differs')
 if type(row['stderr']) is not str or row['stderr']!=stderr:raise ValueError('Candidate complete raw stderr differs')
 return {'handler_count':len(handler),'handler_only_count':sum(d['message'] not in stderr for d in handler),'native_stderr_exact':True,'basis':'policy/fixture-derived complete expectations; raw evidence unchanged'}

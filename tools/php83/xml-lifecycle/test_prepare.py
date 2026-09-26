import copy,hashlib,importlib.util,json,pathlib,subprocess,sys,tempfile,unittest
from unittest.mock import patch
HERE=pathlib.Path(__file__).resolve().parent
def module(n):
 s=importlib.util.spec_from_file_location(n,HERE/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prepare=module('prepare');collect=module('collect')
def wrapper(on):return {'http':on,'https':on,'all':['file','http','https'] if on else ['file']}
def state(phase,on):
 return {'phase':phase,'wrappers':wrapper(on),'marker_seen':on,'parse_return':True,'value':'SYNTHETIC_LIFECYCLE_MARKER' if on else '',
 'callback_identity_available':True,'callback_same':True}
def fixture(case='bootstrap',variant='original',runtime='83'):
 b={'schema':1,'runtime':{'php_id':80300,'error_reporting':32767,'modules':['soap','dom','libxml']},'variant':'original','case':case,
 'classes':{'config':'kEnvironment','soap':'SoapClient','transport':'kSoapClient'},
 'environment_keys':['cache_root_path','general_cache_dir','response_cache_dir','syndication_core_xsd_path'],
 'events':[state('before-kConf',True),state('after-kConf',False),state('after-operation',case in collect.FAIL_CASES)],
 'result':None,'exception':{'class':'SoapFault','message':'synthetic failure'} if case in collect.FAIL_CASES else None,
 'functions':[] if case in ('bootstrap','construct-malformed','construct-missing') else ['PingResponse ping(Ping $parameters)'],'diagnostics':[],'resolver_events':[],'transport_events':[],'nested_results':[],
 'loaded':dict(collect.PINS['original']['files']),'probe_sha256':'p','real_transport_coverage':False,'full_application_bootstrap':False,'application_patch_selected':False}

 b['variant']=variant;b['loaded']=dict(collect.PINS[variant]['files']);b['runtime']['php_id']=80300 if runtime=='83' else 70433
 if case in collect.POSITIVE:
  b['result']={'value':'SYNTHETIC_RESPONSE'}
  b['transport_events']=[{'depth':0,'location':'urn:xml-lifecycle:transport','action':'urn:xml-lifecycle:ping','version':1,'request_sha256':'a'*64,'wrappers':wrapper(True)}]
 if case in collect.CALLBACK_CASES:
  b['resolver_events']=[{'phase':'observer:before-kConf','public':None,'system':'file:///audit/probe/fixtures/marker.txt','wrappers':wrapper(True)},
   {'phase':'operation:construct','public':None,'system':'file:///audit/probe/fixtures/good.wsdl','wrappers':wrapper(True)}]
 if case.startswith('nested-'):
  b['nested_results']=[{'site':'resolver-inner' if case=='nested-construct' else 'transport-inner','exception':None}]
 return b

class Tests(unittest.TestCase):
 def check(self,b,stderr=''):return collect.validate(b,b['variant'],b['case'],'83' if b['runtime']['php_id']==80300 else '74','p',stderr)
 def test_positive_bootstrap(self):self.check(fixture())
 def test_positive_old_flaws(self):
  for c in collect.FAIL_CASES:self.assertTrue(self.check(fixture(c))['existing_exception_cleanup_flaw_observed'])
 def test_wrong_runtime(self):
  b=fixture();b['runtime']['php_id']=80400
  with self.assertRaises(ValueError):collect.validate(b,'original',b['case'],'83','p','')
 def test_bool_schema(self):
  b=fixture();b['schema']=True
  with self.assertRaises(ValueError):self.check(b)
 def test_missing_loaded(self):
  b=fixture();b['loaded']={}
  with self.assertRaises(ValueError):self.check(b)
 def test_source_hash(self):
  b=fixture();b['probe_sha256']='wrong'
  with self.assertRaises(ValueError):self.check(b)
 def test_false_application_claim(self):
  b=fixture();b['full_application_bootstrap']=True
  with self.assertRaises(ValueError):self.check(b)
 def test_no_marker_canary(self):
  b=fixture();b['events'][0]=state('before-kConf',False)
  with self.assertRaises(ValueError):self.check(b)
 def test_leaky_kconf(self):
  b=fixture();b['events'][1]=state('after-kConf',True)
  with self.assertRaises(ValueError):self.check(b)
 def test_lost_original_flaw(self):
  b=fixture('construct-missing');b['events'][-1]=state('after-operation',False)
  with self.assertRaises(ValueError):self.check(b)
 def test_bool_marker(self):
  b=fixture();b['events'][0]['marker_seen']=1
  with self.assertRaises(ValueError):self.check(b)
 def test_bad_exception(self):
  b=fixture();b['exception']='failure'
  with self.assertRaises(ValueError):self.check(b)
 def test_duplicate_events(self):
  b=fixture();b['events'].append(copy.deepcopy(b['events'][-1]))
  with self.assertRaises(ValueError):self.check(b)
 def test_missing_warning_stderr(self):
  b=fixture();b['diagnostics']=[{'phase':'test','severity':2,'message':'native warning','file':'probe.php','line':1}]
  with self.assertRaises(ValueError):self.check(b)
  self.check(b,'Warning: native warning at line 1')
 def test_module_missing(self):
  b=fixture();b['runtime']['modules'].remove('soap')
  with self.assertRaises(ValueError):self.check(b)
 def test_prepare_exact(self):
  with tempfile.TemporaryDirectory() as d:
   out=pathlib.Path(d)/'stage';r=prepare.prepare(out);m=json.loads((out/'identities.json').read_text())
   self.assertEqual(r['files'],18);self.assertEqual(len(m['files']),18)
   for n,h in m['files'].items():self.assertEqual(hashlib.sha256((out/n).read_bytes()).hexdigest(),h)
   self.assertFalse((out/'fixtures/missing.wsdl').exists())
 def test_existing_refused(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):prepare.prepare(pathlib.Path(d))
 def test_archive_pin_bad(self):
  bad=copy.deepcopy(prepare.PINS);bad['original']['archive_sha256']='0'*64
  with tempfile.TemporaryDirectory() as d,patch.object(prepare,'PINS',bad):
   with self.assertRaises(ValueError):prepare.prepare(pathlib.Path(d)/'stage')
 def test_source_pin_bad(self):
  bad=copy.deepcopy(prepare.PINS);bad['original']['files']['alpha/config/kConf.php']='0'*64
  with tempfile.TemporaryDirectory() as d,patch.object(prepare,'PINS',bad):
   with self.assertRaises(ValueError):prepare.prepare(pathlib.Path(d)/'stage')
 def test_oserror_retained(self):
  with tempfile.TemporaryDirectory() as d:
   stage=pathlib.Path(d)/'stage';prepare.prepare(stage);out=pathlib.Path(d)/'out.json'
   with patch.object(sys,'argv',['collect','83',str(stage),str(out)]),patch.object(collect.subprocess,'run',side_effect=OSError('synthetic')):
    with self.assertRaises(SystemExit):collect.main()
   x=json.loads(out.read_text());self.assertEqual(len(x['records']),22);self.assertEqual(len(x['failures']),22)
 def test_static_no_unapproved_transport(self):
  s=(HERE/'run.sh').read_text();p=(HERE/'probe.php').read_text()
  for n in ['PrivateNetwork=yes','socket socketpair','open_basedir=/audit/probe','soap.wsdl_cache_enabled=0']:self.assertIn(n,s)
  self.assertIn('return false;',p);self.assertIn('public function __doRequest',p)
  self.assertNotIn('/etc/passwd',p);self.assertNotIn('LIBXML_NOERROR',p);self.assertNotIn('libxml_disable_entity_loader(',p)

 def test_all_synthetic_case_families(self):
  for rt in ['74','83']:
   for v in ['original','exp11']:
    for c in collect.CASES:self.check(fixture(c,v,rt))
 def test_callback_observer_does_not_prove_soap(self):
  b=fixture('callback-existing');b['resolver_events']=b['resolver_events'][:1]
  with self.assertRaises(ValueError):self.check(b)
 def test_wsdl_called_by_observer_not_enough(self):
  b=fixture('callback-existing');b['resolver_events'][1]['phase']='observer:after-kConf'
  with self.assertRaises(ValueError):self.check(b)
 def test_callback_policy_outcomes_are_observed(self):
  for exposed in [False,True]:
   b=fixture('callback-existing')
   for index in [1,2]:
    b['events'][index]['marker_seen']=exposed
    b['events'][index]['value']='SYNTHETIC_LIFECYCLE_MARKER' if exposed else ''
   r=self.check(b);self.assertEqual(r['callback_observer_marker_after_kConf'],exposed);self.assertTrue(r['callback_policy_relation_unadjudicated'])
 def test_native_response_missing(self):
  b=fixture('explicit-ok');b['result']=None
  with self.assertRaises(ValueError):self.check(b)
 def test_transport_not_reached(self):
  b=fixture('magic-ok');b['transport_events']=[]
  with self.assertRaises(ValueError):self.check(b)
 def test_nested_not_reached(self):
  b=fixture('nested-call-ok');b['nested_results']=[]
  with self.assertRaises(ValueError):self.check(b)
 def test_wsdl_functions_missing(self):
  b=fixture('construct-good');b['functions']=[]
  with self.assertRaises(ValueError):self.check(b)
 def test_phase_restore_and_trace(self):
  p=(HERE/'probe.php').read_text()
  self.assertEqual(p.count('finally { $phase=$previousPhase; }'),2)
  self.assertIn("'phase'=>$phase,'public'=>$public",p)

if __name__=='__main__':unittest.main()

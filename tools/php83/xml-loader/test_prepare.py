import copy,hashlib,importlib.util,itertools,json,tempfile,unittest,sys,subprocess
from unittest.mock import patch
from pathlib import Path
HERE=Path(__file__).resolve().parent
def module(n):
 s=importlib.util.spec_from_file_location(n,HERE/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prepare=module('prepare');collect=module('collect')
def fixture(policy='enabled',parser='dom'):
 rows=[]
 for doc,flag in itertools.product(collect.DOCS,collect.FLAGS):
  value='PLAIN' if doc=='plain' else ('INTERNAL' if doc=='internal' and flag=='noent' else '')
  if policy=='enabled' and (doc,flag) in [('file','noent'),('wrapper','noent'),('dtd','noent_dtdload')]:value=collect.MARKER
  rows.append({'document':doc,'flag':flag,'options':collect.OPTIONS[collect.FLAGS.index(flag)],'value':value,
   'initial_parse_return':doc!='malformed','marker_seen':collect.MARKER in value,'internal_seen':'INTERNAL' in value,
   'diagnostics':[{'severity':2,'message':'synthetic','file':'probe.php','line':1}] if doc=='malformed' else [],
   'loader_calls':[{'public':None,'system':'synthetic'}] if policy=='deny' and doc in ('file','wrapper','dtd') else [],
   'wrapper_events':[],'exception':None})
 return {'policy':policy,'parser':parser,'source':{'probe':'p','marker':'m','dtd':'d'},'runtime':{'php_id':80300,'error_reporting':32767,'internal_errors':False,'extensions':['libxml','dom','SimpleXML','xmlreader']},'records':rows,'policy_return':True if policy in ('enabled','legacy','deny') else None,'policy_diagnostics':[{'severity':8192,'message':'Function libxml_disable_entity_loader() is deprecated','file':'probe.php','line':1}] if policy in ('enabled','legacy') else [],'application_coverage':False}
class Tests(unittest.TestCase):
 def check(self,b):return collect.validate(b,b['policy'],b['parser'],'83',{'probe':'p','marker':'m','dtd':'d'})
 def test_prepare(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'new';r=prepare.prepare(p);m=(p/'identities.json').read_bytes()
   self.assertEqual(r['manifest_sha256'],hashlib.sha256(m).hexdigest());self.assertEqual(len(json.loads(m)['files']),4)
 def test_existing(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):prepare.prepare(Path(d))
 def test_matrix_positive(self):
  for policy,parser in itertools.product(collect.POLICIES,collect.PARSERS):self.assertEqual(self.check(fixture(policy,parser))['rows'],42)
 def test_missing_row(self):
  b=fixture();b['records'].pop()
  with self.assertRaises(ValueError):self.check(b)
 def test_duplicate(self):
  b=fixture();b['records'][1]=copy.deepcopy(b['records'][0])
  with self.assertRaises(ValueError):self.check(b)
 def test_boolean_options(self):
  b=fixture();b['records'][0]['options']=False
  with self.assertRaises(ValueError):self.check(b)
 def test_integer_boolean(self):
  b=fixture();b['records'][0]['marker_seen']=0
  with self.assertRaises(ValueError):self.check(b)
 def test_wrong_php(self):
  b=fixture();b['runtime']['php_id']=80400
  with self.assertRaises(ValueError):self.check(b)
 def test_missing_canary(self):
  b=fixture()
  for r in b['records']:
   if r['document']=='file':r['value']='';r['marker_seen']=False
  with self.assertRaises(ValueError):self.check(b)
 def test_blocked_disclosure(self):
  b=fixture('deny');b['records'][0]['value']=collect.MARKER;b['records'][0]['marker_seen']=True
  with self.assertRaises(ValueError):self.check(b)
 def test_missing_callback(self):
  b=fixture('deny')
  for r in b['records']:r['loader_calls']=[]
  with self.assertRaises(ValueError):self.check(b)
 def test_warning_suppression(self):
  b=fixture();b['runtime']['internal_errors']=True
  with self.assertRaises(ValueError):self.check(b)
 def test_source_drift(self):
  b=fixture();b['source']['probe']='wrong'
  with self.assertRaises(ValueError):self.check(b)
 def test_static_security(self):
  s=(HERE/'run.sh').read_text();p=(HERE/'probe.php').read_text()
  for needle in ['PrivateNetwork=yes','socket socketpair','SystemCallErrorNumber=EPERM','BindReadOnlyPaths','open_basedir=/audit/probe','error_reporting=32767']:self.assertIn(needle,s)
  for needle in ['/etc/passwd','LIBXML_NOERROR','LIBXML_NOWARNING','@simplexml','@libxml']:self.assertNotIn(needle,p)
  self.assertIn('return false; // Retain native stderr',p)

 def test_runtime_object(self):
  b=fixture();b['runtime']='bad'
  with self.assertRaises(ValueError):self.check(b)
 def test_row_object(self):
  b=fixture();b['records'][0]=None
  with self.assertRaises(ValueError):self.check(b)
 def test_blocked_wrapper(self):
  b=fixture('deny');b['records'][0]['wrapper_events']=[{'operation':'open','path':'xfixture://marker'}]
  with self.assertRaises(ValueError):self.check(b)
 def test_blocked_diagnostic_disclosure(self):
  b=fixture('deny');b['records'][0]['diagnostics']=[{'severity':2,'message':collect.MARKER,'file':'probe.php','line':1}]
  with self.assertRaises(ValueError):self.check(b)
 def test_exception_type(self):
  b=fixture();b['records'][0]['exception']='anything'
  with self.assertRaises(ValueError):self.check(b)
 def test_policy_diagnostics_type(self):
  b=fixture();b['policy_diagnostics']='anything'
  with self.assertRaises(ValueError):self.check(b)
 def test_diagnostic_type(self):
  b=fixture();b['records'][0]['diagnostics']=[{'severity':True,'message':'x','file':'probe.php','line':1}]
  with self.assertRaises(ValueError):self.check(b)
 def test_missing_deprecation(self):
  b=fixture();b['policy_diagnostics']=[]
  with self.assertRaises(ValueError):self.check(b)
 def test_policy_return_type(self):
  b=fixture();b['policy_return']=1
  with self.assertRaises(ValueError):self.check(b)
 def test_each_canary_missing(self):
  for doc in ['file','wrapper','dtd']:
   b=fixture()
   for r in b['records']:
    if r['document']==doc:r['value']='';r['marker_seen']=False
   with self.assertRaises(ValueError):self.check(b)


 def test_oserror_evidence_retained(self):
  with tempfile.TemporaryDirectory() as d:
   stage=Path(d)/'stage';prepare.prepare(stage);out=Path(d)/'out.json'
   with patch.object(sys,'argv',['collect','83',str(stage),str(out)]), patch.object(collect.subprocess,'run',side_effect=OSError('synthetic ssh failure')):
    with self.assertRaises(SystemExit):collect.main()
   r=json.loads(out.read_text());self.assertEqual(r['status'],'FAIL');self.assertEqual(len(r['records']),12)
 def test_timeout_evidence_retained(self):
  with tempfile.TemporaryDirectory() as d:
   stage=Path(d)/'stage';prepare.prepare(stage);out=Path(d)/'out.json'
   e=subprocess.TimeoutExpired(['synthetic'],75,output=b'partial stdout',stderr=b'partial stderr')
   with patch.object(sys,'argv',['collect','83',str(stage),str(out)]), patch.object(collect.subprocess,'run',side_effect=e):
    with self.assertRaises(SystemExit):collect.main()
   r=json.loads(out.read_text());self.assertEqual(len(r['records']),12)
   for x in r['records']:self.assertTrue(x['incomplete']);self.assertEqual(x['stdout'],'partial stdout');self.assertEqual(x['stderr'],'partial stderr')

if __name__=='__main__':unittest.main()

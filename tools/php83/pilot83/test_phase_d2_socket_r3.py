"""Pure socket representation regression; never opens sockets or starts services."""
import importlib.util,json,pathlib,types,unittest
P=pathlib.Path(__file__).parent
def load(name):
 spec=importlib.util.spec_from_file_location(name,P/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=load('application-phase-d2-private-logs-r3')
BASE={'127.0.0.1:3306','127.0.0.1:9312','127.0.0.1:11211','[::1]:11211','*:80'}
def base():return [(x,'unchanged baseline') for x in sorted(BASE)]
def java(address):return (address,'LISTEN 0 4096 '+address+' *:* users:(("java",pid=123,fd=1))')
class Tests(unittest.TestCase):
 def test_actual_observed_forms(self):
  receipt=P.parents[2]/'doc/php83/evidence/phase-d2-lab6-execution-r1/socket-diagnostic.json';data=json.loads(receipt.read_bytes())
  self.assertEqual(data['new_listeners'],[{'address':'[::ffff:127.0.0.1]:9200','java_process':True},{'address':'[::ffff:127.0.0.1]:9300','java_process':True}])
  observed=base()+[java(row['address']) for row in data['new_listeners']];out=m.canonical_es_rows(observed)
  m.require_es_listeners(out,BASE);self.assertEqual(out[:len(BASE)],observed[:len(BASE)])
  self.assertEqual([line for _,line in out],[line for _,line in observed])
 def test_existing_ipv4_supported(self):m.require_es_listeners(m.canonical_es_rows(base()+[java('127.0.0.1:9200'),java('127.0.0.1:9300')]),BASE)
 def test_wildcard_nonloopback_unknown_rejected(self):
  for address in ('*:9200','0.0.0.0:9200','[::]:9300','[::1]:9200','[::ffff:192.168.56.83]:9200','192.168.56.83:9300','[::ffff:127.0.0.2]:9200','::ffff:127.0.0.1:9200','[::FFFF:127.0.0.1]:9200','[::ffff:127.0.0.1%lo]:9200',':9300','garbage:9200'):
   with self.subTest(address=address),self.assertRaisesRegex(ValueError,'ES_LISTENER_REPRESENTATION'):m.canonical_es_rows([java(address)])
 def test_mapped_other_ports_not_reclassified(self):
  for address in ('[::ffff:127.0.0.1]:3306','[::ffff:127.0.0.1]:9201','[::ffff:127.0.0.1]:09200'):
   row=java(address);self.assertEqual(m.canonical_es_rows([row]),[row])
   with self.assertRaisesRegex(ValueError,'EXACT_LOCAL_LISTENERS'):m.require_es_listeners(m.canonical_es_rows(base()+[java('127.0.0.1:9200'),java('127.0.0.1:9300'),row]),BASE)
 def test_missing_extra_and_non_java_rejected(self):
  good=m.canonical_es_rows(base()+[java('[::ffff:127.0.0.1]:9200'),java('[::ffff:127.0.0.1]:9300')])
  for bad in (good[:-1],good+[('127.0.0.1:9400','extra')],good[:-1]+[('127.0.0.1:9300','users:(("other",pid=123,fd=1))')]):
   with self.assertRaises(ValueError):m.require_es_listeners(bad,BASE)
 def test_duplicate_canonical_socket_rejected(self):
  rows=base()+[java('127.0.0.1:9200'),java('[::ffff:127.0.0.1]:9200'),java('127.0.0.1:9300')]
  with self.assertRaisesRegex(ValueError,'JAVA_LOCAL_LISTENER'):m.require_es_listeners(m.canonical_es_rows(rows),BASE)
 def test_adapter_nested_readiness_and_restore(self):
  rows=base()+[java('[::ffff:127.0.0.1]:9200'),java('[::ffff:127.0.0.1]:9300')];original=lambda f:rows;p=types.SimpleNamespace(listeners=original)
  def readiness():return {address for address,_ in p.listeners(None)}-(BASE|{'127.0.0.1:9200','127.0.0.1:9300'})
  with m.listener_adapter(p):m.require_es_listeners(p.listeners(None),BASE);self.assertEqual(readiness(),set())
  self.assertIs(p.listeners,original)
  with self.assertRaisesRegex(RuntimeError,'synthetic'):
   with m.listener_adapter(p):raise RuntimeError('synthetic')
  self.assertIs(p.listeners,original)
 def test_frozen_package_helper_recovery_preserved(self):
  old=load('application-phase-d2-private-logs-r2')
  for key in ('ROW','PRESTART_PIN','D1_PIN','INVENTORY_PIN','RUN','RETIRED_RUN','SUCCESS','PENDING'):self.assertEqual(getattr(m,key),getattr(old,key))
  import ast
  def functions(path):return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(path.read_text()).body if isinstance(x,ast.FunctionDef) and x.name!='execute'}
  oldf=functions(P/'application-phase-d2-private-logs-r2.py');newf=functions(P/'application-phase-d2-private-logs-r3.py')
  self.assertTrue(all(newf[name]==body for name,body in oldf.items()))
if __name__=='__main__':unittest.main()

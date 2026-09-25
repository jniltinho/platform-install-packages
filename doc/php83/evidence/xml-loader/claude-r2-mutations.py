import sys,copy,json;sys.dont_write_bytecode=True;sys.path.insert(0,'tools/php83/xml-loader')
import test_prepare as t
c=t.collect;S={'probe':'p','marker':'m','dtd':'d'}
def run(name,pol,mut):
 b=t.fixture(pol);mut(b)
 try:c.validate(b,pol,'dom','83',S);print(name,'ACCEPTED')
 except Exception as e:print(name,'REJECTED',type(e).__name__,e)
def m1(b):
 for r in b['records']:
  if r['document']=='malformed':r['diagnostics']=[];r['exception']={'class':'','message':''}
def m2(b):b['records'][0]['exception']={'class':'X','message':'m','extra':1}
def m3(b):b['records'][14]['wrapper_events']=[{'operation':'open','path':'xfixture://marker'}]
def m4(b):b['records'][14]['diagnostics']=[{'severity':2,'message':c.MARKER,'file':'f','line':1}]
def m5(b):b['policy_diagnostics'][0]['message']=''
def m6(b):b['records'][14]['loader_calls']=[{'public':None,'system':'file:///x/'+c.MARKER}]
def m7(b):b['records'][14]['diagnostics']=[{'severity':True,'message':'x','file':'f','line':1}]
def m8(b):b['records'][14]['value']=c.MARKER[:5]+'​'+c.MARKER[5:]
run('malformed-empty-exception-dict','enabled',m1)
run('exception-extra-key','enabled',m2)
run('deny-wrapper-event','deny',m3)
run('legacy-diag-marker','legacy',m4)
run('empty-deprecation-message','legacy',m5)
run('deny-marker-in-loader-systemid','deny',m6)
run('bool-severity','enabled',m7)
run('obfuscated-marker-in-value-legacy','legacy',m8)

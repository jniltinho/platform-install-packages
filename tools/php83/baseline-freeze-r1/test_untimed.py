import ast,copy,hashlib,json,pathlib,subprocess,sys,tempfile,types,unittest
HERE=pathlib.Path(__file__).parent;sys.path.insert(0,str(HERE.parent/'baseline-api'))
import rehearsal as h
import run_untimed as r
import test_v2
from transport import Reply
class UntimedTests(unittest.TestCase):
 def round(self,fail=False):
  row,_=test_v2.V2Tests().inputs();fixture=row['fixture'];tokens=[];calls=[]
  class Fake:
   def request(self,params):
    calls.append(params)
    if fail and len(calls)==70:raise RuntimeError('SYNTHETIC_SECRET')
    if params['service']=='session':value=f'{len(calls):015d}-SYNTHETIC-SESSION-TOKEN'
    elif params['action']=='list':value={'objectType':'KalturaMediaListResponse','totalCount':'1','objects':[fixture['entry']]}
    else:value=fixture['entry']
    return Reply(value,1,2)
  result=h.protocol.run_round(h.TrackedTransport(Fake(),tokens),h.protocol.Credentials(102,'synthetic','SYNTHETIC-SECRET-VALUE'),fixture)
  return result,tokens,calls,row
 def test100_user_current_and_tracking(self):
  result,tokens,calls,_=self.round();self.assertEqual(len(tokens),34);self.assertEqual(len(calls),100);self.assertTrue(all(x['type']==0 for x in calls[:34]));self.assertTrue(all(x['version']==-1 for x in calls[67:]));self.assertTrue(h.validate_round(result)['functional_round_pass'])
 def test_failed_call_preserved_no_message(self):
  result,tokens,_,_=self.round(True);out=h.validate_round(result);self.assertEqual(out['failed'],1);self.assertEqual(out['attempted'],100);self.assertNotIn('SYNTHETIC',json.dumps(out))
 def test_all_private_patterns_covered_with32cap(self):
  _,tokens,_,_=self.round();batches=h.patterns('SYNTHETIC-SECRET-VALUE','INITIAL-SESSION-TOKEN',tokens);flat=sum(batches,[])
  self.assertTrue(all(2<=len(b)<=32 for b in batches));self.assertLessEqual(len(batches),3)
  for token in tokens:self.assertIn(token.encode(),flat);self.assertIn(token[:15].encode(),flat)
 def test_singleton_rebalanced33_and65(self):
  for n,expected in ((15,33),(31,65)):
   tokens=['S'*15+'UNIQUE-TOKEN-A']+[f'{i:015d}'+'T'*20 for i in range(1,n)]
   batches=h.patterns('S'*20,'I'*20,tokens);flat=sum(batches,[])
   self.assertEqual(len(flat),expected);self.assertTrue(all(2<=len(b)<=32 for b in batches));self.assertEqual(len(flat),len(set(flat)))
   for value in ['S'*20,'I'*20]+tokens:self.assertIn(value.encode(),flat);self.assertIn(value[:15].encode(),flat)
 def test_no_untrusted_round_field_or_timing(self):
  for mutate in ('field','timing'):
   row,_,_,_=self.round()
   if mutate=='field':row['records'][0]['message']='SYNTHETIC'
   else:row['records'][0]['child_http_ns']=None
   self.assertRaises(Exception,h.validate_round,row)
 def test_common_cutoff_drift_rejected(self):
  tree=ast.parse((HERE/'guest_untimed.py').read_text());fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='audit_all')
  for drift in (False,True):
   cutoff={'fixed':types.SimpleNamespace(size=4)};calls=iter([cutoff,{'fixed':types.SimpleNamespace(size=5)} if drift else cutoff])
   scope={'files':types.SimpleNamespace(snapshot=lambda x:next(calls)),'legacy':types.SimpleNamespace(logs=lambda:[]),'journal':types.SimpleNamespace(snapshot=lambda:'PRIVATE_CURSOR'),'audit':lambda batch,start,jstart:{'files':{'end_offsets':{'fixed':4}}},'need':lambda condition,code: None if condition else (_ for _ in ()).throw(ValueError(code))}
   exec(compile(ast.Module(body=[fn],type_ignores=[]),'fixture','exec'),scope)
   if drift:self.assertRaises(ValueError,scope['audit_all'],[[b'a'*16,b'b'*16]],{},None)
   else:self.assertTrue(scope['audit_all']([[b'a'*16,b'b'*16]],{},None)['common_end_verified'])
 def test_guest_reproducible_pins_no_upload(self):
  with tempfile.TemporaryDirectory() as d:
   output=pathlib.Path(d)/'guest.py';p=subprocess.run([sys.executable,'-B',str(HERE/'prepare_untimed.py'),'--output',str(output)],capture_output=True);self.assertEqual(p.returncode,0);self.assertEqual(output.read_bytes(),(HERE/'guest_untimed.py').read_bytes())
  for name,pin in r.PINS.items():self.assertEqual(hashlib.sha256((HERE/name).read_bytes()).hexdigest(),pin)
  self.assertNotIn("value('media','add'",(HERE/'guest_untimed.py').read_text())
 def test_round_public_projection_only_safe_fields(self):
  result,tokens,_,row=self.round();row['untimed_round']=h.validate_round(result);row['round_token_count']=34
  batches=h.patterns('SYNTHETIC-SECRET-VALUE','INITIAL-SESSION-TOKEN',tokens)
  privacy=[]
  for batch in batches:
   item=copy.deepcopy(row['media_privacy']);item['files']['counts']=[0]*len(batch);item['journal']['counts']=[0]*len(batch);privacy.append(item)
  row['round_privacy']={'common_end_verified':True,'pattern_count':sum(map(len,batches)),'batches':privacy};row['unknown']='SYNTHETIC_SECRET'
  out=r.public_rows((json.dumps(row)+'\n').encode());self.assertEqual(out[-1]['untimed_round']['passed'],100);self.assertNotIn('SYNTHETIC',json.dumps(out))
if __name__=='__main__':unittest.main()

import unittest,hashlib,json,importlib.util,tempfile,os
from email.parser import BytesParser
from email.policy import default
from pathlib import Path
from unittest.mock import patch
import long_upload as l,prepare_long_upload_r1 as g,run_long_upload_r1 as r
import test_thumbnail_r5 as old
H=Path(__file__).parent
DATA=b'\x00'*16+os.urandom(l.SIZE-16)
TOKEN='0_'+'a'*32
def planner():
 s=importlib.util.spec_from_file_location('frozen_plan',H.parent/'long-upload-plan-r1'/'plan.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class Fake:
 def __init__(self,bad_at=None,edit=None,raise_at=None):
  self.calls=[];self.posts=[];self.size=0;self.bad_at=bad_at;self.edit=edit;self.raise_at=raise_at
 def call(self,service,action,**f):
  self.calls.append((service,action))
  if (service,action)==('uploadtoken','add'):return {'objectType':'KalturaUploadToken','id':TOKEN,'status':0}
  if (service,action)==('media','add'):return {'objectType':'KalturaMediaEntry','id':'0_newentry'}
  if (service,action)==('media','addContent'):return {'objectType':'KalturaMediaEntry','id':f['entryId'],'status':'4'}
  raise AssertionError(service)
 def post(self,params,content):
  n=len(self.posts)+1;self.posts.append((dict(params),content))
  if n==self.raise_at:raise OSError('boom')
  self.size+=len(content);v={'objectType':'KalturaUploadToken','id':params['uploadTokenId'],'uploadedFileSize':float(self.size),'status':2 if params['finalChunk'] else 1}
  if n==self.bad_at:self.edit(v)
  return json.dumps(v).encode()
class Tests(unittest.TestCase):
 def run_upload(self,fake,clock=None):
  self.progress=[]
  kw={'progress':self.progress.append}
  if clock:kw['clock']=clock
  return l.upload(fake.call,fake.post,'k'*40,DATA,'baseline-long-'+'0123456789abcdef01234567',**kw)
 def test_plan_matches_frozen_planner(self):
  m=planner();ours=l.plan();frozen=m.plan(m.SIZE,m.SHA256)
  self.assertEqual((m.SIZE,m.SHA256,m.CHUNK),(l.SIZE,l.SHA256,l.CHUNK))
  self.assertEqual([(p.number,p.offset,p.length,p.resume,p.final_chunk) for p in frozen],ours)
 def test_sequence_and_success(self):
  with patch.object(l,'SHA256',hashlib.sha256(DATA).hexdigest()):
   f=Fake();v=self.run_upload(f)
  self.assertEqual(len(f.posts),112);self.assertEqual(b''.join(c for _,c in f.posts),DATA)
  first,second,last=f.posts[0][0],f.posts[1][0],f.posts[-1][0]
  self.assertEqual((first['resume'],first['finalChunk'],first['resumeAt']),(0,0,-1))
  self.assertEqual((second['resume'],second['finalChunk'],second['resumeAt']),(1,0,1048576))
  self.assertEqual((last['resume'],last['finalChunk'],last['resumeAt']),(1,1,111*1048576))
  self.assertTrue(all(p['ks']=='k'*40 and p['uploadTokenId']==TOKEN for p,_ in f.posts))
  self.assertEqual(f.calls,[('uploadtoken','add'),('media','add'),('media','addContent')])
  with patch.object(l,'SHA256',hashlib.sha256(DATA).hexdigest()):l.validate(v)
  self.assertEqual(self.progress[-1],{'token_created':True,'acked_parts':112,'acked_bytes':l.SIZE,'entry_created':True,'entry_id':'0_newentry'})
  for p in self.progress:l.validate_progress(p)
  self.assertNotIn('k'*40,json.dumps(v)+json.dumps(self.progress))
 def test_stop_without_retry(self):
  edits=[lambda v:v.update(uploadedFileSize=v['uploadedFileSize']-1),lambda v:v.update(status=2),lambda v:v.update(id='0_'+'b'*32),lambda v:v.update(objectType='KalturaAPIException'),lambda v:v.update(uploadedFileSize=1.5)]
  with patch.object(l,'SHA256',hashlib.sha256(DATA).hexdigest()):
   for e in edits:
    f=Fake(bad_at=7,edit=e)
    with self.assertRaises(l.Rejected) as x:self.run_upload(f)
    self.assertEqual(str(x.exception),'LONG_PART_ACK');self.assertEqual(len(f.posts),7);self.assertEqual(f.calls,[('uploadtoken','add')])
    self.assertEqual(self.progress[-1]['acked_parts'],6)
   f=Fake(raise_at=3)
   with self.assertRaises(l.Rejected) as x:self.run_upload(f)
   self.assertEqual((str(x.exception),len(f.posts)),('LONG_PART_TRANSPORT',3))
   t=iter([0]+[1]*5+[10**6]*500)
   with self.assertRaises(l.Rejected) as x:self.run_upload(Fake(),clock=lambda:next(t))
   self.assertEqual(str(x.exception),'LONG_BUDGET')
 def test_source_and_token_guards(self):
  self.assertRaises(l.Rejected,l.upload,Fake().call,Fake().post,'k'*40,DATA,'baseline-long-x'*2)
  with patch.object(l,'SHA256',hashlib.sha256(DATA).hexdigest()):
   f=Fake();f.call=lambda s,a,**k:{'objectType':'KalturaAPIException'}
   self.assertRaises(l.Rejected,self.run_upload,f)
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'d'/'fullhd60.mp4';p.parent.mkdir();p.write_bytes(b'x');self.assertRaises(l.Rejected,l.read_source,p)
 def test_multipart_parses(self):
  body,ctype=l.multipart({'service':'uploadtoken','resumeAt':-1},b'\x00\r\n--x\xff','baseline-long-0123456789abcdef')
  msg=BytesParser(policy=default).parsebytes(b'Content-Type: '+ctype.encode()+b'\r\n\r\n'+body)
  parts={p.get_param('name',header='content-disposition'):p for p in msg.iter_parts()}
  self.assertEqual(parts['service'].get_content(),'uploadtoken');self.assertEqual(parts['fileData'].get_payload(decode=True),b'\x00\r\n--x\xff')
  self.assertRaises(l.Rejected,l.multipart,{},b'..baseline-long-0123456789abcdef..','baseline-long-0123456789abcdef')
  self.assertRaises(l.Rejected,l.multipart,{'bad key':1},b'','baseline-long-0123456789abcdef')
 def good(self):
  return {'case':'FULLHD60_CHUNKED_UPLOAD_PHASE_A','parts':112,'bytes':l.SIZE,'source_sha256':l.SHA256,'acknowledged_bytes':l.SIZE,'token_final_status':2,'auto_finalize_requested':False,'retries':0,'upload_seconds':42.5,'owned_entry_id':'0_newentry','entry_status_after_add_content':4,'ready_verified':False,'full_acceptance':False}
 def test_request_bound_and_stage_script(self):
  body,_=l.multipart({'k':1},b'x'*l.CHUNK,'baseline-long-0123456789abcdef');self.assertLessEqual(len(body),l.REQUEST_LIMIT)
  self.assertRaises(l.Rejected,l.multipart,{},b'x'*(l.CHUNK+1),'baseline-long-0123456789abcdef')
  import stage_long_fixture as st,ast
  for cleanup in (False,True):
   code=st.REMOTE%{'tmp':'/home/vagrant/.fullhd60-0123456789abcdef.tmp','target':st.TARGET,'size':st.SIZE,'sha':st.SHA256,'cleanup_only':cleanup};ast.parse(code)
   self.assertIn("if "+repr(cleanup)+":",code)
  self.assertEqual((st.SIZE,st.SHA256,st.TARGET+'/fullhd60.mp4'),(l.SIZE,l.SHA256,str(l.SOURCE)))
 def test_schema_negative(self):
  good=self.good();l.validate(good)
  for k,v in [('retries',1),('ready_verified',True),('parts',111),('owned_entry_id','x'),('upload_seconds',601),('full_acceptance',True)]:self.assertRaises(l.Rejected,l.validate,dict(good,**{k:v}))
  self.assertRaises(l.Rejected,l.validate_progress,{'token_created':True,'acked_parts':3,'acked_bytes':5,'entry_created':False,'entry_id':None})
  self.assertRaises(l.Rejected,l.validate_progress,{'token_created':True,'acked_parts':3,'acked_bytes':3*l.CHUNK,'entry_created':True,'entry_id':'0_newentry'})
 def test_guest_and_runner_derivation(self):
  s=g.build();self.assertEqual(s,(H/'guest_long_upload_r1.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertEqual(s.count('longup.upload('),1);self.assertNotIn('thumb.observe(',s);self.assertIn(hashlib.sha256((H/'long_upload.py').read_bytes()).hexdigest(),s)
  self.assertIn("('192.168.56.74','https',8443),tls_ca,",s);self.assertIn("sphinx.scan(list(patterns))",s)
  self.assertLess(s.index("report['phase']='long-upload-phase-a'"),s.index("failure_stage='QUIET_SETTLE'"))
  for u in ('b93f7882','5df47596','e16b8e67','ec290fc3','128d02f3','6858a1eb'):self.assertIn('baseline-freeze-'+u+'.service',r.REMOTE_GUARD)
  self.assertIn('/var/lib/kaltura-baseline-long-upload-r1',r.REMOTE_GUARD+r.STAGE);self.assertIn("fullhd60.mp4')",r.REMOTE_GUARD);self.assertNotIn('thumbnail-r5',r.REMOTE_GUARD+r.STAGE)
  r.PROOF_PIN='a'*64;self.assertIn('/var/lib/kaltura-baseline-long-upload-r1/guest_long_upload_r1.py ',r.unit_command('baseline-freeze-00000000'))
 def row(self):
  x=old.Tests();v=x.row();v.pop('thumbnail');v.pop('thumbnail_diagnostics')
  v['long_upload']=self.good();v['long_upload_progress']={'token_created':True,'acked_parts':112,'acked_bytes':l.SIZE,'entry_created':True,'entry_id':'0_newentry'};return v
 def test_public_projection(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual(out['long_upload']['parts'],112);self.assertNotIn('thumbnail',out)
  self.assertIs(out['upload_attempted'],True);self.assertIs(out['phase_a_upload_mutation'],True)
  self.assertTrue(s_:=(H/'guest_long_upload_r1.py').read_text().startswith('"""FullHD60 phase A'))
  for edit in [lambda v:v['long_upload'].update(retries=1),lambda v:v['long_upload_progress'].update(acked_parts=111,acked_bytes=111*l.CHUNK),lambda v:v.update(thumbnail={}),lambda v:v['sphinx_binlog_audits'][0].update(counts=[1,0])]:
   v=self.row();edit(v);self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
  f={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'LONG_PART_ACK','long_upload_progress':{'token_created':True,'acked_parts':6,'acked_bytes':6*l.CHUNK,'entry_created':False,'entry_id':None},'raw':'SECRET'}
  out=r.public_rows(json.dumps(f).encode())[0];self.assertEqual(out['long_upload_progress']['acked_parts'],6);self.assertNotIn('SECRET',json.dumps(out))
  self.assertRaises(Exception,r.public_rows,json.dumps(dict(f,thumbnail_diagnostics={})).encode())
if __name__=='__main__':unittest.main()

import unittest,hashlib,json,os
from pathlib import Path
from unittest.mock import patch
import flavor_progressive as fp,short_delivery443 as sd,prepare_flavor_progressive_r1 as g,run_flavor_progressive_r1 as r
import test_thumbnail_r5 as old
H=Path(__file__).parent
URL='https://192.168.56.74/p/102/sp/10200/serveFlavor/entryId/0_3h92ab2l/v/2/flavorId/0_j6rfow09/fileName/baseline-long-fullhd60-0123_(Lab_Decision7).mp4/name/a.mp4'
DATA=os.urandom(3*fp.CHUNK-5)
class Tests(unittest.TestCase):
 def setUp(self):
  self.p=[patch.object(fp,'SIZE',len(DATA)),patch.object(fp,'SHA256',hashlib.sha256(DATA).hexdigest())]
  for x in self.p:x.start()
 def tearDown(self):
  for x in self.p:x.stop()
 def observe(self,url=URL,data=DATA,api=None,headers_edit=None,clock=None):
  self.events=[];self.diag={}
  def call(**f):self.events.append(f['action']);return api if api is not None else url
  def request(u,h,limit):
   self.events.append('GET');start,end=map(int,h['Range'][6:].split('-'))
   pairs=[('Content-Type','video/mp4'),('Content-Range','bytes %d-%d/%d'%(start,end,len(data))),('Content-Length',str(end-start+1))]
   if headers_edit:pairs=headers_edit(pairs,start)
   return 206,pairs,data[start:end+1]
  fetch=lambda u,h,limit,status:sd.fetch(request,u,h,limit,status)
  return fp.observe(call,lambda u:self.events.append('enroll'),fetch,'s'*32,'k'*32,lambda k,v:self.diag.update({k:v}),clock or (lambda:0))
 def test_success(self):
  v=self.observe();fp.validate(dict(v,range_requests=-(-fp.SIZE//fp.CHUNK)));self.assertEqual(self.events,['getUrl','enroll','GET','GET','GET'])
  self.assertEqual(self.diag['URL']['grammar'],True);fp.diagnostics(self.diag)
  self.observe(url=URL.replace('/name/a.mp4',''));self.observe(url=URL.replace('/v/2/','/v/2/pv/3/ev/4/'))
 def test_url_rejected_after_enrollment(self):
  for bad in [URL.replace('74/','74:8443/'),URL+'?x=1',URL.replace('https','http'),URL.replace('0_3h92ab2l','0_other000'),URL.replace('/name/a.mp4','/ks/'+'k'*32),URL.replace('fileName/','fileName/'+'k'*15)]:
   with self.assertRaises(fp.Rejected):self.observe(url=bad)
   self.assertEqual(self.events,['getUrl','enroll'])
 def test_api_error_closed_code(self):
  with self.assertRaises(fp.Rejected) as e:self.observe(api={'objectType':'KalturaAPIException','code':'ASSET_ID_NOT_FOUND','message':'SECRET msg'})
  self.assertEqual((str(e.exception),self.diag),('PROG_API',{'API_ERROR':{'code':'ASSET_ID_NOT_FOUND'}}));fp.diagnostics(self.diag)
  self.assertRaises(fp.Rejected,self.observe,api={'objectType':'KalturaAPIException','code':'WEIRD<x>'});self.assertEqual(self.diag['API_ERROR']['code'],'OTHER')
 def test_transfer_failures(self):
  for edit,code in [(lambda p,s:[p[0],('Content-Range','bytes 0-0/1'),p[2]],'PROG_RANGE'),(lambda p,s:p+[('Location','x')],'PROG_RESPONSE'),(lambda p,s:[p[0],p[1],('Content-Length','7')],'PROG_RESPONSE'),(lambda p,s:[p[0],p[1]],'PROG_RANGE')]:
   with self.assertRaises(fp.Rejected) as e:self.observe(headers_edit=edit)
   self.assertEqual(str(e.exception),code)
  other=bytearray(DATA);other[-1]^=1
  with self.assertRaises(fp.Rejected) as e:self.observe(data=bytes(other))
  self.assertEqual(str(e.exception),'PROG_HASH')
  t=iter([0,0,0,0,631])
  with self.assertRaises(fp.Rejected) as e:self.observe(clock=lambda:next(t))
  self.assertEqual(str(e.exception),'PROG_BUDGET')
  t=iter([0,0,700,700])
  with self.assertRaises(fp.Rejected) as e:self.observe(clock=lambda:next(t))
  self.assertEqual(str(e.exception),'PROG_BUDGET')
 def test_schema(self):
  v={'case':'DELIVERED_PROGRESSIVE_1080P60','flavor_id':fp.FLAVOR,'entry_id':fp.ENTRY,'range_requests':-(-fp.SIZE//fp.CHUNK),'bytes':fp.SIZE,'sha256':fp.SHA256,'delivered_equals_stored_decoded':True,'full_body_single_request':False,'full_acceptance':False}
  fp.validate(v)
  for k,x in [('range_requests',1),('delivered_equals_stored_decoded',False),('sha256','0'*64),('full_acceptance',True)]:self.assertRaises(fp.Rejected,fp.validate,dict(v,**{k:x}))
  self.assertRaises(fp.Rejected,fp.diagnostics,{'API_ERROR':{'code':'SECRET'}});self.assertRaises(fp.Rejected,fp.diagnostics,{'URL':{'scheme':'HTTPS'}})
 def test_real_constants(self):
  for x in self.p:x.stop()
  try:
   self.assertEqual((fp.SIZE,fp.SHA256),(31441393,'c14cbe84aa6f401c813200a12b427518cd3f0c7dd68fb5b7f4d4bd7f8c9ccf7a'))
   import flavor_decode;self.assertLessEqual(fp.CHUNK,sd.MAX_BODY)
  finally:
   for x in self.p:x.start()
 def test_derivation(self):
  s=g.build();self.assertEqual(s,(H/'guest_flavor_progressive_r1.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertEqual(s.count('prog.observe('),1);self.assertIn('enrollment.enroll(url,tracked_tokens)',s);self.assertIn('get443.request(tls_ca,u,hh,l)',s)
  for u in ('8372955c','c603dc7e'):self.assertIn('baseline-freeze-'+u+'.service',r.REMOTE_GUARD)
  r.PROOF_PIN='a'*64;self.assertIn('/var/lib/kaltura-baseline-flavor-progressive-r1/guest_flavor_progressive_r1.py ',r.unit_command('baseline-freeze-00000000'))
 def test_public_projection(self):
  for x in self.p:x.stop()
  try:
   r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
   out=r.public_rows(json.dumps(self.row_real()).encode())[0];self.assertTrue(out['flavor_progressive']['delivered_equals_stored_decoded'])
   for edit in [lambda v:v['progressive_diagnostics']['URL'].update(port='8443'),lambda v:v['flavor_progressive'].update(sha256='0'*64),lambda v:v.update(flavor_decode={})]:
    v=self.row_real();edit(v);self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
   f={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'PROG_API','progressive_diagnostics':{'API_ERROR':{'code':'ASSET_ID_NOT_FOUND'}},'raw':'SECRET'}
   out=r.public_rows(json.dumps(f).encode())[0];self.assertEqual(out['progressive_diagnostics']['API_ERROR']['code'],'ASSET_ID_NOT_FOUND');self.assertNotIn('SECRET',json.dumps(out))
  finally:
   for x in self.p:x.start()
 def row_real(self):
  x=old.Tests();v=x.row();v.pop('thumbnail');v.pop('thumbnail_diagnostics');n=-(-fp.SIZE//fp.CHUNK)
  v['flavor_progressive']={'case':'DELIVERED_PROGRESSIVE_1080P60','flavor_id':fp.FLAVOR,'entry_id':fp.ENTRY,'range_requests':n,'bytes':fp.SIZE,'sha256':fp.SHA256,'delivered_equals_stored_decoded':True,'full_body_single_request':False,'full_acceptance':False}
  v['progressive_diagnostics']={'URL':{'scheme':'HTTPS','owned_host':True,'port':'443','query':False,'fragment':False,'userinfo':False,'grammar':True},'TRANSFER':{'range_requests':n,'bytes':fp.SIZE}}
  return v
if __name__=='__main__':unittest.main()

import unittest,hashlib,json,copy
from pathlib import Path
import lab_profile as lp,prepare_lab_profile_r1 as g,run_lab_profile_r1 as r
import test_thumbnail_r5 as old
H=Path(__file__).parent
SRC={'objectType':'KalturaFlavorParams','id':7,'partnerId':0,'name':'HD/1080 - WEB (H264/4000)','systemName':'','createdAt':1,'isSystemDefault':1,'requiredPermissions':[],
 'tags':'web,mbr,dash','videoCodec':'h264h','videoBitrate':4000,'audioCodec':'aac','audioBitrate':128,'height':1080,'width':0,'frameRate':0,'maxFrameRate':0,
 'conversionEngines':'2,99,3','format':'mp4','twoPass':False,'gopSize':60,'isGopInSec':0,'watermarkData':None}
class Fake:
 def __init__(self,exists=False,src=None,profile_after='0,2,3,4,5,6,7,19',params_edit=None):
  self.calls=[];self.exists=exists;self.src=src or copy.deepcopy(SRC);self.after=profile_after;self.params_edit=params_edit;self.gets=0;self.forms={};self.default_flip=False
 def call(self,s,a,**f):
  self.calls.append((s,a));self.forms[(s,a)]=f
  if a=='list':return {'objectType':'X','totalCount':1 if self.exists else 0,'objects':[]}
  if (s,a)==('flavorparams','get'):return copy.deepcopy(self.src)
  if (s,a)==('flavorparams','add'):
   v={k[len('flavorParams:'):]:x for k,x in f.items() if k.startswith('flavorParams:') and k!='flavorParams:objectType'}
   v.update(objectType='KalturaFlavorParams',id=42,partnerId=102)
   if self.params_edit:self.params_edit(v)
   return v
  if (s,a)==('conversionprofile','get'):
   self.gets+=1;return {'objectType':'KalturaConversionProfile','id':14,'partnerId':102,'isPartnerDefault':True if self.gets==1 or not self.default_flip else False,'flavorParamsIds':'0,2,3,4,5,6,7,19' if self.gets==1 else self.after}
  if (s,a)==('conversionprofile','add'):
   return {'objectType':'KalturaConversionProfile','id':20,'partnerId':102,'systemName':f['conversionProfile:systemName'],'flavorParamsIds':f['conversionProfile:flavorParamsIds'],'isDefault':0,'isPartnerDefault':False}
  raise AssertionError((s,a))
class Tests(unittest.TestCase):
 def test_success(self):
  f=Fake();v=lp.setup(f.call,'A'*40);lp.validate(v)
  self.assertEqual((v['lab_params_id'],v['lab_profile_id'],v['lab_profile_flavor_params']),(42,20,[0,2,3,4,5,6,19,42]))
  form=f.forms[('flavorparams','add')];self.assertEqual(form['flavorParams:maxFrameRate'],60);self.assertEqual(form['flavorParams:systemName'],lp.PARAMS_SYSTEM)
  for k in ('id','partnerId','createdAt','isSystemDefault','requiredPermissions','watermarkData'):self.assertNotIn('flavorParams:'+k,form)
  self.assertEqual(form['flavorParams:twoPass'],0);self.assertEqual(form['flavorParams:videoCodec'],'h264h')
  pf=f.forms[('conversionprofile','add')];self.assertEqual((pf['conversionProfile:isDefault'],pf['conversionProfile:flavorParamsIds']),(0,'0,2,3,4,5,6,42,19'))
  self.assertEqual(f.calls,[('flavorparams','list'),('conversionprofile','list'),('flavorparams','get'),('flavorparams','add'),('conversionprofile','get'),('conversionprofile','add'),('conversionprofile','get')])
  self.assertNotIn('A'*40,json.dumps(v))
 def test_fail_closed(self):
  f=Fake(exists=True)
  with self.assertRaises(lp.Rejected) as e:lp.setup(f.call,'A'*40)
  self.assertEqual(str(e.exception),'LAB_PROFILE_EXISTS');self.assertNotIn(('flavorparams','add'),f.calls)
  for src,code in [(dict(SRC,height=720),'LAB_PROFILE_SOURCE'),(dict(SRC,maxFrameRate=30),'LAB_PROFILE_SOURCE'),(dict(SRC,partnerId=102),'LAB_PROFILE_SOURCE')]:
   f=Fake(src=src)
   with self.assertRaises(lp.Rejected) as e:lp.setup(f.call,'A'*40)
   self.assertEqual(str(e.exception),code);self.assertNotIn(('flavorparams','add'),f.calls)
  for edit in [lambda v:v.update(maxFrameRate=30),lambda v:v.update(height=720),lambda v:v.update(partnerId=0)]:
   self.assertRaises(lp.Rejected,lp.setup,Fake(params_edit=edit).call,'A'*40)
  f=Fake(profile_after='0,2,3,4,5,6,42,19');seen=[]
  with self.assertRaises(lp.Rejected) as e:lp.setup(f.call,'A'*40,progress=seen.append)
  self.assertEqual((str(e.exception),seen[-1]),('LAB_PROFILE_PROFILE',{'lab_params_id':42,'lab_profile_id':20}))
  seen=[]
  self.assertRaises(lp.Rejected,lp.setup,Fake(params_edit=lambda v:v.update(maxFrameRate=30)).call,'A'*40,progress=seen.append)
  self.assertEqual(seen,[{'lab_params_id':42,'lab_profile_id':None}])
  f=Fake();f.default_flip=True
  with self.assertRaises(lp.Rejected) as e:lp.setup(f.call,'A'*40)
  self.assertEqual(str(e.exception),'LAB_PROFILE_PROFILE')
  f=Fake();f.call=lambda s,a,**k:{'objectType':'KalturaAPIException'}
  self.assertRaises(lp.Rejected,lp.setup,f.call,'A'*40)
 def test_schema(self):
  v=lp.setup(Fake().call,'A'*40)
  for k,x in [('partner_default_changed',True),('lab_profile_id',14),('lab_params_max_frame_rate',30),('full_acceptance',True),('copied_param_fields',['id'])]:self.assertRaises(lp.Rejected,lp.validate,dict(v,**{k:x}))
  self.assertRaises(lp.Rejected,lp.validate,dict(v,lab_profile_flavor_params=[0,7,19]))
 def test_derivation(self):
  s=g.build();self.assertEqual(s,(H/'guest_lab_profile_r1.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertEqual(s.count('labp.setup('),1);self.assertNotIn('longready.observe(',s)
  self.assertLess(s.index('tracked_tokens.append(admin_secret)'),s.index("secret=admin_secret)"))
  self.assertLess(s.index("secret=admin_secret)"),s.index('tracked_tokens.append(admin_ks)'));self.assertLess(s.index('tracked_tokens.append(admin_ks)'),s.index('labp.setup('))
  self.assertIn("ks[:15].encode()]+admin_patterns,start,jstart)",s);self.assertEqual(s.count('newlogs.scan(files,start,patterns,legacy.logs)'),2)
  for u in ('068f5a98','18154d61'):self.assertIn('baseline-freeze-'+u+'.service',r.REMOTE_GUARD)
  self.assertIn('now=time.gmtime();assert now.tm_min<30',r.REMOTE_GUARD)
  r.PROOF_PIN='a'*64;self.assertIn('/var/lib/kaltura-baseline-lab-profile-r1/guest_lab_profile_r1.py ',r.unit_command('baseline-freeze-00000000'))
 def row(self):
  x=old.Tests();v=x.row();v.pop('thumbnail');v.pop('thumbnail_diagnostics');v['lab_profile']=lp.setup(Fake().call,'A'*40);v['lab_profile_progress']={'lab_params_id':42,'lab_profile_id':20};return v
 def test_public_projection(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual(out['lab_profile']['lab_params_max_frame_rate'],60)
  for edit in [lambda v:v['lab_profile'].update(partner_default_changed=True),lambda v:v.pop('lab_profile'),lambda v:v.update(long_ready={}),lambda v:v['lab_profile_progress'].update(lab_profile_id=21)]:
   v=self.row();edit(v);self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
  f={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'LAB_PROFILE_PROFILE','lab_profile_progress':{'lab_params_id':42,'lab_profile_id':None},'raw':'SECRET'}
  out=r.public_rows(json.dumps(f).encode())[0];self.assertEqual((out['failure_code'],out['lab_profile_progress']['lab_params_id']),('LAB_PROFILE_PROFILE',42));self.assertNotIn('SECRET',json.dumps(out))
if __name__=='__main__':unittest.main()

import unittest,hashlib,json
from pathlib import Path
from unittest.mock import patch
import long_upload as l1,long_upload_r2 as l,prepare_long_upload_r2 as g,run_long_upload_r2 as r
import test_long_upload_r1 as t1,test_thumbnail_r5 as old
H=Path(__file__).parent
class Fake(t1.Fake):
 def __init__(self,profile=15,**kw):
  super().__init__(**kw);self.profile=profile
 def call(self,service,action,**f):
  v=super().call(service,action,**f)
  if (service,action)==('media','add'):self.add_form=f;v=dict(v,conversionProfileId=self.profile)
  return v
class Tests(unittest.TestCase):
 def run_upload(self,fake):
  self.progress=[]
  with patch.object(l,'SHA256',hashlib.sha256(t1.DATA).hexdigest()):
   return l.upload(fake.call,fake.post,'k'*40,t1.DATA,'baseline-long-'+'0123456789abcdef01234567',progress=self.progress.append)
 def test_only_profile_differs(self):
  a=Path('long_upload.py').read_text().splitlines();b=Path('long_upload_r2.py').read_text().splitlines()
  diff=[x for x in b if x not in a];self.assertTrue(all('PROFILE' in x or 'conversion_profile_id' in x or x.startswith(('"""R2','params 118')) for x in diff),diff)
 def test_profile_pinned_and_checked(self):
  f=Fake();v=self.run_upload(f)
  self.assertEqual(f.add_form['entry:conversionProfileId'],15);self.assertEqual(v['conversion_profile_id'],15)
  with patch.object(l,'SHA256',hashlib.sha256(t1.DATA).hexdigest()):l.validate(v)
  f=Fake(profile=14)
  with self.assertRaises(l.Rejected) as e:self.run_upload(f)
  self.assertEqual(str(e.exception),'LONG_MEDIA_ADD');self.assertEqual(self.progress[-1]['entry_created'],True)  # created entry stays visible
  self.assertNotIn(('media','addContent'),f.calls)
 def test_derivation(self):
  s=g.build();self.assertEqual(s,(H/'guest_long_upload_r2.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertEqual(s.count('longup.upload('),1);self.assertEqual(s.count('newlogs.scan(files,start,patterns,legacy.logs)'),2);self.assertIn("load('long_upload_r2'",s)
  for u in ('18154d61','2e9f8e2c','56fbc341'):self.assertIn('baseline-freeze-'+u+'.service',r.REMOTE_GUARD)
  self.assertIn("fullhd60.mp4')",r.REMOTE_GUARD);self.assertIn('now=time.gmtime();assert now.tm_min<30',r.REMOTE_GUARD)
  r.PROOF_PIN='a'*64;self.assertIn('/var/lib/kaltura-baseline-long-upload-r2/guest_long_upload_r2.py ',r.unit_command('baseline-freeze-00000000'))
 def row(self):
  x=old.Tests();v=x.row();v.pop('thumbnail');v.pop('thumbnail_diagnostics')
  v['long_upload']=dict(t1.Tests().good(),conversion_profile_id=15);v['long_upload_progress']={'token_created':True,'acked_parts':112,'acked_bytes':l.SIZE,'entry_created':True,'entry_id':'0_newentry'};return v
 def test_public_projection(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual((out['long_upload']['conversion_profile_id'],out['upload_attempted']),(15,True))
  for edit in [lambda v:v['long_upload'].update(conversion_profile_id=14),lambda v:v['long_upload_progress'].update(entry_id='0_other000'),lambda v:v.update(long_ready={})]:
   v=self.row();edit(v);self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
  f={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'LONG_MEDIA_ADD','long_upload_progress':{'token_created':True,'acked_parts':112,'acked_bytes':l.SIZE,'entry_created':True,'entry_id':'0_newentry'}}
  out=r.public_rows(json.dumps(f).encode())[0];self.assertEqual(out['long_upload_progress']['entry_id'],'0_newentry')
if __name__=='__main__':unittest.main()

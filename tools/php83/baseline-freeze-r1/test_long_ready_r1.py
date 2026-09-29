import unittest,hashlib,json,importlib.util,tempfile,os,time
from pathlib import Path
from unittest.mock import patch
import long_ready as lr,privacy_new_logs as nl,prepare_long_ready_r1 as g,run_long_ready_r1 as r
import test_thumbnail_r5 as old
H=Path(__file__).parent
def scanner():
 s=importlib.util.spec_from_file_location('append_window_scan',H.parent/'baseline-rehearsal'/'privacy'/'append-window-v1'/'scan.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
F=scanner()
PAT=[b'PRIVATE-PATTERN-01',b'PRIVATE-PATTERN-02']
def asset(pid,status=2,w=1920,h=1080,fps=60,orig=False,i='0_asset00'):
 return {'objectType':'KalturaFlavorAsset','id':i,'entryId':lr.ENTRY,'partnerId':102,'flavorParamsId':pid,'status':status,'isOriginal':orig,'width':w,'height':h,'frameRate':fps,'bitrate':5000,'size':'1000','videoCodecId':'avc1','containerFormat':'isom','version':'1'}
ASSETS=[asset(0,orig=True,i='0_orig0000'),asset(2,w=640,h=360,fps=25,i='0_flav0002'),asset(7,i='0_flav0007')]
class Fake:
 def __init__(self,statuses=(4,1,2),assets=ASSETS,entry=None):
  self.statuses=list(statuses);self.assets=assets;self.entry=entry or {};self.calls=[]
 def call(self,s,a,**f):
  self.calls.append((s,a))
  if (s,a)==('media','get'):
   st=self.statuses.pop(0) if len(self.statuses)>1 else self.statuses[0]
   return dict({'objectType':'KalturaMediaEntry','id':lr.ENTRY,'partnerId':102,'status':st,'conversionProfileId':14,'mediaType':1,'msDuration':60000},**self.entry)
  if (s,a)==('flavorasset','getByEntryId'):return [dict(x) for x in self.assets]
  raise AssertionError((s,a))
class Tests(unittest.TestCase):
 def test_new_logs_scanned_whole(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.log';a.write_bytes(b'old ');inv=lambda:sorted(Path(t).glob('*.log'))
   start=F.snapshot(inv())
   a.write_bytes(b'old appended '+PAT[0]);b=Path(t)/'b.log';b.write_bytes(b'new file '+PAT[1]+b' '+PAT[1])
   with self.assertRaises(F.Incomplete) as e:F.scan_window(start,PAT,inventory=inv)
   self.assertEqual(str(e.exception),'INVENTORY_CHANGED')
   v=nl.scan(F,start,PAT,inv);self.assertEqual(v['counts'],[1,2]);self.assertEqual(v['status'],'COMPLETE_FINITE_FILE_WINDOW')
   c=Path(t)/'c.log';c.write_bytes(b'');st=os.stat(c)
   self.assertEqual(nl.augment(start,inv,F.Mark)[str(c)].mtime_ns,st.st_mtime_ns)
   os.utime(c,ns=(st.st_atime_ns,st.st_mtime_ns+10**9))
   aug=nl.augment(start,inv,F.Mark);os.utime(c,ns=(st.st_atime_ns,st.st_mtime_ns+2*10**9))
   with self.assertRaises(F.Incomplete) as e:F.scan_window(aug,PAT,inventory=inv)
   self.assertEqual(str(e.exception),'REWRITTEN')
 def test_new_log_during_scan_retries(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.log';a.write_bytes(b'x');inv=lambda:sorted(Path(t).glob('*.log'));start=F.snapshot(inv())
   real=F.scan_window;n={'i':0}
   def flaky(s,p,inventory):
    n['i']+=1
    if n['i']==1:(Path(t)/'late.log').write_bytes(PAT[0]);raise F.Incomplete('INVENTORY_CHANGED')
    return real(s,p,inventory=inventory)
   with patch.object(F,'scan_window',flaky):v=nl.scan(F,start,PAT,inv,pause=0)
   self.assertEqual((n['i'],v['counts']),(2,[1,0]))
   with patch.object(F,'scan_window',side_effect=F.Incomplete('INVENTORY_CHANGED')):self.assertRaises(F.Incomplete,nl.scan,F,start,PAT,inv,attempts=2,pause=0)
   with patch.object(F,'scan_window',side_effect=F.Incomplete('TRUNCATED')) as m:
    self.assertRaises(F.Incomplete,nl.scan,F,start,PAT,inv,pause=0);self.assertEqual(m.call_count,1)
   b=Path(t)/'b.log';b.write_bytes(b'y');start=F.snapshot(inv());os.rename(b,Path(t)/'b.log.1')
   self.assertRaises(nl.Rejected,nl.augment,start,lambda:[a,Path(t)/'b.log.1'],F.Mark)
   os.link(a,Path(t)/'hard.log');self.assertRaises(nl.Rejected,nl.augment,start,inv,F.Mark)
 def test_vanished_new_log_fails_closed(self):
  # Reproduction of the Opus finding: a new in-window log holding a marker disappears during the scan.
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.log';a.write_bytes(b'x');inv=lambda:sorted(Path(t).glob('*.log'));start=F.snapshot(inv())
   b=Path(t)/'b.log';b.write_bytes(b'marker '+PAT[0])
   real=F.scan_window;n={'i':0}
   def vanish(s,p,inventory):
    n['i']+=1
    if n['i']==1:b.unlink();raise F.Incomplete('INVENTORY_CHANGED')
    return real(s,p,inventory=inventory)
   with patch.object(F,'scan_window',vanish):
    with self.assertRaises(nl.Rejected) as e:nl.scan(F,start,PAT,inv,pause=0)
   self.assertEqual(str(e.exception),'NEW_LOG_VANISHED')
  with tempfile.TemporaryDirectory() as t:  # registry persists across audit_once calls of one window
   a=Path(t)/'a.log';a.write_bytes(b'x');inv=lambda:sorted(Path(t).glob('*.log'));start=F.snapshot(inv())
   b=Path(t)/'b.log';b.write_bytes(b'marker '+PAT[0]);self.assertEqual(nl.scan(F,start,PAT,inv)['counts'],[1,0])
   b.unlink();self.assertRaises(nl.Rejected,nl.scan,F,start,PAT,inv,pause=0)
   other=F.snapshot(inv());self.assertEqual(nl.scan(F,other,PAT,inv)['counts'],[0,0])  # a different window is independent
  with tempfile.TemporaryDirectory() as t:  # shrink between augment and scan is detected
   a=Path(t)/'a.log';a.write_bytes(b'x');inv=lambda:sorted(Path(t).glob('*.log'));start=F.snapshot(inv())
   b=Path(t)/'b.log';b.write_bytes(b'0123456789'+PAT[1]);real=F.scan_window
   def shrink(s,p,inventory):
    with open(b,'r+b') as f:f.truncate(3)
    return real(s,p,inventory=inventory)
   with patch.object(F,'scan_window',shrink):
    with self.assertRaises(nl.Rejected) as e:nl.scan(F,start,PAT,inv,pause=0)
   self.assertEqual(str(e.exception),'NEW_LOG_TRUNCATED')
 def test_window_registry_bound(self):
  with patch.dict(nl._WINDOWS,{i:(object(),{}) for i in range(32)},clear=True):
   self.assertRaises(nl.Rejected,nl._seen,{})
 def observe(self,fake,**kw):
  return lr.observe(fake.call,'k'*40,sleep=lambda s:None,**kw)
 def test_ready_and_flavors(self):
  f=Fake();v=self.observe(f);v['stored_original_sha256_match']=True;lr.validate(v)
  self.assertEqual((v['ready_polls'],v['ready_flavor_params'],v['delivered_1080p60_flavor_present'],v['original_flavor_id']),(3,[0,2,7],True,'0_orig0000'))
  self.assertEqual(f.calls.count(('flavorasset','getByEntryId')),1);self.assertNotIn('k'*40,json.dumps(v))
  v=self.observe(Fake(assets=[ASSETS[0],asset(7,fps=30,i='0_flav0007')]));self.assertFalse(v['delivered_1080p60_flavor_present'])
  v=self.observe(Fake(assets=[ASSETS[0],asset(7,status=1,i='0_flav0007')]));self.assertEqual(v['not_ready_flavor_count'],1)
 def test_ready_failures(self):
  for fake,code in [(Fake(statuses=(1,-1)),'LONG_READY_ERROR_STATE'),(Fake(entry={'conversionProfileId':15}),'LONG_READY_ENTRY'),(Fake(entry={'partnerId':5}),'LONG_READY_ENTRY'),
                    (Fake(assets=[asset(0,orig=True,i='0_orig0000'),asset(0,orig=True,i='0_orig0001')]),'LONG_READY_FLAVORS'),(Fake(assets=[ASSETS[0],asset(9,i='0_flav0009')]),'LONG_READY_FLAVORS'),
                    (Fake(assets=[ASSETS[0],dict(ASSETS[1],entryId='0_other000')]),'LONG_READY_FLAVORS')]:
   with self.assertRaises(lr.Rejected) as e:self.observe(fake)
   self.assertEqual(str(e.exception),code)
  t=iter([0]+[1000]*10)
  with self.assertRaises(lr.Rejected) as e:self.observe(Fake(statuses=(1,)),clock=lambda:next(t))
  self.assertEqual(str(e.exception),'LONG_READY_TIMEOUT')
  t=iter([0,239,241,241,241])  # READY returned only after the budget is not accepted
  with self.assertRaises(lr.Rejected) as e:self.observe(Fake(statuses=(1,2)),clock=lambda:next(t))
  self.assertEqual(str(e.exception),'LONG_READY_TIMEOUT')
 def test_schema(self):
  v=self.observe(Fake());self.assertRaises(lr.Rejected,lr.validate,v)  # sha match must be set by guest
  v['stored_original_sha256_match']=True
  for k,x in [('stream_inspected',True),('entry_id','0_other000'),('full_acceptance',True)]:self.assertRaises(lr.Rejected,lr.validate,dict(v,**{k:x}))
  bad=json.loads(json.dumps(v));bad['flavors'][0]['videoCodecId']='x'*40;self.assertRaises(lr.Rejected,lr.validate,bad)
  for edit in [lambda x:x.update(original_flavor_id='0_flav0002'),lambda x:x.update(ready_flavor_params=[0]),lambda x:x.update(not_ready_flavor_count=1),lambda x:x.update(delivered_1080p60_flavor_present=False),lambda x:x['flavors'].append(dict(x['flavors'][1]))]:
   bad=json.loads(json.dumps(v));edit(bad);self.assertRaises(lr.Rejected,lr.validate,bad)
  self.assertEqual(lr.flavor(dict(ASSETS[0],videoCodecId='<script>'))['videoCodecId'],'OTHER')
 def test_derivation(self):
  s=g.build();self.assertEqual(s,(H/'guest_long_ready_r1.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertEqual(s.count('newlogs.scan(files,start,patterns,legacy.logs)'),2);self.assertNotIn('files.scan_window(',s)
  self.assertEqual(s.count('longready.observe('),1);self.assertNotIn('longup.upload',s);self.assertNotIn("'uploadtoken'",s)
  self.assertLess(s.index("newlogs=load("),s.index("legacy.logs() # Mandatory"))
  for u in ('b93f7882','5df47596','e16b8e67','ec290fc3','128d02f3','6858a1eb','56fbc341'):self.assertIn('baseline-freeze-'+u+'.service',r.REMOTE_GUARD)
  r.PROOF_PIN='a'*64;self.assertIn('/var/lib/kaltura-baseline-long-ready-r1/guest_long_ready_r1.py ',r.unit_command('baseline-freeze-00000000'))
 def row(self):
  x=old.Tests();v=x.row();v.pop('thumbnail');v.pop('thumbnail_diagnostics')
  ready=self.observe(Fake());ready['stored_original_sha256_match']=True;v['long_ready']=ready;return v
 def test_public_projection(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual(out['long_ready']['entry_status'],2);self.assertNotIn('thumbnail',out)
  for edit in [lambda v:v['long_ready'].update(stored_original_sha256_match=False),lambda v:v.update(thumbnail={}),lambda v:v.pop('long_ready')]:
   v=self.row();edit(v);self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
  f={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'LONG_READY_TIMEOUT','raw':'SECRET'}
  out=r.public_rows(json.dumps(f).encode())[0];self.assertEqual(out['failure_code'],'LONG_READY_TIMEOUT');self.assertNotIn('SECRET',json.dumps(out))
if __name__=='__main__':unittest.main()

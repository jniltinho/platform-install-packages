import unittest,copy,json,hashlib,ast,tempfile
from pathlib import Path
from unittest.mock import patch
import thumbnail_r4 as t,thumbnail_decode as d,prepare_thumbnail_r5 as g,run_thumbnail_r5 as r
import privacy_sphinx_binlog as sb,os
import test_hls_id3 as old
H=Path(__file__).parent
ROW={'objectType':'KalturaThumbAsset','id':'0_abcdefgh','entryId':t.ENTRY,'partnerId':102,'status':2,'version':2,'thumbParamsId':1,'width':320,'height':180,'size':23817,'fileExt':'jpg'}
URL='https://192.168.56.74/api_v3/index.php/service/thumbAsset/action/serve/thumbAssetId/0_abcdefgh/v/2'
SB={'status':'COMPLETE_FULL_CONTENT_SCAN','counts':[0,0],'files':3,'bytes':11,'deleted_between_audits_covered':False}
DECODE={'codec':'mjpeg','width':320,'height':180,'frames':1,'full_image_decode':True,'api_dimensions_match':True,'dynamic_library_cohort_attested':False,'full_acceptance':False}
class Tests(unittest.TestCase):
 def observe(self,url=URL):
  self.events=[];self.diag={}
  def call(**f):
   self.events.append(f['action']);return {'objectType':'KalturaThumbAssetListResponse','totalCount':1,'objects':[copy.deepcopy(ROW)]} if f['action']=='list' else url
  return t.observe(call,lambda u:self.events.append('enroll'),lambda *args:(self.events.append('GET') or (200,[('Content-Type','image/jpeg')],b'\xff\xd8fake\xff\xd9')),lambda *args:copy.deepcopy(DECODE),'s'*32,'k'*32,lambda k,v:self.diag.update({k:v}))
 def test_success(self):
  v=self.observe();t.validate(v);self.assertEqual(self.events,['list','getUrl','enroll','GET']);self.assertEqual(set(self.diag),{'METADATA','URL','IMAGE','DECODE'})
 def test_bad_url_enrolled_before_reject(self):
  for url in [URL+'?ks=x',URL+'/ks/'+'k'*32,URL.replace('192.168.56.74','192.168.56.20'),URL+'/extra/x']:
   with self.assertRaises(t.Rejected):self.observe(url)
   self.assertEqual(self.events,['list','getUrl','enroll'])
 def test_ownership_cardinality(self):
  for key,value in [('entryId','0_otherxxx'),('partnerId',1),('status',1),('version',0),('width',True)]:
   row=dict(ROW);row[key]=value
   self.assertRaises(t.Rejected,t.collect,lambda **f:{'objectType':'KalturaThumbAssetListResponse','totalCount':1,'objects':[row]})
  self.assertRaises(t.Rejected,t.collect,lambda **f:{'objectType':'KalturaThumbAssetListResponse','totalCount':2,'objects':[ROW,ROW]})
 def row(self):
  x=old.Tests();x.setUp();v=x.row();v.pop('hls_delivery');v.pop('hls_diagnostics');v.pop('hls_segment_diagnostics');v.pop('playback_context',None);v['thumbnail']=self.observe();v['thumbnail_diagnostics']=self.diag;v['sphinx_binlog_audits']=[dict(SB,audit=1)];return v
 def test_full_public_success(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual(out['thumbnail']['gets'],1);self.assertNotIn('hls_delivery',out)
 def test_full_public_negatives(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
  for edit in [lambda v:v.pop('round_privacy'),lambda v:v['thumbnail']['decode'].update(private='SECRET'),lambda v:v['thumbnail_diagnostics']['URL'].update(port='8444'),lambda v:v.update(sources_after={})]:
   v=self.row();edit(v);self.assertRaises(Exception,r.public_rows,json.dumps(v).encode())
 def test_failed_closed_projection(self):
  self.observe();v={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'THUMB_ROUTE','thumbnail_diagnostics':self.diag,'raw':'SECRET'}
  out=r.public_rows(json.dumps(v).encode());self.assertNotIn('SECRET',json.dumps(out));self.assertEqual(out[0]['failure_code'],'THUMB_ROUTE')
 def test_real_pin_loop(self):
  s=g.build();self.assertEqual(s,(H/'guest_thumbnail_r5.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  n=next(n for n in ast.walk(ast.parse(s)) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Attribute) and isinstance(n.iter.func.value,ast.Dict) and any(isinstance(k,ast.Constant) and k.value=='thumbnail_r4.py' for k in n.iter.func.value.keys))
  code=compile(ast.Module(body=[n],type_ignores=[]),'actual_thumbnail_pin_loop','exec')
  def need(ok,code):
   if not ok:raise ValueError(code)
  exec(code,{'NEW_HERE':H,'need':need,'hashlib':hashlib})
  with tempfile.TemporaryDirectory() as temp:
   self.assertRaises(Exception,exec,code,{'NEW_HERE':Path(temp),'need':need,'hashlib':hashlib})
  self.assertIn('baseline-freeze-b93f7882.service',r.REMOTE_GUARD);self.assertIn('baseline-freeze-5df47596.service',r.REMOTE_GUARD);self.assertIn('baseline-freeze-e16b8e67.service',r.REMOTE_GUARD);self.assertIn('baseline-freeze-ec290fc3.service',r.REMOTE_GUARD);self.assertIn('baseline-freeze-128d02f3.service',r.REMOTE_GUARD)
  self.assertIn('/var/lib/kaltura-baseline-thumbnail-r5',r.REMOTE_GUARD);self.assertNotIn('thumbnail-r4',r.REMOTE_GUARD+r.STAGE);self.assertNotIn('thumbnail-r3',r.REMOTE_GUARD+r.STAGE);self.assertNotIn('thumbnail-r1',r.REMOTE_GUARD+r.STAGE);self.assertNotIn('thumbnail-r2',r.REMOTE_GUARD+r.STAGE)
 def test_decoder_fixed_input_and_commands(self):
  seen=[]
  def run(fd,args,media):
   seen.append(args);return json.dumps({'streams':[{'codec_type':'video','codec_name':'mjpeg','width':320,'height':180,'nb_read_frames':'1'}]}).encode() if '-show_entries' in args else b''
  with patch.object(d.runtime,'run',side_effect=run),patch.object(d.runtime,'pinned',return_value=b'binary'):
   self.assertEqual(d.decode(b'\xff\xd8fake\xff\xd9',320,180),DECODE)
  self.assertTrue(all(x[x.index('-protocol_whitelist')+1]=='file' and x[x.index('-f')+1]=='mjpeg' for x in seen))
  self.assertTrue(all(x[x.index('-err_detect')+1]=='explode' for x in seen))
  self.assertRaises(d.Rejected,d.decode,b'not JPEG',320,180)
 def test_size_is_bytes(self):
  import thumbnail as r1
  row=dict(ROW)
  self.assertRaises(r1.Rejected,r1.collect,lambda **f:{'objectType':'KalturaThumbAssetListResponse','totalCount':1,'objects':[row]})
  self.assertEqual(t.collect(lambda **f:{'objectType':'KalturaThumbAssetListResponse','totalCount':1,'objects':[row]})[1]['size_API_bytes'],23817)
  row['size']=1024*1024;self.assertEqual(t.collect(lambda **f:{'objectType':'KalturaThumbAssetListResponse','totalCount':1,'objects':[row]})[1]['size_API_bytes'],1024*1024)
  seen={};dup=dict(ROW,status=1)
  self.assertRaises(t.Rejected,t.collect,lambda **f:{'objectType':'KalturaThumbAssetListResponse','totalCount':2,'objects':[ROW,dup]},lambda k,v:seen.update({k:v}))
  c=seen['ROW_CHECKS'];self.assertEqual((c['row_index'],[k for k in t.ROW_CHECK_KEYS if not c['checks'][k]]),(1,['id_unique']))
  row['size']=1024*1024+1;self.assertRaises(t.Rejected,t.collect,lambda **f:{'objectType':'KalturaThumbAssetListResponse','totalCount':1,'objects':[row]})
 def test_row_checks_identify_field_without_values(self):
  for key,value,expect in [('size',1024*1024+1,'size'),('fileExt','png','fileExt'),('width',None,'width'),('partnerId',1,'partnerId'),('id','BAD-ID-secret','id_format')]:
   row=dict(ROW);row[key]=value
   if value is None:row.pop(key)
   seen={}
   with self.assertRaises(t.Rejected) as e:t.collect(lambda **f:{'objectType':'KalturaThumbAssetListResponse','totalCount':1,'objects':[row]},lambda k,v:seen.update({k:v}))
   self.assertEqual(str(e.exception),'THUMB_ROW');c=seen['ROW_CHECKS']['checks']
   self.assertEqual([k for k in t.ROW_CHECK_KEYS if not c[k]],[expect]);t.diagnostics(seen);self.assertNotIn('secret',json.dumps(seen))
  self.assertEqual(c['fileExt_class'],'jpg')
  row=dict(ROW,fileExt='<script>');seen={}
  self.assertRaises(t.Rejected,t.collect,lambda **f:{'objectType':'KalturaThumbAssetListResponse','totalCount':1,'objects':[row]},lambda k,v:seen.update({k:v}))
  self.assertEqual(seen['ROW_CHECKS']['checks']['fileExt_class'],'OTHER')
  good=t.row_checks(ROW,set());self.assertTrue(all(good[k] for k in t.ROW_CHECK_KEYS))
  self.assertRaises(t.Rejected,t.diagnostics,{'ROW_CHECKS':{'row_index':0,'rows':1,'checks':good}})
  self.assertRaises(t.Rejected,t.diagnostics,{'ROW_CHECKS':{'row_index':0,'rows':1,'checks':dict(c,extra=True)}})
 def test_failed_row_projection(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004;seen={}
  row=dict(ROW,size=10**9)
  self.assertRaises(t.Rejected,t.observe,lambda **f:{'objectType':'KalturaThumbAssetListResponse','totalCount':1,'objects':[row]},None,None,None,'s'*32,'k'*32,lambda k,v:seen.update({k:v}))
  v={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'THUMB_ROW','thumbnail_diagnostics':seen,'raw':'SECRET'}
  out=r.public_rows(json.dumps(v).encode())[0];self.assertNotIn('SECRET',json.dumps(out))
  self.assertEqual(out['thumbnail_diagnostics']['ROW_CHECKS']['checks']['size'],False)
 def test_route_checks_keys_only(self):
  ks='FAKEKS'+'SECRET'+'x'*32
  for url,keys,prefix in [(URL+'/ks/'+ks+'/ks/'+ks,['thumbAssetId','v','ks','ks'],True),(URL+'/relocate/0_wzmt2sfy.jpg',['thumbAssetId','v','relocate'],True),
    (URL.replace('/v/2','/v/3'),['thumbAssetId','v'],False),('https://192.168.56.74/p/102/sp/10200/thumbnail/entry_id/0_wzmt2sfy',[],False)]:
   with self.assertRaises(t.Rejected) as e:self.observe(url)
   self.assertEqual(str(e.exception),'THUMB_ROUTE');rc=self.diag['ROUTE_CHECKS']
   self.assertEqual((rc['keys'],rc['prefix']),(keys,prefix));t.diagnostics(self.diag)
   self.assertNotIn('SECRET',json.dumps(self.diag));self.assertNotIn('0_wzmt2sfy.jpg',json.dumps(self.diag))
   self.assertEqual(self.events,['list','getUrl','enroll'])
  self.observe();self.assertNotIn('ROUTE_CHECKS',self.diag)
  for bad in [{'base':True,'prefix':True,'pairs_even':True,'keys':['secretvalue']},{'base':False,'prefix':False,'pairs_even':False,'keys':['ks']},{'base':True,'prefix':True,'pairs_even':True,'keys':['ks'],'x':1}]:
   self.assertRaises(t.Rejected,t.diagnostics,{'ROUTE_CHECKS':bad})
 def test_failed_route_projection(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
  self.assertRaises(t.Rejected,self.observe,URL+'/ks/'+'Z'*40+'/pv/1')
  v={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'THUMB_ROUTE','thumbnail_diagnostics':self.diag,'raw':'SECRET'}
  out=r.public_rows(json.dumps(v).encode())[0];self.assertEqual(out['thumbnail_diagnostics']['ROUTE_CHECKS']['keys'],['thumbAssetId','v','ks','pv']);self.assertNotIn('Z'*20,json.dumps(out))
 def test_generated_download_ks_route(self):
  gen='GENERATEDdownloadKS'+'a'*40
  v=self.observe(URL+'/pv/3/ev/4/ks/'+gen);t.validate(v);self.assertIs(v['download_ks_in_path'],True);self.assertEqual(self.events,['list','getUrl','enroll','GET'])
  self.assertEqual(self.diag['DECODE'],v['decode']);self.assertNotIn(gen,json.dumps(v)+json.dumps(self.diag))
  v=self.observe();self.assertIs(v['download_ks_in_path'],False)
  for bad in [URL+'/ks/'+'a'*15,URL+'/ks/'+gen+'/extra/x',URL+'/ks/'+gen+'.jpg',URL+'/ks/'+gen+'/',URL+'/ks/'+'k'*32]:
   self.assertRaises(t.Rejected,self.observe,bad)
  with self.assertRaises(t.Rejected) as e:self.observe(URL+'/ks/'+'k'*32)
  self.assertEqual(str(e.exception),'THUMB_CREDENTIAL')
 def test_decode_diagnostic_schema(self):
  good=dict(DECODE);t.diagnostics({'DECODE':good})
  for edit in [dict(DECODE,codec='png'),dict(DECODE,full_acceptance=True),dict(DECODE,extra=1),dict(DECODE,frames=2)]:self.assertRaises(t.Rejected,t.diagnostics,{'DECODE':edit})
 def test_privacy_failed_round_keeps_decode(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004;self.observe(URL+'/ks/'+'G'*40)
  v={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'MEDIA_PRIVACY','failure_code':'THUMB_RESPONSE','thumbnail_diagnostics':self.diag,'raw':'SECRET'}
  out=r.public_rows(json.dumps(v).encode())[0];self.assertEqual(out['thumbnail_diagnostics']['DECODE'],DECODE);self.assertNotIn('G'*20,json.dumps(out))
 def sphinx_dir(self,temp,names={'binlog.meta':b'x'*11,'binlog.lock':b'','binlog.001':b''}):
  d=Path(temp)/'log'/'sphinx'/'data';d.mkdir(parents=True)
  for n,v in names.items():(d/n).write_bytes(v)
  return d
 def test_sphinx_exclude_and_full_scan(self):
  with tempfile.TemporaryDirectory() as temp,patch.object(sb,'DIRECTORY',self.sphinx_dir(temp)):
   d=sb.DIRECTORY;other=Path(temp)/'log'/'a.log';other.write_bytes(b'')
   kept=sb.exclude(lambda:[other,*sorted(d.iterdir())]);self.assertEqual(kept,[other])
   v=sb.scan([b'SECRETPATTERN1',b'xxxxxxxxxx']);self.assertEqual((v['counts'],v['files'],v['bytes']),([0,2],3,11))
   (d/'binlog.002').write_bytes(b'..SECRETPATTERN1..SECRETPATTERN1');v=sb.scan([b'SECRETPATTERN1']);self.assertEqual(v['counts'],[2])
   self.assertNotIn('SECRETPATTERN1',json.dumps(v));sb.validate(dict(v,audit=1))
   (d/'binlog.meta').write_bytes(b'y'*11)  # same-size rewrite is fine for full-content scan
   self.assertEqual(sb.scan([b'yyyyyyyyyyy'])['counts'],[1])
 def test_sphinx_fail_closed(self):
  for names in [{'binlog.meta':b'','notes.txt':b''},{}]:
   with tempfile.TemporaryDirectory() as temp,patch.object(sb,'DIRECTORY',self.sphinx_dir(temp,names)):
    self.assertRaises(sb.Rejected,sb.scan,[b'patternxx']);self.assertRaises(sb.Rejected,sb.exclude,lambda:[])
  with tempfile.TemporaryDirectory() as temp,patch.object(sb,'DIRECTORY',self.sphinx_dir(temp)):
   os.symlink('/etc/hostname',sb.DIRECTORY/'binlog.009');self.assertRaises(sb.Rejected,sb.scan,[b'patternxx'])
  with tempfile.TemporaryDirectory() as temp,patch.object(sb,'DIRECTORY',self.sphinx_dir(temp)):
   real=sb._marks;state={'n':0}
   def drifting(dfd,names):
    state['n']+=1;m=real(dfd,names);return {k:(a,b,c,e+state['n']) for k,(a,b,c,e) in m.items()}
   with patch.object(sb,'_marks',drifting):
    with self.assertRaises(sb.Rejected) as e:sb.scan([b'patternxx'],attempts=2,pause=0)
   self.assertEqual(str(e.exception),'SPHINX_BINLOG_UNSTABLE')
  for bad in [dict(SB,audit=1,extra=1),dict(SB,audit=0),dict(SB,audit=1,status='X'),dict(SB,audit=1,deleted_between_audits_covered=True)]:self.assertRaises(sb.Rejected,sb.validate,bad)
 def test_sphinx_alias_and_directory_swap(self):
  with tempfile.TemporaryDirectory() as temp,patch.object(sb,'DIRECTORY',self.sphinx_dir(temp)):
   alias=Path(temp)/'log'/'alias.log';os.symlink(sb.DIRECTORY/'binlog.meta',alias)
   self.assertRaises(sb.Rejected,sb.exclude,lambda:[alias])
   self.assertEqual(sb.exclude(lambda:[sb.DIRECTORY]),[])
   dalias=Path(temp)/'dalias';os.symlink(sb.DIRECTORY,dalias);self.assertRaises(sb.Rejected,sb.exclude,lambda:[dalias])
   moved=Path(temp)/'moved';real_read=sb._read
   def swap(dfd,name,mark):
    data=real_read(dfd,name,mark)
    if not moved.exists():sb.DIRECTORY.rename(moved);self.sphinx_dir(temp)
    return data
   with patch.object(sb,'_read',swap):self.assertRaises(sb.Rejected,sb.scan,[b'patternxx'],attempts=1,pause=0)
  with tempfile.TemporaryDirectory() as temp,patch.object(sb,'DIRECTORY',self.sphinx_dir(temp)):
   real_marks=sb._marks;calls={'n':0}
   def vanish(dfd,names):
    calls['n']+=1
    if calls['n']==1:raise FileNotFoundError
    return real_marks(dfd,names)
   with patch.object(sb,'_marks',vanish):self.assertEqual(sb.scan([b'patternxx'],attempts=2,pause=0)['status'],'COMPLETE_FULL_CONTENT_SCAN')
 def test_guest_injections(self):
  s=(H/'guest_thumbnail_r5.py').read_text()
  self.assertIn("legacy.logs=lambda:sphinx.exclude(lambda:media_logs.extend(lambda:tls_logs.extend(old_logs)))",s)
  self.assertEqual(s.count('sphinx.scan(list(patterns))'),1);self.assertIn(hashlib.sha256((H/'privacy_sphinx_binlog.py').read_bytes()).hexdigest(),s)
  self.assertLess(s.index('legacy.logs=lambda:sphinx.exclude'),s.index('legacy.logs() # Mandatory'))
  a=s.index('def audit_once');self.assertTrue(a<s.index('sphinx.scan(list(patterns))')<s.index('def audit(patterns'))
  self.assertEqual(r.PINS['privacy_sphinx_binlog.py'],hashlib.sha256((H/'privacy_sphinx_binlog.py').read_bytes()).hexdigest())
 def test_sphinx_public_projection(self):
  r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004;self.observe()
  v={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'MEDIA_PRIVACY','failure_code':'PRIVATE_MARKER_LOGGED','thumbnail_diagnostics':self.diag,'sphinx_binlog_audits':[dict(SB,audit=3,counts=[0,1])]}
  out=r.public_rows(json.dumps(v).encode())[0];self.assertEqual(out['sphinx_binlog_audits'][0]['counts'],[0,1])
  row=self.row();row['sphinx_binlog_audits']=[dict(SB,audit=1,counts=[1,0])];self.assertRaises(Exception,r.public_rows,json.dumps(row).encode())
if __name__=='__main__':unittest.main()

import unittest,copy,json,hashlib,ast,tempfile
from pathlib import Path
from unittest.mock import patch
import thumbnail_r3 as t,thumbnail_decode as d,prepare_thumbnail_r3 as g,run_thumbnail_r3 as r
import test_hls_id3 as old
H=Path(__file__).parent
ROW={'objectType':'KalturaThumbAsset','id':'0_abcdefgh','entryId':t.ENTRY,'partnerId':102,'status':2,'version':2,'thumbParamsId':1,'width':320,'height':180,'size':23817,'fileExt':'jpg'}
URL='https://192.168.56.74/api_v3/index.php/service/thumbAsset/action/serve/thumbAssetId/0_abcdefgh/v/2'
DECODE={'codec':'mjpeg','width':320,'height':180,'frames':1,'full_image_decode':True,'api_dimensions_match':True,'dynamic_library_cohort_attested':False,'full_acceptance':False}
class Tests(unittest.TestCase):
 def observe(self,url=URL):
  self.events=[];self.diag={}
  def call(**f):
   self.events.append(f['action']);return {'objectType':'KalturaThumbAssetListResponse','totalCount':1,'objects':[copy.deepcopy(ROW)]} if f['action']=='list' else url
  return t.observe(call,lambda u:self.events.append('enroll'),lambda *args:(self.events.append('GET') or (200,[('Content-Type','image/jpeg')],b'\xff\xd8fake\xff\xd9')),lambda *args:copy.deepcopy(DECODE),'s'*32,'k'*32,lambda k,v:self.diag.update({k:v}))
 def test_success(self):
  v=self.observe();t.validate(v);self.assertEqual(self.events,['list','getUrl','enroll','GET']);self.assertEqual(set(self.diag),{'METADATA','URL','IMAGE'})
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
  x=old.Tests();x.setUp();v=x.row();v.pop('hls_delivery');v.pop('hls_diagnostics');v.pop('hls_segment_diagnostics');v.pop('playback_context',None);v['thumbnail']=self.observe();v['thumbnail_diagnostics']=self.diag;return v
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
  s=g.build();self.assertEqual(s,(H/'guest_thumbnail_r3.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  n=next(n for n in ast.walk(ast.parse(s)) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Attribute) and isinstance(n.iter.func.value,ast.Dict) and any(isinstance(k,ast.Constant) and k.value=='thumbnail_r3.py' for k in n.iter.func.value.keys))
  code=compile(ast.Module(body=[n],type_ignores=[]),'actual_thumbnail_pin_loop','exec')
  def need(ok,code):
   if not ok:raise ValueError(code)
  exec(code,{'NEW_HERE':H,'need':need,'hashlib':hashlib})
  with tempfile.TemporaryDirectory() as temp:
   self.assertRaises(Exception,exec,code,{'NEW_HERE':Path(temp),'need':need,'hashlib':hashlib})
  self.assertIn('baseline-freeze-b93f7882.service',r.REMOTE_GUARD);self.assertIn('baseline-freeze-5df47596.service',r.REMOTE_GUARD);self.assertIn('baseline-freeze-e16b8e67.service',r.REMOTE_GUARD)
  self.assertIn('/var/lib/kaltura-baseline-thumbnail-r3',r.REMOTE_GUARD);self.assertNotIn('thumbnail-r1',r.REMOTE_GUARD+r.STAGE);self.assertNotIn('thumbnail-r2',r.REMOTE_GUARD+r.STAGE)
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
  for url,keys,prefix in [(URL+'/ks/'+ks,['thumbAssetId','v','ks'],True),(URL+'/relocate/0_wzmt2sfy.jpg',['thumbAssetId','v','relocate'],True),
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
  self.assertRaises(t.Rejected,self.observe,URL+'/ks/'+'Z'*40)
  v={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_stage':'API_ROUND','failure_code':'THUMB_ROUTE','thumbnail_diagnostics':self.diag,'raw':'SECRET'}
  out=r.public_rows(json.dumps(v).encode())[0];self.assertEqual(out['thumbnail_diagnostics']['ROUTE_CHECKS']['keys'],['thumbAssetId','v','ks']);self.assertNotIn('Z'*20,json.dumps(out))
if __name__=='__main__':unittest.main()

"""Phase B of the FullHD60 fixture: read-only observation of the phase-A entry (0_wzlsbwmy) until READY,
then its flavor set (READY budget 240s). No mutation, no retry of failed calls (polling media.get is observation).
Enums from pinned Rigel-18.20.0: KalturaEntryStatus ERROR_IMPORTING=-2, ERROR_CONVERTING=-1, IMPORT=0,
PRECONVERT=1, READY=2, DELETED=3, PENDING=4, MODERATE=5, BLOCKED=6, NO_CONTENT=7; KalturaFlavorAssetStatus
ERROR=-1, QUEUED=0, CONVERTING=1, READY=2, DELETED=3, NOT_APPLICABLE=4, TEMP=5, WAIT_FOR_CONVERT=6,
IMPORTING=7, VALIDATING=8, EXPORTING=9. Exports closed projections only (ids, enums, numbers, short codec
names); whether 1080p60 is delivered is recorded, not assumed."""
import re,time
ENTRY='0_wzlsbwmy';PARTNER=102;PROFILE=14
PROFILE_PARAMS={0,2,3,4,5,6,7}
READY_BUDGET=240;POLL=5 # entry was uploaded long before phase B; keeps READY+audits inside RuntimeMaxSec=1100
CODES=('LONG_READY_API','LONG_READY_ENTRY','LONG_READY_TIMEOUT','LONG_READY_ERROR_STATE','LONG_READY_FLAVORS','LONG_READY_SCHEMA')
TOKEN=re.compile(r'[A-Za-z0-9 ._-]{0,32}')
ASSET=re.compile(r'[01]_[a-z0-9]{8}')
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def whole(v,lo=-(2**31),hi=2**31-1):
 n=v if type(v) is int else int(v) if type(v) is float and v.is_integer() else int(v) if type(v) is str and re.fullmatch('-?[0-9]{1,12}',v) else None
 return n if n is not None and lo<=n<=hi else None
def number(v):
 return float(v) if type(v) in (int,float) and not type(v) is bool else float(v) if type(v) is str and re.fullmatch(r'[0-9]{1,9}(\.[0-9]{1,6})?',v) else None
def text(v):
 return v if type(v) is str and TOKEN.fullmatch(v) else 'OTHER' if v is not None else None
def derived(rows):
 hd60=[r for r in rows if not r['isOriginal'] and r['status']==2 and r['width']==1920 and r['height']==1080 and r['frameRate'] is not None and abs(r['frameRate']-60)<=0.5]
 return {'ready_flavor_params':sorted({r['flavorParamsId'] for r in rows if r['status']==2}),'not_ready_flavor_count':sum(r['status'] not in (2,4) for r in rows),'delivered_1080p60_flavor_present':bool(hd60)}
def get(call,ks):
 try:v=call('media','get',ks=ks,entryId=ENTRY,version=-1)
 except Exception:raise Rejected('LONG_READY_API') from None
 need(type(v) is dict and v.get('objectType')=='KalturaMediaEntry' and v.get('id')==ENTRY and whole(v.get('partnerId'))==PARTNER,'LONG_READY_ENTRY')
 return v
def flavor(a):
 need(type(a) is dict and a.get('objectType')=='KalturaFlavorAsset' and a.get('entryId')==ENTRY and whole(a.get('partnerId'))==PARTNER and type(a.get('id')) is str and ASSET.fullmatch(a['id']) is not None,'LONG_READY_FLAVORS')
 out={'flavorParamsId':whole(a.get('flavorParamsId'),0),'status':whole(a.get('status'),-1,9),'isOriginal':a.get('isOriginal') in (True,1,'1'),
  'width':whole(a.get('width'),0,8192),'height':whole(a.get('height'),0,8192),'frameRate':number(a.get('frameRate')),'bitrate':whole(a.get('bitrate'),0),
  'size_API':whole(a.get('size'),0),'videoCodecId':text(a.get('videoCodecId')),'containerFormat':text(a.get('containerFormat')),'version':whole(a.get('version'),0),'id':a['id']}
 need(out['flavorParamsId'] is not None and out['status'] is not None,'LONG_READY_FLAVORS');return out
def observe(call,ks,clock=time.monotonic,sleep=time.sleep):
 # call() in the guest is legacy PostTransport.request: each API call runs under deadline._bounded(deadline=30)
 # (baseline-api/transport.py:78), so one poll adds at most 30s after the pre-poll budget check. If that bound
 # were ever exceeded, validate() rejects ready_wait_seconds>budget+30 and the round fails closed.
 started=clock();polls=0
 while True:
  need(clock()-started<READY_BUDGET,'LONG_READY_TIMEOUT') # budget enforced before every poll, READY included
  e=get(call,ks);polls+=1;status=whole(e.get('status'),-2,7)
  need(status is not None,'LONG_READY_ENTRY')
  if status==2:break
  need(status not in (-2,-1,3,6,7),'LONG_READY_ERROR_STATE');sleep(max(0,min(POLL,READY_BUDGET-(clock()-started))))
 ready_seconds=round(clock()-started,3)
 need(whole(e.get('conversionProfileId'))==PROFILE and whole(e.get('mediaType'))==1,'LONG_READY_ENTRY')
 try:assets=call('flavorasset','getByEntryId',ks=ks,entryId=ENTRY)
 except Exception:raise Rejected('LONG_READY_API') from None
 need(type(assets) is list and 1<=len(assets)<=32,'LONG_READY_FLAVORS')
 rows=sorted((flavor(a) for a in assets),key=lambda r:(r['flavorParamsId'],r['id']))
 ids=[r['id'] for r in rows];need(len(set(ids))==len(ids),'LONG_READY_FLAVORS')
 originals=[r for r in rows if r['isOriginal']];need(len(originals)==1 and originals[0]['flavorParamsId']==0,'LONG_READY_FLAVORS')
 need({r['flavorParamsId'] for r in rows}<=PROFILE_PARAMS,'LONG_READY_FLAVORS')
 return {'case':'FULLHD60_READY_PHASE_B','entry_id':ENTRY,'entry_status':2,'conversion_profile_id':PROFILE,'ready_polls':polls,'ready_wait_seconds':ready_seconds,
  'duration_ms':whole(e.get('msDuration'),0),'flavors':rows,'original_flavor_id':originals[0]['id'],
  **derived(rows),'stored_original_sha256_match':None,'stream_inspected':False,'full_acceptance':False}
FLAVOR_KEYS={'flavorParamsId','status','isOriginal','width','height','frameRate','bitrate','size_API','videoCodecId','containerFormat','version','id'}
def validate(v):
 need(type(v) is dict and set(v)=={'case','entry_id','entry_status','conversion_profile_id','ready_polls','ready_wait_seconds','duration_ms','flavors','original_flavor_id','ready_flavor_params','not_ready_flavor_count','delivered_1080p60_flavor_present','stored_original_sha256_match','stream_inspected','full_acceptance'},'LONG_READY_SCHEMA')
 need(v['case']=='FULLHD60_READY_PHASE_B' and v['entry_id']==ENTRY and v['entry_status']==2 and v['conversion_profile_id']==PROFILE and v['stream_inspected'] is False and v['full_acceptance'] is False,'LONG_READY_SCHEMA')
 need(type(v['ready_polls']) is int and v['ready_polls']>=1 and type(v['ready_wait_seconds']) in (int,float) and 0<=v['ready_wait_seconds']<=READY_BUDGET+30,'LONG_READY_SCHEMA') # budget + one bounded API call
 need(v['duration_ms'] is None or type(v['duration_ms']) is int,'LONG_READY_SCHEMA')
 need(type(v['flavors']) is list and 1<=len(v['flavors'])<=32 and all(type(r) is dict and set(r)==FLAVOR_KEYS for r in v['flavors']),'LONG_READY_SCHEMA')
 for r in v['flavors']:
  need(type(r['id']) is str and ASSET.fullmatch(r['id']) is not None and type(r['isOriginal']) is bool and type(r['flavorParamsId']) is int and r['flavorParamsId'] in PROFILE_PARAMS and type(r['status']) is int,'LONG_READY_SCHEMA')
  need(all(r[k] is None or type(r[k]) is int for k in ('width','height','bitrate','size_API','version')) and (r['frameRate'] is None or type(r['frameRate']) is float),'LONG_READY_SCHEMA')
  need(all(r[k] is None or type(r[k]) is str and (r[k]=='OTHER' or TOKEN.fullmatch(r[k])) for k in ('videoCodecId','containerFormat')),'LONG_READY_SCHEMA')
 need(type(v['original_flavor_id']) is str and sum(r['isOriginal'] for r in v['flavors'])==1 and type(v['ready_flavor_params']) is list and type(v['not_ready_flavor_count']) is int,'LONG_READY_SCHEMA')
 need(type(v['delivered_1080p60_flavor_present']) is bool and v['stored_original_sha256_match'] in (True,False),'LONG_READY_SCHEMA')
 ids=[r['id'] for r in v['flavors']];originals=[r for r in v['flavors'] if r['isOriginal']]
 need(len(set(ids))==len(ids) and len(originals)==1 and originals[0]['id']==v['original_flavor_id'] and originals[0]['flavorParamsId']==0,'LONG_READY_SCHEMA')
 need({k:v[k] for k in ('ready_flavor_params','not_ready_flavor_count','delivered_1080p60_flavor_present')}==derived(v['flavors']),'LONG_READY_SCHEMA')
 return dict(v)

"""Fixed read-only private backup comparison after an ambiguous native split.
No application bootstrap, API, save, rollback or recovery mutation.
"""
import hashlib,importlib.util,json,os,re,stat
from pathlib import Path
STATE=Path('/var/lib/kaltura-baseline-delivery-split-r1')
TRANSPORT_PIN='9735aad64f31a3329de5844f9061da9f18f12e1b34787971d9ee360872443776'
COLUMNS=('id','type','created_at','updated_at','partner_id','name','system_name','description','url','host_name','is_default','parent_id','recognizer','tokenizer','status','streamer_type','media_protocols','custom_data','priority')
SELECT=','.join("IF("+c+" IS NULL,'N',CONCAT('H',HEX(CAST("+c+" AS BINARY))))" for c in COLUMNS)
SQL="SET SESSION max_statement_time=3;\nSTART TRANSACTION READ ONLY;\nSELECT 'IDENTITY',@@hostname,@@socket,@@datadir,CURRENT_USER(),DATABASE();\nSELECT 'ROW',"+SELECT+" FROM delivery_profile WHERE id=1001 OR (partner_id=0 AND type=61 AND is_default=1) ORDER BY id LIMIT 4;\nCOMMIT;\n"
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('RECOVERY_OBSERVATION_REJECTED')
def object_pairs(pairs):
 d={}
 for k,v in pairs:need(k not in d);d[k]=v
 return d
def validate_before(v):
 need(type(v) is dict and set(v)=={'schema','row'} and type(v['schema']) is int and v['schema']==1)
 r=v['row'];need(type(r) is dict and tuple(r)==COLUMNS and all(x is None or type(x) is str for x in r.values()))
 expected={'id':'1001','type':'61','partner_id':'0','url':'192.168.56.74:88/hls','host_name':'192.168.56.74','is_default':'1','parent_id':'0','recognizer':None,'tokenizer':None,'status':'0','streamer_type':'applehttp','media_protocols':None,'custom_data':None,'priority':'0'}
 need(all(r[k]==x for k,x in expected.items()));return r
def backup():
 for p in (Path('/'),Path('/var'),Path('/var/lib'),STATE):
  s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and not s.st_mode&0o022 and not os.listxattr(p))
 need(stat.S_IMODE(STATE.lstat().st_mode)==0o700)
 p=STATE/'before.json';fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:
  s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and s.st_size<=65536 and not os.listxattr(fd));raw=os.read(fd,65537);need(len(raw)==s.st_size)
 finally:os.close(fd)
 return validate_before(json.loads(raw,object_pairs_hook=object_pairs))
def decode_row(row):
 need(type(row) is list and len(row)==len(COLUMNS));out={}
 for key,value in zip(COLUMNS,row):
  if value=='N':out[key]=None;continue
  need(type(value) is str and re.fullmatch('H(?:[0-9A-F]{2}){0,8192}',value) is not None)
  try:out[key]=bytes.fromhex(value[1:]).decode('utf-8')
  except UnicodeError:raise Rejected('RECOVERY_OBSERVATION_REJECTED') from None
 return out
def expected_delta(before,after,new):
 expected=dict(before);expected['media_protocols']='https' if new else 'http'
 if new:expected['id']=after['id'];expected['url']='192.168.56.74:8444/hls'
 for key in COLUMNS:
  if key=='updated_at' or new and key=='created_at':
   if type(after[key]) is not str or re.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',after[key]) is None:return False
  elif after[key]!=expected[key]:return False
 return True
def compare(raw,before,identity):
 need(type(raw) is bytes and len(raw)<=32768)
 try:lines=[v.split('\t') for v in raw.decode('ascii').splitlines()]
 except UnicodeError:raise Rejected('RECOVERY_OBSERVATION_REJECTED') from None
 need(lines and lines[0][0]=='IDENTITY');identity([lines[0][1:]])
 need(1<=len(lines)-1<=3 and all(v[0]=='ROW' for v in lines[1:]))
 rows=[decode_row(v[1:]) for v in lines[1:]];ids=[]
 for r in rows:need(type(r['id']) is str and re.fullmatch('[1-9][0-9]{0,9}',r['id']) is not None);ids.append(int(r['id']))
 need(len(set(ids))==len(ids) and ids.count(1001)==1)
 original=rows[ids.index(1001)]
 relation='EXACT_BACKUP' if original==before else 'EXPECTED_HTTP_DELTA' if expected_delta(before,original,False) else 'OTHER_DRIFT'
 candidates=[r for r in rows if r['id']!='1001'];matching=[int(r['id']) for r in candidates if expected_delta(before,r,True)]
 return {'status':'READ_ONLY_SPLIT_RECOVERY_OBSERVED','original_profile_id':1001,'original_relation':relation,'candidate_rows':len(candidates),'matching_https_clone_ids':matching,'unexpected_candidate_rows':len(candidates)-len(matching),'candidate_scope':'GLOBAL_TYPE61_DEFAULTS_ONLY','sql_select_count':3,'db_identity_verified':True,'private_before_compared':True,'transaction_rollback_proven':False,'cache_state_verified':False,'recovery_performed':False,'retry_authorized':False,'full_acceptance':False}
def transport():
 p=Path(__file__).with_name('profile_socket.py');s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and s.st_nlink==1 and not s.st_mode&0o022 and s.st_size<=32768 and hashlib.sha256(p.read_bytes()).hexdigest()==TRANSPORT_PIN)
 spec=importlib.util.spec_from_file_location('recovery_socket',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.SQL=SQL;m.PINS={'alpha/lib/model/om/BaseDeliveryProfilePeer.php':'9805a9bf1c4d0fe721ff90673ec848b9732722f8e5f6df8e3a4bf44d928f75e0','alpha/apps/kaltura/lib/db/KalturaPDO.php':'97b756bed876d42da87f6a023b6ecf7af7c2b8454bb382da56ba9c54acae848d'};return m
def main():
 phase='TARGET_SOURCE'
 try:
  m=transport();m.guard();phase='PRIVATE_BACKUP';before=backup();phase='PRIVATE_OPTION';password=m.secret_read();phase='DB_IDENTITY';first=m.query(password,True).decode('ascii').splitlines();need(len(first)==1 and first[0].startswith('IDENTITY\t'));m.identity([first[0].split('\t')[1:]])
  phase='READ_ONLY_COMPARISON';result=compare(m.query(password),before,m.identity)
 except Exception:result={'status':'RECOVERY_OBSERVATION_FAILED_CLOSED','failure_stage':phase,'recovery_performed':False,'retry_authorized':False,'full_acceptance':False}
 print(json.dumps(result,sort_keys=True));return 0 if result['status']=='READ_ONLY_SPLIT_RECOVERY_OBSERVED' else 2
if __name__=='__main__':raise SystemExit(main())

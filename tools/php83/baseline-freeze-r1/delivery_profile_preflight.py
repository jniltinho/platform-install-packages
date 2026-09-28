"""Read-only selected profile 1001 shape; no opaque values, API or mutation."""
import hashlib, importlib.util, json, re, stat
from pathlib import Path
TRANSPORT_PIN='9735aad64f31a3329de5844f9061da9f18f12e1b34787971d9ee360872443776'
PINS={
 'alpha/lib/model/om/BaseDeliveryProfilePeer.php':'9805a9bf1c4d0fe721ff90673ec848b9732722f8e5f6df8e3a4bf44d928f75e0',
 'alpha/lib/model/map/DeliveryProfileTableMap.php':'75a6eb94c163600443111e405ba38fb666d81feb0cec35fea7cab6f31eaf2669',
}
SQL="""SET SESSION max_statement_time=3;
START TRANSACTION READ ONLY;
SELECT 'IDENTITY',@@hostname,@@socket,@@datadir,CURRENT_USER(),DATABASE();
SELECT 'PROFILE',id,partner_id,type,status,is_default,COALESCE(parent_id,'NULL'),COALESCE(priority,'NULL'),streamer_type,media_protocols IS NULL,url='192.168.56.74:88/hls',host_name IS NULL,host_name='192.168.56.74',recognizer IS NULL,COALESCE(OCTET_LENGTH(recognizer),0),tokenizer IS NULL,COALESCE(OCTET_LENGTH(tokenizer),0),custom_data IS NULL,COALESCE(OCTET_LENGTH(custom_data),0) FROM delivery_profile WHERE id=1001 LIMIT 2;
COMMIT;
"""
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('DELIVERY_PREFLIGHT_REJECTED')
def integer(value,nullable=False):
 if nullable and value=='NULL':return None
 need(type(value) is str and re.fullmatch(r'-?(0|[1-9][0-9]{0,9})',value) is not None)
 result=int(value);need(-2147483648<=result<=2147483647);return result
def flag(value):
 need(value in ('0','1'));return value=='1'
def parse(raw,identity):
 need(type(raw) is bytes and len(raw)<=32768)
 try:rows=[line.split('\t') for line in raw.decode('ascii').splitlines()]
 except UnicodeError:raise Rejected('DELIVERY_PREFLIGHT_REJECTED') from None
 need(len(rows)==2 and rows[0][0]=='IDENTITY' and rows[1][0]=='PROFILE');identity([rows[0][1:]])
 r=rows[1][1:];need(len(r)==18)
 need(r[:5]==['1001','0','61','0','1'] and r[7]=='applehttp')
 parent=integer(r[5],True);priority=integer(r[6],True)
 protocols_null=flag(r[8]);url_exact=flag(r[9]);host_null=flag(r[10])
 need(r[11] in ('NULL','0','1') and (r[11]=='NULL')==host_null)
 opaque={}
 for name,offset in (('recognizer',12),('tokenizer',14),('custom_data',16)):
  null=flag(r[offset]);length=integer(r[offset+1]);need(0<=length<=1048576 and (not null or length==0))
  opaque[name]={'is_null':null,'byte_length':length}
 return {'schema':1,'status':'READ_ONLY_DELIVERY_PROFILE_PREFLIGHT','profile_id':1001,'partner_id':0,'profile_type':61,'profile_status':0,'is_default':True,'parent_id':parent,'priority':priority,'streamer_type':'applehttp','media_protocols_null':protocols_null,'original_http_url_exact':url_exact,'host_name_null':host_null,'host_name_owned':None if host_null else flag(r[11]),'opaque_fields':opaque,'sql_select_count':3,'db_identity_verified':True,'opaque_semantics_verified':False,'whole_row_backup_created':False,'cache_invalidation_verified':False,'mutation_ready':False,'configuration_changed':False,'full_acceptance':False}
def load_transport():
 p=Path(__file__).with_name('profile_socket.py');s=p.lstat()
 need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and s.st_nlink==1 and not s.st_mode&0o022 and s.st_size<=32768)
 need(hashlib.sha256(p.read_bytes()).hexdigest()==TRANSPORT_PIN)
 spec=importlib.util.spec_from_file_location('delivery_preflight_socket',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 module.PINS=PINS.copy();module.SQL=SQL;return module
def main():
 phase='SOURCE_TRANSPORT'
 try:
  transport=load_transport();phase='TARGET_SOURCE_GUARD';transport.guard()
  phase='PRIVATE_OPTION_READ';password=transport.secret_read();phase='DB_IDENTITY'
  first=transport.query(password,True).decode('ascii').splitlines();need(len(first)==1 and first[0].startswith('IDENTITY\t'));transport.identity([first[0].split('\t')[1:]])
  phase='READ_ONLY_PROFILE_SHAPE';raw=transport.query(password);phase='CLOSED_PROJECTION';result=parse(raw,transport.identity)
 except Exception:result={'status':'FAILED_CLOSED','failure_stage':phase,'mutation_ready':False,'full_acceptance':False}
 print(json.dumps(result,sort_keys=True));return 0 if result['status']=='READ_ONLY_DELIVERY_PROFILE_PREFLIGHT' else 2
if __name__=='__main__':raise SystemExit(main())

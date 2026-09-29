"""Read-only inventory of flavor params (partners 0/102) and partner 102 conversion profiles, to decide how a lab
profile can deliver 1080p60 and 360p25. Reuses the pinned profile_socket transport (READ ONLY transaction, DB
identity check, guest-side password). Exports configuration fields only (no secrets); maxFrameRate is
extracted from custom_data by the database, the rest of custom_data is never read. No API, no mutation."""
import hashlib,json,re,sys
from pathlib import Path
import thumb_ks_reason as base
SQL=r"""SET SESSION max_statement_time=5;
START TRANSACTION READ ONLY;
SELECT 'IDENTITY',@@hostname,@@socket,@@datadir,CURRENT_USER(),DATABASE();
SELECT 'FP',id,partner_id,IFNULL(system_name,''),IFNULL(tags,''),width,height,frame_rate,IFNULL(video_codec,''),video_bitrate,is_default,type,IFNULL(REGEXP_SUBSTR(custom_data,'maxFrameRate";[a-z]:[0-9.:"]+'),'') FROM flavor_params WHERE partner_id IN (0,102) AND deleted_at IS NULL AND type IN (1,2) ORDER BY id LIMIT 200;
SELECT 'CP',id,partner_id,IFNULL(system_name,''),status,type FROM conversion_profile_2 WHERE partner_id=102 AND deleted_at IS NULL ORDER BY id LIMIT 50;
SELECT 'FPCP',conversion_profile_id,flavor_params_id FROM flavor_params_conversion_profile WHERE conversion_profile_id IN (SELECT id FROM conversion_profile_2 WHERE partner_id=102 AND deleted_at IS NULL) ORDER BY conversion_profile_id,flavor_params_id LIMIT 500;
SELECT 'SHORT',a.flavor_params_id,a.width,a.height,a.frame_rate,a.status FROM flavor_asset a WHERE a.entry_id='0_wzmt2sfy' AND a.partner_id=102 AND a.type=1 ORDER BY a.flavor_params_id LIMIT 32;
COMMIT;
"""
SAFE=re.compile(r'[\x20-\x7e]{0,200}')
def parse(raw,identity):
 base.need(type(raw) is bytes and len(raw)<=262144);groups={k:[] for k in ('IDENTITY','FP','CP','FPCP','SHORT')}
 for line in raw.decode('ascii').splitlines():
  row=line.split('\t');base.need(row[0] in groups and (row[0]=='IDENTITY' or all(SAFE.fullmatch(v) for v in row[1:])));groups[row[0]].append(row[1:])
 identity(groups['IDENTITY'])
 keys={'FP':('id','partner_id','system_name','tags','width','height','frame_rate','video_codec','video_bitrate','is_default','type','max_frame_rate_raw'),'CP':('id','partner_id','system_name','status','type'),'FPCP':('profile','flavor_params_id'),'SHORT':('flavor_params_id','width','height','frame_rate','status')}
 out={'status':'READ_ONLY_FLAVOR_PARAMS_OBSERVED','db_identity_verified':True}
 for k,names in keys.items():
  base.need(all(len(r)==len(names) for r in groups[k]));out[k.lower()]=[dict(zip(names,r)) for r in groups[k]]
 return out
def guest_code():
 code=base.guest_code().replace('def parse(raw,identity):','def reason_parse(raw,identity):',1)
 return code.replace('\nSQL='+repr(base.SQL)+'\n','\nSQL='+repr(SQL)+'\n',1)
if __name__=='__main__':
 import inspect
 # Replace the reason parser with this module's parser; keep the pinned transport, guard and source pins.
 code=guest_code();old=inspect.getsource(base.parse).replace('def parse(raw,identity):','def reason_parse(raw,identity):',1)
 base.need(code.count(old)==1 and code.count('\nSQL='+repr(SQL)+'\n')==1)
 code=code.replace(old,'SAFE=re.compile('+repr(SAFE.pattern)+')\n'+inspect.getsource(parse).replace('def parse(raw,identity):','def reason_parse(raw,identity):',1).replace('base.need','need'),1)
 import run_thumbnail_r3 as r
 r.pinned(r.CONFIG,'15f687f3db61c013654442404e916b1b2ad7f0d1835e1f30ef10ca80355ceef3',True);r.pinned(r.KEYS,'6b6a9652a16acd478a01b508962452556138ce3a3f0c2cc4584baab58f00c4c6',True)
 rc,info,_=r.bounded(['VBoxManage','showvminfo',r.UUID,'--machinereadable']);base.need(rc==0);r.host_guard(info.decode())
 rc,out,err=r.remote(code.replace("'READ_ONLY_KS_REASON_OBSERVED'","'READ_ONLY_FLAVOR_PARAMS_OBSERVED'"),60)
 base.need(rc==0 and len(out)<=262144);v=json.loads(out);print(json.dumps(dict(v,guest_stderr_bytes=err),indent=1,sort_keys=True))
 sys.exit(0 if v.get('status')=='READ_ONLY_FLAVOR_PARAMS_OBSERVED' else 2)

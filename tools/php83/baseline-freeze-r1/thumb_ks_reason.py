"""Read-only: why does thumbAsset.getUrl embed a download KS for 0_wzmt2sfy?
asset::isKsNeededForDownload() is true if partner 102/0 has FEATURE_ENTITLEMENT, or entry::isSecuredEntry()
(moderation pending/rejected, future start_date, end_date within 24h, no access control, or ACL with rules).
Reuses the pinned profile_socket transport (READ ONLY transaction, DB identity check, guest-side password).
Exports counts/booleans only. No API, bootstrap, GET, staging or mutation."""
import hashlib,json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
TRANSPORT_PIN='9735aad64f31a3329de5844f9061da9f18f12e1b34787971d9ee360872443776'
SOURCE_PINS={'alpha/lib/model/entry.php':'b677a171f5cc51f6a692eab774938b1a582e21e177ec40ff36aaf4277886dfb5','alpha/lib/model/asset.php':'34f9e81972369706ea01f5e8a3ba19cd6999d2f6804f25ccdf89cac0bf74933d','alpha/lib/model/PermissionPeer.php':'95f41a27363ab23d76a2f52259f9a325139da1174fdefd17500479b2c1a2ad16','alpha/lib/model/accessControl.php':'9934c0263e43c89e7e11e38b2530735d2da8550664f02f77d51b7024e57bcacd','alpha/lib/model/thumbAsset.php':'478e479282058b84e1f7c1368d5d94d9fb1f00f5c558052496690587b253d24b'}
E="e.id='0_wzmt2sfy' AND e.partner_id=102"
SQL=f"""SET SESSION max_statement_time=3;
START TRANSACTION READ ONLY;
SELECT 'IDENTITY',@@hostname,@@socket,@@datadir,CURRENT_USER(),DATABASE();
SELECT 'ENTRY',COUNT(*),IFNULL(SUM(e.moderation_status IN (1,3)),0),IFNULL(SUM(e.start_date IS NOT NULL AND e.start_date>=NOW()),0),IFNULL(SUM(e.end_date IS NOT NULL AND e.end_date<=NOW()+INTERVAL 1 DAY),0),IFNULL(SUM(e.access_control_id IS NULL),0) FROM entry e WHERE {E};
SELECT 'ACL',COUNT(*),IFNULL(SUM(a.deleted_at IS NULL),0),IFNULL(SUM(a.rules IS NOT NULL AND a.rules<>'' AND a.rules<>'a:0:{{}}'),0),IFNULL(SUM(a.partner_id=102),0) FROM entry e JOIN access_control a ON a.id=e.access_control_id WHERE {E};
SELECT 'PERM',partner_id,status,COUNT(*) FROM permission WHERE name='FEATURE_ENTITLEMENT' AND partner_id IN (0,102) GROUP BY partner_id,status ORDER BY partner_id,status LIMIT 8;
COMMIT;
"""
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('KS_REASON_REJECTED')
def ints(row,n):
 need(len(row)==n and all(re.fullmatch('-?[0-9]{1,10}',v) is not None for v in row));return [int(v) for v in row]
def parse(raw,identity):
 need(type(raw) is bytes and len(raw)<=32768);groups={k:[] for k in ('IDENTITY','ENTRY','ACL','PERM')}
 for line in raw.decode('ascii').splitlines():
  row=line.split('\t');need(row[0] in groups);groups[row[0]].append(row[1:])
 identity(groups['IDENTITY'])
 need(len(groups['ENTRY'])==1 and len(groups['ACL'])==1 and len(groups['PERM'])<=8)
 n,moderation,future_start,ending,no_acl=ints(groups['ENTRY'][0],5);need(n==1 and all(v in (0,1) for v in (moderation,future_start,ending,no_acl)))
 acl_rows,acl_live,acl_rules,acl_owned=ints(groups['ACL'][0],4);need(acl_rows in (0,1) and all(0<=v<=acl_rows for v in (acl_live,acl_rules,acl_owned)))
 perms=[dict(zip(('partner_id','status','rows'),ints(r,3))) for r in groups['PERM']];need(all(p['partner_id'] in (0,102) and p['rows']>=1 for p in perms))
 entitlement_active=any(p['status']==1 for p in perms)
 secured=bool(moderation or future_start or ending or no_acl or not acl_live or acl_rules)
 return {'status':'READ_ONLY_KS_REASON_OBSERVED','entry_rows':n,'moderation_pending_or_rejected':bool(moderation),'start_date_future':bool(future_start),'end_date_within_24h':bool(ending),
  'access_control_id_null':bool(no_acl),'access_control_rows':acl_rows,'access_control_live':bool(acl_live),'access_control_rules_nonempty':bool(acl_rules),'access_control_owned_by_102':bool(acl_owned),
  'feature_entitlement_rows':perms,'feature_entitlement_active_status1':entitlement_active,'derived_secured_entry':secured,'derived_ks_needed':secured or entitlement_active,
  'select_count':4,'db_identity_verified':True,'compressed_rules_decoded':False,'full_acceptance':False}
GUEST_TAIL='''
PINS=%r
def run():
 phase='TARGET_SOURCE_GUARD'
 try:
  guard();phase='PRIVATE_OPTION_READ';password=secret_read();phase='DB_IDENTITY';first=query(password,True).decode('ascii').splitlines();need(len(first)==1 and first[0].startswith('IDENTITY\\t'));identity([first[0].split('\\t')[1:]])
  phase='BOUNDED_READ_ONLY_SQL';raw=query(password);phase='PUBLIC_PROJECTION';out=reason_parse(raw,identity)
 except Exception:out={'status':'FAILED_CLOSED','failure_stage':phase,'full_acceptance':False}
 print(json.dumps(out,sort_keys=True))
run()
'''
def guest_code():
 raw=(HERE/'profile_socket.py').read_bytes();need(hashlib.sha256(raw).hexdigest()==TRANSPORT_PIN);s=raw.decode()
 tail="if __name__=='__main__':raise SystemExit(main())";need(s.count(tail)==1);s=s.replace(tail,'')
 import inspect
 return s+'\nimport re\nSQL='+repr(SQL)+'\nclass KSRejected(ValueError):pass\n'+inspect.getsource(ints).replace('Rejected','KSRejected')+inspect.getsource(parse)+GUEST_TAIL%SOURCE_PINS
def main():
 import run_thumbnail_r3 as r
 r.pinned(r.CONFIG,'15f687f3db61c013654442404e916b1b2ad7f0d1835e1f30ef10ca80355ceef3',True);r.pinned(r.KEYS,'6b6a9652a16acd478a01b508962452556138ce3a3f0c2cc4584baab58f00c4c6',True)
 rc,raw,_=r.bounded(['VBoxManage','showvminfo',r.UUID,'--machinereadable']);need(rc==0);r.host_guard(raw.decode())
 code=guest_code().replace('def parse(raw,identity):','def reason_parse(raw,identity):',1)
 rc,out,err=r.remote(code,60);need(rc==0 and len(out)<=8192)
 v=json.loads(out);need(type(v) is dict and v.get('status') in ('READ_ONLY_KS_REASON_OBSERVED','FAILED_CLOSED'))
 print(json.dumps(dict(v,guest_stderr_bytes=err),sort_keys=True));return 0 if v['status']=='READ_ONLY_KS_REASON_OBSERVED' else 2
if __name__=='__main__':
 try:raise SystemExit(main())
 except Rejected:print('{"status":"RUNNER_REJECTED"}');raise SystemExit(2)

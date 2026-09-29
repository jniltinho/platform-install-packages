"""Read-only existing lab74 media observation after finite privacy gates; no upload."""
from urllib.parse import urlsplit
import ast,hashlib,importlib.util,json,os,stat,re,secrets,socket,subprocess,sys,time
from pathlib import Path
NEW_HERE=Path(__file__).resolve().parent
HERE=Path('/home/vagrant/privacy-media-overlay-v3/tools/php83/baseline-rehearsal/privacy/media-overlay-v3')
EXPECTED_OVERLAY_MANIFEST='cf16bc5c49acbe5863934ba737c72e2b65878c84048389354e79163afeca0cb8'
JOURNAL_STATUS="COMPLETE_FINITE_JOURNAL_WINDOW"
FIXED_FAILURE_CODES=['THUMB_API', 'THUMB_LIST', 'THUMB_ROW', 'THUMB_SELECTION', 'THUMB_URL', 'THUMB_ORIGIN', 'THUMB_CREDENTIAL', 'THUMB_ROUTE', 'THUMB_ENROLLMENT', 'THUMB_RESPONSE', 'THUMB_IMAGE', 'THUMB_SCHEMA', 'THUMB_DECODE_INPUT', 'THUMB_DECODE_BINARY', 'THUMB_DECODE_METADATA', 'THUMB_DECODE_FAILED', 'THUMB_PIN', 'THUMB_SOURCE_PIN']+['HLS_CONTEXT_REJECTED', 'HLS_PROFILE_JOIN', 'HLS_ACCESS_ACTIONS', 'HLS_MASTER_REJECTED', 'HLS_MEDIA_REJECTED', 'HLS_REFERENCE_ENROLLMENT', 'HLS_MASTER_CARDINALITY', 'NESTED_URL_SHAPE', 'NESTED_CREDENTIAL', 'NESTED_ORIGIN', 'NESTED_ROUTE_PREFIX', 'NESTED_ROUTE_KEY', 'NESTED_ROUTE_VALUE', 'NESTED_ROUTE_DUPLICATE', 'SEGMENT_MANIFEST_SHAPE', 'SEGMENT_MANIFEST_TAG', 'SEGMENT_MANIFEST_ORDER', 'SEGMENT_CARDINALITY', 'SEGMENT_DURATION', 'SEGMENT_CREDENTIAL', 'SEGMENT_ROUTE', 'SEGMENT_LIMIT', 'SEGMENT_FRAMING', 'SEGMENT_RESPONSE', 'HLS_DECODE_SHAPE', 'HLS_DECODE_BINARY', 'HLS_DECODE_METADATA', 'HLS_DECODE_FAILED', 'HLS_DELIVERY_SCHEMA']+['COMMON_AUDIT_SCHEMA', 'COMMON_AUDIT_POSITIVE', 'COMMON_AUDIT_UNSAFE_DRIFT', 'COMMON_AUDIT_CONVERGENCE_EXHAUSTED', 'COMMON_AUDIT_DEADLINE']+['HLS_PIN', 'HLS_SOURCE_PIN', 'HLS_CONTEXT_REJECTED', 'HLS_PROFILE_JOIN', 'HLS_ACCESS_ACTIONS', 'HLS_MASTER_REJECTED', 'HLS_MEDIA_REJECTED', 'HLS_REFERENCE_ENROLLMENT', 'HLS_MASTER_CARDINALITY', 'NESTED_URL_SHAPE', 'NESTED_CREDENTIAL', 'NESTED_ORIGIN', 'NESTED_ROUTE_PREFIX', 'NESTED_ROUTE_KEY', 'NESTED_ROUTE_VALUE', 'NESTED_ROUTE_DUPLICATE']+['SPLIT_RECEIPT','PROFILE_SELECTION_ID','CONTEXT_REQUEST_SHAPE','CONTEXT_RESPONSE_REJECTED','CONTEXT_SELECTION_CARDINALITY','CONTEXT_SELECTION_FIELDS','PROFILE_SELECTION_MISMATCH','SELECTED_ASSET', 'SELECTED_SIZE', 'SELECTED_TAGS','CONTEXT_CALL', 'CONTEXT_TYPE', 'URL_ENROLLMENT_INCOMPLETE', 'RESPONSE_COVERAGE_INCOMPLETE', 'SOURCE_TYPE', 'SOURCE_FIELDS', 'CONTEXT_ARRAY', 'CONTEXT_PIN','AUDIT_CONVERGENCE_DEADLINE', 'AUDIT_CONVERGENCE_EXHAUSTED', 'AUDIT_CONVERGENCE_PIN','SOURCE_ROUTE_SHAPE', 'SOURCE_ROUTE_CREDENTIAL', 'SOURCE_ROUTE_ENCODING', 'SOURCE_ROUTE_ORIGIN', 'SOURCE_ROUTE_AUTH', 'SOURCE_ROUTE_ORDER', 'SOURCE_ROUTE_EMPTY_SEGMENT', 'SOURCE_ROUTE_UNKNOWN_KEY', 'SOURCE_ROUTE_DUPLICATE_KEY', 'SOURCE_ROUTE_EXPECTED_VALUE','ROUTE_DESCRIPTOR_PIN', 'ROUTE_SOURCE_PIN', 'ROUTE_NAME_ROW', 'ROUTE_FILENAME_INPUT', 'ROUTE_URL_SHAPE', 'ROUTE_PATTERN_LIMIT', 'ROUTE_RESPONSE_TYPE','DIRECT_STORAGE_ROOT', 'DIRECT_STORAGE_PATH', 'DIRECT_STORAGE_JOIN', 'DIRECT_URL_SHAPE', 'DIRECT_CREDENTIAL_SHAPE', 'DIRECT_PATTERN_LIMIT', 'DIRECT_URL_CREDENTIAL', 'DIRECT_URL_AUTH', 'DIRECT_URL_MISMATCH', 'DIRECT_SOURCE_PIN', 'PROVENANCE_PIN', 'PROVENANCE_LIMIT', 'DIRECT_ROW','DELIVERY_PIN', 'DELIVERY_DEADLINE', 'DELIVERY_REJECTED', 'URL_SHAPE', 'URL_PATTERN_LIMIT', 'URL_CREDENTIAL', 'URL_AUTH_SHAPE', 'DELIVERY_URL', 'DELIVERY_ORIGIN', 'DELIVERY_TRANSPORT', 'DELIVERY_RESPONSE', 'DELIVERY_STATUS', 'DELIVERY_BODY_LIMIT', 'DELIVERY_HEADERS', 'DELIVERY_HEADER_NAME', 'DELIVERY_DUPLICATE_HEADER', 'DELIVERY_ENCODING_REDIRECT', 'DELIVERY_LENGTH', 'DELIVERY_SOURCE_HASH', 'DELIVERY_CONTENT_RANGE', 'DELIVERY_RANGE_BYTES','METADATA_API_CALL_FAILED', 'METADATA_RESPONSE_TYPE', 'METADATA_TOTAL', 'METADATA_CARDINALITY', 'METADATA_ASSET_TYPE', 'METADATA_ASSET_ID', 'METADATA_DUPLICATE', 'METADATA_PARTNER', 'METADATA_OWNERSHIP', 'METADATA_STATUS', 'METADATA_ORIGINAL_TYPE', 'METADATA_VERSION', 'METADATA_PARAMS', 'METADATA_SIZE', 'METADATA_EXTENSION', 'METADATA_SOURCE_BINDING','METADATA_PIN','METADATA_RESPONSE_REJECTED','TLS_LOG_ADAPTER_PIN','TLS_CA_PIN','ADMIN_ESCALATION_CONTROL', 'CLI_VERSION', 'COMMON_AUDIT_END_DRIFT', 'CONFIG_DRIFT', 'DEPENDENCY_PIN', 'DUPLICATE_NETWORK_PROPERTY', 'ENTRY_DB_BINDING', 'EXACT_PRIOR_PARTNER', 'FILES_BOOT_CHANGED', 'FILES_BYTE_LIMIT', 'FILES_COMPLETE_FINITE_FILE_WINDOW', 'FILES_COMPLETE_FINITE_JOURNAL_WINDOW', 'FILES_CURSOR_CONTINUITY', 'FILES_DEADLINE', 'FILES_DUPLICATE_JSON_FIELD', 'FILES_EMPTY_JOURNAL', 'FILES_END_CURSOR_MISSING', 'FILES_IDENTITY_CHANGED', 'FILES_INVALID_JSON', 'FILES_INVENTORY', 'FILES_INVENTORY_CHANGED', 'FILES_JOURNAL_PROCESS', 'FILES_JOURNAL_STDERR', 'FILES_JOURNAL_TIMEOUT', 'FILES_LATEST_IDENTITY', 'FILES_LIMITS', 'FILES_OBSERVED_CURSOR_MISSING', 'FILES_OBSERVED_TAIL_MISSING', 'FILES_PATTERNS', 'FILES_RECORD_IDENTITY', 'FILES_RECORD_LIMIT', 'FILES_REWRITTEN', 'FILES_SCAN_FAILED', 'FILES_SHORT_READ', 'FILES_SNAPSHOT_FAILED', 'FILES_START', 'FILES_START_CURSOR_MISSING', 'FILES_SYMLINK', 'FILES_TAIL_REGRESSED', 'FILES_TRUNCATED', 'FILES_UNDRAINED_JOURNAL_TAIL', 'FILES_UNDRAINED_TAIL', 'FILES_UNSAFE_FILE', 'FILES_UNSAFE_PATH', 'FILES_UNSUPPORTED_FIELD', 'FILES__BOOT_ID', 'FILES___CURSOR', 'FILE_TAIL_DURING_JOURNAL', 'FILE_WINDOW_INCOMPLETE', 'JOURNAL_BOOT_CHANGED', 'JOURNAL_BYTE_LIMIT', 'JOURNAL_COMPLETE_FINITE_FILE_WINDOW', 'JOURNAL_COMPLETE_FINITE_JOURNAL_WINDOW', 'JOURNAL_CURSOR_CONTINUITY', 'JOURNAL_DEADLINE', 'JOURNAL_DUPLICATE_JSON_FIELD', 'JOURNAL_EMPTY_JOURNAL', 'JOURNAL_END_CURSOR_MISSING', 'JOURNAL_IDENTITY_CHANGED', 'JOURNAL_INVALID_JSON', 'JOURNAL_INVENTORY', 'JOURNAL_INVENTORY_CHANGED', 'JOURNAL_JOURNAL_PROCESS', 'JOURNAL_JOURNAL_STDERR', 'JOURNAL_JOURNAL_TIMEOUT', 'JOURNAL_LATEST_IDENTITY', 'JOURNAL_LIMITS', 'JOURNAL_OBSERVED_CURSOR_MISSING', 'JOURNAL_OBSERVED_TAIL_MISSING', 'JOURNAL_PATTERNS', 'JOURNAL_RECORD_IDENTITY', 'JOURNAL_RECORD_LIMIT', 'JOURNAL_REWRITTEN', 'JOURNAL_SCAN_FAILED', 'JOURNAL_SHORT_READ', 'JOURNAL_SNAPSHOT_FAILED', 'JOURNAL_START', 'JOURNAL_START_CURSOR_MISSING', 'JOURNAL_STATUS', 'JOURNAL_SYMLINK', 'JOURNAL_TAIL_REGRESSED', 'JOURNAL_TRUNCATED', 'JOURNAL_UNDRAINED_JOURNAL_TAIL', 'JOURNAL_UNDRAINED_TAIL', 'JOURNAL_UNSAFE_FILE', 'JOURNAL_UNSAFE_PATH', 'JOURNAL_UNSUPPORTED_FIELD', 'JOURNAL_WINDOW_INCOMPLETE', 'JOURNAL__BOOT_ID', 'JOURNAL___CURSOR', 'LAB_IDENTITY', 'LAB_IP', 'LIST_IDENTITY', 'LOCAL_SOURCE_BINDING', 'MEDIA_SOURCE_PIN', 'NETWORK_POLICY', 'OBSERVATION_PIN', 'OBSERVED_PROFILE_SELECTION', 'ORIGINAL_ASSET_COUNT', 'OVERLAY_MANIFEST', 'OVERLAY_STAGE', 'OWNED_ASSET_ENTRY_BINDING', 'OWNED_ENTRY_BINDING', 'OWNED_LIST', 'OWNED_OBJECT_SHAPE', 'OWNED_PARTNER_BINDING', 'PATTERN_COUNT', 'PRIOR_ASSET_IDENTITY', 'PRIVATE_DIAGNOSTIC_PARENT', 'PRIVATE_MARKER_LOGGED', 'PRIVATE_SECRET_FORMAT', 'QUIET_WINDOW_NOT_ESTABLISHED', 'REHEARSAL_PIN', 'RUNTIME_PIN', 'SCAN_RESULT', 'SETTLE_PIN', 'SOURCE_AFTER', 'SOURCE_DRIFT', 'STORED_SOURCE_BYTES', 'SYNTHETIC_PARTNER_PROVENANCE', 'SYNTHETIC_PARTNER_STATE', 'UNIT', 'UNTIMED_ROUND_FAILED', 'USER_KS', 'VERSION_PROJECTION', 'WRONG_SECRET_CONTROL']
class Rejected(RuntimeError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def network_policy(raw):
 values={}
 for line in raw.splitlines():
  key,value=line.split('=',1);need(key not in values,'DUPLICATE_NETWORK_PROPERTY');values[key]=value
 need(values.get('NoNewPrivileges')=='yes','NETWORK_POLICY')
 need(set(values.get('IPAddressDeny','').split())=={'0.0.0.0/0','::/0'},'NETWORK_POLICY')
 need(set(values.get('IPAddressAllow','').split())=={'127.0.0.0/8','::1/128','192.168.56.74/32'},'NETWORK_POLICY')
def bind_tenant(value,partner):
 need(type(value) is dict,'OWNED_OBJECT_SHAPE')
 actual=value.get('partnerId')
 need(type(actual) in {int,str} and str(actual)==str(partner),'OWNED_PARTNER_BINDING')
def bind_entry(value,partner,entry_id=None):
 bind_tenant(value,partner)
 need(type(value.get('id')) is str and (entry_id is None or value['id']==entry_id),'OWNED_ENTRY_BINDING')
def bind_asset(value,partner,entry_id):
 bind_tenant(value,partner)
 need(type(value.get('entryId')) is str and value['entryId']==entry_id,'OWNED_ASSET_ENTRY_BINDING')
def allowed_codes(module):
 return {n.value for n in ast.walk(ast.parse(Path(module.__file__).read_bytes())) if isinstance(n,ast.Constant) and type(n.value) is str and re.fullmatch('[A-Z_]+',n.value)}
def scanner_code(error,allowed):
 code=str(error);return code if code in allowed else 'UNKNOWN_SCANNER_CODE'
def private_json(path,data):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as out:json.dump(data,out);out.flush();os.fsync(out.fileno())
def accepted(a,b):
 for row in [a,b]:
  need(type(row) is dict and type(row.get('counts')) is list and len(row['counts'])>=2,'SCAN_RESULT')
  need(all(type(v) is int and v==0 for v in row['counts']),'PRIVATE_MARKER_LOGGED')
 need(a.get('status')=='COMPLETE_FINITE_FILE_WINDOW' and type(a.get('uncovered_tail_bytes')) is int and a['uncovered_tail_bytes']==0,'FILE_WINDOW_INCOMPLETE')
 # Journal status is checked by its authoritative scanner; completion flag is supplied by adapter below.
 need(b.get('complete') is True,'JOURNAL_WINDOW_INCOMPLETE')
 return True
def main(unit,proof_pin):
 report={'status':'INCOMPLETE','phase':'preflight','baseline_label':'PUBLISHED_PHP74_WITH_APPROVED_PRIVACY_OVERLAY','benchmark_executed':False,'user_attempted':False,'upload_attempted':False,'universal_privacy':False}
 media_window=None;tracked_tokens=[];failure_stage='PREFLIGHT';secret=None;ks=None;canary=None
 def checkpoint():print(json.dumps(report if report.get('phase')=='done' or report.get('status')=='FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION' else {'status':'INCOMPLETE'},sort_keys=True),flush=True)
 try:
  need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline','LAB_IDENTITY')
  rows=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={a.get('local') for x in rows for a in x.get('addr_info',[])}
  need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'LAB_IP')
  need(re.fullmatch('baseline-freeze-[0-9a-f]{8}',unit) is not None,'UNIT')
  policy=subprocess.check_output(['systemctl','show',unit+'.service','-p','IPAddressDeny','-p','IPAddressAllow','-p','NoNewPrivileges'],timeout=10).decode()
  network_policy(policy)
  stage=Path('/home/vagrant/privacy-media-overlay-v3')
  frozen={'tools/php83/baseline-api/protocol.py': '4587eab6222c2cacc381b6ef100dc557f1afb814250dcc5ba92b3b2ee7eeca34', 'tools/php83/baseline-api/transport.py': '5a5896f22aeef0a8baf0ba3869b2cbfebcd655b94ab5671dc13580d1035edf20', 'tools/php83/baseline-protocol/deadline_transport.py': '330c7aedaa57c439af579b9fa9f262c1062bbd66014d3e4c0adbe9b8a6c1dbe2', 'tools/php83/baseline-protocol/guarded_http.py': '4cc44f15645ced42e1e156586a79a2795d38f929c6f812eb695e427ee7e47b59', 'tools/php83/baseline-rehearsal/privacy/append-window-v1/scan.py': '43189edbe0cfb9f4a0654b7b8425f8f4a876bf270a309f96309142a0ec5b34fc', 'tools/php83/baseline-rehearsal/privacy/journal-window-v1/scan.py': 'a390e2464c3df47b36ed0b2e19607887b908351d3e7245439e392646239ba5e8', 'tools/php83/baseline-rehearsal/privacy/media-overlay-v3/guest.py': '716786236935d53bbe513275b4cac71b4f9b42b67cf1615d50031d76789b6810', 'tools/php83/baseline-rehearsal/untimed_driver.py': 'b461835902bde19d3ec3ca555a88dac640176aa7318315d9cb4bee3d29df14b5'}
  for name,pin in frozen.items():
   p=stage/name;st=p.lstat();need(stat.S_ISREG(st.st_mode) and st.st_uid==0 and not st.st_mode&0o222 and hashlib.sha256(p.read_bytes()).hexdigest()==pin,'DEPENDENCY_PIN')
  obsraw=(NEW_HERE/'observation_v2.py').read_bytes();need(hashlib.sha256(obsraw).hexdigest()=='ec32386df1c745f5754ece19f3127f6da85415e644c8556e6c07666b2ea1abc5','OBSERVATION_PIN')
  obs=load('baseline_observation',NEW_HERE/'observation_v2.py')
  for name,pin in {'protocol_v2.py': '147d74b0a04779fd0819ebe210d8a1a6aea4af8fbc773683a278e540ce70d4b8', 'rehearsal.py': 'ccf78ba0b1d3c94f05f63fd2d87c351953022c149c0e75392b5c86be2c02bb70'}.items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'REHEARSAL_PIN')
  sys.path.insert(0,str(NEW_HERE))
  sys.path.insert(0,str(HERE.parents[1]))
  legacy=__import__('untimed_driver') # Importable by multiprocessing spawn children.
  need(hashlib.sha256((NEW_HERE/'privacy_logs_r2.py').read_bytes()).hexdigest()=='d67eb65900c3134c91efaf94b18ba482b59261c81b0084de0cea3bcd37d5246c','TLS_LOG_ADAPTER_PIN')
  tls_logs=load('baseline_tls_logs_r2',NEW_HERE/'privacy_logs_r2.py')
  need(hashlib.sha256((NEW_HERE/'privacy_media_tls.py').read_bytes()).hexdigest()=='24ea4beb525a9084e1a17667654a815cbdb1fc1d6a84188133454b4c5e0c19a0','TLS_LOG_ADAPTER_PIN')
  media_logs=load('baseline_media_tls_logs',NEW_HERE/'privacy_media_tls.py')
  need(hashlib.sha256((NEW_HERE/'delivery_context_pair_r2.py').read_bytes()).hexdigest()=='ecfbec3480ef22772e50717773277834125404bef681ec687ea39a6b38b0f385','CONTEXT_PIN')
  for name,pin in {'hls_context_proof.py': 'a2bf5ee4de39119ad4c0c2eb743bdb381e7550eb2d2dd80534dc28572644bdc5', 'hls_media8444.py': 'cc97c2b6fdd5fc49f01b98a6a9fe332189ee9309a7a795400c517d239ebc7381', 'hls_nested8444.py': 'fcbadbb8a86b84c6bea05880ce7dfe341188a63bceb1564d5d9239946b73cb3e', 'hls_playlist_bridge.py': '9f19a1e72e378e9867cda2a60f8823275de90948cc28564739886536f3b03e52', 'hls_response.py': 'a43fb5f9a0848cbf5fef5d7cf70423255a023f6f7b06d8a9d81da0508f93f62a', 'hls_source_r2.py': 'b1b4e5ed19d1589b84fb4e09bf4b98dd32d668e64b54ea69efde59bdf33d80bb', 'short_delivery443.py': '9aa829f6c1927eb493fa4f1f5d9c1584d6a8f93b253015912ce253ba24fb1e76', 'manifest_diagnostic.py': 'c270871ab2ccfdd1b848e2081470b165052e2bcd0dc4b2ccad6151e5c7fc0ce4', 'nested_descriptor.py': '8d912931a8f41e23bd068d8f5576250a8c19bef79fcf3b3a88e348c603a4a89f', 'media_get443.py': '7417ba4ca341f84626c7b0138ac4fbdf7103e89a0975b55be210e7047d95af30', 'media_get8444.py': '741712af0acb01c0cf5531cd5c474da34572b9725afcbf19223e5b35a815c064'}.items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'HLS_PIN')
  pair=load('hls_context_proof',NEW_HERE/'hls_context_proof.py')
  for name,pin in {'hls_segments.py': '5d8e38218b899dff4181caf3bc8febf5966989d3a61f77f29c15380fab4bee05', 'hls_decode.py': '2fda1a247b2d3cc284329224525e6afcb5593463bb3d685bafd0c83a6f69e72a', 'hls_delivery8444.py': 'cd805d0e83070fdac669d196a502e76ae83e134d88ba0ebad2c5f50896dbefa5', 'offline_decode.py': '8940b878a572b968969acdc66090184568169dadff2713e51dcf64126ca1cae4'}.items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'HLS_PIN')
  for name,pin in {'hls_decode_r2.py': '9bb3ad909ca3225b76eed3f42adb58b662517399ad4561fca3d03654dc1fb3fd', 'hls_delivery8444_r2.py': 'fec502c37cc418de0dc7167855f98c822d5b3bc3db86d4033fb30b87d7640ada', 'decode_diagnostic.py': 'e6c913791e8176df8883e85cde449111d6e5aee7c9d55ed8a3df2581b8e9fc01'}.items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'HLS_PIN')
  for name,pin in {'decode_diagnostic_r3.py': '0aa4ce20f348c43d586d60bc8e0582f31091cb5060ca9e48db86afff10ad92d8', 'hls_decode_r3.py': '5fde3ab2d4d3daafa910f32148870f53b392dbf4d856063d7fe4487d43aa8733', 'hls_delivery8444_r3.py': 'e93dba292d3e574828d215c13deeaae588c1efb3167bbc6ba54d8e39f85a37d0'}.items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'HLS_PIN')
  for name,pin in {'thumbnail_r4.py': 'f389bb35737957fefc3518a7b081ee81c0ca81924f91cb7caf928ac8aae8a686', 'thumbnail_decode.py': '75b104a7acd9d6e5a35bbd0b461fe70df0a1f956ef77f08652eafddf97eb22a4'}.items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'THUMB_PIN')
  thumb=load('thumbnail_r4',NEW_HERE/'thumbnail_r4.py')
  thumbdecode=load('thumbnail_decode',NEW_HERE/'thumbnail_decode.py')
  def thumb_source_guard():
   for name,pin in {'api_v3/services/ThumbAssetService.php': 'f6f10cae05c4fc6eef2931b1fba651c8451448384bdbeaf21104983afd32679f', 'alpha/lib/model/thumbAsset.php': '478e479282058b84e1f7c1368d5d94d9fb1f00f5c558052496690587b253d24b', 'api_v3/lib/types/conversionProfile/KalturaThumbAsset.php': 'ab2ce68922da90c23a4aece918a15871f2ad0eb84ab57c3adc0dcb7294013c59'}.items():need(legacy.checksum(Path('/opt/kaltura/app')/name)==pin,'THUMB_SOURCE_PIN')
  thumb_source_guard()
  get443=load('media_get443',NEW_HERE/'media_get443.py');get8444=load('media_get8444',NEW_HERE/'media_get8444.py')
  def hls_source_guard():
   for name,pin,size in [('/usr/bin/ffmpeg','ed16af623947494a72e284b6eb8ff225f2da22b38b5d5069c2fd4b4ba3384e41',342488),('/usr/bin/ffprobe','272f6ebc634a63d9c8b4ca68e964119d980f25154e5aa2c35e5487da48e9a58f',191888)]:
    f=Path(name);m=f.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==m.st_gid==0 and m.st_nlink==1 and m.st_size==size and stat.S_IMODE(m.st_mode)==0o755 and not os.listxattr(f) and hashlib.sha256(f.read_bytes()).hexdigest()==pin,'HLS_DECODE_BINARY')
   for name,pin in {'alpha/lib/model/DeliveryProfileVodPackagerHls.php': '664b7d41cc60728c329ae3eb38409c02e5d83a54a0be12d02416af8dfd2e6241', 'alpha/lib/model/DeliveryProfileVod.php': 'e9058bbd6cc16aa79a928ddf91ef80e819481f43404ed7d3fddb35ec4b310494', 'alpha/apps/kaltura/lib/myEntryUtils.class.php': '70ebf2b99fbd5b898f88700b5c696eb1d64258f52bbfeb77bb68f8ef57306089'}.items():
    f=Path('/opt/kaltura/app')/name;m=f.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==0 and m.st_nlink==1 and m.st_size<=512*1024 and not m.st_mode&0o002 and hashlib.sha256(f.read_bytes()).hexdigest()==pin,'HLS_SOURCE_PIN')
  hls_source_guard()
  proof=NEW_HERE/'split-proof.json';pm=proof.lstat()
  need(stat.S_ISREG(pm.st_mode) and pm.st_uid==pm.st_gid==0 and pm.st_nlink==1 and stat.S_IMODE(pm.st_mode)==0o444 and pm.st_size<=65536 and not os.listxattr(proof),'SPLIT_RECEIPT')
  proof_raw=proof.read_bytes();need(re.fullmatch('[a-f0-9]{64}',proof_pin) is not None and hashlib.sha256(proof_raw).hexdigest()==proof_pin,'SPLIT_RECEIPT')
  try:expected_https_id=pair.receipt_id(json.loads(proof_raw))
  except pair.Rejected:raise Rejected('SPLIT_RECEIPT') from None
  report['split_receipt_sha256']=proof_pin
  report['media_tls_logs_in_every_inventory']=True
  old_logs=legacy.logs
  legacy.logs=lambda:media_logs.extend(lambda:tls_logs.extend(old_logs))
  legacy.logs() # Mandatory metadata inventory before any credential request/read.
  tls_ca=legacy.read_file(Path('/var/lib/kaltura-baseline-tls-r2/ca.crt'),16384,private=True)
  need(hashlib.sha256(tls_ca).hexdigest()=='5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef','TLS_CA_PIN')

  files=load('nonce_files',HERE.parent/'append-window-v1/scan.py')
  journal=load('nonce_journal',HERE.parent/'journal-window-v1/scan.py')
  overlay_root=Path('/home/vagrant/privacy-application-overlay-v4')
  raw=(overlay_root/'manifest.json').read_bytes()
  need(hashlib.sha256(raw).hexdigest()==EXPECTED_OVERLAY_MANIFEST,'OVERLAY_MANIFEST')
  manifest=json.loads(raw)
  for n,h in manifest['files'].items():need(hashlib.sha256((overlay_root/n).read_bytes()).hexdigest()==h,'OVERLAY_STAGE')
  overlay=load('nonce_overlay',overlay_root/'guest.py')
  parent=Path('/root/kaltura-baseline-private');info=parent.lstat()
  need(stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o077,'PRIVATE_DIAGNOSTIC_PARENT')
  private_dir=parent/unit;private_dir.mkdir(mode=0o700)
  audit_number=0;codes={'files':allowed_codes(files),'journal':allowed_codes(journal)}
  for name,pin in {'direct_content.py': 'c8d3ce3e02cc5389407f6c3e9bda8aa348b60ab53735580f72056a754c75fb37', 'privacy_provenance.py': 'ecb0a81c37d19d9842699a928e16e6e2838fb35f68fefb281c495f5505923931'}.items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'PROVENANCE_PIN')
  content=load('direct_content',NEW_HERE/'direct_content.py');provenance=load('privacy_provenance',NEW_HERE/'privacy_provenance.py')
  need(hashlib.sha256((NEW_HERE/'settle.py').read_bytes()).hexdigest()=='2b1382fc7ff4163240d9c6e3342738ce90ab8537df9ea9999497a44e24d84764','SETTLE_PIN')
  settle=load('baseline_settle_v1',NEW_HERE/'settle.py')
  def direct_source_guard():
   for name,pin in {'/opt/kaltura/app/alpha/lib/model/asset.php': '34f9e81972369706ea01f5e8a3ba19cd6999d2f6804f25ccdf89cac0bf74933d', '/opt/kaltura/app/alpha/lib/model/DeliveryProfileVod.php': 'e9058bbd6cc16aa79a928ddf91ef80e819481f43404ed7d3fddb35ec4b310494', '/opt/kaltura/app/alpha/apps/kaltura/lib/myContentStorage.class.php': '090d3232baca0482cf7cf52f7011eb896270f3e18e778fdee7e2171421c3f2a9', '/opt/kaltura/app/configurations/apache/conf.d/enabled.kaltura.conf': '0cc12e21735c3f7e968ceb9fcf35426fab678ce8a68c9fdfc71fd03612ba8ba5'}.items():
    p=Path(name);info=p.lstat();need(stat.S_ISREG(info.st_mode) and info.st_uid==0 and info.st_nlink==1 and info.st_size<=512*1024 and not info.st_mode&0o002 and hashlib.sha256(p.read_bytes()).hexdigest()==pin,'DIRECT_SOURCE_PIN')
  hls_source_guard()
  direct_source_guard()
  need(hashlib.sha256((NEW_HERE/'route_descriptor.py').read_bytes()).hexdigest()=='a9276e52f8a238303c1011f781f13f066134d12b315afd3634f9f87eeea1fee9','ROUTE_DESCRIPTOR_PIN')
  descriptor=load('route_descriptor',NEW_HERE/'route_descriptor.py')
  def route_source_guard():
   for name,pin in {'/opt/kaltura/app/alpha/lib/model/flavorAsset.php': '18973d5b14c451199f16dcb45b7f9ee758bcd7733264ab01612dc40be5ae3bf0', '/opt/kaltura/app/alpha/lib/model/om/BaseassetPeer.php': '953adc4eccaea24a3e485919828a91a283f6d6f538465fc2a7fdfdaaf00fee56', '/opt/kaltura/app/alpha/lib/model/om/BaseassetParamsPeer.php': '78121b1671247f156358e32b6ce9d6d994939b7396a5112c5c94438908ca3844', '/opt/kaltura/app/alpha/apps/kaltura/lib/kAssetUtils.class.php': '4ee947a8fe89b6ee9fc5e5f97b641f4dbf411a47666892d4d90950bfc011e03b', '/opt/kaltura/app/infra/general/kString.class.php': 'df428ba6ae157a814f63b9b9359054bfa931376947d2a3419511355b9dd7f383'}.items():
    file=Path(name);meta=file.lstat();need(stat.S_ISREG(meta.st_mode) and meta.st_uid==0 and meta.st_nlink==1 and meta.st_size<=512*1024 and hashlib.sha256(file.read_bytes()).hexdigest()==pin,'ROUTE_SOURCE_PIN')
  route_source_guard()
  def serve_source_guard():
   f=Path('/opt/kaltura/app/alpha/lib/model/DeliveryProfileAkamaiHttp.php');m=f.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==0 and m.st_nlink==1 and m.st_size<=512*1024 and hashlib.sha256(f.read_bytes()).hexdigest()=='116ebbe16200e83e16e008f3aea610b7e9ae2a012704f7796068926e447ad2b9','ROUTE_SOURCE_PIN')
   for name,pin in {'/opt/kaltura/app/vendor/symfony/controller/sfRouting.class.php': '52a0fb006d480654a2f233514729b9bd61001efd930b3745d6a25472abf5bbdb', '/opt/kaltura/app/alpha/apps/kaltura/modules/extwidget/actions/serveFlavorAction.class.php': '9e4d7470625adb3288b7692cbd093c8a0162f8bf781f72495c03524c79bb7610', '/opt/kaltura/app/alpha/apps/kaltura/config/routing.yml': '835673cace780736154e06ba55c3c66c3c4a5e24d1c588d3a72b62c3aa50ca9b', '/opt/kaltura/app/api_v3/services/FlavorAssetService.php': '162606b083296c54258ba364f25bbb305b688ba8d4cf8a547b9a19a821355206'}.items():
    f=Path(name);m=f.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==0 and m.st_nlink==1 and m.st_size<=512*1024 and hashlib.sha256(f.read_bytes()).hexdigest()==pin,'ROUTE_SOURCE_PIN')
  serve_source_guard()
  private_before=legacy.logging_preflight();config_before=overlay.audits()[1]
  source_before=overlay.source_state(manifest['after']);report['sources_before']=source_before
  for p,h in manifest['modules'].items():need(overlay.digest(p)==h,'RUNTIME_PIN')
  report['apache_runtime_current']='UNVERIFIED_NO_WEB_FILE_PROBE'
  report['cli_version']=subprocess.check_output(['/usr/bin/php','-n','-r','echo PHP_VERSION;'],timeout=10).decode()
  need(re.fullmatch(r'7\.4\.[0-9]+',report['cli_version']) is not None,'CLI_VERSION')
  state=Path('/root/kaltura-sanity.rc').read_text();match=re.fullmatch(r'PARTNER_ID=([1-9][0-9]*)\s*',state)
  need(match is not None,'SYNTHETIC_PARTNER_STATE');partner=int(match[1])
  # No credential read until wrong-secret logging gate succeeds.
  user='privacy-'+secrets.token_hex(16);canary='invalid-'+secrets.token_hex(24)+'-secret-marker'
  def call(**params):return legacy.PostTransport(legacy.Origin('192.168.56.74','https',8443),tls_ca,'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef').request(dict(format=1,**params)).value
  def record_match(phase,patterns,f,j,number):
   item=provenance.receipt(number,phase,patterns,f,j,secret=secret.encode() if secret else None,ks=ks.encode() if ks else None,canary=canary.encode() if canary else None,candidates=[v.encode() for v in tracked_tokens])
   private_json(private_dir/('matches-'+str(number)+'-'+phase+'.json'),item)
   records=report.setdefault('match_provenance',[]);need(len(records)<128,'PROVENANCE_LIMIT');records.append(item)
  need(hashlib.sha256((NEW_HERE/'convergence.py').read_bytes()).hexdigest()=='b7f8114c27a930c471d3640c76ad60f28e0c0133b63abb5a4d805fa7c01cceca','AUDIT_CONVERGENCE_PIN')
  convergence=load('convergence',NEW_HERE/'convergence.py')
  need(hashlib.sha256((NEW_HERE/'common_end.py').read_bytes()).hexdigest()=='3264c66211a8730c35ca192a764603f71c8cd21fad0f64ca68c7db7aa637b096','AUDIT_CONVERGENCE_PIN')
  common_end=load('common_end',NEW_HERE/'common_end.py')
  def audit_once(patterns,start,jstart):
   nonlocal audit_number
   audit_number+=1;number=audit_number
   private_json(private_dir/('boundary-'+str(number)+'.json'),{'file_marks':{p:vars(mark) for p,mark in start.items()},'journal':{'token':jstart.token,'boot':jstart.boot}})
   def scan(which,phase,operation):
    module=files if which=='files' else journal
    report['privacy_phase']=phase;checkpoint()
    try:return operation()
    except module.Incomplete as error:
     code=scanner_code(error,codes[which]);report.setdefault('privacy_errors',[]).append({'phase':phase,'code':code,'audit':number})
     try:after={p:vars(mark) for p,mark in files.snapshot(legacy.logs()).items()}
     except Exception:after=None
     private_json(private_dir/('failure-'+str(number)+'-'+phase+'.json'),{'phase':phase,'code':code,'current_file_marks':after})
     raise Rejected(which.upper()+'_'+code) from None
   try:quiet=settle.wait_quiet(lambda:(files.snapshot(legacy.logs()),journal.snapshot()))
   except settle.Unsettled:raise Rejected('QUIET_WINDOW_NOT_ESTABLISHED') from None
   item=dict(quiet,audit=number,stage=failure_stage)
   private_json(private_dir/('quiet-'+str(number)+'.json'),item)
   report['last_audit_quiet']=item
   f=scan('files','files_initial',lambda:files.scan_window(start,patterns,inventory=legacy.logs))
   if any(f.get('counts',[])):
    record_match('files_and_journal',patterns,f,{'counts':[0]*len(patterns)},number)
    raise Rejected('PRIVATE_MARKER_LOGGED')
   j=scan('journal','journal',lambda:journal.scan_window(jstart,patterns))
   if any(j.get('counts',[])):
    record_match('files_and_journal',patterns,f,j,number)
    raise Rejected('PRIVATE_MARKER_LOGGED')
   need(j.get('status')==JOURNAL_STATUS and j.get('cutoff_covered') is True,'JOURNAL_STATUS');j['complete']=True
   # Recheck the same file window after journal drain, without hiding any earlier hit.
   report['last_privacy_observation']={'files':f,'journal':j};checkpoint()
   record_match('files_and_journal',patterns,f,j,number)
   accepted(f,j)
   f_after=scan('files','files_after_journal',lambda:files.scan_window(start,patterns,inventory=legacy.logs))
   report['last_privacy_observation']['files_after_journal']=f_after
   record_match('files_after_journal',patterns,f_after,j,number)
   accepted(f_after,j)
   need(f_after['end_offsets']==f['end_offsets'],'FILE_TAIL_DURING_JOURNAL')
   f=f_after
   need(len(f.get('counts',[]))==len(patterns) and len(j.get('counts',[]))==len(patterns),'PATTERN_COUNT')
   accepted(f,j)
   need(legacy.logging_preflight()==private_before and overlay.audits()[1]==config_before,'CONFIG_DRIFT')
   need(overlay.source_state(manifest['after'])==source_before,'SOURCE_DRIFT')
   for p,h in manifest['modules'].items():need(overlay.digest(p)==h,'RUNTIME_PIN')
   return {'files':f,'journal':j,'scope':'finite phase only; no history or future-write claim'}
  def audit(patterns,start,jstart):
   try:return convergence.run(lambda:audit_once(patterns,start,jstart),Rejected)
   except convergence.Exhausted as error:raise Rejected(str(error)) from None
  def audit_all(batches,start,jstart):
   def quiet():
    try:settle.wait_quiet(lambda:(files.snapshot(legacy.logs()),journal.snapshot()))
    except settle.Unsettled:raise Rejected('QUIET_WINDOW_NOT_ESTABLISHED') from None
   def emitted(value):
    rows=report.setdefault('common_end_attempts',[]);need(len(rows)<9,'COMMON_AUDIT_SCHEMA');rows.append(value)
   try:return common_end.run(batches,start,jstart,snapshot=lambda:(files.snapshot(legacy.logs()),journal.snapshot()),quiet=quiet,audit_once=audit_once,emit=emitted)
   except common_end.Rejected as error:raise Rejected(str(error)) from None
  report['phase']='invalid-nonce';start=files.snapshot(legacy.logs());jstart=journal.snapshot()
  value=call(service='session',action='start',partnerId=partner,userId=user,type=0,expiry=60,secret=canary)
  need(type(value) is dict and value.get('objectType')=='KalturaAPIException' and value.get('code')=='START_SESSION_ERROR','WRONG_SECRET_CONTROL')
  failure_stage='INVALID_NONCE_PRIVACY';report['invalid_nonce']=audit([canary.encode(),canary[:15].encode()],start,jstart)
  report['wrong_secret_rejected']=True;checkpoint()
  report['phase']='synthetic-user'
  rows=legacy.sql('SELECT id,admin_email,secret FROM partner WHERE id='+str(partner))
  need(len(rows)==1 and len(rows[0])==3 and rows[0][0]==str(partner) and rows[0][1]=='sanity@kaltura.local','SYNTHETIC_PARTNER_PROVENANCE')
  need(partner==102,'EXACT_PRIOR_PARTNER')
  secret=rows[0][2];need(re.fullmatch(r'[A-Za-z0-9_+/=-]{16,4096}',secret) is not None,'PRIVATE_SECRET_FORMAT')
  start=files.snapshot(legacy.logs());jstart=journal.snapshot();report['user_attempted']=True;checkpoint()
  media_window=(start,jstart);ks=''
  ks=call(service='session',action='start',partnerId=partner,userId=user,type=0,expiry=1200,secret=secret)
  need(type(ks) is str and 20<=len(ks)<=8192,'USER_KS')
  denied=call(service='session',action='start',partnerId=partner,userId=user,type=2,expiry=60,secret=secret)
  need(type(denied) is dict and denied.get('objectType')=='KalturaAPIException' and denied.get('code')=='START_SESSION_ERROR','ADMIN_ESCALATION_CONTROL')
  failure_stage='USER_PRIVACY';report['user_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)
  report['user_session_accepted']=True;report['admin_escalation_rejected']=True;checkpoint()
  rehearsal=load('baseline_rehearsal_v2',NEW_HERE/'rehearsal.py')
  source=Path('/home/vagrant/privacy-media-overlay-v3/short360.mp4');raw=source.read_bytes()
  need(len(raw)<=2*1024*1024 and hashlib.sha256(raw).hexdigest()==legacy.SOURCE_PIN,'MEDIA_SOURCE_PIN')
  report['source_sha256']=legacy.SOURCE_PIN
  start=files.snapshot(legacy.logs());jstart=journal.snapshot()
  def value(service,action,**params):return legacy.api_value(call(service=service,action=action,**params))
  media_window=(start,jstart)
  report['phase']='existing-entry-observation';entry_id=obs.ENTRY
  entry=value('media','get',ks=ks,entryId=entry_id,version=-1);bind_entry(entry,partner,entry_id)
  report['media_projection']=obs.projection(entry)
  assets=value('flavorasset','getByEntryId',ks=ks,entryId=entry_id)
  report['actual_assets']=obs.assets_projection(assets)
  originals=[a for a in assets if type(a.get('isOriginal')) in {bool,int,str} and a.get('isOriginal') in [True,1,'1']];need(len(originals)==1,'ORIGINAL_ASSET_COUNT')
  asset=originals[0];bind_asset(asset,partner,entry_id);asset_id=asset.get('id');version=str(asset.get('version'))
  need(asset_id=='0_ewuu0o46' and version=='2','PRIOR_ASSET_IDENTITY')
  rows=legacy.sql("SELECT id,partner_id,object_id,version,file_root,file_path,status FROM file_sync WHERE object_type=4 AND object_sub_type=1 AND file_type=1 AND status=2 AND partner_id="+str(partner)+" AND object_id='"+asset_id+"' AND version='"+version+"' LIMIT 2")
  candidates=[]
  for row in rows:
   try:candidates.append(legacy.owned_storage(row,partner,asset_id,version))
   except legacy.Failed:continue
  need(len(candidates)==1,'LOCAL_SOURCE_BINDING');stored,sync_id=candidates[0]
  need(sync_id==315 and legacy.checksum(stored)==legacy.SOURCE_PIN,'STORED_SOURCE_BYTES')
  selected_rows=[row for row in rows if row[0]=='315'];need(len(selected_rows)==1,'DIRECT_ROW');storage_root=selected_rows[0][4];storage_path=selected_rows[0][5]
  try:content.mapping(storage_root,storage_path,str(stored))
  except content.Rejected as error:raise Rejected(str(error)) from None
  report.update(original_asset_id=asset_id,asset_version=version,file_sync_id=sync_id,stored_source_sha256=legacy.SOURCE_PIN)
  listing=value('media','list',ks=ks,**{'filter:objectType':'KalturaMediaEntryFilter','filter:idEqual':entry_id,'filter:orderBy':'+createdAt','pager:objectType':'KalturaFilterPager','pager:pageSize':1,'pager:pageIndex':1})
  need(type(listing) is dict and type(listing.get('objects')) is list and len(listing['objects'])==1 and str(listing.get('totalCount'))=='1','OWNED_LIST')
  need(legacy.typed_equal(legacy.media_projection(listing['objects'][0]),report['media_projection']),'LIST_IDENTITY')
  report['list_total_count']=listing['totalCount']
  rows=legacy.sql("SELECT id,partner_id,COALESCE(data,''),conversion_profile_id FROM entry WHERE id='0_wzmt2sfy' AND partner_id=102 LIMIT 2")
  need(len(rows)==1 and len(rows[0])==4 and rows[0][:2]==['0_wzmt2sfy','102'],'ENTRY_DB_BINDING')
  concrete=obs.entry_version(rows[0][2]);selected=rows[0][3]
  need(selected=='14','OBSERVED_PROFILE_SELECTION')
  report['version_observations']=[]
  for version in [-1,0]+([concrete] if concrete is not None and concrete not in (-1,0) else []):
   reply=call(service='media',action='get',ks=ks,entryId=entry_id,version=version)
   if type(reply) is dict and reply.get('objectType')=='KalturaAPIException':
    report['version_observations'].append({'requested':version,'outcome':'API_REJECTED'})
   else:
    need(obs.typed_equal(obs.projection(reply),report['media_projection']),'VERSION_PROJECTION')
    report['version_observations'].append({'requested':version,'outcome':'TYPED_PROJECTION_MATCH'})
  positive=concrete is not None and any(r['requested']==concrete and r['outcome']=='TYPED_PROJECTION_MATCH' for r in report['version_observations'])
  report['fixture']=obs.fixture(entry,listing,concrete)
  report['entry_version_status']='OBSERVED_FROM_ENTRY_DATA' if concrete is not None else 'UNRESOLVED'
  profile_reply=call(service='conversionprofile',action='get',ks=ks,id=int(selected)) if re.fullmatch('[1-9][0-9]*',selected) else None
  report['profile']=obs.profile(profile_reply,selected)
  report['phase']='thumbnail';failure_stage='API_ROUND'
  enrollment=load('context_urls',NEW_HERE/'context_urls.py')
  def described(stage,value):report.setdefault('thumbnail_diagnostics',{})[stage]=value
  try:
   report['thumbnail']=thumb.observe(lambda **form:call(ks=ks,**form),lambda url:enrollment.enroll(url,tracked_tokens),lambda url,headers,limit:get443.request(tls_ca,url,headers,limit),thumbdecode.decode,secret,ks,described)
  except (thumb.Rejected,thumbdecode.Rejected) as error:raise Rejected(str(error) if str(error) in thumb.CODES+thumbdecode.CODES else 'THUMB_RESPONSE') from None
  failure_stage='QUIET_SETTLE'
  try:report['quiet_window']=settle.wait_quiet(lambda:(files.snapshot(legacy.logs()),journal.snapshot()))
  except settle.Unsettled:raise Rejected('QUIET_WINDOW_NOT_ESTABLISHED') from None
  failure_stage='MEDIA_PRIVACY'
  report['media_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)
  failure_stage='BATCH_PRIVACY'
  report['round_privacy']=audit_all(rehearsal.patterns(secret,ks,tracked_tokens),start,jstart)
  failure_stage='POSTCHECK'
  thumb_source_guard()
  hls_source_guard()
  direct_source_guard()
  route_source_guard()
  serve_source_guard()
  need(legacy.checksum(stored)==legacy.SOURCE_PIN and legacy.checksum(source)==legacy.SOURCE_PIN,'SOURCE_AFTER')
  report['sources_after']=overlay.source_state(manifest['after']);report['overlay_manifest_sha256']=EXPECTED_OVERLAY_MANIFEST;report['runtime_pins_verified']=True;report['tls_transport']={'scheme':'https','port':8443,'ca_sha256':'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef','tls_logs_in_every_inventory':True};report['status']='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE';report['phase']='done'

 except Exception as error:
  # Only bounded fixed codes; no repr/value/credential or arbitrary backend error text.
  report['failure_stage']=failure_stage;report['failure_code']=str(error) if type(error) is Rejected and str(error) in FIXED_FAILURE_CODES else 'UNEXPECTED_OR_DEPENDENCY_FAILURE'
  report['status']='FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION'
  if media_window is not None:
   try:
    if tracked_tokens:report['media_failure_privacy_batches']=audit_all(rehearsal.patterns(secret,ks,tracked_tokens),*media_window)
    else:report['media_failure_privacy']=audit([v for v in [secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()] if v],*media_window)
   except Exception as scan_error:
    report['media_privacy_failure_class']='FINITE_SCAN_INCOMPLETE'
    report['media_privacy_failure_code']=str(scan_error) if type(scan_error) is Rejected and str(scan_error) in FIXED_FAILURE_CODES else 'UNEXPECTED_OR_DEPENDENCY_FAILURE'
 checkpoint();return 0 if report['status']=='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE' else 2
if __name__=='__main__':sys.exit(main(sys.argv[1],sys.argv[2]))

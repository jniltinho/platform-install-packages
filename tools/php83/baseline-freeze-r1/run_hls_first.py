"""V3 root-coordinator-only host runner for versioned V2 observation. --check does not stage or authenticate API."""
import argparse,base64,hashlib,json,os,re,secrets,selectors,shlex,signal,stat,subprocess,time,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
UUID='9e954729-16f3-4eda-9db5-b94e5ada9e44'
CONFIG=Path('/tmp/php74-baseline-strict-r1.conf')
KEYS=Path('/tmp/php74-baseline-hostkey-r1')
PINS={'guest_hls_first.py': '453af48e64cd98f36e8302dc5970cebe07229b2fe0257c1db4bbe21f1fc95d16', 'observation_v2.py': 'ec32386df1c745f5754ece19f3127f6da85415e644c8556e6c07666b2ea1abc5', 'protocol_v2.py': '147d74b0a04779fd0819ebe210d8a1a6aea4af8fbc773683a278e540ce70d4b8', 'rehearsal.py': 'ccf78ba0b1d3c94f05f63fd2d87c351953022c149c0e75392b5c86be2c02bb70', 'settle.py': '2b1382fc7ff4163240d9c6e3342738ce90ab8537df9ea9999497a44e24d84764', 'privacy_logs_r2.py': 'd67eb65900c3134c91efaf94b18ba482b59261c81b0084de0cea3bcd37d5246c', 'url_privacy.py': '338f0339e23b7d385fce17ea6fa152016342bca8d42129d5efc3f2a5183c1f6f', 'direct_content.py': 'c8d3ce3e02cc5389407f6c3e9bda8aa348b60ab53735580f72056a754c75fb37', 'privacy_provenance.py': 'ecb0a81c37d19d9842699a928e16e6e2838fb35f68fefb281c495f5505923931', 'route_descriptor.py': 'a9276e52f8a238303c1011f781f13f066134d12b315afd3634f9f87eeea1fee9', 'convergence.py': 'b7f8114c27a930c471d3640c76ad60f28e0c0133b63abb5a4d805fa7c01cceca', 'playback_context_r4.py': '8bb6c410b034a8c140ef9408c8e49ee826e5561399eae5b0778629effed9a0f5', 'context_urls.py': '1ecf0476baed260a405ddd6fb6da0b1eee42b612de61d5762761c84b3c6a2bff', 'context_selected.py': '64bd6fb3cd957eec51b6abd9baf9ccd4713bbf930a6405d6f07cf7db94344d8b', 'short_metadata.py': 'a3a60d6ad5ddfcadebf13181d757915e41fb4fd65d16c1c08c3f5b4263bf59bb', 'hls_source_r2.py': 'b1b4e5ed19d1589b84fb4e09bf4b98dd32d668e64b54ea69efde59bdf33d80bb', 'hls_first.py': 'ca5bc2ad461642c8efc5f600881de32f8850f5ef18f7bb1878fcce375ac503ad', 'short_delivery443.py': '9aa829f6c1927eb493fa4f1f5d9c1584d6a8f93b253015912ce253ba24fb1e76', 'media_get443.py': '7417ba4ca341f84626c7b0138ac4fbdf7103e89a0975b55be210e7047d95af30'}
STAGE='/var/lib/kaltura-baseline-hls-first-r1'
SSH=['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=10','-F',str(CONFIG),'baseline74']
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('RUNNER_REJECTED')
def sha(b):return hashlib.sha256(b).hexdigest()
def bounded(argv,data=None,timeout=30,cap=4*1024*1024):
 # All pipes, including stdin, obey one deadline; no raw stderr persists.
 need(data is None or len(data)<=1024*1024)
 p=subprocess.Popen(argv,stdin=subprocess.PIPE if data is not None else subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 sel=selectors.DefaultSelector();out=bytearray();err=0;sent=0;deadline=time.monotonic()+timeout;completed=False
 try:
  for stream,kind in ((p.stdout,'out'),(p.stderr,'err')):
   os.set_blocking(stream.fileno(),False);sel.register(stream,selectors.EVENT_READ,kind)
  if data is not None:
   os.set_blocking(p.stdin.fileno(),False);sel.register(p.stdin,selectors.EVENT_WRITE,'in')
  while sel.get_map():
   need(time.monotonic()<deadline)
   for key,_ in sel.select(min(.2,max(0,deadline-time.monotonic()))):
    if key.data=='in':
     if sent<len(data):sent+=os.write(key.fileobj.fileno(),data[sent:sent+4096])
     if sent==len(data):sel.unregister(key.fileobj);key.fileobj.close()
     continue
    raw=os.read(key.fileobj.fileno(),65536)
    if not raw:sel.unregister(key.fileobj);continue
    if key.data=='out':out.extend(raw)
    else:err+=len(raw)
    need(len(out)+err<=cap)
  rc=p.wait(timeout=max(.1,deadline-time.monotonic()));completed=True;return rc,bytes(out),err
 finally:
  if not completed:
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
  if p.poll() is None:p.wait(timeout=10)
  sel.close();p.stdout.close();p.stderr.close()
  if p.stdin is not None and not p.stdin.closed:p.stdin.close()
def pinned(path,pin,private=False):
 s=path.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not path.is_symlink())
 if private:need(s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o600)
 raw=path.read_bytes();need(sha(raw)==pin);return raw
def host_guard(text):
 rows={}
 for line in text.splitlines():
  k,sep,v=line.partition('=')
  if sep:
   need(k not in rows);rows[k.strip('"')]=v.strip('"')
 need(rows.get('UUID')==UUID and rows.get('name')=='kaltura-php74-noble-baseline' and rows.get('VMState')=='running' and rows.get('cpus')=='4' and rows.get('memory')=='8192')
 need(any(len(v.split(','))==6 and v.split(',')[1:]==['tcp','127.0.0.1','2201','','22'] for k,v in rows.items() if re.fullmatch(r'Forwarding\(\d+\)',k)))
 return {k:rows[k] for k in ('UUID','name','VMState','cpus','memory')}
REMOTE_GUARD='''import hashlib,json,os,socket,stat,subprocess
from pathlib import Path
assert os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline'
a=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10))
ips={v.get('local') for row in a for v in row.get('addr_info',[])}
assert '192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'})
for name in ('/','/var','/var/lib'):
 p=Path(name);s=p.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and not s.st_mode&0o022 and not os.listxattr(p)
stage=Path('/var/lib/kaltura-baseline-hls-first-r1');assert not os.path.lexists(stage)
old=subprocess.run(['systemctl','is-active','baseline-freeze-968111b3.service'],capture_output=True,timeout=10)
assert old.returncode in (3,4) and old.stdout.strip() in (b'inactive',b'unknown')
p=Path('/root/kaltura-baseline-private');s=p.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==0 and not s.st_mode&0o077
'''
def remote(code,timeout=30):return bounded(SSH+['sudo -n python3 -B -'],code.encode(),timeout)
def check():
 pinned(CONFIG,'15f687f3db61c013654442404e916b1b2ad7f0d1835e1f30ef10ca80355ceef3',True)
 pinned(KEYS,'6b6a9652a16acd478a01b508962452556138ce3a3f0c2cc4584baab58f00c4c6',True)
 blobs={k:pinned(HERE/k,v) for k,v in PINS.items()}
 rc,raw,_=bounded(['VBoxManage','showvminfo',UUID,'--machinereadable']);need(rc==0);host=host_guard(raw.decode())
 rc,raw,_=remote(REMOTE_GUARD+'print("CHECKED")\n');need(rc==0 and raw==b'CHECKED\n')
 return blobs,host
def unit_command(unit):
 need(re.fullmatch('baseline-freeze-[a-f0-9]{8}',unit) is not None)
 return 'sudo -n systemd-run --quiet --wait --pipe --collect --unit '+unit+' -p IPAddressDeny=any -p IPAddressAllow=localhost -p IPAddressAllow=192.168.56.74/32 -p NoNewPrivileges=yes -p ProtectSystem=strict -p ProtectHome=read-only -p PrivateTmp=yes -p ReadWritePaths=/root/kaltura-baseline-private -p RuntimeMaxSec=1100 /usr/bin/python3 -B '+STAGE+'/guest_hls_first.py '+unit

EXPECTED_SOURCES={'alpha/apps/kaltura/lib/db/KalturaStatement.php': {'gid': 0, 'mode': 436, 'sha256': 'bd8ab13a8fb745eb603b9c35633e24637adb5356a1792642d884c6f7e1d85bd2', 'uid': 0}, 'api_v3/lib/KalturaDispatcher.php': {'gid': 0, 'mode': 436, 'sha256': '9ce4b17a9fb1bef95fbbbbc6f08cb396a6cc944b055bac8413d740ce5d73c7b9', 'uid': 0}, 'api_v3/lib/KalturaFrontController.php': {'gid': 0, 'mode': 436, 'sha256': '79570bd2be507f0045281a903aa13bd2de4037c2e12df3370075c4445184a4ca', 'uid': 0}, 'infra/log/KalturaLog.php': {'gid': 0, 'mode': 436, 'sha256': '40e4db5733cfab59e0e873f94ee64166de380d86425625411dc716f6cb1003dd', 'uid': 0}, 'infra/log/KalturaSerializableStream.php': {'gid': 0, 'mode': 436, 'sha256': '8411013a6f2ac78b6d092594d088ba9a5fbe71ada9de00692a369388c40dc04c', 'uid': 0}}
def audit_quiet_projection(value):
 need(type(value) is dict and set(value)=={'status','samples','quiet_seconds','maximum_seconds','audit','stage'})
 need(value['status']=='QUIET_WINDOW_OBSERVED' and type(value['samples']) is int and 2<=value['samples']<=121 and type(value['audit']) is int and 1<=value['audit']<=128)
 need(type(value['quiet_seconds']) is int and value['quiet_seconds']==2 and type(value['maximum_seconds']) is int and value['maximum_seconds']==30)
 need(value['stage'] in ('PREFLIGHT','INVALID_NONCE_PRIVACY','USER_PRIVACY','API_ROUND','QUIET_SETTLE','MEDIA_PRIVACY','BATCH_PRIVACY','POSTCHECK'))
 return value

def provenance_projection(value):
 import privacy_provenance
 need(type(value) is list and len(value)<=128)
 return [privacy_provenance.validate_public(v) for v in value]

def shape_projection(value):
 need(type(value) is dict and set(value)=={'scheme','port','target_host_match','query_present','credential_path'})
 need(value['scheme'] in ('http','https','other') and value['port'] in ('80','443','8443','other'))
 need(all(type(value[k]) is bool for k in ('target_host_match','query_present','credential_path')))
 return dict(value)

def route_projection(value):
 import route_descriptor
 return route_descriptor.validate(value)

def context_projection(v):
 keys={'case','api_calls','sources','selected_hls_tag_match','selected_https_hls_descriptors','actions','messages','flavor_assets','response_secret_coverage_complete','delivery_authorized','hls_fetched','decoded','full_acceptance'}
 need(type(v) is dict and set(v)==keys and v['case']=='NATIVE_HLS_CONTEXT_NO_GET')
 for k,cap in [('api_calls',1),('sources',16),('selected_https_hls_descriptors',16),('actions',100),('messages',100),('flavor_assets',100)]:need(type(v[k]) is int and 0<=v[k]<=cap)
 need(v['selected_hls_tag_match'] is None or type(v['selected_hls_tag_match']) is bool)
 need(v['api_calls']==1 and v['selected_https_hls_descriptors']<=v['sources'])
 for k in ['response_secret_coverage_complete','delivery_authorized','hls_fetched','decoded','full_acceptance']:need(v[k] is False)
 return dict(v)

def hls_projection(v):
 keys={'case','requests','bytes','playlist_kind','references','nested_requests','decoded','response_secret_coverage_complete','full_acceptance'}
 need(type(v) is dict and set(v)==keys and v['case']=='FIRST_HLS_MANIFEST_ONLY' and type(v['requests']) is int and v['requests']==1 and type(v['bytes']) is int and 0<v['bytes']<=65536 and v['playlist_kind'] in ('master','media') and type(v['references']) is int and 1<=v['references']<=32 and type(v['nested_requests']) is int and v['nested_requests']==0)
 need(all(v[k] is False for k in ('decoded','response_secret_coverage_complete','full_acceptance')));return dict(v)
def hls_route_projection(v):
 expected={'route':'NATIVE_PLAYMANIFEST','source_bound':True,'credential_free_fixed_grammar':True,'nested_get_authorized':False}
 need(type(v) is dict and v==expected and all(type(v[k]) is type(x) for k,x in expected.items()));return expected

def round_projection(row):
 sys.path.insert(0,str(HERE.parent/'baseline-api'))
 import rehearsal
 from assemble_v2 import privacy
 out={}
 need('untimed_round' not in row and 'round_token_count' not in row)
 if 'hls_manifest' in row:out['hls_manifest']=hls_projection(row['hls_manifest'])
 if 'hls_route' in row:out['hls_route']=hls_route_projection(row['hls_route'])
 if 'playback_context' in row:out['playback_context']=context_projection(row['playback_context'])
 if 'route_observation' in row:out['route_observation']=route_projection(row['route_observation'])
 if 'round_privacy' in row:
  v=row['round_privacy'];need(type(v) is dict and set(v)=={'common_end_verified','pattern_count','batches'} and v['common_end_verified'] is True and type(v['pattern_count']) is int and 2<=v['pattern_count']<=72)
  batches=v['batches'];need(type(batches) is list and 1<=len(batches)<=3)
  projected=[]
  for b in batches:
   privacy(b);need(2<=len(b['files']['counts'])<=32 and len(b['files']['counts'])==len(b['journal']['counts']))
   projected.append({'files':{k:b['files'][k] for k in ('counts','status','uncovered_tail_bytes')},'journal':{k:b['journal'][k] for k in ('counts','status','cutoff_covered','complete')},'scope':'FINITE_COMMON_END_ROUND_WINDOW'})
  need(sum(len(b['files']['counts']) for b in batches)==v['pattern_count'])
  out['round_privacy']={'common_end_verified':True,'pattern_count':v['pattern_count'],'batches':projected}
 if 'quiet_window' in row:
  q=row['quiet_window'];need(type(q) is dict and set(q)=={'status','samples','quiet_seconds','maximum_seconds'} and q['status']=='QUIET_WINDOW_OBSERVED' and type(q['samples']) is int and 2<=q['samples']<=121 and q['quiet_seconds']==2 and q['maximum_seconds']==30)
  out['quiet_window']=q
 return out

FAILURE_CODES=['HLS_CONTEXT', 'HLS_CONTEXT_COVERAGE', 'HLS_SOURCE_COUNT', 'HLS_ACCESS_ACTIONS', 'HLS_SOURCE_GUARD', 'HLS_REFERENCE_ENROLLMENT', 'HLS_MANIFEST_REJECTED', 'HLS_PIN','SELECTED_ASSET','SELECTED_SIZE','SELECTED_TAGS','CONTEXT_CALL', 'CONTEXT_TYPE', 'URL_ENROLLMENT_INCOMPLETE', 'RESPONSE_COVERAGE_INCOMPLETE', 'SOURCE_TYPE', 'SOURCE_FIELDS', 'CONTEXT_ARRAY', 'CONTEXT_PIN','AUDIT_CONVERGENCE_DEADLINE','AUDIT_CONVERGENCE_EXHAUSTED','AUDIT_CONVERGENCE_PIN','SOURCE_ROUTE_SHAPE', 'SOURCE_ROUTE_CREDENTIAL', 'SOURCE_ROUTE_ENCODING', 'SOURCE_ROUTE_ORIGIN', 'SOURCE_ROUTE_AUTH', 'SOURCE_ROUTE_ORDER', 'SOURCE_ROUTE_EMPTY_SEGMENT', 'SOURCE_ROUTE_UNKNOWN_KEY', 'SOURCE_ROUTE_DUPLICATE_KEY', 'SOURCE_ROUTE_EXPECTED_VALUE','ROUTE_DESCRIPTOR_PIN', 'ROUTE_SOURCE_PIN', 'ROUTE_NAME_ROW', 'ROUTE_FILENAME_INPUT', 'ROUTE_URL_SHAPE', 'ROUTE_PATTERN_LIMIT', 'ROUTE_RESPONSE_TYPE','DIRECT_STORAGE_ROOT', 'DIRECT_STORAGE_PATH', 'DIRECT_STORAGE_JOIN', 'DIRECT_URL_SHAPE', 'DIRECT_CREDENTIAL_SHAPE', 'DIRECT_PATTERN_LIMIT', 'DIRECT_URL_CREDENTIAL', 'DIRECT_URL_AUTH', 'DIRECT_URL_MISMATCH', 'DIRECT_SOURCE_PIN', 'PROVENANCE_PIN', 'PROVENANCE_LIMIT', 'DIRECT_ROW','DELIVERY_PIN', 'DELIVERY_DEADLINE', 'DELIVERY_REJECTED', 'URL_SHAPE', 'URL_PATTERN_LIMIT', 'URL_CREDENTIAL', 'URL_AUTH_SHAPE', 'DELIVERY_URL', 'DELIVERY_ORIGIN', 'DELIVERY_TRANSPORT', 'DELIVERY_RESPONSE', 'DELIVERY_STATUS', 'DELIVERY_BODY_LIMIT', 'DELIVERY_HEADERS', 'DELIVERY_HEADER_NAME', 'DELIVERY_DUPLICATE_HEADER', 'DELIVERY_ENCODING_REDIRECT', 'DELIVERY_LENGTH', 'DELIVERY_SOURCE_HASH', 'DELIVERY_CONTENT_RANGE', 'DELIVERY_RANGE_BYTES','METADATA_API_CALL_FAILED', 'METADATA_RESPONSE_TYPE', 'METADATA_TOTAL', 'METADATA_CARDINALITY', 'METADATA_ASSET_TYPE', 'METADATA_ASSET_ID', 'METADATA_DUPLICATE', 'METADATA_PARTNER', 'METADATA_OWNERSHIP', 'METADATA_STATUS', 'METADATA_ORIGINAL_TYPE', 'METADATA_VERSION', 'METADATA_PARAMS', 'METADATA_SIZE', 'METADATA_EXTENSION', 'METADATA_SOURCE_BINDING','METADATA_PIN','METADATA_RESPONSE_REJECTED','TLS_LOG_ADAPTER_PIN','TLS_CA_PIN','ADMIN_ESCALATION_CONTROL', 'CLI_VERSION', 'COMMON_AUDIT_END_DRIFT', 'CONFIG_DRIFT', 'DEPENDENCY_PIN', 'DUPLICATE_NETWORK_PROPERTY', 'ENTRY_DB_BINDING', 'EXACT_PRIOR_PARTNER', 'FILES_BOOT_CHANGED', 'FILES_BYTE_LIMIT', 'FILES_COMPLETE_FINITE_FILE_WINDOW', 'FILES_COMPLETE_FINITE_JOURNAL_WINDOW', 'FILES_CURSOR_CONTINUITY', 'FILES_DEADLINE', 'FILES_DUPLICATE_JSON_FIELD', 'FILES_EMPTY_JOURNAL', 'FILES_END_CURSOR_MISSING', 'FILES_IDENTITY_CHANGED', 'FILES_INVALID_JSON', 'FILES_INVENTORY', 'FILES_INVENTORY_CHANGED', 'FILES_JOURNAL_PROCESS', 'FILES_JOURNAL_STDERR', 'FILES_JOURNAL_TIMEOUT', 'FILES_LATEST_IDENTITY', 'FILES_LIMITS', 'FILES_OBSERVED_CURSOR_MISSING', 'FILES_OBSERVED_TAIL_MISSING', 'FILES_PATTERNS', 'FILES_RECORD_IDENTITY', 'FILES_RECORD_LIMIT', 'FILES_REWRITTEN', 'FILES_SCAN_FAILED', 'FILES_SHORT_READ', 'FILES_SNAPSHOT_FAILED', 'FILES_START', 'FILES_START_CURSOR_MISSING', 'FILES_SYMLINK', 'FILES_TAIL_REGRESSED', 'FILES_TRUNCATED', 'FILES_UNDRAINED_JOURNAL_TAIL', 'FILES_UNDRAINED_TAIL', 'FILES_UNSAFE_FILE', 'FILES_UNSAFE_PATH', 'FILES_UNSUPPORTED_FIELD', 'FILES__BOOT_ID', 'FILES___CURSOR', 'FILE_TAIL_DURING_JOURNAL', 'FILE_WINDOW_INCOMPLETE', 'JOURNAL_BOOT_CHANGED', 'JOURNAL_BYTE_LIMIT', 'JOURNAL_COMPLETE_FINITE_FILE_WINDOW', 'JOURNAL_COMPLETE_FINITE_JOURNAL_WINDOW', 'JOURNAL_CURSOR_CONTINUITY', 'JOURNAL_DEADLINE', 'JOURNAL_DUPLICATE_JSON_FIELD', 'JOURNAL_EMPTY_JOURNAL', 'JOURNAL_END_CURSOR_MISSING', 'JOURNAL_IDENTITY_CHANGED', 'JOURNAL_INVALID_JSON', 'JOURNAL_INVENTORY', 'JOURNAL_INVENTORY_CHANGED', 'JOURNAL_JOURNAL_PROCESS', 'JOURNAL_JOURNAL_STDERR', 'JOURNAL_JOURNAL_TIMEOUT', 'JOURNAL_LATEST_IDENTITY', 'JOURNAL_LIMITS', 'JOURNAL_OBSERVED_CURSOR_MISSING', 'JOURNAL_OBSERVED_TAIL_MISSING', 'JOURNAL_PATTERNS', 'JOURNAL_RECORD_IDENTITY', 'JOURNAL_RECORD_LIMIT', 'JOURNAL_REWRITTEN', 'JOURNAL_SCAN_FAILED', 'JOURNAL_SHORT_READ', 'JOURNAL_SNAPSHOT_FAILED', 'JOURNAL_START', 'JOURNAL_START_CURSOR_MISSING', 'JOURNAL_STATUS', 'JOURNAL_SYMLINK', 'JOURNAL_TAIL_REGRESSED', 'JOURNAL_TRUNCATED', 'JOURNAL_UNDRAINED_JOURNAL_TAIL', 'JOURNAL_UNDRAINED_TAIL', 'JOURNAL_UNSAFE_FILE', 'JOURNAL_UNSAFE_PATH', 'JOURNAL_UNSUPPORTED_FIELD', 'JOURNAL_WINDOW_INCOMPLETE', 'JOURNAL__BOOT_ID', 'JOURNAL___CURSOR', 'LAB_IDENTITY', 'LAB_IP', 'LIST_IDENTITY', 'LOCAL_SOURCE_BINDING', 'MEDIA_SOURCE_PIN', 'NETWORK_POLICY', 'OBSERVATION_PIN', 'OBSERVED_PROFILE_SELECTION', 'ORIGINAL_ASSET_COUNT', 'OVERLAY_MANIFEST', 'OVERLAY_STAGE', 'OWNED_ASSET_ENTRY_BINDING', 'OWNED_ENTRY_BINDING', 'OWNED_LIST', 'OWNED_OBJECT_SHAPE', 'OWNED_PARTNER_BINDING', 'PATTERN_COUNT', 'PRIOR_ASSET_IDENTITY', 'PRIVATE_DIAGNOSTIC_PARENT', 'PRIVATE_MARKER_LOGGED', 'PRIVATE_SECRET_FORMAT', 'QUIET_WINDOW_NOT_ESTABLISHED', 'REHEARSAL_PIN', 'RUNTIME_PIN', 'SCAN_RESULT', 'SETTLE_PIN', 'SOURCE_AFTER', 'SOURCE_DRIFT', 'STORED_SOURCE_BYTES', 'SYNTHETIC_PARTNER_PROVENANCE', 'SYNTHETIC_PARTNER_STATE', 'UNIT', 'UNTIMED_ROUND_FAILED', 'USER_KS', 'VERSION_PROJECTION', 'WRONG_SECRET_CONTROL', 'UNEXPECTED_OR_DEPENDENCY_FAILURE']
SCANNER_CODES=['BOOT_CHANGED', 'BYTE_LIMIT', 'COMPLETE_FINITE_FILE_WINDOW', 'COMPLETE_FINITE_JOURNAL_WINDOW', 'CURSOR_CONTINUITY', 'DEADLINE', 'DUPLICATE_JSON_FIELD', 'EMPTY_JOURNAL', 'END_CURSOR_MISSING', 'IDENTITY_CHANGED', 'INVALID_JSON', 'INVENTORY', 'INVENTORY_CHANGED', 'JOURNAL_PROCESS', 'JOURNAL_STDERR', 'JOURNAL_TIMEOUT', 'LATEST_IDENTITY', 'LIMITS', 'OBSERVED_CURSOR_MISSING', 'OBSERVED_TAIL_MISSING', 'PATTERNS', 'RECORD_IDENTITY', 'RECORD_LIMIT', 'REWRITTEN', 'SCAN_FAILED', 'SHORT_READ', 'SNAPSHOT_FAILED', 'START', 'START_CURSOR_MISSING', 'SYMLINK', 'TAIL_REGRESSED', 'TRUNCATED', 'UNDRAINED_JOURNAL_TAIL', 'UNDRAINED_TAIL', 'UNSAFE_FILE', 'UNSAFE_PATH', 'UNSUPPORTED_FIELD', '_BOOT_ID', '__CURSOR']
def failure_projection(row):
 code=row.get('failure_code');phase=row.get('failure_stage')
 need(code in FAILURE_CODES and phase in ('PREFLIGHT','INVALID_NONCE_PRIVACY','USER_PRIVACY','API_ROUND','QUIET_SETTLE','MEDIA_PRIVACY','BATCH_PRIVACY','POSTCHECK'))
 out={'failure_code':code,'failure_stage':phase}
 if 'media_privacy_failure_class' in row:
  need(row['media_privacy_failure_class']=='FINITE_SCAN_INCOMPLETE' and row.get('media_privacy_failure_code') in FAILURE_CODES)
  out['failure_privacy']={'finite_scans_complete_and_zero':False,'class':'FINITE_SCAN_INCOMPLETE','code':row['media_privacy_failure_code']}
 if 'last_audit_quiet' in row:out['last_audit_quiet']=audit_quiet_projection(row['last_audit_quiet'])
 if 'match_provenance' in row:out['match_provenance']=provenance_projection(row['match_provenance'])
 if 'native_url_shape' in row:out['native_url_shape']=shape_projection(row['native_url_shape'])
 from assemble_v2 import privacy
 if 'media_failure_privacy' in row or 'media_failure_privacy_batches' in row:
  observed=row.get('media_failure_privacy_batches')
  batches=observed.get('batches') if type(observed) is dict else [row.get('media_failure_privacy')]
  passed=False
  try:
   need(type(batches) is list and 1<=len(batches)<=3)
   if observed is not None:round_projection({'round_privacy':observed})
   for item in batches:privacy(item)
   passed=True
  except Exception:pass
  out['failure_privacy']={'finite_scans_complete_and_zero':passed}

 if 'privacy_errors' in row:
  errors=row['privacy_errors'];need(type(errors) is list and len(errors)<=32)
  for value in errors:need(type(value) is dict and set(value)=={'phase','code','audit'} and value['phase'] in ('files_initial','journal','files_after_journal') and value['code'] in SCANNER_CODES and type(value['audit']) is int and 1<=value['audit']<=32)
  out['privacy_errors']=errors
 return out

def public_rows(raw):
 from assemble_v2 import assemble,ENV_KEYS
 rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
 need(0<len(rows)<=256 and all(type(row) is dict for row in rows))
 out=[]
 for row in rows:
  status=row.get('status')
  need(status in ('INCOMPLETE','FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE'))
  if status!='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE':
   # Deliberately reduced projection: arbitrary nested diagnostics are never copied.
   partial={'status':status}
   if status=='FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION':partial.update(failure_projection(row))
   if any(k in row for k in ('route_observation','playback_context','hls_manifest','hls_route')):partial.update(round_projection(row))
   out.append(partial);continue
  need(row.get('sources_before')==row.get('sources_after')==EXPECTED_SOURCES)
  env=dict.fromkeys(ENV_KEYS);env.update(vm_uuid=UUID,observed_readonly=True)
  validated=assemble(row,env)
  safe={k:row[k] for k in ('status','baseline_label','upload_attempted','wrong_secret_rejected','admin_escalation_rejected','source_sha256','stored_source_sha256','original_asset_id','file_sync_id','version_observations','entry_version_status','overlay_manifest_sha256','runtime_pins_verified','asset_version')}
  safe.update(fixture=validated['protocol_fixture'],profile=validated['profile'],sources_before=EXPECTED_SOURCES,sources_after=EXPECTED_SOURCES)
  for phase in ('invalid_nonce','user_privacy','media_privacy'):
   v=row[phase];safe[phase]={'files':{k:v['files'][k] for k in ('counts','status','uncovered_tail_bytes')},'journal':{k:v['journal'][k] for k in ('counts','status','cutoff_covered','complete')},'scope':'FINITE_OBSERVATION_WINDOW'}
  expected_tls={'scheme':'https','port':8443,'ca_sha256':'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef','tls_logs_in_every_inventory':True}
  need(row.get('tls_transport')==expected_tls and type(row['tls_transport']['port']) is int and row['tls_transport']['tls_logs_in_every_inventory'] is True)
  safe['tls_transport']=expected_tls
  safe['last_audit_quiet']=audit_quiet_projection(row['last_audit_quiet'])
  safe['match_provenance']=provenance_projection(row['match_provenance'])
  need(safe['match_provenance'] and all(not v['any_match'] and v['file_window_complete'] and v['journal_window_complete'] for v in safe['match_provenance']))
  safe.update(round_projection(row));need('round_privacy' in safe and 'quiet_window' in safe and 'playback_context' in safe and 'hls_manifest' in safe and 'hls_route' in safe)
  out.append(safe)
 return out

def main(check_only,output):
 if not check_only:need(output is not None and not os.path.lexists(output))
 blobs,host=check()
 if check_only:return {'status':'READ_ONLY_PREFLIGHT_PASSED','guest_execution':False,'approved_freeze':False}
 unit='baseline-freeze-'+secrets.token_hex(4)
 # Exclusive local intent precedes any guest staging. A consumed path is never retried.
 dest=Path(output);dest.mkdir(mode=0o700)
 intent={'status':'STAGING_INTENT','unit':unit,'stage':STAGE,'files':PINS,'host':host}
 with (dest/'intent.json').open('x') as f:json.dump(intent,f,sort_keys=True)
 payload={k:base64.b64encode(v).decode() for k,v in blobs.items()}
 stage_code=REMOTE_GUARD+'''import base64
payload='''+repr(payload)+'''
pins='''+repr(PINS)+'''
assert set(payload)==set(pins)=={'direct_content.py', 'media_get443.py', 'guest_hls_first.py', 'short_metadata.py', 'hls_source_r2.py', 'route_descriptor.py', 'rehearsal.py', 'observation_v2.py', 'protocol_v2.py', 'context_selected.py', 'settle.py', 'convergence.py', 'hls_first.py', 'context_urls.py', 'privacy_logs_r2.py', 'playback_context_r4.py', 'privacy_provenance.py', 'short_delivery443.py', 'url_privacy.py'}
values={k:base64.b64decode(v,validate=True) for k,v in payload.items()}
assert all(hashlib.sha256(v).hexdigest()==pins[k] for k,v in values.items())
stage.mkdir(mode=0o755)
for name,value in values.items():
 fd=os.open(stage/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
 with os.fdopen(fd,'wb') as f:f.write(value);f.flush();os.fsync(f.fileno())
 os.chmod(stage/name,0o444)
print('STAGED')
'''
 rc,raw,_=remote(stage_code);need(rc==0 and raw==b'STAGED\n')
 result={'status':'INCOMPLETE','guest_exit':None,'approved_freeze':False,'unit':unit,'files':PINS}
 failure_stage='CAPTURE'
 try:
  rc,raw,err=bounded(SSH+[unit_command(unit)],timeout=1130)
  result.update(guest_exit=rc,stderr_bytes=err,stdout_bytes=len(raw))
  failure_stage='PUBLIC_PROJECTION'
  result['phase_receipts']=public_rows(raw)
  failure_stage='TERMINAL_STATUS'
  need(rc!=0 or result['phase_receipts'][-1]['status']=='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE')
  result['status']='OBSERVATION_CAPTURED_NOT_APPROVED' if rc==0 else 'FAILED_OBSERVATION'
 except Exception:result.update(status='FAILED_OR_INCOMPLETE_CAPTURE',failure_stage=failure_stage)
 finally:
  try:
   rc,_,_=bounded(SSH+['sudo -n systemctl stop '+unit+'.service'],timeout=30)
   q,state,_=bounded(SSH+['systemctl is-active '+unit+'.service'],timeout=10)
   result['unit_inactive']=state.strip() in (b'inactive',b'unknown') and q in (3,4)
  except Exception:result['unit_inactive']=False
  if not result['unit_inactive']:result['status']='FAILED_CLEANUP'
  with (dest/'result.json').open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
 return {'status':result['status'],'guest_exit':result['guest_exit'],'unit_inactive':result['unit_inactive'],'approved_freeze':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--output');a=p.parse_args()
 try:
  r=main(a.check,a.output);print(json.dumps(r));raise SystemExit(0 if r['status'] in ('READ_ONLY_PREFLIGHT_PASSED','OBSERVATION_CAPTURED_NOT_APPROVED') else 2)
 except Exception:print('{"status":"RUNNER_REJECTED","approved_freeze":false}');raise SystemExit(2)

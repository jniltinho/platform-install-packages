"""Pure externally pinned observation join; no VM access or acceptance promotion."""
import argparse,hashlib,json,re,stat
from pathlib import Path
import assemble_v2 as a
from observation_v2 import need
UUID='9e954729-16f3-4eda-9db5-b94e5ada9e44'
PROFILE_SOURCE='9735aad64f31a3329de5844f9061da9f18f12e1b34787971d9ee360872443776'
WEB_RUNNER='4db6ccebda5874b896916a45103a50b4a411d599a175de98874b6afdd59dd288'
WEB_GUEST='9f84a50ff7aa74db30574d076c56486345c64059a4bb1f5ad397b6f71d4ae5cd'
OBS_FILES={'guest_v2.py':'6eaaf54dd2365eb8093952631234fed1711badd607976c0e6b39115f0a6994f8','observation_v2.py':'ec32386df1c745f5754ece19f3127f6da85415e644c8556e6c07666b2ea1abc5'}
WEB_MODULES=set('Core|FFI|PDO|Phar|Reflection|SPL|SimpleXML|Zend OPcache|apache2handler|apcu|calendar|ctype|curl|date|dom|exif|fileinfo|filter|ftp|gd|gettext|gmp|hash|iconv|intl|json|ldap|libxml|mbstring|memcache|mysqli|mysqlnd|openssl|pcre|pdo_mysql|posix|readline|session|shmop|sockets|sodium|ssh2|standard|sysvmsg|sysvsem|sysvshm|tokenizer|xml|xmlreader|xmlwriter|xsl|zip|zlib'.split('|'))
def assemble(observation,environment,profile,web):
 need(observation.get('status')=='OBSERVATION_CAPTURED_NOT_APPROVED' and type(observation.get('guest_exit')) is int and observation['guest_exit']==0 and observation.get('unit_inactive') is True and observation.get('files')==OBS_FILES,'OBS_CAPTURE')
 rows=observation.get('phase_receipts');need(type(rows) is list and 0<len(rows)<=256,'OBS_ROWS')
 env=environment.get('environment');need(type(env) is dict and env.get('vm_uuid')==UUID and env.get('cpus')==4 and env.get('memory_mib')==8192,'ENV_TARGET')
 out=a.assemble(rows[-1],env)
 need(profile.get('source_sha256')==PROFILE_SOURCE and type(profile.get('exit_status')) is int and profile['exit_status']==0 and type(profile.get('stderr_bytes')) is int and profile['stderr_bytes']==0,'PROFILE_RECEIPT')
 p=profile.get('observation');need(type(p) is dict and set(p)=={'schema','status','entry_id','entry_partner_id','selected_profile_id','profile_partner_id','profile_status','profile_type','profile_not_deleted','configured_flavor_ids','select_count','db_identity_verified','api_authorization_verified','full_acceptance'},'PROFILE_SCHEMA')
 need(p['schema']==1 and p['status']=='READ_ONLY_STORED_PROFILE_OBSERVED' and p['entry_id']=='0_wzmt2sfy' and p['entry_partner_id']==102 and p['selected_profile_id']==14 and p['profile_partner_id']==102 and p['profile_status']==2 and p['profile_type']==1 and p['profile_not_deleted'] is True and p['select_count']==5 and p['db_identity_verified'] is True and p['api_authorization_verified'] is False and p['full_acceptance'] is False,'PROFILE_JOIN')
 for key in ('schema','entry_partner_id','selected_profile_id','profile_partner_id','profile_status','profile_type','select_count'):need(type(p[key]) is int,'PROFILE_TYPES')
 need(type(p['configured_flavor_ids']) is list and p['configured_flavor_ids']==[0,2,3,4,5,6,7,19] and all(type(n) is int for n in p['configured_flavor_ids']),'CONFIGURED_FLAVORS')
 need(out['profile']['selected_profile_id']==14,'API_STORED_PROFILE_JOIN')
 need(web.get('status')=='CURRENT_WEB_OBSERVATION_CAPTURED' and type(web.get('guest_exit')) is int and web['guest_exit']==0 and web.get('unit_inactive') is True and web.get('host_unchanged') is True and web.get('runner_sha256')==WEB_RUNNER and web.get('source_pins',{}).get('tools/php83/baseline-web-runtime-r1/guest.py')==WEB_GUEST,'WEB_RECEIPT')
 need(web.get('host')=={'UUID':UUID,'name':'kaltura-php74-noble-baseline','VMState':'running','cpus':'4','memory':'8192'},'WEB_HOST')
 w=web.get('provider');need(type(w) is dict and w.get('status')=='CURRENT_APACHE_PHP74_OBSERVED_OWN_PROBE_REMOVED' and w.get('probe_removed') is True and w.get('nonce_verified') is True and w.get('app_credentials_read') is False and w.get('sql_executed') is False and w.get('version')=='7.4.33' and w.get('sapi')=='apache2handler' and w.get('ini_file')=='/etc/php/7.4/apache2/php.ini','WEB_PROVIDER')
 modules=w.get('modules');need(type(modules) is list and len(modules)==len(WEB_MODULES) and all(type(v) is str for v in modules) and set(modules)==WEB_MODULES,'OBSERVED_MODULE_SET')
 out.update(status='UNTIMED_API_REHEARSAL_INPUTS_ASSEMBLED_NOT_ACCEPTED',apache_runtime_current={'version':'7.4.33','sapi':'apache2handler','ini_file':'/etc/php/7.4/apache2/php.ini','modules':sorted(WEB_MODULES),'soap_observed':False},stored_profile=p,api_profile_authorization_verified=False,performance_measurement_ready=False,full_acceptance=False,approved_freeze=False)
 out['protocol_plan']={'schema':2,'calls_per_round':100,'session_start':34,'media_list':33,'media_get':33,'media_get_selection':-1,'warmup_rounds_required':2,'measured_rounds_required_minimum':5,'source_fixtures_required':['SHORT_10S_640X360_25FPS','FULLHD_60S_1920X1080_60FPS'],'timing_statistics':['median','nearest_rank_p95'],'regression_review_threshold_percent':20}
 out['next_execution']={'kind':'ONE_UNTIMED_API_PROTOCOL_REHEARSAL','mutations':'USER_SESSION_CREATION_ONLY_NO_UPLOAD_PROFILE_CHANGE','requires':'NEW_REVIEWED_PRIVACY_WRAPPED_NATIVE_V2_RUNNER','benchmark_acceptance':False}
 out['remaining']=['Original box archive checksum/provenance unresolved; do not substitute an arbitrary newer box','Coherent current recovery checkpoint not attested in supplied environment','Candidate disk/controller/runtime profile parity and host contention not established','Current API profile authorization remains unresolved; SQL only proves stored configuration','Native V2 100-call rehearsal not executed by this assembly','Short and fullHD upload/worker/stream plus UI/session flow and two warmups/five measured rounds still required','Published-package provenance and approved privacy overlay must remain distinct','Observed web modules exclude SOAP; exercised extension requirements/parity not inferred']
 return out
def read(path,pin):
 p=Path(path);st=p.lstat();need(stat.S_ISREG(st.st_mode) and st.st_size<=8*1024*1024,'INPUT_FILE');raw=p.read_bytes();need(hashlib.sha256(raw).hexdigest()==pin,'EXTERNAL_PIN');return json.loads(raw)
def main():
 p=argparse.ArgumentParser()
 for n in ('observation','environment','profile','web'):p.add_argument('--'+n,required=True);p.add_argument('--'+n+'-sha256',required=True)
 p.add_argument('--output',required=True);args=p.parse_args();values=[read(getattr(args,n),getattr(args,n+'_sha256')) for n in ('observation','environment','profile','web')];out=assemble(*values)
 with Path(args.output).open('x') as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
if __name__=='__main__':main()

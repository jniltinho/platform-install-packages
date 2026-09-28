"""Preparation/read-only guest simulation only. This program has NO installer mode."""
import argparse,hashlib,json,os,pathlib,re,socket,subprocess
HOST='kaltura-php83-lab';IP='192.168.56.83'
PACKAGES={'kaltura-postinst','kaltura-ffmpeg','kaltura-base','kaltura-front','kaltura-html5-studio3','kaltura-ffmpeg-aux','kaltura-server','kaltura-batch','kaltura-nginx','kaltura-html5-analytics','kaltura-html5-studio','kaltura-html5lib','kaltura-elasticsearch','kaltura-html5lib3','kaltura-sphinx','kaltura-kmcng','kaltura-db'}
ORDER=[['kaltura-postinst','kaltura-base'],['kaltura-kmcng','kaltura-html5lib','kaltura-html5lib3','kaltura-html5-studio','kaltura-html5-studio3','kaltura-html5-analytics'],['kaltura-front'],['kaltura-sphinx'],['kaltura-db'],['kaltura-batch'],['kaltura-nginx'],['kaltura-elasticsearch'],['kaltura-server']]
EXTERNAL={'package':'elasticsearch','version':'7.17.29','architecture':'amd64','sha256':'4a4ecb74e77a6b04a35c5c007d1ec212e99979d300f1fe281d5225562a16cb73'}
HEX=re.compile(r'^[0-9a-f]{64}$')
def need(ok,code):
 if not ok:raise ValueError(code)
def sha(b):return hashlib.sha256(b).hexdigest()
def validate(c):
 need(c.get('status')=='REVIEWED_INPUTS_READY','PENDING_INPUTS_NO_ACTION')
 need(type(c.get('schema')) is int and c['schema']==1,'SCHEMA')
 need(c.get('target')=={'hostname':HOST,'ip':IP},'TARGET')
 rows=c.get('packages',[]);need(len(rows)==17 and {r['package'] for r in rows}==PACKAGES,'PACKAGE_SET')
 for r in rows:
  need(type(r.get('version')) is str and '+php83lab' in r['version'],'PRIVATE_VERSION')
  p=pathlib.PurePosixPath(r['path']);need(p.is_absolute() and '..' not in p.parts and str(p).startswith('/var/lib/kaltura-php83-pilot/packages/') and p.suffix=='.deb','PACKAGE_PATH')
  need(type(r.get('sha256')) is str and HEX.fullmatch(r['sha256']) is not None,'PACKAGE_PIN')
 need(len({r['path'] for r in rows})==17,'DUPLICATE_PATH')
 external=c.get('external_debs',[]);need(len(external)==1,'EXTERNAL_DEB_COUNT')
 e=external[0];need({k:e.get(k) for k in EXTERNAL}==EXTERNAL,'EXTERNAL_DEB_IDENTITY')
 p=pathlib.PurePosixPath(e['path']);need(p.is_absolute() and '..' not in p.parts and str(p).startswith('/var/lib/kaltura-php83-pilot/packages-external/') and p.suffix=='.deb','EXTERNAL_DEB_PATH')
 for key in ['private_deb_verification','dependency_origins','recovery_point']:
  v=c.get(key,{});need(type(v.get('sha256')) is str and HEX.fullmatch(v['sha256']) is not None and type(v.get('path')) is str and v['path'].startswith('/var/lib/kaltura-php83-pilot/proofs/'),'REQUIRED_PROOF_'+key)
 runtime=c.get('runtime_files',[]);need(bool(runtime) and len({r['path'] for r in runtime})==len(runtime),'RUNTIME_CLOSURE')
 need(any(r['path']=='/usr/bin/php8.3' for r in runtime),'NATIVE_PHP_REQUIRED')
 for r in runtime:need(r['path'].startswith(('/usr/bin/','/usr/lib/','/lib/')) and '..' not in pathlib.PurePosixPath(r['path']).parts and HEX.fullmatch(r.get('sha256','')) is not None,'RUNTIME_PIN')
 need(c.get('php_package_version')=='8.3.6-0ubuntu0.24.04.11','PHP_VERSION')
 return c

def plan(c):
 # A pending plan is printable; it is never an executable authorization or input attestation.
 return {'status':'LOCAL_RECIPE_ONLY_NO_INSTALLER','target':{'hostname':HOST,'ip':IP},'inputs_ready':c.get('status')=='REVIEWED_INPUTS_READY','legacy_order':ORDER,'dependency_only_packages':['kaltura-ffmpeg','kaltura-ffmpeg-aux'],'steps':[
 'Verify independently authenticated DEB hashes, exact native provider/dependency origins and recovery-point receipt; unknown/PENDING blocks before guest actions.',
 'Read-only hostname/IP/root/empty app+datadir/root .my.cnf/.mylogin.cnf guards; verify installed runtime file hashes and native PHP package revision.',
 'APT --simulate all17 local private DEBs plus the single pinned official Elasticsearch DEB; retain complete private solver output and public exit/hash. Resolve origins and reject every PHP74/foreign runtime or removal before mutation.',
 'Future reviewed executor: create new root0700 private state; generate fresh credentials there, never argv or exported env; debconf via stdin only.',
 'Future reviewed executor: prevent automatic service start during dependency transaction; write lower_case_table_names=1 BEFORE any MariaDB package postinst or datadir initialization. Abort if datadir already exists. No legacy mysql-settings fallback.',
 'Install matched native dependencies and pinned local Elasticsearch/ICU files only after authenticated origin review. Never run legacy PPA bootstrap or live curl prerequisite hook.',
 'Initialize fresh MariaDB using approved config; establish private socket/@@datadir before SQL. Root/app/admin credentials only through private defaults files and SQL stdin.',
 'Normal APT package transactions in listed legacy order, no manual hooks/dpkg force; verify solver-selected prerequisites. Capture all exits, private logs and installation canary windows.',
 'On error, stop exact owned services; retain failed evidence then restore pre-install VM recovery point. Do not erase logs or call destructive legacy drop-db.',
 'Installation privacy, CLI/web/worker/provider/cache gates must pass before nonce/USER/media. This recipe implements NONE of those acceptance gates.'
 ],'mutation_implemented':False,'auth_implemented':False,'rollback_implemented':False}

def checked_file(path,pin):
 p=pathlib.Path(path);need(p.is_file() and not p.is_symlink(),'INPUT_REGULAR');need(sha(p.read_bytes())==pin,'INPUT_DRIFT')

def simulation_args(c):
 validate(c)
 return ['apt-get','--simulate','--no-remove','--no-install-recommends','install']+[r['path'] for r in sorted(c['packages'],key=lambda x:x['package'])]+[c['external_debs'][0]['path']]

def guest_preflight(c):
 validate(c) # MUST precede any subprocess, hostname inspection or simulation.
 need(os.geteuid()==0 and socket.gethostname()==HOST,'LAB_IDENTITY')
 def command(args):
  p=subprocess.run(args,capture_output=True,timeout=120);need(p.returncode==0,'READONLY_COMMAND_FAILED');return p.stdout
 addresses=json.loads(command(['ip','-j','-4','addr']));ips={x.get('local') for i in addresses for x in i.get('addr_info',[])}
 need(IP in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.74'}),'LAB_ADDRESS')
 for name in ['/opt/kaltura/app','/var/lib/mysql','/root/.my.cnf','/root/.mylogin.cnf']:
  need(not os.path.lexists(name),'FRESH_STATE_REQUIRED')
 for r in c['packages']+c['external_debs']+c['runtime_files']+[c[k] for k in ['private_deb_verification','dependency_origins','recovery_point']]:checked_file(r['path'],r['sha256'])
 e=c['external_debs'][0]
 for key,field in [('package','Package'),('version','Version'),('architecture','Architecture')]:
  need(command(['dpkg-deb','-f',e['path'],field]).decode().strip()==e[key],'EXTERNAL_CONTROL_IDENTITY')
 version=command(['dpkg-query','-W','-f=${Version}','php8.3-cli']).decode();need(version==c['php_package_version'],'NATIVE_REVISION_DRIFT')
 installed=command(['dpkg-query','-W','-f=${binary:Package}\t${db:Status-Abbrev}\n']).decode()
 need(not any(line.startswith(('php7.4','libapache2-mod-php7.4')) and '\tii ' in line for line in installed.splitlines()),'PHP74_INSTALLED')
 # This does not authorize installation: full solver output needs provider/origin review.
 args=simulation_args(c)
 p=subprocess.run(args,capture_output=True,timeout=180)
 solver=p.stdout+p.stderr
 need(not re.search(rb'\b(?:php7\.4|libapache2-mod-php7\.4)',solver),'PHP74_SOLVER')
 return {'status':'SIMULATED_ONLY_NOT_INSTALL_APPROVED' if p.returncode==0 else 'APT_SIMULATION_FAILED','apt_exit':p.returncode,'stdout_sha256':sha(p.stdout),'stderr_sha256':sha(p.stderr),'private_packages':17,'external_packages':1,'package_arguments':18,'native_php_revision':version,'mutation':False,'dependency_origins_accepted':False},p.stdout,p.stderr

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['plan','guest-preflight']);p.add_argument('--contract',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();need(not a.output.exists(),'FRESH_OUTPUT');c=json.loads(a.contract.read_text())
 if a.mode=='plan':result=plan(c);streams=[]
 else:
  validate(c);result,out,err=guest_preflight(c);streams=[('apt.stdout',out),('apt.stderr',err)]
 a.output.mkdir(mode=0o700,parents=False)
 for name,raw in streams:
  fd=os.open(a.output/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(raw)
 (a.output/'report.json').write_text(json.dumps(result,indent=2)+'\n');os.chmod(a.output/'report.json',0o600)
 print(json.dumps({'status':result['status'],'mutation':False}))
if __name__=='__main__':main()

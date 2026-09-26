#!/usr/bin/env python3
"""Read-only public-artifact inventory; NOT web/provider/source attestation."""
import hashlib,json,os
from pathlib import Path
import re,socket,subprocess
def command(args):
    r=subprocess.run(args,capture_output=True,timeout=15)
    if r.returncode:raise RuntimeError('Inventory command failed')
    return r.stdout.decode('utf-8')
def digest(path):
    p=Path(path)
    if not p.is_file():return None
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def packages(text):
    installed=[];other=[]
    for line in text.splitlines():
        fields=line.split('\t')
        if len(fields)!=4 or not re.fullmatch(r'[A-Za-z? ]{3}',fields[0]) or not re.fullmatch(r'[A-Za-z0-9.+:~_-]+',fields[1]):
            raise RuntimeError('Unexpected package inventory')
        status,name,version,arch=fields
        if status=='ii ':
            if any(not re.fullmatch(r'[A-Za-z0-9.+:~_-]+',x) for x in [version,arch]):raise RuntimeError('Unexpected package inventory')
            installed.append([name,version,arch])
        else:other.append({'package':name,'dpkg_status':status})
    if not installed:raise RuntimeError('Unexpected package inventory')
    return installed,other
def main():
    if socket.gethostname()!='kaltura-php74-baseline':raise RuntimeError('Wrong guest')
    addresses=json.loads(command(['ip','-j','-4','addr','show']))
    ips={a['local'] for link in addresses for a in link.get('addr_info',[]) if 'local' in a}
    if '192.168.56.74' not in ips or any(ip in ips for ip in ['192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83']):raise RuntimeError('Wrong network identity')
    php=Path('/usr/bin/php7.4')
    version=command([str(php),'-n','-r','echo PHP_VERSION;']).strip()
    if not re.fullmatch(r'7\.4\.\d+',version):raise RuntimeError('Wrong CLI runtime')
    modules_text=command([str(php),'-m'])
    modules=[x.strip() for x in modules_text.splitlines() if re.fullmatch(r'[A-Za-z0-9_ ]+',x.strip()) and x.strip()]
    fmt='-f='+chr(36)+'{db:Status-Abbrev}\t'+chr(36)+'{Package}\t'+chr(36)+'{Version}\t'+chr(36)+'{Architecture}\n'
    versions=command(['dpkg-query','-W',fmt,'php7.4*','kaltura*'])
    package_rows,not_installed=packages(versions)
    public_files=['/opt/kaltura-baseline/repo.tar.gz','/opt/kaltura-baseline/install-aio.sh','/usr/bin/php7.4','/usr/lib/apache2/modules/libphp7.4.so','/etc/apache2/mods-enabled/php7.4.load','/etc/apache2/mods-enabled/php7.4.conf']
    public={p:digest(p) for p in public_files}
    app=Path('/opt/kaltura/app')
    relative=['api_v3/services/MediaService.php','api_v3/lib/KalturaEntryService.php','api_v3/lib/KalturaJsonSerializer.php','api_v3/lib/KalturaSerializer.php','alpha/lib/model/entry.php']
    sources={p:digest(app/p) for p in relative}
    return {'status':'READ_ONLY_PUBLIC_INVENTORY_NOT_ATTESTATION','hostname':socket.gethostname(),'target_ip':'192.168.56.74','cli_version':version,'cli_default_module_names':modules,'package_versions':package_rows,'noninstalled_dpkg_matches':not_installed,'public_file_sha256':public,'critical_source_subset_sha256':sources,'missing_inventory_files':[k for k,v in dict(public,**sources).items() if v is None],'critical_source_root_resolved':str(app.resolve()),'cpus':os.cpu_count(),'web_runtime_proven':False,'source_manifest_complete':False,'private_config_read':False,'credential_read':False,'sql_executed':False,'http_requests':0,'baseline_acceptance':False}
if __name__=='__main__':
    try:print(json.dumps(main(),sort_keys=True))
    except Exception:
        print('Public baseline inventory rejected',file=__import__('sys').stderr)
        raise SystemExit(1)

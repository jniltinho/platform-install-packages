#!/usr/bin/env python3
"""Authorized exclusive-lab four-process observation; no SQL or patch selection."""
import hashlib,io,json,shlex,subprocess,tarfile,tempfile
from pathlib import Path
import prepare,compare
REPO=Path(__file__).resolve().parents[3]
OUT=REPO/'doc/php83/evidence/criteria-marker'
STAGE='/home/vagrant/php-criteria-marker'

def remote(runtime,command,data=None):
    alias={'74':'baseline74','83':'php83'}[runtime]
    return subprocess.run(['ssh','-T','-F','/tmp/kaltura-php'+runtime+'-ssh.conf',alias,command],input=data,capture_output=True,timeout=120)
def checked(runtime,command,data=None):
    p=remote(runtime,command,data)
    if p.returncode: raise RuntimeError(command+': '+p.stderr.decode())
    return p.stdout.decode()
def runtime_identity(runtime):
    php='/usr/bin/php'+{'74':'7.4','83':'8.3'}[runtime]
    opts=' -d extension=json' if runtime=='74' else ''
    code='echo json_encode(["version"=>PHP_VERSION,"modules"=>get_loaded_extensions(),"extension_dir"=>ini_get("extension_dir"),"ini"=>php_ini_loaded_file()]);'
    info=json.loads(checked(runtime,php+' -n'+opts+' -r '+shlex.quote(code)))
    program='''import hashlib,json,pathlib,subprocess,re
php=PATH
paths={str(pathlib.Path(php).resolve())}
for line in subprocess.check_output(['ldd',php],text=True).splitlines():
 for x in re.findall(r'(/[^\\s()]+)',line):
  if pathlib.Path(x).is_file(): paths.add(str(pathlib.Path(x).resolve()))
EXTRA
print(json.dumps({p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in sorted(paths)}))'''.replace('PATH',repr(php)).replace('EXTRA',"paths.add("+repr(info['extension_dir']+'/json.so')+")" if runtime=='74' else '')
    return {'php':info,'files':json.loads(checked(runtime,'python3 -c '+shlex.quote(program)))}
def main():
    report=OUT/'primary.json'
    if report.exists(): raise ValueError('Refuse existing evidence')
    records=[]; result={'status':'INCOMPLETE','records':records,'patch_selected':False,'application_acceptance':False}
    report.write_text(json.dumps(result,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='criteria-marker-stage-') as t:
        base=Path(t)/'fixture';ids=prepare.prepare(Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip'),base)
        raw=(base/'identities.json').read_bytes();pin=hashlib.sha256(raw).hexdigest();result['identities']=ids;result['identities_sha256']=pin
        expected=dict(ids['files'],**{'identities.json':pin})
        archive=io.BytesIO()
        with tarfile.open(fileobj=archive,mode='w') as tar:
            for f in sorted(base.iterdir()):tar.add(f,arcname=f.name)
        result['labs']={}
        for runtime in ['74','83']:
            hostname={'74':'kaltura-php74-baseline','83':'kaltura-php83-lab'}[runtime]
            command='test "$(hostname)" = '+hostname+' && mkdir '+STAGE+' && tar -xf - -C '+STAGE+' && sudo chown -R root:root '+STAGE+' && sudo chmod -R a-w '+STAGE
            checked(runtime,command,archive.getvalue())
            def source():
                data=checked(runtime,'cd '+STAGE+' && sha256sum '+' '.join(expected))
                actual={l.split()[1]:l.split()[0] for l in data.splitlines()}
                if actual!=expected:raise ValueError('Parent source identity mismatch')
                return actual
            before=source();rb=runtime_identity(runtime)
            for variant in ['original','declaration']:
                command='bash '+STAGE+'/run.sh '+variant+' '+pin
                p=remote(runtime,command);stdout=p.stdout.decode();stderr=p.stderr.decode()
                prefix=OUT/('primary-'+variant+runtime)
                prefix.with_suffix('.stdout').write_text(stdout);prefix.with_suffix('.stderr').write_text(stderr);prefix.with_suffix('.exit').write_text(str(p.returncode)+'\n')
                try:body=json.loads(stdout)
                except ValueError:body=None
                records.append({'mode':variant+runtime,'command':command,'exit':p.returncode,'stdout':stdout,'stderr':stderr,'body':body})
                report.write_text(json.dumps(result,indent=2)+'\n')
            after=source();ra=runtime_identity(runtime)
            if rb!=ra:raise ValueError('Runtime changed')
            result['labs'][runtime]={'source_before':before,'source_after':after,'runtime_before':rb,'runtime_after':ra}
            report.write_text(json.dumps(result,indent=2)+'\n')
        result['status']='OBSERVATIONS_COLLECTED'
        try:result['comparison']=compare.validate(records,ids)
        except Exception as e:result['comparison_error']=str(e);result['status']='OBSERVATIONS_COMPARISON_FAILED'
        result['collector_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        report.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'status':result['status'],'comparison_error':result.get('comparison_error'),'exits':[r['exit'] for r in records]}))
if __name__=='__main__':main()

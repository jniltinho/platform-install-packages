#!/usr/bin/env python3
"""Exclusive authorized native83 stage and four bounded composition observations."""
import hashlib,io,json,shlex,subprocess,tarfile,tempfile
from pathlib import Path
import fixture,prepare,validate
REPO=Path(__file__).resolve().parents[3]
OUT=REPO/'doc/php83/evidence/criteria-selection'
STAGE='/home/vagrant/php-criteria-composition-v1'
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
    report=OUT/'composition-primary.json'
    if report.exists():raise ValueError('Refuse existing evidence')
    result={'status':'INCOMPLETE','records':[],'patch_selected':False,'application_acceptance':False}
    report.write_text(json.dumps(result,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='criteria-composition-') as t:
        base=Path(t)/'fixture'
        ids=fixture.build(Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip'),REPO.parent/'platform-install-packages-php83-artifacts/exp11/Rigel-18.20.0-php83-experimental.exp11.zip',base)
        raw=(base/'identities.json').read_bytes();pin=prepare.sha(raw)
        (OUT/'composition-identities83.json').write_bytes(raw)
        expected=dict(ids['files'],**{'identities.json':pin})
        archive=io.BytesIO()
        with tarfile.open(fileobj=archive,mode='w') as tar:
            for f in sorted(base.iterdir()):tar.add(f,arcname=f.name)
        checked('83','test "$(hostname)" = kaltura-php83-lab && mkdir '+STAGE+' && tar -xf - -C '+STAGE+' && sudo chown -R root:root '+STAGE+' && sudo chmod -R a-w '+STAGE,archive.getvalue())
        def source():
            actual={l.split()[1]:l.split()[0] for l in checked('83','cd '+STAGE+' && sha256sum '+' '.join(expected)).splitlines()}
            if actual!=expected:raise ValueError('Parent source hash mismatch')
            return actual
        before=source();rb=runtime_identity('83')
        prior=json.loads((REPO/'doc/php83/evidence/criteria-marker/attribute/primary.json').read_text())['labs']['83']['runtime_before']
        if rb!=prior:raise ValueError('Runtime differs from recorded attribute cycle')
        result['identities']=ids;result['identities_sha256']=pin;result['source_before']=before;result['runtime_before']=rb
        try:
            for mode in validate.MODES:
                variant,corpus=mode.split('-');command='bash '+STAGE+'/run.sh '+variant+' '+corpus+' '+pin;p=remote('83',command)
                stdout=p.stdout.decode();stderr=p.stderr.decode();prefix=OUT/('composition-primary-'+mode)
                prefix.with_suffix('.stdout').write_text(stdout);prefix.with_suffix('.stderr').write_text(stderr);prefix.with_suffix('.exit').write_text(str(p.returncode)+'\n')
                try:body=json.loads(stdout)
                except ValueError:body=None
                result['records'].append({'mode':mode,'command':command,'exit':p.returncode,'stdout':stdout,'stderr':stderr,'body':body})
                report.write_text(json.dumps(result,indent=2)+'\n')
        finally:
            result['source_after']=source();result['runtime_after']=runtime_identity('83')
            report.write_text(json.dumps(result,indent=2)+'\n')
        if result['runtime_after']!=rb:raise ValueError('Runtime changed')
        try:result['comparison']=validate.validate(result['records'],ids);result['status']='BOUNDED_COMPOSITION_PASS'
        except Exception as e:result['status']='OBSERVATIONS_COMPARISON_FAILED';result['comparison_error']=str(e)
        report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'error':result.get('comparison_error'),'exits':[r['exit'] for r in result['records']]}))
if __name__=='__main__':main()

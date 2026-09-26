"""Versioned four-target policy, original and exp14; never installs or builds ZIPs."""
import argparse, importlib.util, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('frozen_logcopy',HERE.parent/'prepare.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
PIN='459feaf9caf2abe55963dce0cac51b8b593e4ff1b46d2eaf9cb7d5c3f13f62a1'
WRITER='infra/log/KalturaSerializableStream.php'
TARGETS=old.TARGETS+[WRITER]
def transform(path,raw):
    if path==WRITER:
        if b'throwableForLog' in raw: raise ValueError('Already transformed')
        return old.replace_once(raw,b'\tprotected function initStream()',
            (HERE/'writer-methods.php.inc').read_bytes()+b'\tprotected function initStream()')
    out=old.transform(path,raw)
    if path==old.TARGETS[0]:
        if out.count(b'if(!$message instanceof Exception)')!=3:raise ValueError('Throwable guard anchor drift')
        out=out.replace(b'if(!$message instanceof Exception)',b'if(!$message instanceof Throwable)')
    return out

def prepare(original,candidate,output):
    if output.exists():raise ValueError('Fresh output required')
    inputs={'original':old.archive(original,old.UPSTREAM,TARGETS),'exp14':old.archive(candidate,PIN,TARGETS)}
    rows=[];writes={}
    for version,files in inputs.items():
        for path,before in files.items():
            after=transform(path,before)
            patch=old.patch_bytes(path,before,after)
            old.strict_replay(path,before,patch,after)
            cumulative=old.patch_bytes(path,inputs['original'][path],after)
            old.strict_replay(path,inputs['original'][path],cumulative,after)
            name=version+'/'+path.replace('/','__')
            writes[name+'.patch']=patch;writes[name+'.cumulative.patch']=cumulative
            writes[version+'/source/'+path]=after
            rows.append({'version':version,'path':path,'before_sha256':old.sha(before),'after_sha256':old.sha(after),
                'patch':name+'.patch','patch_sha256':old.sha(patch),'cumulative_patch':name+'.cumulative.patch','cumulative_sha256':old.sha(cumulative)})
    result={'status':'PREPARED_NOT_DEPLOYED','original_sha256':old.UPSTREAM,'exp14_sha256':PIN,'targets':rows,
        'helpers':{str(p.relative_to(HERE.parent)):old.sha(p.read_bytes()) for p in [HERE/'prepare.py',HERE/'writer-methods.php.inc',HERE.parent/'prepare.py',HERE.parent/'log-copy-methods.php.inc']},
        'policy':'display copies only; structural Throwable arguments; retain intrinsic messages',
        'requires_effective_configuration_audit':True,'privacy_acceptance':False,'native_executed':False}
    output.mkdir(parents=True)
    for name,data in writes.items():
        p=output/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    (output/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    print(json.dumps(prepare(a.original,a.candidate,a.output),indent=2))

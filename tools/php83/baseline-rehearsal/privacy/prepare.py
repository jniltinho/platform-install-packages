#!/usr/bin/env python3
"""Prepare source-pinned log-copy experiments only. Never deploy or build a ZIP."""
import argparse,difflib,hashlib,io,json,subprocess,tempfile,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
UPSTREAM='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
EXP12='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
TARGETS=['infra/log/KalturaLog.php','api_v3/lib/KalturaFrontController.php','api_v3/lib/KalturaDispatcher.php']
BEFORE={'infra/log/KalturaLog.php':'9b7a7c3dd37616ffd2ac9720ece862641c43bb687a2db4e8fc9cbcb259ff5449','api_v3/lib/KalturaFrontController.php':'5f2eeffe526d4a0ee245b6f10f4e9600e0f7c8bcb4a52eef41e3a66bbd9ab7a1'}
PRIOR={'infra/log/KalturaLog.php':'dd2a01851114e821a88f266dd060e55a80d7cd795001369c9c14e7d2a794381f','api_v3/lib/KalturaFrontController.php':'189607dca3b5ef33270d8e4dfe081daf6a76f39d5fd49066ee0b83f24c62d71a'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def replace_once(raw,old,new):
    if raw.count(old)!=1:raise ValueError('Exact source anchor changed')
    return raw.replace(old,new,1)
def transform(path,raw):
    if path not in TARGETS:raise ValueError('Unknown target')
    if b'paramsForLog' in raw or b'argumentsForLog' in raw:raise ValueError('Already transformed')
    if path==TARGETS[0]:
        return replace_once(raw,b'\tpublic static function isInitialized()', (HERE/'log-copy-methods.php.inc').read_bytes()+b'\tpublic static function isInitialized()')
    if path==TARGETS[1]:
        raw=replace_once(raw,b'print_r($this->params, true)',b'print_r(KalturaLog::paramsForLog($this->params), true)')
        return replace_once(raw,b"'ks' => kCurrentContext::$ks,",b"'ks' => KalturaLog::sensitiveValueForLog(kCurrentContext::$ks),")
    return replace_once(raw,b'print_r($this->arguments, true)',b'print_r(KalturaLog::argumentsForLog($this->arguments, $actionParams), true)')
def archive(path,pin,members=None):
    raw=Path(path).read_bytes()
    if sha(raw)!=pin:raise ValueError('Archive drift')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Duplicate members')
        values={}
        for name in (TARGETS if members is None else members):
            info=z.getinfo('server-Rigel-18.20.0/'+name)
            if (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Symlink source')
            values[name]=z.read(info)
    return values
def patch_bytes(path,before,after):
    return ''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),'a/'+path,'b/'+path)).encode()
def strict_replay(path,before,patch,after):
    with tempfile.TemporaryDirectory(prefix='privacy-local-replay-') as tmp:
        target=Path(tmp)/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
        p=subprocess.run(['patch','--batch','--fuzz=0','-p1'],cwd=tmp,input=patch,capture_output=True)
        diagnostics=(p.stdout+p.stderr).lower()
        if p.returncode or b'offset' in diagnostics or b'fuzz' in diagnostics or target.read_bytes()!=after:raise ValueError('Strict patch replay failed')
def prepare(original,exp12,output):
    output=Path(output)
    if output.exists():raise ValueError('Refuse existing output')
    base=archive(original,UPSTREAM);prior=archive(exp12,EXP12)
    for path,pin in BEFORE.items():
        if sha(base[path])!=pin or sha(prior[path])!=PRIOR[path]:raise ValueError('Known target drift')
    if base[TARGETS[2]]!=prior[TARGETS[2]]:raise ValueError('Dispatcher prior drift')
    records=[];writes={}
    for variant,inputs in [('baseline74-policy',base),('exp12-policy',prior)]:
        for path,raw in inputs.items():
            after=transform(path,raw);delta=patch_bytes(path,raw,after);cumulative=patch_bytes(path,base[path],after)
            strict_replay(path,raw,delta,after);strict_replay(path,base[path],cumulative,after)
            key=variant+'/'+path.replace('/','__')
            writes[key+'.delta.patch']=delta;writes[key+'.cumulative.patch']=cumulative;writes[variant+'/source/'+path]=after
            records.append({'variant':variant,'path':path,'original_sha256':sha(base[path]),'prior_sha256':sha(raw),'after_sha256':sha(after),'delta_patch':key+'.delta.patch','delta_sha256':sha(delta),'cumulative_patch':key+'.cumulative.patch','cumulative_sha256':sha(cumulative)})
    manifest={'status':'PREPARED_NOT_SELECTED_NOT_DEPLOYED','upstream_sha256':UPSTREAM,'exp12_sha256':EXP12,'helper_sha256':sha((HERE/'log-copy-methods.php.inc').read_bytes()),'preparer_sha256':sha(Path(__file__).read_bytes()),'patch_version':subprocess.check_output(['patch','--version']).decode().splitlines()[0],'targets':records,'global_privacy_claim':False,'exception_trace_gate':'PENDING','runtime_tests_executed':False,'same_policy_required_both_labs':True,'application_acceptance':False}
    output.mkdir(parents=True)
    for name,raw in writes.items():
        p=output/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('original');p.add_argument('exp12');p.add_argument('output');args=p.parse_args()
    print(json.dumps(prepare(args.original,args.exp12,args.output),indent=2))

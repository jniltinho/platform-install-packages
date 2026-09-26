#!/usr/bin/env python3
"""Independent executor repeat, no mutation of frozen native inputs."""
import hashlib,json
from pathlib import Path
import collect,validate
def main():
    target=collect.OUT/'composition-cursor.json'
    prefixes=[collect.OUT/('composition-cursor-'+m) for m in validate.MODES]
    if target.exists() or any(p.with_suffix(s).exists() for p in prefixes for s in ['.stdout','.stderr','.exit']):raise ValueError('Refuse existing repeat')
    primary=json.loads((collect.OUT/'composition-primary.json').read_text())
    if primary['status']!='BOUNDED_COMPOSITION_PASS':raise ValueError('Primary not passed')
    ids=primary['identities'];pin=primary['identities_sha256'];expected=dict(ids['files'],**{'identities.json':pin})
    def check():
        text=collect.checked('83','cd '+collect.STAGE+' && sha256sum '+' '.join(expected))
        actual={l.split()[1]:l.split()[0] for l in text.splitlines()}
        if actual!=expected:raise ValueError('Frozen source changed')
        return actual
    before=check();rb=collect.runtime_identity('83')
    if rb!=primary['runtime_before']:raise ValueError('Runtime differs')
    result={'status':'INCOMPLETE','records':[],'source_before':before,'runtime_before':rb,'patch_selected':False,'application_acceptance':False}
    target.write_text(json.dumps(result,indent=2)+'\n')
    try:
        for mode,prefix in zip(validate.MODES,prefixes):
            variant,corpus=mode.split('-');command='bash '+collect.STAGE+'/run.sh '+variant+' '+corpus+' '+pin
            p=collect.remote('83',command);stdout=p.stdout.decode();stderr=p.stderr.decode()
            prefix.with_suffix('.stdout').write_text(stdout);prefix.with_suffix('.stderr').write_text(stderr);prefix.with_suffix('.exit').write_text(str(p.returncode)+'\n')
            try:body=json.loads(stdout)
            except ValueError:body=None
            result['records'].append({'mode':mode,'command':command,'exit':p.returncode,'stdout':stdout,'stderr':stderr,'body':body})
            target.write_text(json.dumps(result,indent=2)+'\n')
    finally:
        result['source_after']=check();result['runtime_after']=collect.runtime_identity('83')
        target.write_text(json.dumps(result,indent=2)+'\n')
    if result['records']!=primary['records']:raise ValueError('Exact repeat differs')
    for name in ['source_before','source_after','runtime_before','runtime_after']:
        if result[name]!=primary[name]:raise ValueError('Identity differs: '+name)
    result['comparison']=validate.validate(result['records'],ids)
    if result['comparison']!=primary['comparison']:raise ValueError('Outcome differs')
    result['status']='EXACT_INDEPENDENT_NATIVE83_REPEAT';result['repeat_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    target.write_text(json.dumps(result,indent=2)+'\n');print('PASS: four native83 records match primary exactly, including stdout/stderr/body, sources and runtime. Strict cross-engine FAIL retained.')
if __name__=='__main__':main()

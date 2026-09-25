#!/usr/bin/env python3
"""Independent executor repeat of frozen attribute inputs; retain strict failure."""
import hashlib,json
from pathlib import Path
import collect,compare

def main():
    target=collect.OUT/'claude.json'
    if target.exists():raise ValueError('Refuse existing repeat')
    primary=json.loads((collect.OUT/'primary.json').read_text());payloads=json.loads((collect.OUT/'legacy-original74.json').read_text());result={'status':'INCOMPLETE','records':[],'labs':{},'patch_selected':False,'application_acceptance':False}
    target.write_text(json.dumps(result,indent=2)+'\n')
    for runtime in ['74','83']:
        original=primary['labs'][runtime];ids=original['identities'];pin=original['identities_sha256'];expected=dict(ids['files'],**{'identities.json':pin})
        def check():
            text=collect.checked(runtime,'cd '+collect.STAGE+' && sha256sum '+' '.join(expected));actual={l.split()[1]:l.split()[0] for l in text.splitlines()}
            if actual!=expected:raise ValueError('Frozen source changed')
            return actual
        before=check();rb=collect.runtime_identity(runtime)
        if rb!=original['runtime_before']:raise ValueError('Runtime differs from primary')
        for variant in ['original','attribute']:
            command='bash '+collect.STAGE+'/run.sh '+variant+' '+pin;p=collect.remote(runtime,command);stdout=p.stdout.decode();stderr=p.stderr.decode();prefix=collect.OUT/('claude-'+variant+runtime)
            prefix.with_suffix('.stdout').write_text(stdout);prefix.with_suffix('.stderr').write_text(stderr);prefix.with_suffix('.exit').write_text(str(p.returncode)+'\n')
            result['records'].append({'mode':variant+runtime,'command':command,'exit':p.returncode,'stdout':stdout,'stderr':stderr,'body':json.loads(stdout)})
            target.write_text(json.dumps(result,indent=2)+'\n')
        after=check();ra=collect.runtime_identity(runtime)
        if rb!=ra:raise ValueError('Runtime drift')
        result['labs'][runtime]={'identities':ids,'identities_sha256':pin,'source_before':before,'source_after':after,'runtime_before':rb,'runtime_after':ra}
    if result['records']!=primary['records'] or result['labs']!=primary['labs']:raise ValueError('Repeat differs from primary')
    try:result['comparison']=compare.validate(result['records'],primary['labs']['74']['identities'],primary['labs']['83']['identities'],payloads)
    except ValueError as e:result['comparison_error']=str(e)
    if result.get('comparison_error')!=primary.get('comparison_error'):raise ValueError('Strict outcome differs')
    result['status']='EXACT_PRIMARY_REPEAT_STRICT_LAYOUT_FAILURE_RETAINED';result['repeat_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    target.write_text(json.dumps(result,indent=2)+'\n');print('Four native rows exactly repeat primary; strict cross-runtime representation failure retained, no attribute selected.')
if __name__=='__main__':main()

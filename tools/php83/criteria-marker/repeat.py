#!/usr/bin/env python3
"""Repeat existing immutable stages only; never stage or change a source."""
import hashlib,json
from pathlib import Path
import collect,compare

def main():
    target=collect.OUT/'claude.json'
    if target.exists():raise ValueError('Refuse existing repeat')
    primary=json.loads((collect.OUT/'primary.json').read_text());ids=primary['identities'];pin=primary['identities_sha256'];expected=dict(ids['files'],**{'identities.json':pin})
    result={'status':'INCOMPLETE','records':[],'patch_selected':False,'application_acceptance':False,'labs':{}}
    target.write_text(json.dumps(result,indent=2)+'\n')
    for runtime in ['74','83']:
        def check():
            data=collect.checked(runtime,'cd '+collect.STAGE+' && sha256sum '+' '.join(expected));actual={l.split()[1]:l.split()[0] for l in data.splitlines()}
            if actual!=expected:raise ValueError('Frozen stage drift')
            return actual
        before=check();rb=collect.runtime_identity(runtime)
        if rb!=primary['labs'][runtime]['runtime_before']:raise ValueError('Runtime differs from primary')
        for variant in ['original','declaration']:
            command='bash '+collect.STAGE+'/run.sh '+variant+' '+pin;p=collect.remote(runtime,command)
            stdout=p.stdout.decode();stderr=p.stderr.decode();base=collect.OUT/('claude-'+variant+runtime)
            base.with_suffix('.stdout').write_text(stdout);base.with_suffix('.stderr').write_text(stderr);base.with_suffix('.exit').write_text(str(p.returncode)+'\n')
            body=json.loads(stdout)
            result['records'].append({'mode':variant+runtime,'command':command,'exit':p.returncode,'stdout':stdout,'stderr':stderr,'body':body})
            target.write_text(json.dumps(result,indent=2)+'\n')
        after=check();ra=collect.runtime_identity(runtime)
        if rb!=ra:raise ValueError('Runtime drift')
        result['labs'][runtime]={'source_before':before,'source_after':after,'runtime_before':rb,'runtime_after':ra}
    result['comparison']=compare.validate(result['records'],ids)
    if result['records']!=primary['records']:raise ValueError('Exact primary/repeat row mismatch')
    result.update(status='EXACT_PRIMARY_REPEAT_BOUNDED_ONLY',identities_sha256=pin,repeat_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    target.write_text(json.dumps(result,indent=2)+'\n');print('Four rows exactly match primary: raw stdout/stderr, native diagnostics, behavior and representation deltas; no patch selected.')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Three native logical snapshots from existing frozen sources and seven74 payloads."""
import hashlib,importlib.util,io,json,tarfile
from pathlib import Path
import collect
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('logical_compare',HERE/'logical-compare.py');compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
STAGE='/home/vagrant/php-criteria-marker-logical-v1'
def main():
    output=collect.OUT/'logical-primary.json'
    if output.exists():raise ValueError('Refuse existing evidence')
    primary=json.loads((collect.OUT/'primary.json').read_text());payload_raw=(collect.OUT/'legacy-original74.json').read_bytes();payloads=json.loads(payload_raw)
    files={'logical.php':(HERE/'logical.php').read_bytes(),'run.sh':(HERE/'logical-run.sh').read_bytes(),'verify.py':(HERE/'logical-verify.py').read_bytes(),'legacy.json':payload_raw}
    ids={'files':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()}};raw=(json.dumps(ids,indent=2)+'\n').encode();pin=hashlib.sha256(raw).hexdigest();files['identities.json']=raw;expected=dict(ids['files'],**{'identities.json':pin})
    (collect.OUT/'logical-identities.json').write_bytes(raw)
    archive=io.BytesIO()
    with tarfile.open(fileobj=archive,mode='w') as tar:
        for n,b in files.items():i=tarfile.TarInfo(n);i.size=len(b);i.mode=0o444;tar.addfile(i,io.BytesIO(b))
    result={'status':'INCOMPLETE','records':[],'labs':{},'attribute_selected':False,'strict_gate_preserved':'FAIL'}
    output.write_text(json.dumps(result,indent=2)+'\n')
    for runtime in ['74','83']:
        hostname={'74':'kaltura-php74-baseline','83':'kaltura-php83-lab'}[runtime]
        collect.checked(runtime,'test "$(hostname)" = '+hostname+' && mkdir '+STAGE+' && tar -xf - -C '+STAGE+' && sudo chown -R root:root '+STAGE+' && sudo chmod -R a-w '+STAGE,archive.getvalue())
        old=primary['labs'][runtime];source_expected=dict(old['identities']['files'],**{'identities.json':old['identities_sha256']})
        def check():
            result={}
            for stage,expected_files in [(STAGE,expected),(collect.STAGE,source_expected)]:
                actual={l.split()[1]:l.split()[0] for l in collect.checked(runtime,'cd '+stage+' && sha256sum '+' '.join(expected_files)).splitlines()}
                if actual!=expected_files:raise ValueError('Source/fixture drift')
                result[stage]=actual
            return result
        before=check();rb=collect.runtime_identity(runtime)
        if rb!=old['runtime_before']:raise ValueError('Runtime differs from reviewed primary')
        for variant in (['original'] if runtime=='74' else ['original','attribute']):
            command='bash '+STAGE+'/run.sh '+variant+' '+pin;p=collect.remote(runtime,command);stdout=p.stdout.decode();stderr=p.stderr.decode();prefix=collect.OUT/('logical-'+variant+runtime)
            prefix.with_suffix('.stdout').write_text(stdout);prefix.with_suffix('.stderr').write_text(stderr);prefix.with_suffix('.exit').write_text(str(p.returncode)+'\n')
            result['records'].append({'mode':variant+runtime,'exit':p.returncode,'stdout':stdout,'stderr':stderr,'body':json.loads(stdout)})
            output.write_text(json.dumps(result,indent=2)+'\n')
        after=check();ra=collect.runtime_identity(runtime)
        if rb!=ra:raise ValueError('Runtime drift')
        result['labs'][runtime]={'before':before,'after':after,'runtime_before':rb,'runtime_after':ra}
    result['comparison']=compare.validate(result['records'],payloads);result['status']='BOUNDED_TYPED_VALUES_MATCH_STRICT_LAYOUT_FAIL_RETAINED';output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
if __name__=='__main__':main()

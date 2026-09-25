#!/usr/bin/env python3
"""Record native full-entrypoint outcomes; unrelated CLI blockers remain failures."""
import argparse, hashlib, json, re, shlex, subprocess
from pathlib import Path
from prepare import HERE, STAGE, sha, require
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
def remote(command): return subprocess.run(SSH+[command],capture_output=True,text=True,timeout=100)
def expected_values(case,runtime,variant):
    if case.startswith('hp'):
        q=['HTMLPurifier_Bootstrap::autoload','fixtureFirst','fixtureTail']+(['__autoload'] if case=='hp-legacy' else [])
        e={'queue-before':['fixtureFirst','fixtureTail'],'queue-after':q,'actual-class-hit':True,
           'actual-class-file':'vendor/htmlpurifier/library/HTMLPurifier/EntityLookup.php',
           'first-hit':True,'prefix-miss':False,'unrelated-miss':False}
        if case=='hp-legacy': e['legacy-hit']=True
        return e
    if case.startswith('core'):
        full=case=='core-full'
        return {'queue':['fixtureFirst']+(['sfCore::splAutoload'] if full else [])+['sfCore::splSimpleAutoload','fixtureTail'],
          'callback':'spl_autoload_call','registered-core-callables':[['sfCore','splAutoload']] if full else [],
          'first-hit':True,'mapped-hit':True,'mapped-file':'/audit/fixtures/map/FixtureMapped.php','mapped-value':'Mapped',
          'miss':False,'unserialize-class':'FixtureUnserialize','unserialize-file':'/audit/fixtures/map/FixtureUnserialize.php','unserialize-value':'Unserialize'}
    if case.startswith('cli-version'):
        queue=case=='cli-version-queue'; prefix=['fixtureFirst','fixtureTail'] if queue else []
        q=prefix+(['Closure'] if variant=='candidate' else ([] if queue else ['__autoload']))
        e={'queue-before':prefix,'post-exit-fixture-phase':True,'queue':q,'map-initially-empty':True,
           'fallback-hit':not(queue and variant=='original'),'missing':False}
        if queue: e.update({'first-hit':True,'map-after-first-empty':True})
        return e
    return {}
TARGETS={'hp':'vendor/htmlpurifier/library/HTMLPurifier.autoload.php','core':'vendor/symfony/util/sfCore.class.php','cli':'vendor/symfony-data/bin/symfony.php'}
def family(case): return 'hp' if 'hp' in case else ('core' if 'core' in case else 'cli')
def expected(case,runtime,variant):
    result=expected_values(case,runtime,variant)
    if case.startswith('hp'):
        hits=[['first','FixtureFirstHit']]
        for cls in ['HTMLPurifier_ProbeMissing','ProbeMissing']:
            hits += [['first',cls],['tail',cls]]+([['legacy',cls]] if case=='hp-legacy' else [])
        if case=='hp-legacy':hits += [[n,'FixtureLegacyHit'] for n in ['first','tail','legacy']]
    elif case.startswith('core'):
        hits=[['first','FixtureFirstHit'],['first','FixtureMapped'],['first','FixtureMissing'],['tail','FixtureMissing'],['first','FixtureUnserialize']]
    elif case=='cli-version-queue':
        hits=[['first','FixtureFirstHit'],['first','FixtureFallback'],['tail','FixtureFallback'],['first','FixtureMissing'],['tail','FixtureMissing']]
    else: hits=[]
    if case=='cli-tasks': return {'queue-before':[]}
    if case=='cli-tasks-configured':return {'queue-before':[],'real-config-value':'/audit/fixtures/project','real-session-cache':'kSessionConf'}
    result['hits']=hits
    return result

def required_loaded(case,variant):
    f=family(case); paths=['source/'+TARGETS[f]]
    if f=='hp':
        paths += ['source/vendor/htmlpurifier/library/HTMLPurifier/Bootstrap.php','source/vendor/htmlpurifier/library/HTMLPurifier/EntityLookup.php','fixtures/extra/FixtureFirstHit.php']
        if case=='hp-legacy': paths+=['fixtures/legacy.php','fixtures/extra/FixtureLegacyHit.php']
    if f=='core': paths += ['source/vendor/symfony/util/sfFinder.class.php','source/vendor/symfony/config/sfConfig.class.php','source/vendor/symfony/util/sfContext.class.php','fixtures/map/FixtureMapped.php','fixtures/map/FixtureUnserialize.php','fixtures/extra/FixtureFirstHit.php']
    if f=='cli':
        paths += ['source/vendor/symfony/vendor/pake/pakeFunction.php','source/vendor/symfony/config/sfConfig.class.php']
        if case=='cli-version-queue':paths+=['fixtures/extra/FixtureFirstHit.php']
        if case.startswith('cli-version') and not(case=='cli-version-queue' and variant=='original'):paths+=['fixtures/project/lib/model/FixtureFallback.php']
    if case=='cli-tasks-configured':paths+=['source/alpha/config/kConf.php','source/alpha/config/kConfCacheManager.php','source/infra/kEnvironment.php','source/alpha/config/cache/kSessionConf.php','source/vendor/symfony-data/config/constants.php']
    return paths

def validate(body,case,runtime,variant,exitcode,stderr,hashes):
    require(body['case']==case,'Case mismatch')
    require(body['php'].startswith('7.4.' if runtime=='74' else '8.3.'),'Runtime mismatch')
    target=TARGETS[family(case)]
    require(body['target']=={'path':target,'sha256':hashes.get(variant+'/'+target)},'Target source identity mismatch')
    require(type(body['loaded']) is dict,'Loaded inventory must be an object')
    for path,digest in body['loaded'].items():
        relative=variant+'/'+path[len('source/'):] if path.startswith('source/') else path
        require(hashes.get(relative)==digest,'Unexpected loaded source or changed hash: '+path)
    if case.startswith('fatal-'):
        require(exitcode==255 and 'fatal' in body and '__autoload() is no longer supported' in stderr,'Missing original83 fatal control')
        require(not body['rows'],'Fatal control continued execution')
        require(body['fatal']['file']==target,'Wrong fatal source')
        return 'EXPECTED_FATAL'
    require(exitcode==0 and 'fatal' not in body and 'exception' not in body,'Real entrypoint failed (not waived)')
    require(all(path in body['loaded'] for path in required_loaded(case,variant)),'Required actual source/fixture not loaded')
    rows=body['rows']; values={r['case']:r['value'] for r in rows}
    require(len(rows)==len(values),'Duplicate row')
    require(set(values)==set(expected(case,runtime,variant)),'Wrong exact case inventory')
    for key,value in expected(case,runtime,variant).items(): require(key in values and values[key]==value,'Expectation mismatch: '+key)
    if case.startswith('cli-tasks'): require('post-exit-fixture-phase' not in values,'Task case replaced with version probe')
    else: require('hits' in values,'Missing callback observations')
    return 'PASS'
def inventory(identity):
    # Python stat/read only: no application code execution.
    code='import pathlib,hashlib,json; p=pathlib.Path('+repr(STAGE)+'); print(json.dumps({x.relative_to(p).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in p.rglob("*") if x.is_file() and x.name!="identity.json"}))'
    r=remote('python3 -c '+shlex.quote(code));require(r.returncode==0,'Inventory failed')
    found=json.loads(r.stdout);require(found==identity['hashes'],'Stage inventory drift');return found

def main():
    p=argparse.ArgumentParser();p.add_argument('identity',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    require(not a.output.exists(),'Refuse existing evidence')
    identity=json.loads(a.identity.read_text());require(identity['stage']==STAGE,'Wrong stage')
    for name in ('probe.php','run.sh'):require(identity['hashes'][name]==sha(HERE/name),'Unfrozen harness')
    records=[];before=inventory(identity)
    matrix=[(runtime,variant,case) for runtime,variant in [('74','original'),('74','candidate'),('83','candidate')] for case in ['hp','core-simple','core-full','cli-version','cli-version-queue','cli-tasks','cli-tasks-configured']]
    matrix += [('74',v,'hp-legacy') for v in ('original','candidate')]
    matrix += [('83','original','fatal-'+c) for c in ('hp','core','cli')]
    for runtime,variant,case in matrix:
        command='bash '+STAGE+'/run.sh '+runtime+' '+variant+' '+case
        r=remote(command);body=None;error=None
        try:
            results=[line[len('AUTOLOAD_RESULT '):] for line in r.stdout.splitlines() if line.startswith('AUTOLOAD_RESULT ')]
            require(len(results)==1,'Missing/duplicate final structured report')
            body=json.loads(results[0]);status=validate(body,case,runtime,variant,r.returncode,r.stderr,before)
        except (ValueError,KeyError,TypeError,AttributeError) as e: status='FAIL';error=str(e)
        records.append({'runtime':runtime,'variant':variant,'case':case,'command':command,'exit':r.returncode,'status':status,'validation_error':error,'result':body,'stdout':r.stdout,'stderr':r.stderr,'stdout_sha256':hashlib.sha256(r.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr.encode()).hexdigest()})
        # Persist completed rows even if later SSH/inventory fails.
        a.output.write_text(json.dumps({'status':'INCOMPLETE','identity':identity,'collector_sha256':sha(__file__),'records':records},indent=2)+'\n')
    after=inventory(identity)
    failed=sum(x['status']=='FAIL' for x in records)
    comparisons=[]
    for case in ['hp','hp-legacy','core-simple','core-full']:
        pair=[next(r for r in records if r['case']==case and r['runtime']=='74' and r['variant']==v) for v in ('original','candidate')]
        equal=all(r['status']=='PASS' for r in pair) and pair[0]['result']['rows']==pair[1]['result']['rows']
        comparisons.append({'case':case,'before_candidate74_functional_rows_equal':equal})
        if not equal:failed+=1
    report={'status':'PASS' if failed==0 else 'FAIL','identity':identity,'collector_sha256':sha(__file__),'records':records,'comparisons':comparisons,'inventory_unchanged':before==after,'matrix_rows':len(matrix),'failed_checks':failed,'application_acceptance':False,'limitations':['Diagnostic equivalence requires independent review; warnings are never suppressed','CLI queue composition delta explicitly expected','No SQL/config-cache generation/no-SPL branch/full application testing']}
    a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','matrix_rows','failed_checks')}));return int(failed!=0)
if __name__=='__main__':raise SystemExit(main())

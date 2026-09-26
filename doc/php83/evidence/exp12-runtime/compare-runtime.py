#!/usr/bin/env python3
"""Strict exp12 bounded runtime reconciliation; pending inputs never become PASS."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[4]
BASE = REPO / 'doc/php83/evidence'
RUN = BASE / 'exp12-runtime'
CURRENT = 'de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
PRIOR = 'f2474f5b951bfd2d121291025c8dd4554697fb5bb4024e132987643dab6144a7'
ARTIFACT = {'zip_sha256':CURRENT,'verified_extracted_files':15242}
PREVIOUS_ARTIFACT = {'zip_sha256':PRIOR,'verified_extracted_files':15240}
INPUTS = ['additions-primary.json','claude-additions.json','api-primary.json','claude-api.json','cli74-primary.json','claude-cli74.json',
          'cli83-primary.json','claude-native83-cli.json','curly-primary.json','claude-curly.json',
          'runtime-before.json','runtime-after.json','claude-runtime-before.json','claude-r2-runtime-after.json',
          'runtime83-before.json','runtime83-after.json','claude-native83-runtime-before.json','claude-native83-runtime-after.json','generator-primary.json','claude-generator-r2.json','criteria-primary.json','claude-criteria.json','additions-post-source.json','claude-additions-post-source.json']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def equal(one,two):
    return canonical(one)==canonical(two)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_exit(value, expected):
    require(type(value) is int and value==expected,'Unexpected or noninteger process status')


def load(path):
    def invalid(value):
        raise ValueError('Non-finite JSON number '+value)
    return json.loads(path.read_text(),parse_constant=invalid)


def local_harness_path(name):
    prefix='/home/vagrant/php-exp12-regression/'
    if name.startswith(prefix):name=name[len(prefix):]
    if name=='tests/curly-offsets-probe.php':return REPO/'tools/php83/curly-offsets/probe.php'
    if name.startswith('tests/'):return REPO/'tools/php83/patch-tests'/name[len('tests/'):]
    if name.startswith('api/'):return REPO/'tools/php83/exp12-api'/name[len('api/'):]
    if name.startswith('exp12-regression/'):return REPO/'tools/php83'/name
    if any(name.startswith(folder+'/') for folder in ['base-object-ternary','autoload83','autoload83-composition']):return REPO/'tools/php83'/name
    raise ValueError('Unexpected harness path '+name)


def verify_harness(mapping):
    require(isinstance(mapping,dict) and bool(mapping),'Missing harness identities')
    for name,want in mapping.items():
        path=local_harness_path(name)
        require(path.resolve().is_relative_to(REPO/'tools/php83') and digest(path.read_bytes())==want,'Local harness drift '+name)


def file_pin(report,field,relative):
    require(report[field]==digest((REPO/relative).read_bytes()),'Collector/helper drift '+relative)


def api_comparison(a,b,prior_report):
    expected_rows=[('74','original'),('83','original'),('83','exp11'),('83','exp12')]
    expected=[]
    for kind in (0,2):
        expected.append(['http-session-start',kind,True])
        for method in ('GET','POST'):expected.append(['http-session-get',kind,method,True])
    for label,code in [('missing','SERVICE_FORBIDDEN'),('malformed','INVALID_KS'),('expired','INVALID_KS'),('wrong-secret','START_SESSION_ERROR'),('escalation','START_SESSION_ERROR')]:
        expected.append(['http-rejected',label,code])
    expected_stdout=json.dumps(expected)+'\n'+json.dumps(['untrusted-ca-rejected',True])+'\n'+json.dumps(expected)+'\n'
    tokens=[]
    for report in (a,b):
        require(report['functional_checks_passed'] is True and report['application_acceptance'] is False,'API collector did not pass bounded checks')
        require(equal(report['artifact'],ARTIFACT) and equal(report['previous_artifact'],PREVIOUS_ARTIFACT),'API artifact mismatch')
        require([(r['runtime'],r['tree']) for r in report['records']]==expected_rows,'API row matrix differs')
        verify_harness(report['harness']);file_pin(report,'collector_sha256','tools/php83/exp12-api/collect.py')
        for name,want in report['imported_helper_sha256'].items():
            require(name in ('collect-api-apache.py','collect-api-mysql.py') and digest((REPO/'tools/php83/patch-tests'/name).read_bytes())==want,'API imported helper drift')
        require(set(report['imported_helper_sha256'])=={'collect-api-apache.py','collect-api-mysql.py'},'Missing API helper pin')
        match=re.fullmatch(r'/tmp/kaltura-pdo-mysql\.([0-9a-f]{32})',report['db']['datadir'])
        require(match is not None,'Unexpected owned DB path')
        token=match.group(1);tokens.append(token);unit='php83-exp12-api-'+token
        require(report['db']['unit']==unit and report['cleanup']['unit']==unit and report['cleanup']['stopped'] is True and report['cleanup']['is_active_output'] in ('inactive','failed','unknown'),'Owned DB cleanup failure')
        for row in report['records']:
            control=row['runtime']=='83' and row['tree']=='original'
            strict_exit(row['returncode'],1 if control else 0)
            require(row['stdout_whitelisted'] is True,'Unwhitelisted API stdout')
            require(row['stdout']==('' if control else expected_stdout),'API golden responses differ')
            require(row['stdout_sha256']==digest(row['stdout'].encode()),'API stdout identity mismatch')
            require(row['signature_failure'] is control,'Wrong original83 signature control')
            require(len(row['runtime_observations'])==(1 if control else 24),'API runtime observation count differs')
            for observation in row['runtime_observations']:
                require(observation['php']==('7.4.33' if row['runtime']=='74' else '8.3.6') and observation['sapi']=='apache2handler' and observation['ini_is_expected'] is True,'Unexpected API runtime/SAPI/INI')
    require(tokens[0]!=tokens[1],'Independent API runs reused DB identity')
    for field in ('artifact','previous_artifact','harness','imported_helper_sha256','collector_sha256','unsupported_cases','comparisons','original83_signature_control'):
        require(equal(a[field],b[field]),'Independent API metadata differs '+field)
    rows=[]
    for one,two in zip(a['records'],b['records']):
        require(set(one)==set(two),'API record field set differs')
        require(equal({k:v for k,v in one.items() if k not in ('duration_ns','stderr_sha256')},{k:v for k,v in two.items() if k not in ('duration_ns','stderr_sha256')}),'Independent API normalized result differs')
        rows.append({'runtime':one['runtime'],'tree':one['tree'],'independent_equal':True,'diagnostic_groups':len(one['diagnostics']),'diagnostic_events':sum(d['count'] for d in one['diagnostics'])})
    expected_diagnostics=next(r['diagnostics'] for r in prior_report['records'] if r['runtime']=='83' and r['tree']=='exp11')
    require(prior_report['artifact']['zip_sha256']==PRIOR,'Historical API source identity differs')
    require(len(expected_diagnostics)==18 and sum(d['count'] for d in expected_diagnostics)==503,'Historical diagnostic baseline differs')
    require(equal(a['records'][2]['diagnostics'],expected_diagnostics),'Exp11 reference drift')
    removed={'severity':'ApplicationDiagnostic','path':'/audit/app/alpha/apps/kaltura/lib/criteriaFilter.class.php','line':51,'count':132}
    require(expected_diagnostics.count(removed)==1,'Missing exact retained marker group')
    permitted=[x for x in expected_diagnostics if x!=removed]
    require(equal(a['records'][3]['diagnostics'],permitted),'Unexpected diagnostic delta beyond reviewed Criteria marker group')
    return {'logical_rows':4,'independent_rows':rows,'removed_exact_group':removed,'prior_groups':18,'prior_events':503,'candidate_groups':17,'candidate_events':371,'distinct_owned_database_tokens':True}



def cli_comparison(reports):
    comparisons=[];zeros=fatals=0
    cases=['environment','legacy-json','zend-json','doc-comment','doc-comment-export','doc-comment-consumer']
    for runtime in ('74','83'):
        a,b=reports[runtime]
        sources=['original'] if runtime=='74' else ['original','exp11','exp12']
        expected=[(s,ini,c) for s in sources for ini in ('standard','minimal') for c in cases]
        for report in (a,b):
            require(report['host']==('kaltura-php74-baseline' if runtime=='74' else 'kaltura-php83-lab'),'Unexpected CLI host')
            require(report['zip_sha256']==CURRENT and type(report['verified_extracted_files']) is int and report['verified_extracted_files']==15242,'CLI artifact mismatch')
            require(equal(report['previous_artifact'],PREVIOUS_ARTIFACT),'CLI prior artifact mismatch')
            require(report['application_acceptance'] is False,'Unexpected aggregate acceptance')
            require([(r['source'],r['ini'],r['case']) for r in report['rows']]==expected,'CLI matrix differs')
            verify_harness(report['harness'])
        require(equal({k:v for k,v in a.items() if k not in ('recorded_at_utc','rows')},{k:v for k,v in b.items() if k not in ('recorded_at_utc','rows')}),'CLI nonvolatile metadata differs')
        for one,two in zip(a['rows'],b['rows']):
            require(equal({k:v for k,v in one.items() if k!='duration_ns'},{k:v for k,v in two.items() if k!='duration_ns'}),'Independent CLI row differs')
            control=runtime=='83' and one['source']=='original' and one['case'] in ('legacy-json','zend-json')
            strict_exit(one['exit'],255 if control else 0);strict_exit(two['exit'],255 if control else 0)
            if control:
                require('Fatal error' in one['stderr'] and 'Array and string offset access syntax with curly braces is no longer supported' in one['stderr'],'Wrong expected original83 failure')
                fatals+=1
            else:zeros+=1
            if one['source'] in ('exp11','exp12') and one['case']!='environment':
                original=next(r for r in reports['74'][0]['rows'] if r['ini']==one['ini'] and r['case']==one['case'])
                left,right=json.loads(one['stdout']),json.loads(original['stdout'])
                if one['case']=='doc-comment-export':left,right=left['entries'],right['entries']
                require(equal(left,right),'Typed CLI output differs from original74')
                comparisons.append({'source':one['source'],'ini':one['ini'],'case':one['case'],'typed_equal':True})
    require(zeros==44 and fatals==4 and len(comparisons)==20,'CLI totals mismatch')
    return {'logical_rows':48,'positive_rows':zeros,'expected_original83_json_failures':fatals,'typed_baseline_comparisons':comparisons,'independent_rows_equal_except_duration':True}


def curly_comparison(a,b,prior):
    require(equal(a,b),'Independent artifact class report differs')
    require(a['functional_checks_passed'] is True and a['application_acceptance'] is False and equal(a['artifact'],ARTIFACT),'Curly artifact checks incomplete')
    verify_harness(a['harness'])
    file_pin(a,'collector_sha256','tools/php83/exp12-api/collect-curly.py')
    file_pin(a,'imported_validator_sha256','tools/php83/curly-offsets/collect.py')
    file_pin(a,'prior_corpus_sha256','doc/php83/evidence/curly-offsets/behavior-primary.json')
    require(prior['functional_checks_passed'] is True,'Prior class corpus not accepted for its scope')
    manifest=load(BASE/'exp12-candidate/selected-manifest.json')
    after={r['path']:r['after_sha256'] for r in manifest['patches']}
    require([r['case'] for r in a['records']]==['google-old','google-new','purifier'],'Wrong class matrix')
    for row,count in zip(a['records'],[20,20,28]):
        strict_exit(row['exit'],0)
        require(row['validation_error'] is None and row['matches_prior_actual_candidate83'] is True,'Artifact class execution failed')
        result=row['result'];require(result['source_sha256']==after[result['source_path']],'Class source hash differs')
        expected=next(r['result'] for r in prior['records'] if r['runtime']=='83' and r['variant']=='candidate' and r['case']==row['case'])
        require(equal(result,expected) and len(result['rows'])==count,'Class actual rows differ from prior83 corpus')
    return {'classes':3,'logical_cases':68,'independent_equal':True,'exact_prior_candidate83_equal':True,'all65_source_runtime_coverage':False}


def runtime_comparison(reports):
    require(all(equal(reports[0],r) for r in reports[1:]),'Before/after or independent fresh runtime identity differs')
    first=reports[0];strict_exit(first['exit'],0)
    require(first['artifact_pin']==CURRENT,'Runtime artifact context mismatch')
    file_pin(first,'collector_sha256','tools/php83/exp12-api/runtime-identity.py')
    tree=ast.parse((REPO/'tools/php83/exp12-api/runtime-identity.py').read_text())
    remote=next(node.value.value for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REMOTE' for t in node.targets))
    require(digest(remote.encode())==first['remote_program_sha256'],'Runtime remote program drift')
    identity=first['identity']
    require(identity['host']=='kaltura-php74-baseline' and type(identity['uid']) is int and identity['uid']==1000,'Runtime identity unexpected host/UID')
    require(bool(identity['files']) and bool(identity['linked_libraries']),'Incomplete runtime snapshot')
    return {'snapshots':4,'all_before_after_independent_bytes_equal':True,'host':identity['host'],'hashed_objects':len(identity['files']),'runtime_modes':len(identity['runtimes']),'scope':'baseline74 native74 and copied83 Apache/CLI/modules/libraries/INI; not a fresh php83lab module snapshot'}



def native83_runtime_comparison(reports, baseline):
    require(all(equal(reports[0],r) for r in reports[1:]),'Native83 before/after or independent runtime identity differs')
    report=reports[0];strict_exit(report['exit'],0)
    file_pin(report,'collector_sha256','tools/php83/exp12-api/runtime83-identity.py')
    require(report['command']==['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83','python3 -'],'Native83 collection command differs')
    identity=report['identity']
    require(identity['host']=='kaltura-php83-lab' and len(identity['files'])==39,'Native83 host/object coverage differs')
    require(set(identity['linked_libraries'])==set(identity['files']),'Missing native83 object library identities')
    require(set(identity['runtimes'])=={'standard','minimal'},'Native83 runtime mode coverage differs')
    for mode,data in identity['runtimes'].items():
        require(data['version'].startswith('PHP 8.3.6 (cli)'),'Unexpected native83 version/SAPI')
        require('[PHP Modules]' in data['modules'] and 'Core' in data['modules'],'Missing native83 module report')
        if mode=='standard':require(bool(data['configuration_sha256']),'Missing standard INI identity')
        else:require(data['configuration_sha256']=={},'Unexpected minimal INI configuration')
    require(identity['files']['/usr/bin/php8.3']==baseline['identity']['files']['/home/vagrant/php-mysql-probe/runtime83/php8.3']['sha256'],'Native and copied83 interpreter identities differ')
    return {'snapshots':4,'all_before_after_independent_bytes_equal':True,'host':identity['host'],
        'hashed_objects':39,'runtime_modes':2,'copied_and_native83_interpreter_hash_equal':True,
        'scope':'Fresh native php83lab CLI/modules/linked libraries and standard/minimal INI; no application acceptance inferred'}


def additions_comparison(a,b):
    import importlib.util
    require(equal(a,b),'Independent additions observations differ')
    require(a['application_acceptance'] is False,'Unexpected additions acceptance');require(a['status']=='FAIL' and a['error']=='ValueError: Actual artifact output differs from reviewed native83 corpus','Original historical loaded-hash mismatch phase not preserved')
    verify_harness(a['harness']);file_pin(a,'collector_sha256','tools/php83/exp12-api/collect-additions.py')
    path=REPO/'tools/php83/exp12-api/validate-additions.py';spec=importlib.util.spec_from_file_location('metadata_validator',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    first=module.validate(a,load(RUN/'additions-post-source.json'));second=module.validate(b,load(RUN/'claude-additions-post-source.json'))
    require(equal(first,second),'Metadata-only revalidation differs')
    return first

def generator_comparison(a,b):
    import importlib.util
    require(equal(a,b),'Independent generator observation differs')
    path=REPO/'tools/php83/exp12-api/generator/validate.py';spec=importlib.util.spec_from_file_location('generator_validator',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.validate(a)

def criteria_comparison(a,b):
    import importlib.util
    require(equal(a,b),'Independent Criteria artifact report differs')
    require(a['status']=='BOUNDED_ARTIFACT_CRITERIA_PASS' and equal(a['before'],a['after']),'Criteria incomplete or drift')
    require(equal(a['before']['artifact'],ARTIFACT),'Criteria actual artifact mismatch')
    identity_path=RUN/'criteria-source-identities.json';require(equal(a['identities'],load(identity_path)) and a['identities_sha256']==digest(identity_path.read_bytes()),'Criteria frozen source manifest differs')
    for row in a['records']:
        variant,corpus=row['mode'].split('-');require(row['command']=='bash /home/vagrant/php-exp12-criteria-v1/run.sh '+variant+' '+corpus+' '+a['identities_sha256'],'Criteria command differs')
    path=REPO/'tools/php83/exp12-api/criteria/validate.py';spec=importlib.util.spec_from_file_location('criteria_validator',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.validate(a['records'],a['identities']);require(equal(result,a['comparison']),'Criteria summary drift');return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).with_name('comparison-runtime.json'))
    args=parser.parse_args()
    missing=[name for name in INPUTS if not (RUN/name).is_file() or not (RUN/name).stat().st_size]
    if missing:
        print(json.dumps({'status':'PENDING','missing_inputs':missing,'comparison_written':False}));return 2
    output=args.output
    require(not output.exists(),'Refusing existing comparison report')
    reports={name:load(RUN/name) for name in INPUTS}
    result={'schema':1,'status':'PASS_BOUNDED_RUNTIME_COMPARISON',
        'additions':additions_comparison(reports['additions-primary.json'],reports['claude-additions.json']),
        'generator':generator_comparison(reports['generator-primary.json'],reports['claude-generator-r2.json']),
        'criteria':criteria_comparison(reports['criteria-primary.json'],reports['claude-criteria.json']),
        'api':api_comparison(reports['api-primary.json'],reports['claude-api.json'],load(BASE/'exp11-runtime/api-primary.json')),
        'cli':cli_comparison({v:(reports[f'cli{v}-primary.json'],reports['claude-cli74.json' if v=='74' else 'claude-native83-cli.json']) for v in ('74','83')}),
        'classes':curly_comparison(reports['curly-primary.json'],reports['claude-curly.json'],load(BASE/'curly-offsets/behavior-primary.json')),
        'runtime_identity':runtime_comparison([reports[n] for n in ('runtime-before.json','runtime-after.json','claude-runtime-before.json','claude-r2-runtime-after.json')]),
        'native83_runtime_identity':native83_runtime_comparison([reports[n] for n in ('runtime83-before.json','runtime83-after.json','claude-native83-runtime-before.json','claude-native83-runtime-after.json')],reports['runtime-before.json']),
        'normalization_policy':{'api':'Exclude only duration_ns and opaque stderr_sha256 from independent row equality; compare exact stdout, signature control, sanitized diagnostics and runtime observations. DB UUIDs differ but each path/unit/cleanup identity is checked and both tokens must be distinct.',
            'api_stderr_limit':'Raw KS-bearing logs were not retained; differing opaque stderr hashes are not asserted to differ solely by known timestamps/UUIDs. Equality claim is explicitly limited to collected sanitized fields.',
            'cli':'Exclude per-row duration_ns and report recorded_at_utc only. stdout/stderr remain byte-exact between executors. Typed baseline comparison excludes environment; doc-comment-export compares entries only.',
            'additions':'Independent observations remain byte-exact. Historical comparator FAIL retained; separate pinned adapter permits only9 exact loaded-source hash fields, every other byte unchanged.',
            'classes':'No independent normalization; full reports and prior83 result objects must match exactly.',
            'runtime':'No normalization; each host has four fresh snapshots which must match exactly within that host; native83 and copied83 interpreter hashes must match.'},
        'input_sha256':{name:digest((RUN/name).read_bytes()) for name in INPUTS},
        'reference_sha256':{name:digest((BASE/name).read_bytes()) for name in ['exp11-runtime/api-primary.json','curly-offsets/behavior-primary.json','exp12-candidate/selected-manifest.json']},
        'comparator_sha256':digest(Path(__file__).read_bytes()),'application_acceptance':False}
    with output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':result['status'],'api_rows':4,'cli_rows':48,'class_cases':68,'diagnostics':'18/503 prior to17/371 candidate; only exact132 marker group removed'}));return 0

if __name__=='__main__':raise SystemExit(main())

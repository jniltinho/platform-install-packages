#!/usr/bin/env python3
"""Strict exp13 bounded runtime reconciliation; pending inputs never become PASS."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[4]
BASE = REPO / 'doc/php83/evidence'
RUN = BASE / 'exp13-runtime'
CURRENT = '6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944'
PRIOR = 'de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
ARTIFACT = {'zip_sha256':CURRENT,'verified_extracted_files':15253}
PREVIOUS_ARTIFACT = {'zip_sha256':PRIOR,'verified_extracted_files':15242}



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
    prefix='/home/vagrant/php-exp13-regression/'
    if name.startswith(prefix):name=name[len(prefix):]
    if name=='tests/curly-offsets-probe.php':return REPO/'tools/php83/curly-offsets/probe.php'
    if name.startswith('tests/'):return REPO/'tools/php83/patch-tests'/name[len('tests/'):]
    if name.startswith('api/'):return REPO/'tools/php83/exp13-api'/name[len('api/'):]
    if name.startswith('exp13-regression/'):return REPO/'tools/php83'/name
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
    expected_rows=[('74','original'),('83','original'),('83','exp12'),('83','exp13')]
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
        verify_harness(report['harness']);file_pin(report,'collector_sha256','tools/php83/exp13-api/collect.py')
        for name,want in report['imported_helper_sha256'].items():
            require(name in ('collect-api-apache.py','collect-api-mysql.py') and digest((REPO/'tools/php83/patch-tests'/name).read_bytes())==want,'API imported helper drift')
        require(set(report['imported_helper_sha256'])=={'collect-api-apache.py','collect-api-mysql.py'},'Missing API helper pin')
        match=re.fullmatch(r'/tmp/kaltura-pdo-mysql\.([0-9a-f]{32})',report['db']['datadir'])
        require(match is not None,'Unexpected owned DB path')
        token=match.group(1);tokens.append(token);unit='php83-exp13-api-'+token
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
    expected_diagnostics=next(r['diagnostics'] for r in prior_report['records'] if r['runtime']=='83' and r['tree']=='exp12')
    require(prior_report['artifact']['zip_sha256']==PRIOR,'Historical API source identity differs')
    require(len(expected_diagnostics)==17 and sum(d['count'] for d in expected_diagnostics)==371,'Historical diagnostic baseline differs')
    require(equal(a['records'][2]['diagnostics'],expected_diagnostics),'Exp12 reference drift')
    observed=[{'severity':'ApplicationDiagnostic','path':'/audit/app/api_v3/lib/KalturaEntryService.php','line':1836,'count':1}]
    require(equal(a['records'][3]['diagnostics'],observed),'Observed exp13 diagnostic inventory differs')
    for report in (a,b):
        require(set(report['post_source'])=={'current','previous'} and all(v['exit']==0 and v['matches'] is True for v in report['post_source'].values()),'Missing post source equality')
    return {'logical_rows':4,'independent_rows':rows,'prior_groups':17,'prior_events':371,'candidate_groups':1,'candidate_events':1,'remaining_diagnostics':observed,'distinct_owned_database_tokens':True,'diagnostic_contract':'Observed category/path/line/count, not exported secret-bearing native message text; stderr hashes retained but excluded from equality because nonce/temp paths vary.'}



def cli_comparison(reports):
    comparisons=[];zeros=fatals=0
    cases=['environment','legacy-json','zend-json','doc-comment','doc-comment-export','doc-comment-consumer']
    for runtime in ('74','83'):
        a,b=reports[runtime]
        sources=['original'] if runtime=='74' else ['original','exp12','exp13']
        expected=[(s,ini,c) for s in sources for ini in ('standard','minimal') for c in cases]
        for report in (a,b):
            require(report['host']==('kaltura-php74-baseline' if runtime=='74' else 'kaltura-php83-lab'),'Unexpected CLI host')
            require(report['zip_sha256']==CURRENT and type(report['verified_extracted_files']) is int and report['verified_extracted_files']==15253,'CLI artifact mismatch')
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
            if one['source'] in ('exp12','exp13') and one['case']!='environment':
                original=next(r for r in reports['74'][0]['rows'] if r['ini']==one['ini'] and r['case']==one['case'])
                left,right=json.loads(one['stdout']),json.loads(original['stdout'])
                if one['case']=='doc-comment-export':left,right=left['entries'],right['entries']
                require(equal(left,right),'Typed CLI output differs from original74')
                comparisons.append({'source':one['source'],'ini':one['ini'],'case':one['case'],'typed_equal':True})
    require(zeros==44 and fatals==4 and len(comparisons)==20,'CLI totals mismatch')
    return {'logical_rows':48,'positive_rows':zeros,'expected_original83_json_failures':fatals,'typed_baseline_comparisons':comparisons,'independent_rows_equal_except_duration':True}


def reconcile():
    api=api_comparison(load(RUN/'api-primary.json'),load(RUN/'claude-api.json'),load(BASE/'exp12-runtime/api-primary.json'))
    cli=cli_comparison({n:(load(RUN/f'cli{n}-primary.json'),load(RUN/f'claude-cli{n}.json')) for n in ('74','83')})
    snapshots={}
    for runtime,helper in [('74','runtime-identity.py'),('83','runtime83-identity.py')]:
        for kind,key in [('runtime','identity'),('original','observed')]:
            paths=[RUN/f'{phase}{runtime}-{kind}-{moment}.json' for phase in ('primary','claude') for moment in ('before','after')]
            reports=[load(p) for p in paths]
            expected_collector=REPO/'tools/php83/exp13-api'/(helper if kind=='runtime' else 'original-source-identity.py')
            for r in reports:
                strict_exit(r['exit'],0);require(r['collector_sha256']==digest(expected_collector.read_bytes()),'Snapshot collector mismatch')
                require(equal(r[key],reports[0][key]),'Snapshot identity differs')
                if kind=='original':
                    require(r['original_zip_sha256']=='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28' and equal(r['observed'],r['expected']) and len(r['observed'])==8,'Original limited join mismatch')
            snapshots[runtime+'-'+kind]={'four_snapshots_equal':True,'paths':[str(p) for p in paths]}
    for runtime in ('74','83'):
        for phase in ('primary','claude'):
            entries=[json.loads(x) for x in (RUN/f'{phase}{runtime}-execution-ledger.jsonl').read_text().splitlines()]
            require(entries[-1]['stopped_at_unexpected_exit'] is None and entries[-1]['after_snapshot_exit_as_expected'] is True,'Incomplete execution ledger')
            for entry in entries:
                if 'command' not in entry:continue
                strict_exit(entry['process_exit'],0)
                for channel in ('stdout','stderr','exit'):
                    require(digest((REPO/entry[channel+'_path']).read_bytes())==entry[channel+'_sha256'],'Ledger output drift')
                if entry['output_sha256'] is not None:require(digest((REPO/entry['output']).read_bytes())==entry['output_sha256'],'Ledger JSON drift')
    return {'status':'PASS_BOUNDED_API4_CLI48_ACTUAL_ARTIFACT_REPEAT','api':api,'cli':cli,'snapshots':snapshots,'application_acceptance':False,'full_original_source_attestation':False,'privacy_acceptance':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
    result=reconcile()
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'status':result['status'],'api_groups_events':[result['api']['candidate_groups'],result['api']['candidate_events']]}))

#!/usr/bin/env python3
"""Independent processes using unchanged real vendor loader implementations."""
import argparse,hashlib,json,re,shlex,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'autoload83'))
from prepare import sha,require
from collect import inventory as source_inventory
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
STAGE='/home/vagrant/php-autoload83-composition-r1'
CASES=['hp-append','hp-prepend','hp-throw','hp-repeat','core-repeat','cli-append','cli-prepend','cli-throw-front','cli-throw-tail','cli-repeat']
TARGETS={'hp':'vendor/htmlpurifier/library/HTMLPurifier.autoload.php','core':'vendor/symfony/util/sfCore.class.php','cli':'vendor/symfony-data/bin/symfony.php'}
def strict_equal(a,b):
    return json.dumps(a,sort_keys=True,separators=(',',':'),allow_nan=False)==json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False)

def expected(case,variant):
    family=case.split('-')[0];framework={'hp':'HTMLPurifier_Bootstrap::autoload','core':'sfCore::splAutoload','cli':'__autoload' if variant=='original' else 'Closure'}[family]
    result={}
    if family=='cli':result['phase']='post-version-composition'
    result['queue-before']=[] if family=='core' else [framework]
    if case=='cli-repeat':return dict(result,**{'about-to-repeat-entire-cli':True,'events':[]})
    if family=='core':
        result['internal-callables']=[['sfCore','splAutoload'],['sfCore','splAutoload']]
        q=['sfCore::splAutoload','sfCore::splSimpleAutoload','finalLoader']
    elif 'prepend' in case or 'throw-front' in case:q=['laterLoader']+([] if family=='cli' and variant=='original' else [framework])+['finalLoader']
    else:q=([] if family=='cli' and variant=='original' else [framework])+['laterLoader','finalLoader']
    result['queue-after']=q
    throwing='throw' in case
    throwhit=case=='cli-throw-front' or (case=='cli-throw-tail' and variant=='original')
    shadow='prepend' in case or (case=='cli-append' and variant=='original')
    exc={'class':'RuntimeException','message':'composition-fixture-exception'}
    result['hit']={'loaded':not throwhit,'exception':exc if throwhit else None}
    if throwhit:winner=None
    elif family=='core':winner='/audit/fixtures/map/FixtureMapped.php'
    elif shadow:winner='/audit/composition-fixtures/'+family+'-shadow.php'
    elif family=='hp':winner='/audit/source/vendor/htmlpurifier/library/HTMLPurifier/EntityLookup.php'
    else:winner='/audit/fixtures/project/lib/model/FixtureFallback.php'
    result['winner']=winner
    result['miss']={'loaded':False,'exception':exc if throwing else None}
    hitclass='HTMLPurifier_EntityLookup' if family=='hp' else 'FixtureFallback'
    events=[['later',hitclass]] if throwhit or shadow else []
    if family!='core':events += [['later','FixtureMissing']]
    if not throwing:events += [['final','FixtureMissing']]
    result['events']=events
    return result

def diagnostic_contract(case,runtime,variant):
    family=case.split('-')[0];rows=[]
    autoload='__autoload() is deprecated, use spl_autoload_register() instead'
    yaml='Methods with the same name as their class will not be constructors in a future version of PHP; pakeYAMLNode has a deprecated constructor'
    if runtime=='74':
        if variant=='original':
            lines=[17,17] if case=='hp-repeat' else ([17] if family=='hp' else ([188,264] if family=='core' else [107]))
            rows += [(TARGETS[family],n,autoload) for n in lines]
        if family=='cli':rows.append(('vendor/symfony/vendor/pake/pakeYaml.class.php',54,yaml))
    diagnostics=[{'severity':8192,'file':f,'line':n,'message_sha256':hashlib.sha256(m.encode()).hexdigest()} for f,n,m in rows]
    stderr=['Deprecated: '+m+' in /audit/source/'+f+' on line '+str(n) for f,n,m in rows]
    if case=='cli-repeat':
        target='/audit/source/'+TARGETS['cli']
        if variant=='original':
            stderr += ['Deprecated: '+autoload+' in '+target+' on line 107','Fatal error: Cannot redeclare __autoload() (previously declared in '+target+':107) in '+target+' on line 107']
        else:stderr += ['Fatal error: Cannot declare class simpleAutoloader, because the name is already in use in '+target+' on line 36']
    return diagnostics,'\n'.join(stderr)

def validate(body,case,runtime,variant,returncode,stderr,hashes):
    require(type(returncode) is int,'Exit must be an integer, not bool/float')
    require(body['case']==case and body['php'].startswith('7.4.' if runtime=='74' else '8.3.'),'Case/runtime mismatch')
    family=case.split('-')[0];target=TARGETS[family]
    require(body['target']=={'path':target,'sha256':hashes['/audit/source/'+target]},'Target hash mismatch')
    require(type(body['loaded']) is dict and '/audit/source/'+target in body['loaded'],'Actual loader not loaded')
    require('/audit/probe.php' in body['loaded'],'Probe identity absent')
    for path,digest in body['loaded'].items():require(hashes.get(path)==digest,'Unknown or altered included source '+path)
    rows=body['rows'];require(len(rows)==len({r['case'] for r in rows}),'Duplicate row')
    require(strict_equal({r['case']:r['value'] for r in rows},expected(case,variant)),'Unexpected exact rows/traces')
    value=expected(case,variant).get('winner')
    if value:require(value in body['loaded'],'Winner provenance absent')
    diagnostics,expected_stderr=diagnostic_contract(case,runtime,variant)
    require(strict_equal(body['diagnostics'],diagnostics),'Unexpected exact diagnostics')
    require(stderr.strip()==expected_stderr,'Unexpected native stderr/fatal message or line')
    if case=='cli-repeat':
        require(returncode==255 and re.search(r'Cannot (redeclare|declare)',stderr) is not None and target in stderr,'Missing native full-file redeclaration fatal')
        return 'EXPECTED_FATAL'
    require(returncode==0 and 'fatal' not in body,'Real source execution failed')
    return 'PASS'

def main():
    p=argparse.ArgumentParser();p.add_argument('source_identity',type=Path);p.add_argument('output',type=Path);a=p.parse_args();require(not a.output.exists(),'Refuse existing output')
    identity=json.loads(a.source_identity.read_text());before=source_inventory(identity)
    own={str(x.relative_to(HERE)):sha(x) for x in [HERE/'probe.php',HERE/'run.sh',*sorted((HERE/'fixtures').glob('*.php'))]}
    def own_inventory():
        c='sha256sum '+' '.join(shlex.quote(STAGE+'/'+x) for x in own)
        r=subprocess.run(SSH+[c],capture_output=True,text=True,timeout=60);require(r.returncode==0,'Harness hash command failed')
        observed={line.split()[1][len(STAGE)+1:]:line.split()[0] for line in r.stdout.splitlines()};require(observed==own,'Harness drift');return observed
    own_inventory();records=[]
    for runtime,variant in [('74','original'),('74','candidate'),('83','candidate')]:
        hashes={('/audit/source/'+path[len(variant)+1:]):digest for path,digest in before.items() if path.startswith(variant+'/')}
        hashes.update({('/audit/'+path):digest for path,digest in before.items() if path.startswith('fixtures/')})
        hashes['/audit/probe.php']=own['probe.php']
        hashes.update({'/audit/composition-fixtures/'+Path(path).name:digest for path,digest in own.items() if path.startswith('fixtures/')})
        for case in CASES:
            command='bash '+STAGE+'/run.sh '+runtime+' '+variant+' '+case
            r=subprocess.run(SSH+[command],capture_output=True,text=True,timeout=90);body=None;error=None
            try:
                lines=[l[len('COMPOSITION_RESULT '):] for l in r.stdout.splitlines() if l.startswith('COMPOSITION_RESULT ')];require(len(lines)==1,'Missing/duplicate structured report')
                body=json.loads(lines[0]);status=validate(body,case,runtime,variant,r.returncode,r.stderr,hashes)
            except (ValueError,TypeError,KeyError,AttributeError) as e:status='FAIL';error=str(e)
            records.append({'runtime':runtime,'variant':variant,'case':case,'command':command,'exit':r.returncode,'status':status,'validation_error':error,'result':body,'stdout':r.stdout,'stderr':r.stderr})
            a.output.write_text(json.dumps({'status':'INCOMPLETE','records':records,'source_identity':identity,'harness':own,'collector_sha256':sha(__file__)},indent=2)+'\n')
    own_inventory();source_inventory(identity)
    failed=sum(r['status']=='FAIL' for r in records)
    report={'status':'FAIL' if failed else 'PASS','records':records,'source_identity':identity,'harness':own,'collector_sha256':sha(__file__),'source_harness_unchanged':True,'failed_checks':failed,'scope':'30 bounded real-loader composition processes; native74 implicit-loader deltas explicit','application_acceptance':False,'diagnostics':'Exact native warning fields/messages and stderr/fatal text/line contract; repeat-include JSON is intentionally emitted before fatal, native stderr verifies outcome'}
    a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'failed_checks':failed}));return int(failed!=0)
if __name__=='__main__':raise SystemExit(main())

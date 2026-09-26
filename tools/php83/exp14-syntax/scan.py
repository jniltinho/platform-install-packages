#!/usr/bin/env python3
"""Explicit narrow adapter over frozen exp13 inventory/lint/runtime orchestration."""
import hashlib
import importlib.util
import json
import pathlib
import re

HERE=pathlib.Path(__file__).resolve().parent
PARENT=HERE/'frozen-exp13-scan.py'
PARENT_PIN='81e5d9a0b181fbfa3f6583f011f88a8b7153660c93df55fc9e0beff9fc56cf0e'
if hashlib.sha256(PARENT.read_bytes()).hexdigest()!=PARENT_PIN:raise RuntimeError('Frozen exp13 scanner drift')
spec=importlib.util.spec_from_file_location('frozen_exp13_scan',PARENT)
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
core=parent.core;require=parent.require;sha=parent.sha;strict_equal=parent.strict_equal
SUFFIXES=parent.SUFFIXES;PHP=parent.PHP;FLAGS=parent.FLAGS;diagnostics=parent.diagnostics
VARIANTS=('exp13','exp14')
FILES={'scan.py','frozen-exp13-scan.py','frozen-core.py','input-contract.json','stage.py','run.sh'}
PRIOR_PIN='6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944'
TARGET='api_v3/lib/KalturaEntryService.php'
TARGETS=[{'path':TARGET,'exp13_sha256':'9495b584f73df1f4a11812efa964f57f42562159a405693b71e1731d53fe4dd5','exp14_sha256':'b48fd2bb6d94157490294d8acb3fd8918c63d7a35c1ae024529658a4f40c895a'}]
REJECTIONS=['vendor/aws/Doctrine/Common/Cache/RiakCache.php','vendor/symfony-data/generator/sfPropelAdmin/default/skeleton/actions/actions.class.php','vendor/symfony-data/generator/sfPropelCrud/default/skeleton/actions/actions.class.php','vendor/symfony-data/skeleton/batch/default.php','vendor/symfony-data/skeleton/batch/rotate_log.php','vendor/symfony-data/skeleton/controller/controller.php','vendor/symfony-data/skeleton/module/module/actions/actions.class.php']
EXPECTED_DIAGNOSTIC='Deprecated: Optional parameter $entryType declared before required parameter $rank is implicitly treated as a required parameter in '+TARGET+' on line 1836'
def digest(value):return type(value) is str and re.fullmatch('[a-f0-9]{64}',value) is not None
def load_contract(path=HERE/'input-contract.json'):
    d=json.loads(pathlib.Path(path).read_text())
    require(type(d.get('schema')) is int and d['schema']==1,'Schema')
    require(set(d.get('pins',{}))==set(VARIANTS) and d['pins']['exp13']==PRIOR_PIN,'Prior pin')
    require(digest(d['pins']['exp14']) and d['pins']['exp14']!=PRIOR_PIN,'Candidate pin pending/invalid')
    require(strict_equal(d.get('counts'),{'exp13':11785,'exp14':11785}),'Counts')
    require(strict_equal(d.get('targets'),TARGETS),'Exactly reviewed one-file source delta required')
    require(strict_equal(d.get('historical_rejections'),REJECTIONS),'Historical reject contract')
    metadata=d.get('metadata_delta_allowlist')
    require(type(metadata) is list and len(metadata)>0,'Exact metadata delta pending')
    seen=set()
    for row in metadata:
        require(set(row)=={'path','exp13_sha256','exp14_sha256'},'Metadata row fields')
        p=row['path'];require(type(p) is str and p.startswith('.php83-experimental/') and len(pathlib.PurePosixPath(p).parts)==2 and '\\' not in p and '..' not in pathlib.PurePosixPath(p).parts and p not in seen,'Metadata path');seen.add(p)
        require(p.endswith('.patch') or p in ('.php83-experimental/manifest.json','.php83-experimental/README.txt'),'Unexpected metadata type')
        require(row['exp13_sha256'] is None or digest(row['exp13_sha256']),'Metadata prior hash')
        require(digest(row['exp14_sha256']) and row['exp13_sha256']!=row['exp14_sha256'],'Metadata candidate hash')
    return d

def compare_reports(reports,contract):
    require(set(reports)==set(VARIANTS),'Variant set');maps={}
    require(strict_equal(contract['counts'],{'exp13':11785,'exp14':11785}) and strict_equal(contract['targets'],TARGETS),'Contract drift')
    for variant in VARIANTS:
        rows=reports[variant]['records'];require(len(rows)==11785,'Missing/truncated rows');mapping={}
        for row in rows:
            require(set(row)=={'path','sha256','command','exit','stdout','stderr','diagnostics','duration_ns'},'Row fields')
            p=row['path'];require(type(p) is str and str(pathlib.PurePosixPath(p))==p and p and not p.startswith('/') and '..' not in pathlib.PurePosixPath(p).parts and '\\' not in p and pathlib.Path(p).suffix.lower() in SUFFIXES and p not in mapping,'Row path')
            require(type(row['exit']) is int and row['exit'] in (0,255),'Incomplete compiler process')
            require(type(row['duration_ns']) is int and row['duration_ns']>=0,'Duration')
            require(digest(row['sha256']) and all(type(row[k]) is str for k in ['stdout','stderr','diagnostics']),'Row types')
            require(row['command']==[PHP]+FLAGS+['/audit/'+variant+'/'+p],'Command')
            require(row['diagnostics']==diagnostics(row['stdout'],row['stderr'],pathlib.Path('/audit/'+variant)),'Diagnostic derivation')
            mapping[p]=row
        maps[variant]=mapping
        inventory=reports[variant]['source_before']
        require({p:h for p,h in inventory.items() if pathlib.Path(p).suffix.lower() in SUFFIXES}=={p:r['sha256'] for p,r in mapping.items()},'Inventory/records mismatch')
    old,new=maps['exp13'],maps['exp14']
    require(old.keys()==new.keys(),'Added/removed PHP source')
    require({p for p in old if old[p]['sha256']!=new[p]['sha256']}=={TARGET},'Unexpected PHP source delta')
    for variant in VARIANTS:
        row=maps[variant][TARGET]
        require(row['sha256']==TARGETS[0][variant+'_sha256'] and row['exit']==0,'Rank target hash/rejection')
    for p in old.keys()-{TARGET}:require((old[p]['exit'],old[p]['diagnostics'])==(new[p]['exit'],new[p]['diagnostics']),'Unchanged outcome drift')
    require(old[TARGET]['diagnostics']==EXPECTED_DIAGNOSTIC and new[TARGET]['diagnostics']=='','Exact rank diagnostic delta')
    rejected=lambda m:sorted(p for p,r in m.items() if r['exit']==255)
    require(rejected(old)==rejected(new)==REJECTIONS,'Historical seven rejects changed')
    inventories={v:reports[v]['source_before'] for v in VARIANTS}
    oldi,newi=inventories['exp13'],inventories['exp14']
    expected={r['path']:r for r in contract['metadata_delta_allowlist']};expected[TARGET]=TARGETS[0]
    actual={p for p in oldi.keys()|newi.keys() if oldi.get(p)!=newi.get(p)}
    require(actual==set(expected),'Unapproved whole-archive delta')
    for p,r in expected.items():
        require(oldi.get(p)==r['exp13_sha256'] and newi.get(p)==r['exp14_sha256'],'Whole-archive delta hash')
    return {'bounded_compiler_nonregression':True,'changed_paths':[TARGET],'added_paths':[],
        'metadata_delta':contract['metadata_delta_allowlist'],'remaining_rejected_paths':REJECTIONS,
        'diagnostic_delta':[{'path':TARGET,'before_diagnostics':old[TARGET]['diagnostics'],'after_diagnostics':new[TARGET]['diagnostics']}],
        'candidate_all_files_compile':False,'application_acceptance':False}

# Frozen functions resolve these explicit globals in their defining module.
parent.VARIANTS=VARIANTS;parent.FILES=FILES;parent.load_contract=load_contract;parent.compare_reports=compare_reports
run=parent.run
if __name__=='__main__':raise SystemExit(run())

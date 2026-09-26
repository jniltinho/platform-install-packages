#!/usr/bin/env python3
"""Thin paired compiler adapter: frozen inventory helpers, explicit added source."""
import concurrent.futures,hashlib,importlib.util,json,os,pathlib,re,subprocess,time
HERE=pathlib.Path(__file__).resolve().parent
CORE=HERE/'frozen-core.py';CORE_PIN='fd98fdb419679017363cdb4fe6fc2f0db0dfcbbe5ee84d3055f79e4260e48f3e'
if hashlib.sha256(CORE.read_bytes()).hexdigest()!=CORE_PIN:raise RuntimeError('Frozen helper drift')
spec=importlib.util.spec_from_file_location('compiler_core',CORE);core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
require=core.require;sha=core.sha;strict_equal=core.strict_equal;SUFFIXES=core.SUFFIXES;FLAGS=core.FLAGS;PHP=core.PHP
VARIANTS=('exp12','exp13');FILES={'scan.py','frozen-core.py','input-contract.json','run.sh','stage.py'}
def load_contract(path=HERE/'input-contract.json'):
 d=json.loads(pathlib.Path(path).read_text());require(type(d.get('schema')) is int and d['schema']==1,'Schema')
 require(set(d['pins'])==set(VARIANTS) and d['pins']['exp12']=='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b','Baseline identity')
 require(type(d['pins']['exp13']) is str and re.fullmatch('[a-f0-9]{64}',d['pins']['exp13']) and d['pins']['exp13']!=d['pins']['exp12'],'Candidate pin pending/invalid')
 require(strict_equal(d['counts'],{'exp12':11784,'exp13':11785}),'Counts')
 require(len(d['targets'])==13,'Target count');seen=set();added=[]
 for t in d['targets']:
  p=t['path'];require(type(p) is str and p and str(pathlib.PurePosixPath(p))==p and not p.startswith('/') and '..' not in pathlib.PurePosixPath(p).parts and '\\' not in p and pathlib.Path(p).suffix.lower() in SUFFIXES and p not in seen,'Target path');seen.add(p)
  for key in ['exp12_sha256','exp13_sha256']:
   if key=='exp12_sha256' and t[key] is None:added.append(p);continue
   require(type(t[key]) is str and re.fullmatch('[a-f0-9]{64}',t[key]),'Target hash')
  require(t['exp12_sha256']!=t['exp13_sha256'],'Unchanged target')
 require(added==['infra/general/kXmlEntityLoaderPolicy.php'],'Added member')
 require(type(d.get('historical_rejections')) is list and len(set(d['historical_rejections']))==len(d['historical_rejections'])==7,'Historical rejects');return d

def diagnostics(stdout,stderr,source):
 return '\n'.join(l for l in (stdout+stderr).splitlines() if not l.startswith('No syntax errors detected')).replace(str(source)+'/', '')
def lint(source,path,pin):
 file=source/path;require(sha(file)==pin,'Source before drift');cmd=[PHP]+FLAGS+[str(file)];start=time.monotonic_ns()
 try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=20);status=r.returncode;out=r.stdout;err=r.stderr
 except subprocess.TimeoutExpired as e:
  status=124;out=e.stdout or '';err=e.stderr or '';out=out.decode() if isinstance(out,bytes) else out;err=err.decode() if isinstance(err,bytes) else err
 require(sha(file)==pin,'Source after drift')
 return {'path':path,'sha256':pin,'command':cmd,'exit':status,'stdout':out,'stderr':err,'diagnostics':diagnostics(out,err,source),'duration_ns':time.monotonic_ns()-start}
def runtime_identity():
 require(os.geteuid()==1000,'Lab uid')
 for name in ['/audit/tools']+['/audit/'+v+suffix for v in VARIANTS for suffix in ['', '.zip']]:require(os.statvfs(name).f_flag & os.ST_RDONLY,'Writable audit bind')
 links=subprocess.check_output(['/usr/bin/ldd',PHP],text=True);require('not found' not in links,'Missing library')
 libraries={p:sha(p) for p in sorted(set(re.findall(r'(/[^\s()]+)',links)))}
 version=subprocess.check_output([PHP,'-n','-v'],text=True);require(version.startswith('PHP 8.3.'),'PHP version')
 ini=subprocess.check_output([PHP,'-n','--ini'],text=True);require('Loaded Configuration File:         (none)' in ini,'INI loaded')
 return {'command':PHP,'resolved_path':str(pathlib.Path(PHP).resolve()),'sha256':sha(PHP),'version':version,'modules':subprocess.check_output([PHP,'-n','-m'],text=True),'ini':ini,'linked_library_sha256':libraries,'environment':{'LC_ALL':os.environ.get('LC_ALL'),'TZ':os.environ.get('TZ')}}
def compare_reports(reports,contract):
 require(set(reports)==set(VARIANTS),'Variant set');maps={}
 for variant in VARIANTS:
  rows=reports[variant]['records'];require(len(rows)==contract['counts'][variant],'Missing/truncated records');m={}
  for r in rows:
   require(set(r)=={'path','sha256','command','exit','stdout','stderr','diagnostics','duration_ns'},'Row fields')
   p=r['path'];require(type(p) is str and p not in m and pathlib.Path(p).suffix.lower() in SUFFIXES and not p.startswith('/') and '..' not in pathlib.PurePosixPath(p).parts,'Record path')
   require(type(r['exit']) is int and r['exit'] in (0,255),'Incomplete compiler process');require(type(r['duration_ns']) is int and r['duration_ns']>=0,'Duration')
   require(all(type(r[k]) is str for k in ['sha256','stdout','stderr','diagnostics']),'Record type');require(re.fullmatch('[a-f0-9]{64}',r['sha256']),'Record hash')
   require(r['command']==[PHP]+FLAGS+['/audit/'+variant+'/'+p],'Command');require(r['diagnostics']==diagnostics(r['stdout'],r['stderr'],pathlib.Path('/audit/'+variant)),'Diagnostic derivation');m[p]=r
  maps[variant]=m
 old,new=maps['exp12'],maps['exp13'];targets={t['path']:t for t in contract['targets']};added={p for p,t in targets.items() if t['exp12_sha256'] is None};changed=set(targets)-added
 require(new.keys()-old.keys()==added and not old.keys()-new.keys(),'Unexpected added/removed source')
 require({p for p in old if old[p]['sha256']!=new[p]['sha256']}==changed,'Unexpected changed source')
 for p,t in targets.items():
  require(new[p]['sha256']==t['exp13_sha256'] and (p in added or old[p]['sha256']==t['exp12_sha256']),'Target identity')
  require(new[p]['exit']==0 and (p in added or old[p]['exit']==0),'Target compiler rejection')
 for p in old.keys()-changed:require((old[p]['exit'],old[p]['diagnostics'])==(new[p]['exit'],new[p]['diagnostics']),'Unchanged source outcome drift')
 rejected=lambda m:sorted(p for p,r in m.items() if r['exit']==255)
 require(rejected(old)==rejected(new)==contract['historical_rejections'],'Historical seven rejections changed')
 delta=[{'path':p,'kind':'added' if p in added else 'changed','before_diagnostics':None if p in added else old[p]['diagnostics'],'after_diagnostics':new[p]['diagnostics']} for p in sorted(targets)]
 return {'bounded_compiler_nonregression':True,'added_paths':sorted(added),'changed_paths':sorted(changed),'remaining_rejected_paths':rejected(new),'diagnostic_delta':delta,'candidate_all_files_compile':False,'application_acceptance':False}
def run():
 contract=load_contract();report={'schema':1,'input_contract':contract,'variants':{},'application_acceptance':False};runtime=None;harness=None
 try:
  runtime=runtime_identity();report['runtime_before']=runtime;harness={n:sha(HERE/n) for n in FILES};report['harness_before']=harness
  for v in VARIANTS:
   archive=pathlib.Path('/audit/'+v+'.zip');source=pathlib.Path('/audit/'+v);before=core.archive_inventory(archive,source,contract['pins'][v]);selected=sorted(p for p in before if pathlib.Path(p).suffix.lower() in SUFFIXES);require(len(selected)==contract['counts'][v],'PHP inventory')
   result={'zip_sha256':contract['pins'][v],'source_before':before,'records':[]};report['variants'][v]=result
   with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for row in pool.map(lambda p:lint(source,p,before[p]),selected):result['records'].append(row)
   result['source_after']=core.archive_inventory(archive,source,contract['pins'][v]);require(result['source_after']==before,'Archive/source post drift');result['summary']=core.summarize(result['records'])
  report['comparison']=compare_reports(report['variants'],contract);report['status']='COMPLETE_BOUNDED'
 except (Exception,KeyboardInterrupt) as e:report['status']='FAILED_OR_INTERRUPTED';report['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  for v,result in report['variants'].items():
   if 'source_after' not in result:
    try:result['source_after']=core.archive_inventory(pathlib.Path('/audit/'+v+'.zip'),pathlib.Path('/audit/'+v),contract['pins'][v])
    except Exception as e:result['post_source_error']=str(e)
  try:report['runtime_after']=runtime_identity();report['harness_after']={n:sha(HERE/n) for n in FILES}
  except Exception as e:report['post_identity_error']=str(e)
  if report.get('runtime_after')!=runtime or report.get('harness_after')!=harness:report['status']='IDENTITY_FAILURE_OR_INCOMPLETE'
  print(json.dumps(report,indent=2))
 return 0 if report['status']=='COMPLETE_BOUNDED' else 2
if __name__=='__main__':raise SystemExit(run())

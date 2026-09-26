"""New phase: unchanged fixture with explicitly pinned, privately extracted SOAP."""
import hashlib,json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
E=HERE.parents[2]/'doc/php83/evidence/xml-lifecycle'
def file_hash(value):
 if type(value) is dict:
  if set(value)!={'resolved_path','sha256'}:raise ValueError('Unexpected file identity schema')
  value=value['sha256']
 if type(value) is not str or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):raise ValueError('Invalid file hash')
 return value
def prepare(out):
 if out.exists():raise ValueError('Refuse existing stage')
 original=Path('/tmp/php-xml-lifecycle-prep-r2');manifest=json.loads((original/'identities.json').read_text())
 if hashlib.sha256((original/'identities.json').read_bytes()).hexdigest()!='5c066127b4342ec61682e44b7b0509bc768cc50cffbf270a7e10b16dbf0c8bd6':raise ValueError('Old stage drift')
 for n,h in manifest['files'].items():
  if hashlib.sha256((original/n).read_bytes()).hexdigest()!=h:raise ValueError('Old payload drift')
 providers={}
 for mode,report,snapshot,php,abi in [('74','provider74-extraction-r2.json','runtime74-before.json','/usr/bin/php7.4','20190902'),('83','provider83-extraction.json','runtime83-provider-before.json','/usr/bin/php8.3','20230831')]:
  p=json.loads((E/report).read_text());r=json.loads((E/snapshot).read_text())['identity']
  expected_version={'74':'1:7.4.33-30+ubuntu24.04.1+deb.sury.org+1','83':'8.3.6-0ubuntu0.24.04.11'}[mode]
  expected_package={'74':'f25c5a8342b852ed5f97154e270f22805f4dc221132b15084c6936f59016511b','83':'eeb541e17950d330e01f5d0c47620ad45de92b64517320980691646777e4ad29'}[mode]
  if p['version']!=expected_version or p['package_sha256']!=expected_package:raise ValueError('Exact provider version/hash')
  if p['status']!='EXTRACTED_NOT_LOADED' or p['abi_directory']!=abi:raise ValueError('Provider identity')
  modules=['xml','dom']+(['json'] if mode=='74' else [])
  files={php:file_hash(r['files'][php]),p['module']:p['module_sha256'],**p['linked_libraries']}
  for m in modules:
   key='/usr/lib/php/'+abi+'/'+m+'.so';files[key]=file_hash(r['files'][key]);files.update(r['linked_libraries'][key])
  files.update(r['linked_libraries'][php])
  files={k:file_hash(v) for k,v in files.items()}
  providers[mode]={'module':p['module'],'files':files,'package_sha256':p['package_sha256'],'provider_report_sha256':hashlib.sha256((E/report).read_bytes()).hexdigest()}
 shutil.copytree(original,out)
 (out/'providers.json').write_text(json.dumps(providers,indent=2)+'\n')
 (out/'run.sh').write_bytes((HERE/'run-private-r2.sh').read_bytes())
 for name in ['providers.json','run.sh']:manifest['files'][name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
 manifest['phase']='private-soap-provider-r1'
 (out/'identities.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return {'manifest_sha256':hashlib.sha256((out/'identities.json').read_bytes()).hexdigest(),'files':len(manifest['files']),'phase':manifest['phase']}
if __name__=='__main__':print(json.dumps(prepare(Path(sys.argv[1]))))

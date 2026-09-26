#!/usr/bin/env python3
"""Revalidate retained17 observations: permit only pinned loaded-source hash fields."""
import argparse,copy,hashlib,importlib.util,json,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('base_additions',HERE/'collect-additions.py');base=importlib.util.module_from_spec(s);s.loader.exec_module(base)
MANIFEST=base.REPO/'doc/php83/evidence/exp12-candidate/selected-manifest.json'
MANIFEST_PIN='593ff6e826978c09704cf89f8cdf099452efdcf74a4c058bc88ee57ca16e74d6'
TARGETS={'vendor/symfony/vendor/pake/pakeApp.class.php','vendor/symfony-data/tasks/sfPakeGenerator.php'}
def references():
 base.need(base.sha(MANIFEST)==MANIFEST_PIN,'Selected metadata drift');manifest=json.loads(MANIFEST.read_text());rows={r['path']:r for r in manifest['patches'] if r['path'] in TARGETS};base.need(set(rows)==TARGETS,'Exact loaded-hash allowance targets')
 oldmanifest=base.REPO/'doc/php83/evidence/exp11-candidate/selected-manifest.json';base.need(base.sha(oldmanifest)=='99f87bf705b0a9c419229fc5c1484919e6de4ebc24dabcccb359b5bb762af2ff','Prior selected metadata drift')
 for revision,pin,field in [('exp11','f2474f5b951bfd2d121291025c8dd4554697fb5bb4024e132987643dab6144a7','before_sha256'),('exp12','de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b','after_sha256')]:
  archive=base.REPO.parent/'platform-install-packages-php83-artifacts'/revision/('Rigel-18.20.0-php83-experimental.'+revision+'.zip');base.need(base.sha(archive)==pin,'Artifact ZIP join drift')
  with zipfile.ZipFile(archive) as z:
   for path,row in rows.items():base.need(hashlib.sha256(z.read('server-Rigel-18.20.0/'+path)).hexdigest()==row[field],'Actual source pair mismatch')
 _,expected=base.reference_records();expected=copy.deepcopy(expected);changes=[]
 for (family,case),r in expected.items():
  marker={'autoload':'AUTOLOAD_RESULT ','composition':'COMPOSITION_RESULT '}.get(family)
  if marker is None:continue
  base.need(r['stdout'].count(marker)==1,'Exact JSON marker');body=json.loads(r['stdout'].split(marker,1)[1]);loaded=body['loaded']
  for path,row in rows.items():
   key=('/audit/source/' if family=='composition' else 'source/')+path
   if key not in loaded:continue
   base.need(loaded[key]==row['before_sha256'],'Historical source hash mismatch')
   old=json.dumps(key)+':'+json.dumps(row['before_sha256']);new=json.dumps(key)+':'+json.dumps(row['after_sha256'])
   base.need(r['stdout'].count(old)==1,'Exact loaded key/hash token occurrence')
   r['stdout']=r['stdout'].replace(old,new,1);changes.append({'family':family,'case':case,'loaded_key':key,'before_sha256':row['before_sha256'],'after_sha256':row['after_sha256']})
 allowed={(family,case,'/audit/source/' + 'vendor/symfony/vendor/pake/pakeApp.class.php' if family=='composition' else 'source/vendor/symfony/vendor/pake/pakeApp.class.php') for family,cases in [('autoload',['cli-version','cli-version-queue','cli-tasks-configured']),('composition',['cli-append','cli-prepend','cli-throw-front','cli-throw-tail','cli-repeat'])] for case in cases}
 allowed.add(('autoload','cli-tasks-configured','source/vendor/symfony-data/tasks/sfPakeGenerator.php'))
 base.need(len(changes)==9 and {(x['family'],x['case'],x['loaded_key']) for x in changes}==allowed,'Exact nine case/path loaded-field replacements')
 return expected,changes
def validate(report,post):
 expected,changes=references();summary=base.validate(report['records'],expected)
 base.need(report['artifact']==post,'Full source drift')
 base.need(report['artifact']['zip_sha256']=='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b','Wrong exp12 artifact')
 return {'summary':summary,'allowed_loaded_field_changes':changes,'all_other_stdout_stderr_exit_bytes_exact':True,'original_collector_status_retained':report['status'],'application_acceptance':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('post_source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=validate(json.loads(a.input.read_text()),json.loads(a.post_source.read_text()))
 with a.output.open('x') as f:json.dump({'validation':r,'input_sha256':base.sha(a.input),'validator_sha256':base.sha(Path(__file__)),'post_source_sha256':base.sha(a.post_source)},f,indent=2);f.write('\n')
 print(json.dumps(r['summary']))

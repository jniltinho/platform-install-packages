#!/usr/bin/env python3
"""Prepare held DEBUG numeric-token experiment; no runtime/network operations."""
import argparse,importlib.util,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('prior',HERE.parent/'build.py');prior=importlib.util.module_from_spec(s);s.loader.exec_module(prior)
TARGET='vendor/symfony-data/tasks/sfPakeGenerator.php'
PIN='67682683048afeaef9ed55bd95a5920792b2c6ab3b4ec11c804985ead4b347eb'
OLD=b'(boolean) $debug'
NEW=b'(int) (boolean) $debug'
def transform(data):
 if prior.sha(data)!=PIN or data.count(OLD)!=3:raise ValueError('Wrong original DEBUG source')
 lines=data.splitlines()
 if [i+1 for i,x in enumerate(lines) if OLD in x]!=[215,248,277]:raise ValueError('Unexpected DEBUG positions')
 candidate=data.replace(OLD,NEW)
 if candidate.replace(NEW,OLD)!=data or candidate.count(b'\n')!=data.count(b'\n'):raise ValueError('Unexpected delta')
 return candidate
def build(output):
 output=Path(output);output.mkdir(exist_ok=False)
 original=prior.read_archive(*prior.ARCHIVES['original']);exp10=prior.read_archive(*prior.ARCHIVES['exp10'])
 if set(original)!=set(exp10) or original[TARGET]!=exp10[TARGET]:raise ValueError('Upstream source cohort drift')
 prerequisite=dict(exp10);prerequisite[prior.TARGET]=prior.transform(exp10[prior.TARGET])
 debug=dict(prerequisite);debug[TARGET]=transform(prerequisite[TARGET])
 variants={'original':original,'exp10':exp10,'prerequisite':prerequisite,'debug':debug}
 for variant,files in variants.items():
  for name,data in files.items():
   p=output/variant/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 r=subprocess.run(['diff','-u','--label','a/'+TARGET,'--label','b/'+TARGET,str(output/'prerequisite'/TARGET),str(output/'debug'/TARGET)],capture_output=True)
 if r.returncode!=1:raise ValueError('Unexpected diff status')
 patch=output/'generator-debug.patch';patch.write_bytes(r.stdout)
 manifest={'schema':1,'status':'HELD_LOCAL_PREPARATION','target':TARGET,'before_sha256':PIN,'after_sha256':prior.sha(debug[TARGET]),'patch_sha256':prior.sha(r.stdout),'runtime_executed':False,'application_acceptance':False,'prerequisite':{'target':prior.TARGET,'before_sha256':prior.PIN,'after_sha256':prior.sha(prerequisite[prior.TARGET]),'selected_into_archive':False},'archives':prior.ARCHIVES,'files':{name:{v:prior.sha(files[name]) for v,files in variants.items()} for name in sorted(original)},'changed_from_prerequisite':[n for n in sorted(debug) if debug[n]!=prerequisite[n]],'debug_mapping_lines':[215,248,277]}
 (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output');build(p.parse_args().output)

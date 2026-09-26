#!/usr/bin/env python3
"""Local source joins for actual archive generator; no SSH or execution."""
import argparse,importlib.util,json,zipfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HELPER=ROOT/'tools/php83/template-generation/generator-debug-v1/build.py'
s=importlib.util.spec_from_file_location('held',HELPER);held=importlib.util.module_from_spec(s);s.loader.exec_module(held)
PIN='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
def stage(artifact,output):
 raw=artifact.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('Actual exp12 artifact mismatch')
 m=held.build(output)
 with zipfile.ZipFile(artifact) as z:
  if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Duplicate ZIP')
  for path,pins in m['files'].items():
   data=z.read('server-Rigel-18.20.0/'+path)
   if hashlib.sha256(data).hexdigest()!=pins['debug']:raise ValueError('Artifact does not match reviewed generator sources')
   (output/'debug'/path).write_bytes(data)
 for name in ['probe.php','run.sh']:(output/name).write_bytes(Path(__file__).with_name(name).read_bytes())
 (output/'artifact-provenance.json').write_text(json.dumps({'artifact_sha256':PIN,'generator_files':len(m['files']),'control':'held closure prerequisite cohort, not wholeexp11','candidate':'actualfull exp12 source mount','application_acceptance':False},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('output',type=Path);a=p.parse_args();stage(a.artifact,a.output)

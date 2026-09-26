#!/usr/bin/env python3
"""Verify existing corpus bytes against both actual artifact ZIPs before staging."""
import argparse,json,hashlib,zipfile
from pathlib import Path
import fixture,prepare
PIN='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
def stage(original,exp11,exp12,output):
 if hashlib.sha256(exp12.read_bytes()).hexdigest()!=PIN:raise ValueError('Actual exp12 pin mismatch')
 ids=fixture.build(original,exp11,output)
 with zipfile.ZipFile(exp12) as z:
  if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Duplicate ZIP')
  expected={'candidate.php':prepare.TARGET,**fixture.SOURCES}
  for name,path in expected.items():
   actual=z.read('server-Rigel-18.20.0/'+path)
   if actual!=(output/name).read_bytes():raise ValueError('Actual artifact/corpus source mismatch')
   (output/name).write_bytes(actual)
 ids['exp12_sha256']=PIN;ids['source_origin']='prior from exp11ZIP; candidate and dependencies byte-joined from exp12ZIP';ids['application_acceptance']=False
 (output/'identities.json').write_text(json.dumps(ids,indent=2)+'\n');return ids
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for name in ['original','exp11','exp12','output']:p.add_argument(name,type=Path)
 a=p.parse_args();stage(a.original,a.exp11,a.exp12,a.output)

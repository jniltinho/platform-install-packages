"""Small exact original-source join; no application/PHP/SQL execution."""
import argparse, hashlib, io, json, subprocess, zipfile
from pathlib import Path
ORIGINAL='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
PATHS=('api_v3/web/index.php','api_v3/lib/KalturaFrontController.php','api_v3/lib/KalturaDispatcher.php','alpha/config/kConf.php','alpha/apps/kaltura/lib/db/KalturaPDO.php','alpha/apps/kaltura/lib/Services_JSON.class.php','vendor/ZendFramework/library/Zend/Json.php','api_v3/lib/reflection/KalturaDocCommentParser.php')
def expected(archive):
 raw=Path(archive).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=ORIGINAL:raise ValueError('Original ZIP pin')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Duplicate ZIP')
  return {p:hashlib.sha256(z.read('server-Rigel-18.20.0/'+p)).hexdigest() for p in PATHS}
def validate(found,want):
 if set(found)!=set(PATHS) or found!=want:raise ValueError('Original scoped source drift')
 return True
REMOTE='''import hashlib,json,socket
from pathlib import Path
number=NUMBER
assert socket.gethostname()==('kaltura-php74-baseline' if number=='74' else 'kaltura-php83-lab')
root=Path('/home/vagrant/php'+number+'-audit/packaged/opt/kaltura/app')
paths=PATH_LIST
assert all((root/p).is_file() and not (root/p).is_symlink() for p in paths)
print(json.dumps({p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},sort_keys=True))
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('runtime',choices=['74','83']);p.add_argument('output',type=Path);a=p.parse_args()
 if a.output.exists():raise ValueError('Existing report')
 want=expected('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip')
 alias='baseline74' if a.runtime=='74' else 'php83'
 script=REMOTE.replace('NUMBER',repr(a.runtime)).replace('PATH_LIST',repr(PATHS))
 r=subprocess.run(['ssh','-T','-F','/tmp/kaltura-php'+a.runtime+'-ssh.conf',alias,'python3 -'],input=script,capture_output=True,text=True,timeout=60)
 report={'exit':r.returncode,'original_zip_sha256':ORIGINAL,'expected':want,'observed':None,'scope':'Eight directly used entry/dispatch/JSON/reflection sources, NOT complete loaded closure or baseline attestation','collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'application_acceptance':False}
 if r.returncode==0:report['observed']=json.loads(r.stdout)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 if r.returncode:raise RuntimeError('Original source snapshot command failed')
 validate(report['observed'],want)
if __name__=='__main__':main()

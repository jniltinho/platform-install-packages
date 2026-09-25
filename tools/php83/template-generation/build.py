#!/usr/bin/env python3
"""Prepare fresh read-only archive-derived fixtures; never contacts a VM."""
import argparse,hashlib,json,stat,subprocess
from pathlib import Path,PurePosixPath
from zipfile import ZipFile
TARGET='vendor/symfony/vendor/pake/pakeApp.class.php'
PIN='72f538165dd3226b46c35ddac7700c0f3a6046e74f4646b74ca5bd541d59b120'
ARCHIVES={'original':('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip','58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'),'exp10':('/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp10/Rigel-18.20.0-php83-experimental.exp10.zip','de177e6cbaedf3a3207661c2325f466cce37febb73190f3a49d31f24b740c053')}
PAKE=['pakeFunction.php']+[n+'.class.php' for n in ['pakeGlobToRegex','pakeNumberCompare','pakeException','pakeYaml','pakeGetopt','pakeFinder','pakeTask','pakeFileTask','pakeColor','pakeApp']]
FILES=['vendor/symfony/vendor/pake/'+n for n in PAKE]+['vendor/symfony/config/'+n+'.class.php' for n in ['sfConfig','sfLoader']]+['vendor/symfony-data/tasks/'+n+'.php' for n in ['sfPakeGenerator','sfPakePropelAdminGenerator','sfPakePropelCrudGenerator']]
PREFIXES=['vendor/symfony-data/skeleton/'+n+'/' for n in ['module','batch','controller']]+['vendor/symfony-data/generator/'+n+'/default/skeleton/' for n in ['sfPropelAdmin','sfPropelCrud']]
OLD=b"create_function('$f', 'return 0 === strpos($f, DIRECTORY_SEPARATOR) ? substr($f, 1) : $f;')"
NEW=b'function ($f) { return 0 === strpos($f, DIRECTORY_SEPARATOR) ? substr($f, 1) : $f; }'
def sha(b):return hashlib.sha256(b).hexdigest()
def transform(b):
 if sha(b)!=PIN or b.count(OLD)!=1:raise ValueError('Target pin/token mismatch')
 c=b.replace(OLD,NEW)
 if c.count(b'\n')!=b.count(b'\n'):raise ValueError('Line drift')
 return c

def read_archive(path,pin):
 if sha(Path(path).read_bytes())!=pin:raise ValueError('Archive pin mismatch')
 result={}
 with ZipFile(path) as z:
  for item in z.infolist():
   prefix='server-Rigel-18.20.0/'
   if not item.filename.startswith(prefix) or item.is_dir():continue
   name=item.filename[len(prefix):]
   if name not in FILES and not any(name.startswith(p) for p in PREFIXES):continue
   if name in result or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or stat.S_IFMT(item.external_attr>>16) not in (0,stat.S_IFREG):raise ValueError('Unsafe archive member')
   result[name]=z.read(item)
 if not set(FILES)<=set(result):raise ValueError('Missing exact prerequisite')
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();a.output.mkdir(exist_ok=False)
 blobs={n:read_archive(*v) for n,v in ARCHIVES.items()}
 if set(blobs['original'])!=set(blobs['exp10']):raise ValueError('Input cohort differs')
 if blobs['original'][TARGET]!=blobs['exp10'][TARGET]:raise ValueError('Target previously modified')
 blobs['candidate']=dict(blobs['exp10']);blobs['candidate'][TARGET]=transform(blobs['exp10'][TARGET])
 for variant,files in blobs.items():
  for name,data in files.items():
   p=a.output/variant/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 r=subprocess.run(['diff','-u','--label','a/'+TARGET,'--label','b/'+TARGET,str(a.output/'exp10'/TARGET),str(a.output/'candidate'/TARGET)],capture_output=True)
 if r.returncode!=1:raise ValueError('Unexpected diff')
 (a.output/'pake-relative-path.patch').write_bytes(r.stdout)
 manifest={'schema':1,'status':'HELD','target':TARGET,'before_sha256':PIN,'after_sha256':sha(blobs['candidate'][TARGET]),'patch_sha256':sha(r.stdout),'archives':ARCHIVES,'files':{n:{v:sha(b[n]) for v,b in blobs.items()} for n in sorted(blobs['original'])},'captured_variables':[],'runtime_executed':False}
 (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()

"""Prepare an unmodified full-source logging closure, never a privacy repair."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
PIN='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
PATHS=('infra/log/KalturaLog.php','infra/log/KalturaLogFactory.php','infra/log/KalturaSerializableStream.php',
 'vendor/ZendFramework/library/Zend/Config.php','vendor/ZendFramework/library/Zend/Log.php',
 'vendor/ZendFramework/library/Zend/Log/Filter/Priority.php','vendor/ZendFramework/library/Zend/Log/Filter/Interface.php',
 'vendor/ZendFramework/library/Zend/Log/Writer/Abstract.php','vendor/ZendFramework/library/Zend/Log/Writer/Stream.php',
 'vendor/ZendFramework/library/Zend/Log/Formatter/Simple.php','vendor/ZendFramework/library/Zend/Log/Formatter/Interface.php')
def prepare(archive,out):
 if out.exists():raise ValueError('Fresh stage required')
 raw=archive.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('Original ZIP drift')
 files={}
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Duplicate archive')
  for path in PATHS:
   i=z.getinfo('server-Rigel-18.20.0/'+path)
   if (i.external_attr>>16)&0o170000==0o120000:raise ValueError('Symlink member')
   files['source/'+path]=z.read(i)
 files['probe.php']=Path(__file__).with_name('probe.php').read_bytes()
 out.mkdir()
 for name,data in files.items():
  p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 report={'status':'UNMODIFIED_SYNTHETIC_PIPELINE_OBSERVATION_ONLY','archive_sha256':PIN,
 'files':{p:hashlib.sha256(b).hexdigest() for p,b in files.items()},
 'source_files':len(PATHS),'product_changes':0,'application_acceptance':False,'privacy_acceptance':False}
 (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 print(json.dumps(prepare(a.archive,a.output),indent=2))

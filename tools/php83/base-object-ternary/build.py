#!/usr/bin/env python3
"""Pinned read-only input; exactly two inserted parentheses. No VM action."""
import hashlib,json,subprocess,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SOURCE=Path('/home/nilton/Projetos/nilton/NOVOS/kaltura-rigel-18.20.0-source/server-Rigel-18.20.0')
TARGET='alpha/apps/kaltura/lib/baseObjectUtils.class.php'
PIN='1834b0ce9ab903af000e95c6a1c065a8dfaa64a91cd454a57de3b44824ee9e03'
FILES=[TARGET,'alpha/apps/kaltura/lib/myBaseObject.class.php','alpha/apps/kaltura/lib/kAssetUtils.class.php','infra/general/kString.class.php','vendor/propel/om/BaseObject.php','vendor/propel/util/BasePeer.php','alpha/lib/enums/entryStatus.php','infra/general/BaseEnum.php']
def sha(b):return hashlib.sha256(b).hexdigest()
def transform(b):
 if sha(b)!=PIN:raise ValueError('Upstream hash mismatch')
 old=b'$res .= $xml_element_name == NULL ? "" :\n\t\t\t$close_xml_element ?'
 new=b'$res .= ($xml_element_name == NULL ? "" :\n\t\t\t$close_xml_element) ?'
 if b.count(old)!=1:raise ValueError('Ambiguous target')
 result=b.replace(old,new)
 if len(result)!=len(b)+2 or result.count(b'\n')!=b.count(b'\n'):raise ValueError('Byte drift')
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();a.output.mkdir(exist_ok=False)
 files=[]
 for name in FILES:
  b=(SOURCE/name).read_bytes();c=transform(b) if name==TARGET else b
  for variant,blob in [('original',b),('candidate',c)]:
   dest=a.output/variant/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
  files.append({'path':name,'before_sha256':sha(b),'after_sha256':sha(c)})
 r=subprocess.run(['diff','-u','--label','a/'+TARGET,'--label','b/'+TARGET,str(a.output/'original'/TARGET),str(a.output/'candidate'/TARGET)],capture_output=True)
 if r.returncode!=1:raise ValueError('Unexpected diff result')
 (a.output/'base-object-ternary.patch').write_bytes(r.stdout)
 (a.output/'manifest.json').write_text(json.dumps({'schema':1,'status':'HELD','scope':'Two parentheses preserve PHP 7.4 left associativity; no release approval','files':files,'patch_sha256':sha(r.stdout),'inserted_bytes':2},indent=2)+'\n')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Read-only local archive/contract join; no SSH, extraction or PHP execution."""
import argparse,hashlib,json,pathlib,stat,zipfile
import scan

def inventory(path,pin):
 raw=pathlib.Path(path).read_bytes();scan.require(hashlib.sha256(raw).hexdigest()==pin,'ZIP pin mismatch');result={}
 with zipfile.ZipFile(path) as z:
  seen=set()
  for item in z.infolist():
   name=item.filename;p=pathlib.PurePosixPath(name)
   scan.require(name not in seen and not p.is_absolute() and p.parts and p.parts[0]=='server-Rigel-18.20.0' and '..' not in p.parts and '\\' not in name,'Unsafe/duplicate ZIP member');seen.add(name)
   scan.require(not stat.S_ISLNK(item.external_attr>>16),'ZIP symlink')
   if not item.is_dir():result[str(pathlib.PurePosixPath(*p.parts[1:]))]=hashlib.sha256(z.read(item)).hexdigest()
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('prior');p.add_argument('candidate');a=p.parse_args();c=scan.load_contract()
 maps={v:inventory(path,c['pins'][v]) for v,path in zip(scan.VARIANTS,[a.prior,a.candidate])}
 old,new=maps['exp13'],maps['exp14'];delta={p for p in old.keys()|new.keys() if old.get(p)!=new.get(p)}
 expected={r['path']:r for r in c['targets']+c['metadata_delta_allowlist']};scan.require(delta==set(expected),'Whole ZIP delta mismatch')
 for name,row in expected.items():scan.require(old.get(name)==row['exp13_sha256'] and new.get(name)==row['exp14_sha256'],'Delta identity mismatch')
 for v,m in maps.items():scan.require(sum(pathlib.Path(p).suffix.lower() in scan.SUFFIXES for p in m)==11785,'PHP-family count')
 print(json.dumps({'status':'LOCAL_PREFLIGHT_ONLY','pins':c['pins'],'delta':sorted(delta),'php_family_counts':c['counts'],'native_executed':False,'preflight_sha256':scan.sha(__file__)}))
if __name__=='__main__':main()

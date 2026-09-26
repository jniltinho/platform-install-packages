#!/usr/bin/env python3
"""Construct HELD signature-only delta patches; no PHP execution or selection."""
import argparse, difflib, hashlib, json, pathlib, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
HERE=pathlib.Path(__file__).resolve().parent
ZIP_SHA='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
MANIFEST_SHA='593ff6e826978c09704cf89f8cdf099452efdcf74a4c058bc88ee57ca16e74d6'
sha=lambda b:hashlib.sha256(b).hexdigest()
# Whole exact declaration lines only. Bodies, comments, parameters and newlines unchanged.
RULES={
 'alpha/apps/kaltura/lib/db/KalturaPDO.php':[
 ('\tpublic function prepare($sql, $driver_options = array())','\tpublic function prepare($sql, $driver_options = array()): PDOStatement|false'),
 ('\tpublic function exec($sql)','\tpublic function exec($sql): int|false'),
 ('\tpublic function query(...$args)','\tpublic function query(...$args): PDOStatement|false')],
 'vendor/propel/util/PropelPDO.php':[
 *[(f'\tpublic function {m}()',f'\t#[\\ReturnTypeWillChange]\n\tpublic function {m}()') for m in ['beginTransaction','commit','rollBack']],
 ('\tpublic function getAttribute($attribute)','\tpublic function getAttribute($attribute): mixed'),
 ('\tpublic function prepare($sql, $driver_options = array())','\tpublic function prepare($sql, $driver_options = array()): PDOStatement|false')],
 'vendor/propel/util/PropelConfiguration.php':[
 ('\tpublic function offsetExists($offset)','\tpublic function offsetExists($offset): bool'),
 ('\tpublic function offsetSet($offset, $value)','\tpublic function offsetSet($offset, $value): void'),
 ('\tpublic function offsetGet($offset)','\tpublic function offsetGet($offset): mixed'),
 ('\tpublic function offsetUnset($offset)','\tpublic function offsetUnset($offset): void')],
 'api_v3/lib/exceptions/KalturaAPIException.php':[
 ('\tpublic function __wakeup()','\tpublic function __wakeup(): void')],
 'vendor/propel/util/DebugPDO.php':[
 ('\tpublic function prepare($sql, $driver_options = array())','\tpublic function prepare($sql, $driver_options = array()): PDOStatement|false')]
}
def transform(path, raw, expected):
 if sha(raw)!=expected:raise ValueError('source hash drift: '+path)
 if path not in RULES:raise ValueError('unapproved target')
 out=raw
 for old,new in RULES[path]:
  a=(old+'\n').encode();b=(new+'\n').encode()
  if out.count(a)!=1:raise ValueError('declaration count: '+old)
  out=out.replace(a,b)
 # Reverse exact edits proves no incidental byte changes.
 reverse=out
 for old,new in reversed(RULES[path]):
  a=(old+'\n').encode();b=(new+'\n').encode()
  if reverse.count(b)!=1:raise ValueError('candidate declaration collision')
  reverse=reverse.replace(b,a)
 if reverse!=raw:raise ValueError('non-declaration byte drift')
 return out

def build(zip_path, output):
 output=pathlib.Path(output)
 if output.exists():raise ValueError('output already exists')
 zbytes=pathlib.Path(zip_path).read_bytes()
 if sha(zbytes)!=ZIP_SHA:raise ValueError('ZIP hash drift')
 manifest=(ROOT/'doc/php83/evidence/exp12-candidate/selected-manifest.json').read_bytes()
 if sha(manifest)!=MANIFEST_SHA:raise ValueError('selected manifest drift')
 pins=json.loads((HERE/'source-pins.json').read_text())
 with zipfile.ZipFile(zip_path) as z:
  sources={p:z.read('server-Rigel-18.20.0/'+p) for p in pins}
 for p,b in sources.items():
  if sha(b)!=pins[p]:raise ValueError('source identity drift')
 patches={};rows=[]
 for p in RULES:
  before=sources[p];after=transform(p,before,pins[p])
  diff=b''.join(difflib.diff_bytes(difflib.unified_diff,before.splitlines(True),after.splitlines(True),fromfile=('a/'+p).encode(),tofile=('b/'+p).encode()))
  name=pathlib.Path(p).name+'.patch';patches[name]=diff
  rows.append({'path':p,'before_sha256':sha(before),'after_sha256':sha(after),'patch':name,'patch_sha256':sha(diff),'declaration_edits':len(RULES[p])})
 result={'status':'HELD_LOCAL_PREPARATION_NOT_RUNTIME_VALIDATED','base_revision':'exp12','base_zip_sha256':ZIP_SHA,'selected_manifest_sha256':MANIFEST_SHA,'patch_kind':'delta against selected exp12, NOT cumulative upstream replacement','files':rows,'native_return_declarations':11,'transaction_attributes':3,'unchanged_MSSQL_sources':{p:pins[p] for p in pins if '/MSSQL/' in p},'open_prerequisites':['DebugPDO query signature remains pre-existing incompatible; v3 held prerequisite NOT included or selected.','Native diagnostic attribution, reflected contracts, full-source load/SQL/serialization tests and independent runtime repeat pending.','Three scoped transaction attributes defer full return typing to preserve MSSQL int|false|true behavior; no casts or method body changes.']}
 output.mkdir(parents=True)
 for name,b in patches.items():(output/name).write_bytes(b)
 (output/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--zip',required=True);a.add_argument('--output',required=True);args=a.parse_args(); print(json.dumps(build(args.zip,args.output),indent=2))

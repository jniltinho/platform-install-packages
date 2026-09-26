#!/usr/bin/env python3
"""Compose explicitly authorized DebugPDO v3 prerequisite and held return deltas."""
import argparse,hashlib,json,pathlib,subprocess,tempfile,zipfile
import build
TARGET='vendor/propel/util/DebugPDO.php'
V3_SHA='f966cf320b74717d134b4dd8710e5deafcbd77f890775cf643868e4cb4ab541e'
V3_AFTER='85ffdb6aefb5b538813de368177148e24071da8513f6aaadc8adccdc822cb6cc'
def apply_patch(source,path,patch):
 with tempfile.TemporaryDirectory() as d:
  base=pathlib.Path(d);p=base/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(source)
  r=subprocess.run(['patch','--batch','--fuzz=0','--posix','-p1'],input=patch,cwd=base,capture_output=True)
  if r.returncode!=0 or any(x in r.stdout.lower()+r.stderr.lower() for x in [b'offset',b'fuzz',b'reversed',b'failed']):raise ValueError('Strict patch replay failed')
  return p.read_bytes()
def compose(archive,output):
 output=pathlib.Path(output)
 if output.exists():raise ValueError('Output exists')
 if build.sha(pathlib.Path(archive).read_bytes())!=build.ZIP_SHA:raise ValueError('Wrong archive')
 pins=json.loads((build.HERE/'source-pins.json').read_text())
 patch=(build.ROOT/'patches/php83/held/DebugPDO-query-v3.patch').read_bytes()
 if build.sha(patch)!=V3_SHA:raise ValueError('v3 prerequisite drift')
 with zipfile.ZipFile(archive) as z:sources={p:z.read('server-Rigel-18.20.0/'+p) for p in pins}
 for p,b in sources.items():
  if build.sha(b)!=pins[p]:raise ValueError('Source drift')
 prerequisite=dict(sources);prerequisite[TARGET]=apply_patch(sources[TARGET],TARGET,patch)
 if build.sha(prerequisite[TARGET])!=V3_AFTER:raise ValueError('v3 resulting hash mismatch')
 candidate=dict(sources)
 for p in build.RULES:candidate[p]=build.transform(p,sources[p],pins[p])
 candidate[TARGET]=apply_patch(candidate[TARGET],TARGET,patch)
 # Independently commute the signature-only edit with prerequisite application.
 reverse_order=build.transform(TARGET,prerequisite[TARGET],V3_AFTER)
 if candidate[TARGET]!=reverse_order:raise ValueError('Composition order differs')
 variants={'exp12':sources,'prerequisite':prerequisite,'candidate':candidate}
 identities={};output.mkdir(parents=True)
 for name,files in variants.items():
  identities[name]={}
  for path,data in files.items():
   p=output/name/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);identities[name][path]=build.sha(data)
 result={'status':'PREPARED_THREE_COHORTS_NOT_RUNTIME_VALIDATED','base_zip_sha256':build.ZIP_SHA,'prerequisite_patch_sha256':V3_SHA,'prerequisite_debug_after_sha256':V3_AFTER,'variants':identities,'composition_commutes':True,'no_artifact_promotion':True,'scope':'Full seven class files as overlays over unchanged full exp12 source. Three cohorts: untouched exp12 expected DebugPDO load failure; v3-only prerequisite; v3 plus family. MSSQL source unchanged.'}
 (output/'identities.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zip',required=True);p.add_argument('--output',required=True);a=p.parse_args();print(json.dumps(compose(a.zip,a.output),indent=2))

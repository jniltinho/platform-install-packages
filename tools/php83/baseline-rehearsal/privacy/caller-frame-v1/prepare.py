"""Exact writer-frame omission only; creates isolated full-class fixtures, never installs."""
import hashlib, importlib.util, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
TARGET='infra/log/KalturaLog.php'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
policy=load('caller_frozen_policy',HERE.parent/'trace-policy-v1/prepare.py')
pipeline=load('caller_frozen_pipeline',HERE.parent/'pipeline/prepare.py')
ANCHOR=b'\t\t\t\t(isset($backtrace[$backtraceIndex]["function"]) && $backtrace[$backtraceIndex]["function"] == \'log\')'
ADDED=b'''\n\t\t\t\t||
\t\t\t\t(isset($backtrace[$backtraceIndex]["class"], $backtrace[$backtraceIndex]["function"])
\t\t\t\t && $backtrace[$backtraceIndex]["class"] === 'KalturaSerializableStream'
\t\t\t\t && $backtrace[$backtraceIndex]["function"] === '_write')'''
def sha(b):return hashlib.sha256(b).hexdigest()
def transform(raw):
 if raw.count(ANCHOR)!=1 or ADDED in raw:raise ValueError('Exact caller anchor drift/already applied')
 return raw.replace(ANCHOR,ANCHOR+ADDED)
def payload(archive,pin):
 original=policy.old.archive(archive,pin,pipeline.PATHS)
 overlay={p:policy.transform(p,b) if p in policy.TARGETS else b for p,b in original.items()}
 repaired=dict(overlay);repaired[TARGET]=transform(overlay[TARGET])
 patch=policy.old.patch_bytes(TARGET,overlay[TARGET],repaired[TARGET]);policy.old.strict_replay(TARGET,overlay[TARGET],patch,repaired[TARGET])
 blobs={v+'/'+p:b for v,fs in [('original',original),('overlay',overlay),('repaired',repaired)] for p,b in fs.items()}
 for n in ['probe.php','guest.py']:blobs[n]=(HERE/n).read_bytes()
 helpers=[HERE/'prepare.py',HERE/'probe.php',HERE/'guest.py',HERE/'validate.py',HERE.parent/'pipeline/prepare.py',HERE.parent/'trace-policy-v1/prepare.py',HERE.parent/'trace-policy-v1/writer-methods.php.inc',HERE.parent/'prepare.py',HERE.parent/'log-copy-methods.php.inc']
 m={'status':'PREPARED_ONLY','base_archive_sha256':pin,'files':{p:sha(b) for p,b in blobs.items()},'source_files_per_variant':len(pipeline.PATHS),'patch_sha256':sha(patch),'target':TARGET,'before_sha256':sha(overlay[TARGET]),'after_sha256':sha(repaired[TARGET]),'helper_hashes':{str(p.relative_to(HERE.parent)):sha(p.read_bytes()) for p in helpers},'application_acceptance':False}
 return blobs,m,patch
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('archive');a.add_argument('pin');a.add_argument('output',type=Path);x=a.parse_args()
 if x.output.exists():raise ValueError('Fresh output required')
 blobs,m,patch=payload(x.archive,x.pin);x.output.mkdir(parents=True)
 for n,b in blobs.items():p=x.output/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 (x.output/'caller.patch').write_bytes(patch);(x.output/'manifest.json').write_text(json.dumps(m,sort_keys=True,indent=2)+'\n')
 print(json.dumps(m,indent=2))

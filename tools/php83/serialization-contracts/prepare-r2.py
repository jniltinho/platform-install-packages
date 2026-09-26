#!/usr/bin/env python3
"""Versioned guarded bridge + independent FileCache fix. No archive extraction."""
import hashlib,importlib.util,json,zipfile,shutil,difflib
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r1',HERE/'prepare.py');r1=importlib.util.module_from_spec(spec);spec.loader.exec_module(r1)
EXTRA=['vendor/aws/Guzzle/Cache/AbstractCacheAdapter.php']+['vendor/aws/Doctrine/Common/Cache/'+n+'.php' for n in ['Cache','FlushableCache','ClearableCache','MultiGetCache']]
PATHS=r1.PATHS+EXTRA
FILECACHE='vendor/aws/Doctrine/Common/Cache/FileCache.php'
BRIDGE_OLD="        return array('payload' => $this->serialize());"
BRIDGE_NEW="""        $payload = $this->serialize();
        if (!is_string($payload)) {
            throw new \\Exception(get_class($this) . '::serialize() must return a string or NULL');
        }
        return array('payload' => $payload);"""
def bridge(source):
 value=r1.candidate(source)
 if value.count(BRIDGE_OLD.encode())!=1:raise ValueError('Bridge mismatch')
 return value.replace(BRIDGE_OLD.encode(),BRIDGE_NEW.encode(),1)
def cachefix(source):
 old=b"implode(str_split(hash('sha256', $id), 2), DIRECTORY_SEPARATOR)";new=b"implode(DIRECTORY_SEPARATOR, str_split(hash('sha256', $id), 2))"
 if source.count(old)!=1:raise ValueError('FileCache mismatch')
 return source.replace(old,new,1)
def sources():
 result={}
 for archive in [r1.ORIGINAL,r1.EXP12]:
  if hashlib.sha256(archive.read_bytes()).hexdigest()!=r1.PINS[str(archive)]:raise ValueError('Archive drift')
  with zipfile.ZipFile(archive) as z:
   rows={}
   for p in PATHS:
    names=[n for n in z.namelist() if n.endswith('/'+p)]
    if len(names)!=1:raise ValueError('Ambiguous ZIP member')
    rows[p]=z.read(names[0])
  result[str(archive)]=rows
 a=result[str(r1.ORIGINAL)];b=result[str(r1.EXP12)]
 root=Path('/home/nilton/Projetos/nilton/NOVOS/kaltura-rigel-18.20.0-source/graph-view')
 for p in PATHS:
  if a[p]!=b[p] or (root/p).read_bytes()!=a[p]:raise ValueError('Source mismatch '+p)
 return a
if __name__=='__main__':
 data=sources();out=HERE/'stage-r2';out.mkdir()
 held=Path('patches/php83/held/serialization-contracts');held.mkdir(parents=True,exist_ok=True)
 changes=[]
 for variant in ['original','cachefix','candidate']:
  for name,source in data.items():
   result=source
   if variant=='candidate' and name in r1.TARGETS:result=bridge(source)
   if variant!='original' and name==FILECACHE:result=cachefix(source)
   dest=out/variant/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(result)
   if variant=='candidate' and source!=result:
    patch=''.join(difflib.unified_diff(source.decode().splitlines(True),result.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    filename=held/(Path(name).stem+'.patch');filename.write_text(patch)
    changes.append({'path':name,'operation':'modify','family':'filecache-implode-order' if name==FILECACHE else 'aws-credential-magic-bridge','before_sha256':hashlib.sha256(source).hexdigest(),'after_sha256':hashlib.sha256(result).hexdigest(),'patch':str(filename),'patch_sha256':hashlib.sha256(filename.read_bytes()).hexdigest()})
 for f in ['probe.php','cache-probe.php']:shutil.copyfile(HERE/f,out/f)
 shutil.copyfile(HERE/'run-r2.sh',out/'run.sh')
 previous=json.loads(Path('doc/php83/evidence/serialization-contracts/stage-identities.json').read_text())
 snapshot74=json.loads(Path('doc/php83/evidence/exp12-runtime/runtime-before.json').read_text())['identity']
 runtime74={p:d['sha256'] for p,d in snapshot74['files'].items()}
 for row in snapshot74['linked_libraries'].values():runtime74.update(row)
 reference=Path('doc/php83/evidence/serialization-contracts/primary.json')
 if hashlib.sha256(reference.read_bytes()).hexdigest()!='ed33ad6ffb28c85c5c2665a237a685550f900663a08f615b90b540d7a7d22951':raise ValueError('Reference wire report drift')
 wires={}
 for row in json.loads(reference.read_text())['records']:
  if row['operation']=='roundtrip':wires[row['variant']+'/'+row['kind']]=json.loads(row['stdout'])['result']['wire']
 (out/'reference-wires.json').write_text(json.dumps(wires,sort_keys=True,indent=2)+'\n')
 shutil.copyfile(out/'reference-wires.json',Path('doc/php83/evidence/serialization-contracts/r2-reference-wires.json'))
 files={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.rglob('*')) if f.is_file()}
 manifest={'phase':'serialization-native83-wire-cache-r2','application_selected':False,'source_archives':r1.PINS,'files':files,'runtime_files':{'native83':previous['runtime_files'],'baseline74':runtime74},'changes':changes}
 (out/'identities.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
 evidence=Path('doc/php83/evidence/serialization-contracts');shutil.copyfile(out/'identities.json',evidence/'r2-stage-identities.json')
 (evidence/'r2-stage-pin.json').write_text(json.dumps({'manifest_sha256':hashlib.sha256((out/'identities.json').read_bytes()).hexdigest(),'local_stage':str(out),'remote_stage':'/home/vagrant/php-serialization-wire-cache-r2'},indent=2)+'\n')
 (held/'manifest.json').write_text(json.dumps({'status':'HELD_R2_UNTESTED','selected':False,'changes':changes,'limitations':['O incompatible with unchanged C-only readers','external subclasses returning null not accepted','mixed-version cache rollout unresolved']},indent=2)+'\n')

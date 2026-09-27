"""Create reviewed four-source overlay stage locally; never SSH or install."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4]
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
policy=load('policy_prepare',HERE.parent/'trace-policy-v1/prepare.py');guest=load('overlay_guest',HERE/'guest.py');audit=load('audit_prepare',HERE.parent/'application-audit-v1/run.py')
def sha(b):return hashlib.sha256(b).hexdigest()
def prepare(out):
 if out.exists():raise ValueError('Fresh local output')
 paths=list(dict.fromkeys(audit.SOURCES+['infra/log/UniqueId.php','alpha/apps/kaltura/lib/request/LogIp.php','infra/log/KalturaLogFilterType.php']))
 source=policy.old.archive('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip',policy.old.UPSTREAM,paths)
 blobs={};before={};after={}
 for name in guest.TARGETS:
  candidate=policy.transform(name,source[name]);policy.old.strict_replay(name,source[name],policy.old.patch_bytes(name,source[name],candidate),candidate)
  blobs['candidate/'+name]=candidate;before[name]=sha(source[name]);after[name]=sha(candidate)
 logger=(HERE.parent/'application-audit-v1/logger.php').read_bytes()
 snapshot=b'''function privateConfigSnapshot($fs,$host) {
 $snapshot=array();foreach(array('logger','kLocalMemCacheConf','kRemoteMemCacheConf') as $name)
  foreach($fs->getFileNames($name,$host) as $p)if(is_file($p))$snapshot[$p]=hash_file('sha256',$p);
 ksort($snapshot);return $snapshot;
}
'''
 logger=policy.old.replace_once(logger,b'$extras=array_keys',snapshot+b'''$allowedExtras=array('timestamp'=>'LogTime','uniqueId'=>'UniqueId','sessionIndex'=>'SessionIndex','logMethod'=>'LogMethod','logIp'=>'LogIp','logDuration'=>'LogDuration');
$extrasClassesReviewed=isset($config['eventItems']) && $config['eventItems']===$allowedExtras;
$extras=array_keys''')
 logger=policy.old.replace_once(logger,b"'writer_count'=>",b"'private_configuration_snapshot'=>privateConfigSnapshot($fs,$host),'extras_classes_reviewed'=>$extrasClassesReviewed,'writer_count'=>")
 cache=(HERE.parent/'application-audit-v1/cache.php').read_bytes()
 cache=policy.old.replace_once(cache,b"'cache_writes'=>0",b"'private_configuration_snapshot'=>$configBefore,'cache_writes'=>0")
 blobs.update({'logger.php':logger,'cache.php':cache,'guest.py':(HERE/'guest.py').read_bytes()})
 manifest={'status':'LAB_OVERLAY_PREPARED_NOT_APPLIED','before':before,'after':after,'support_sources':{n:sha(source[n]) for n in paths if n not in guest.TARGETS},
  'modules':dict(audit.RUNTIME,**{'/usr/lib/php/20190902/memcache.so':'cd5f48204d0752697476fd3488b4a39ac7fe3a75f6ae8ba52e354a1bd38c7616'}),
  'files':{n:sha(b) for n,b in blobs.items()},'original_zip':policy.old.UPSTREAM,'trace_policy_source_sha256':sha((HERE.parent/'trace-policy-v1/writer-methods.php.inc').read_bytes())}
 out.mkdir(parents=True)
 for name,b in blobs.items():
  p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();print(json.dumps(prepare(a.output),indent=2))

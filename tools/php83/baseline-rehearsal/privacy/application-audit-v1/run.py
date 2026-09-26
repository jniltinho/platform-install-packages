"""Read-only lab74 audit. No source/config/private-file staging or writes on guest."""
import hashlib,io,json,subprocess,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4]
OUT=REPO/'doc/php83/evidence/baseline-rehearsal/privacy/application-audit-v1'
PIN='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
SOURCES=['infra/log/KalturaLog.php','infra/log/KalturaSerializableStream.php','api_v3/lib/KalturaFrontController.php','api_v3/lib/KalturaDispatcher.php',
 'infra/log/KalturaLogFactory.php','alpha/apps/kaltura/lib/cache/kLoggerCache.php','api_v3/bootstrap.php','alpha/config/kConfCacheManager.php',
 'infra/kEnvironment.php','alpha/config/cache/kFileSystemConf.php','alpha/config/cache/kBaseConfCache.php','alpha/config/cache/kMapCacheInterface.php',
 'vendor/ZendFramework/library/Zend/Config.php','vendor/ZendFramework/library/Zend/Config/Ini.php','vendor/ZendFramework/library/Zend/Config/Exception.php','vendor/ZendFramework/library/Zend/Exception.php']
RUNTIME={'/usr/bin/php7.4':'5ed671ea6fe1cfb9f6e7dde2b259ec5821d7e0eae95c31d103d5468f2e617c59','/usr/lib/php/20190902/json.so':'80efe3d6f144e717b9fcef7750f81736cbd55c1e91041d24be58e70c18199343'}
def payload():
 raw=Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip').read_bytes()
 if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('Original archive changed')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Duplicate archive')
  pins={p:hashlib.sha256(z.read('server-Rigel-18.20.0/'+p)).hexdigest() for p in SOURCES}
 return {'sources':pins,'runtime':RUNTIME,'logger_code':(HERE/'logger.php').read_text()}
def main():
 if (OUT/'primary.json').exists() or (OUT/'primary.exit').exists():raise ValueError('Never overwrite')
 data=payload();code=('PAYLOAD='+repr(data)+'\n').encode()+(HERE/'guest.py').read_bytes()
 p=subprocess.run(['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74','python3 -'],input=code,capture_output=True,timeout=60)
 (OUT/'primary.exit').write_text(str(p.returncode)+'\n');(OUT/'primary-stderr-sha256.txt').write_text(hashlib.sha256(p.stderr).hexdigest()+'\n')
 if p.returncode:raise ValueError('Read-only audit rejected; no raw error exported')
 report=json.loads(p.stdout)
 (OUT/'primary.json').write_text(json.dumps({'guest_sha256':hashlib.sha256(code).hexdigest(),'source_archive_sha256':PIN,'result':report},indent=2)+'\n')
 print(report['status'])
if __name__=='__main__':main()

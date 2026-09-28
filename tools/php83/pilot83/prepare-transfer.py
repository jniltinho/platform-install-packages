"""Create non-secret staged package/proof inputs locally. No SSH/install/auth."""
import hashlib,json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];EV=ROOT/'doc/php83/evidence/pilot83'
def sha(b):return hashlib.sha256(b).hexdigest()
def prepare(out):
 if out.exists():raise ValueError('Fresh transfer')
 report=json.loads((EV/'verifier-actual-r2.json').read_text());repeat=json.loads((EV/'claude-private-debs-r2.json').read_text())
 if report!=repeat or report['status']!='PRIVATE_DEB_BYTES_VERIFIED_NOT_INSTALLED':raise ValueError('Independent verification')
 controls=json.loads((EV/'control-preparation-r1.json').read_text());versions={r['package']:r['after_version'] for r in controls['packages']}
 runtime=json.loads((EV/'runtime-before-apt-r1.json').read_text())['identity'];files=dict(runtime['files'])
 for libs in runtime['linked_libraries'].values():
  for name,pin in libs.items():
   if name in files and files[name]!=pin:raise ValueError('Conflicting runtime pin')
   files[name]=pin
 resolved=json.loads((EV/'runtime-canonical-paths-r1.json').read_text());canonical={}
 if {r['path']:r['sha256'] for r in resolved}!=files:raise ValueError('Runtime resolution source join')
 for r in resolved:
  n=r['resolved_path']
  if not n.startswith(('/usr/bin/','/usr/lib/')) or '..' in pathlib.PurePosixPath(n).parts:raise ValueError('Runtime canonical path')
  if n in canonical and canonical[n]!=r['sha256']:raise ValueError('Canonical collision')
  canonical[n]=r['sha256']
 files=canonical
 origin=ROOT/'doc/php83/evidence/pilot83-elastic-origin/verified-artifacts.json';origin_body=json.loads(origin.read_text())
 if not origin_body['release_signature_verified'] or not origin_body['deb_download_verified']:raise ValueError('Elastic origin')
 snapshot={'vm_uuid':'33f4f25f-1cf2-4cc5-90ff-d519c29b2aee','snapshot_uuid':'5fbc9e28-ae82-4410-aa24-978eb408f019','name':'php83-pre-private-pilot-20260928','create_exit':int((EV/'snapshot-create-r1.exit').read_text()),'after_inventory_sha256':sha((EV/'snapshot-after-r1.txt').read_bytes())}
 if snapshot['create_exit']!=0:raise ValueError('Recovery point')
 guest='/var/lib/kaltura-php83-pilot';writes={};packages=[]
 for r in report['packages']:
  matches=list((ROOT.parent/'platform-install-packages-php83-artifacts/pilot83-private-r2/packages').glob(r['package']+'_'+versions[r['package']]+'_*.deb'))
  if len(matches)!=1:raise ValueError('Package input')
  f=matches[0];b=f.read_bytes()
  if sha(b)!=r['sha256']:raise ValueError('Package drift')
  rel='packages/'+f.name;writes[rel]=b;packages.append({'package':r['package'],'version':versions[r['package']],'path':guest+'/'+rel,'sha256':r['sha256']})
 ext=pathlib.Path('/tmp/php83-elastic-origin/elasticsearch-7.17.29-amd64.deb');plugin=pathlib.Path('/tmp/php83-elastic-origin/analysis-icu-7.17.29.zip')
 for file,pin in [(ext,origin_body['package']['SHA256']),(plugin,origin_body['plugin']['sha256'])]:
  b=file.read_bytes()
  if sha(b)!=pin:raise ValueError('External artifact drift')
  writes['packages-external/'+file.name]=b
 writes['proofs/private-deb-verification.json']=(EV/'verifier-actual-r2.json').read_bytes();writes['proofs/dependency-origins.json']=origin.read_bytes();writes['proofs/recovery-point.json']=(json.dumps(snapshot,indent=2)+'\n').encode()
 writes['tools/install-lab.py']=(ROOT/'tools/php83/pilot83/install-lab.py').read_bytes()
 c={'status':'REVIEWED_INPUTS_READY','schema':1,'target':{'hostname':'kaltura-php83-lab','ip':'192.168.56.83'},'packages':packages,'external_debs':[{'package':'elasticsearch','version':'7.17.29','architecture':'amd64','path':guest+'/packages-external/'+ext.name,'sha256':origin_body['package']['SHA256']}],'runtime_files':[{'path':n,'sha256':pin} for n,pin in sorted(files.items())],'php_package_version':'8.3.6-0ubuntu0.24.04.11'}
 for name,filename in [('private_deb_verification','private-deb-verification.json'),('dependency_origins','dependency-origins.json'),('recovery_point','recovery-point.json')]:c[name]={'path':guest+'/proofs/'+filename,'sha256':sha(writes['proofs/'+filename])}
 writes['preflight-contract.json']=(json.dumps(c,indent=2)+'\n').encode()
 out.mkdir()
 for rel,data in writes.items():
  p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 manifest={'status':'NONSECRET_TRANSFER_PREPARED_NOT_INSTALLED','files':{n:sha(b) for n,b in writes.items()},'contract_sha256':sha(writes['preflight-contract.json']),'runtime_objects':len(files),'private_credentials_generated':False}
 (out/'transfer-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('output',type=pathlib.Path);x=a.parse_args();print(json.dumps(prepare(x.output),indent=2))

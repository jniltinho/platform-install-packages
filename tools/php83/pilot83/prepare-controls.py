"""Read exact published controls and emit private derivatives; no DEB build/VM."""
import argparse,importlib.util,io,json,pathlib,subprocess,tarfile,tempfile
HERE=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('payload',HERE/'compose-payload.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
s=importlib.util.spec_from_file_location('controls',HERE/'control-policy.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def prepare(out):
 if out.exists():raise ValueError('FRESH_OUTPUT')
 inputs=json.loads(p.pinned(p.ROOT/'doc/php83/evidence/pilot83/published-control-inputs.json',p.INPUT_PIN));writes={};rows=[]
 with tarfile.open(fileobj=io.BytesIO(p.pinned(p.BUNDLE,p.BUNDLE_PIN)),mode='r:gz') as bundle:
  for pkg in inputs['packages']:
   raw=bundle.extractfile(pkg['member']).read()
   if p.sha(raw)!=pkg['sha256']:raise ValueError('PACKAGE_HASH')
   with tempfile.TemporaryDirectory(prefix='pilot-controls-') as temp:
    path=pathlib.Path(temp)/'input.deb';path.write_bytes(raw)
    result=subprocess.run(['dpkg-deb','--ctrl-tarfile',str(path)],capture_output=True,timeout=30)
    if result.returncode:raise ValueError('DEB_READ')
    with tarfile.open(fileobj=io.BytesIO(result.stdout),mode='r:*') as archive:
     members=[x for x in archive.getmembers() if x.name.removeprefix('./')=='control']
     if len(members)!=1 or not members[0].isfile():raise ValueError('CONTROL_MEMBER')
     before=archive.extractfile(members[0]).read()
   name=pkg['control']['Package'];after,metadata=c.transform(before,name)
   writes[name+'/control']=after;writes[name+'/control.diff']=p.patch_bytes('DEBIAN/control',before,after)
   rows.append(dict(metadata,before_sha256=p.sha(before),after_sha256=p.sha(after),diff_sha256=p.sha(writes[name+'/control.diff'])))
 out.mkdir(parents=True)
 for n,b in writes.items():
  f=out/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 report={'status':'PRIVATE_CONTROLS_PREPARED_NOT_BUILT','bundle_sha256':p.BUNDLE_PIN,'packages':rows,'apt_resolution':'NOT_EXECUTED','native_provider_proof':'PENDING_INSTALLATION','installed':False}
 (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('output',type=pathlib.Path);args=a.parse_args();print(json.dumps(prepare(args.output),indent=2))

"""Build public embedded payload locally from exact reviewed sources; no runtime actions."""
import argparse,base64,hashlib,importlib.util,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];TOOLS=ROOT/'tools/php83'
PINS={
'pilot83/nginx-first-start.py':'f4cd76e8da7b8f3b388217424310ec26d0f52f54f0be9394ea17a533de59a9d6',
'nginx-log-privacy-config/render_closure.py':'edcd1d84cffe4d2c3edc6810522546e8be5930151a5ae01c04264c341a12d059',
'nginx-log-privacy-config/source-pins.json':'56c92ec9e0b2556acef83437a3bb0e1c91d221b880f12bd3d7de75382b48253c',
'nginx-log-privacy-config/transform.py':'af2e7e54c9196df2d65e67fb22c428c485b97e00d45935517a5c6a83f72f44ce',
'nginx-service-integration/generate.py':'188a61e275ff060c634cbf080aae231cbcfbc28d451d07ab82725f45a0ce6603',
'nginx-service-integration/service.py':'1122d48c325e1eda5296f4580d7a3b0da1801db86307ca24d6ccfe816a3a5f51',
'nginx-log-privacy-supervisor/lab_adapter.py':'090c5e8faaf9a0fc468ad31994b2077cc8b50858b3577a0d1c7e327433be1af5',
'nginx-log-privacy/sanitizer.py':'b44f3cdc8c38c6c00a1ef099c0a4742650b3b209e70814924115c1c5f146fffb'}
def sha(b):return hashlib.sha256(b).hexdigest()
def inject(base,pin,bundle):
 if not re.fullmatch('[a-f0-9]{64}',pin) or sha(base)!=pin:raise ValueError('BASE_PIN')
 if base.count(b'BUNDLE = None\n')!=1:raise ValueError('BUNDLE_ANCHOR')
 final=base.replace(b'BUNDLE = None\n',b'BUNDLE = '+repr(bundle).encode('ascii')+b'\n');compile(final,'assembled-helper','exec');return final
def assemble(base,pin):
 raw={k:(TOOLS/k).read_bytes() for k in PINS}
 if any(sha(raw[k])!=v for k,v in PINS.items()):raise ValueError('SOURCE_PIN')
 def module(name,path):
  spec=importlib.util.spec_from_file_location(name,TOOLS/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 previous=sys.modules.get('transform')
 try:
  sys.modules['transform']=module('transform','nginx-log-privacy-config/transform.py')
  renderer=module('render_closure','nginx-log-privacy-config/render_closure.py');gen=module('generate','nginx-service-integration/generate.py')
  source_root=ROOT/'doc/php83/evidence/nginx-r3-privacy/sources/opt/kaltura/nginx/conf'
  pins=json.loads(raw['nginx-log-privacy-config/source-pins.json']);source={k:(source_root/k).read_bytes() for k in pins}
  rendered=renderer.render(source);art=gen.artifacts()
 finally:
  if previous is None:sys.modules.pop('transform',None)
  else:sys.modules['transform']=previous
 enc=lambda b:base64.b64encode(b).decode('ascii')
 bundle={'old_helper':enc(raw['pilot83/nginx-first-start.py']),'rendered':{k:enc(v) for k,v in sorted(rendered.items())},'init':enc(art['kaltura-nginx.init'].encode()),'unit':enc(art['kaltura-nginx.service'].encode()),'modules':{name:enc(raw[path]) for name,path in [('service.py','nginx-service-integration/service.py'),('lab_adapter.py','nginx-log-privacy-supervisor/lab_adapter.py'),('sanitizer.py','nginx-log-privacy/sanitizer.py')]}}
 return inject(base,pin,bundle)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--base-sha256',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 out=assemble(pathlib.Path(a.base).read_bytes(),a.base_sha256)
 with pathlib.Path(a.output).open('xb') as f:f.write(out)
 print(json.dumps({'status':'PUBLIC_BUNDLE_ASSEMBLED_NOT_EXECUTED','sha256':sha(out),'base_sha256':a.base_sha256,'input_pins':PINS}))

"""Control-only lab nginx derivative. Explicit helper pin required; no installs."""
import argparse,hashlib,json,pathlib,types
import prepare
BASE=pathlib.Path(__file__).resolve().parent.parent/'pilot83'
SERVICES_PIN='280ccf7bc1fb5d6b08f5fa87c80028d6276d7ddfe57ce8473fd466d3527c6959'
def services():
 path=BASE/'build-services-r3.py';raw=path.read_bytes()
 if prepare.sha(raw)!=SERVICES_PIN:raise ValueError('BUILDER_HELPER_PIN')
 m=types.ModuleType('pinned_services');m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);return m
def derive(raw,helper,helper_pin):
 if prepare.sha(raw)!=prepare.SOURCE_PIN:raise ValueError('DEB_PIN')
 h=services();ar=h.archive_module();rows=ar.ar_read(raw)
 if [x[0] for x in rows]!=['debian-binary','control.tar.xz','data.tar.xz']:raise ValueError('ARCHIVE_LAYOUT')
 before={m.name:data for m,data in h.members(rows[1][2])}
 hook,control=prepare.transform(before['./postinst'],before['./control'],helper,helper_pin)
 changed=h.rewrite(rows[1][2],{'./control':control,'./postinst':hook});out=bytearray(b'!<arch>\n')
 for name,header,body in rows:
  if name=='control.tar.xz':body=changed;header=header[:48]+str(len(body)).encode().ljust(10,b' ')+header[58:]
  out.extend(header+body+(b'\n' if len(body)%2 else b''))
 final=bytes(out);after=ar.ar_read(final)
 if after[0]!=rows[0] or after[2]!=rows[2]:raise ValueError('PAYLOAD_DRIFT')
 return final,{'postinst_sha256':prepare.sha(hook),'control_sha256':prepare.sha(control)}
def build(source,helper_path,helper_pin,output):
 final,identities=derive(pathlib.Path(source).read_bytes(),pathlib.Path(helper_path).read_bytes(),helper_pin)
 with pathlib.Path(output).open('xb') as stream:stream.write(final)
 return {'status':'EXPERIMENTAL_LAB3_BUILT_NOT_INSTALLED','source_sha256':prepare.SOURCE_PIN,'helper_sha256':helper_pin,'sha256':prepare.sha(final),'bytes':len(final),'data_archive_byte_identical':True,'installed':False,**identities}
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ('source','helper','helper-sha256','output'):p.add_argument('--'+k,required=True)
 a=p.parse_args();print(json.dumps(build(a.source,a.helper,a.helper_sha256,a.output)))

"""Exact experimental lab2->lab3 post-hook transform, never executes hooks."""
import argparse,hashlib,json,pathlib,re
SOURCE_PIN='993b5a45e6c3db5488cd98c34fc8ee6634dfbafae98ac3129b8dc17276271519'
HOOK_PIN='a64f2670ea8f97b229891cd0a857201d289a7335a2a9d77ec681dd354d5ed78b'
CONTROL_PIN='3897636081d33cf89199169295895b9109a25e338def238f354344a75dff0c99'
TAG=b'PILOT83_NGINX_DEPLOY_LAB3'
ANCHOR=b'pilot83_nginx_guard post || exit 11\n'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def transform(hook,control,helper,helper_pin):
 if sha(hook)!=HOOK_PIN or sha(control)!=CONTROL_PIN:raise ValueError('SOURCE_PIN')
 if not isinstance(helper_pin,str) or not re.fullmatch('[a-f0-9]{64}',helper_pin) or sha(helper)!=helper_pin:raise ValueError('HELPER_PIN')
 if not helper.endswith(b'\n') or b'\x00' in helper or TAG in helper:raise ValueError('HELPER_FRAMING')
 compile(helper,'reviewed-deploy-helper','exec') # syntax only, never execution
 if hook.count(ANCHOR)!=1 or not hook.endswith(ANCHOR+b'invoke-rc.d kaltura-nginx restart\n'):raise ValueError('POST_ANCHOR')
 old=b'Version: 1.23.0-1+php83lab2\n';new=b'Version: 1.23.0-1+php83lab3\n'
 if control.count(old)!=1:raise ValueError('VERSION')
 replacement=b"/usr/bin/python3 -I - <<'"+TAG+b"' || exit 11\n"+helper+TAG+b'\n'
 return hook.replace(ANCHOR,replacement),control.replace(old,new)
def main():
 p=argparse.ArgumentParser()
 for k in ('hook','control','helper','helper-sha256','output'):p.add_argument('--'+k,required=True)
 a=p.parse_args();hook,control=transform(pathlib.Path(a.hook).read_bytes(),pathlib.Path(a.control).read_bytes(),pathlib.Path(a.helper).read_bytes(),a.helper_sha256)
 out=pathlib.Path(a.output);out.mkdir();(out/'postinst').write_bytes(hook);(out/'control').write_bytes(control)
 print(json.dumps({'status':'PREPARED_ONLY','postinst_sha256':sha(hook),'control_sha256':sha(control),'helper_sha256':a.helper_sha256}))
if __name__=='__main__':main()

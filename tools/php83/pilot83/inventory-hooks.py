"""Read-only bounded inventory of pinned published DEB maintainer hooks."""
import hashlib, io, json, pathlib, subprocess, tarfile, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
BUNDLE=pathlib.Path('/tmp/kaltura-php83-audit/release/kaltura-server-noble-repo.tar.gz')
EXPECTED='91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b'
def sha(b): return hashlib.sha256(b).hexdigest()
assert sha(BUNDLE.read_bytes())==EXPECTED
control=json.loads((ROOT/'doc/php83/evidence/pilot83/published-control-inputs.json').read_text())
rows=[]
with tarfile.open(BUNDLE,'r:gz') as bundle:
 for pkg in control['packages']:
  member=bundle.getmember(pkg['member']); assert member.isfile() and member.size==pkg['bytes']
  data=bundle.extractfile(member).read(); assert sha(data)==pkg['sha256']
  with tempfile.TemporaryDirectory(prefix='pilot83-hook-read-') as temp:
   deb=pathlib.Path(temp)/'input.deb'; deb.write_bytes(data)
   result=subprocess.run(['dpkg-deb','--ctrl-tarfile',str(deb)],capture_output=True,timeout=30)
   assert result.returncode==0
   with tarfile.open(fileobj=io.BytesIO(result.stdout),mode='r:*') as archive:
    for hook in archive.getmembers():
     name=hook.name.removeprefix('./')
     if name not in ('preinst','postinst','prerm','postrm','config'): continue
     assert hook.isfile() and hook.size<2_000_000
     raw=archive.extractfile(hook).read(); lines=raw.decode().splitlines()
     source=ROOT/'deb'/pkg['control']['Package']/'debian'/name
     rows.append({'package':pkg['control']['Package'],'hook':name,'sha256':sha(raw),'bytes':len(raw),
      'checkout_path':str(source.relative_to(ROOT)),'checkout_exists':source.is_file(),
      'checkout_exact_match':source.is_file() and source.read_bytes()==raw,
      'review_lines':{
       'mysql_password_argv':[i for i,s in enumerate(lines,1) if 'mysql' in s and ('-p$' in s or '-p"$' in s)],
       'secret_identifier_in_command':[i for i,s in enumerate(lines,1) if any(x in s for x in ('SECRET','PASSWD','DB1_PASS')) and any(x in s for x in ('php ','sed ','mysql '))],
       'php74_reference':[i for i,s in enumerate(lines,1) if 'php7.4' in s],
       'delete_log_candidate':[i for i,s in enumerate(lines,1) if 'rm ' in s and ('log' in s or 'LOG' in s)]}})
print(json.dumps({'status':'READONLY_STATIC_CANDIDATES_NOT_EXHAUSTIVE','bundle_sha256':EXPECTED,'hooks':rows,'executed_hooks':False,'derived_packages_built':False},indent=2))

"""Private exact SOAP package acquisition; no package installation or PHP load."""
import hashlib,json,os,re,subprocess,sys
from pathlib import Path
mode=sys.argv[1]
S={'74':('kaltura-php74-baseline','1:7.4.33-30+ubuntu24.04.1+deb.sury.org+1','f25c5a8342b852ed5f97154e270f22805f4dc221132b15084c6936f59016511b','ppa.launchpadcontent.net_ondrej_php_ubuntu_dists_noble','main','https://ppa.launchpadcontent.net/ondrej/php/ubuntu/','20190902'), '83':('kaltura-php83-lab','8.3.6-0ubuntu0.24.04.11','eeb541e17950d330e01f5d0c47620ad45de92b64517320980691646777e4ad29','us.archive.ubuntu.com_ubuntu_dists_noble-updates','universe','http://us.archive.ubuntu.com/ubuntu/','20230831')}
host,version,want,prefix,component,origin,abi=S[mode]
assert os.getuid()==1000 and os.uname().nodename==host
root=Path('/home/vagrant/php-xml-soap-provider-r2' if mode=='74' else '/home/vagrant/php-xml-soap-provider-r1');root.mkdir();os.chdir(root)
def run(cmd):
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
 steps.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 if r.returncode:raise RuntimeError('Provider command failed: '+str(cmd))
 return r.stdout
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
steps=[]
try:
 lists=Path('/var/lib/apt/lists')
 if mode=='74':
  sources=list(Path('/etc/apt/sources.list.d').glob('*ondrej*'));assert len(sources)==1
  source=sources[0].read_bytes();assert b'trusted=yes' not in source and b'Signed-By:' in source
  (root/'ondrej.sources').write_bytes(source)
  for d in ['lists/partial','cache/archives/partial','log']:(root/d).mkdir(parents=True)
  config='\n'.join([
   'Dir::Etc::main "-";', 'Dir::Etc::parts "-";',
   'Dir::Etc::sourcelist "'+str(root/'ondrej.sources')+'";',
   'Dir::Etc::sourceparts "-";',
   'Dir::State::lists "'+str(root/'lists')+'";',
   'Dir::Cache "'+str(root/'cache')+'";',
   'Dir::Log "'+str(root/'log')+'";',
   'Acquire::Languages "none";',
   'Acquire::AllowInsecureRepositories "false";',
   'Acquire::AllowDowngradeToInsecureRepositories "false";',
   'APT::Get::AllowUnauthenticated "false";',
   'APT::Get::List-Cleanup "false";',
  ])+'\n'
  (root/'apt.conf').write_text(config);os.environ['APT_CONFIG']=str(root/'apt.conf')
  run(['apt-config','dump'])
  run(['apt-get','update','-o','APT::Update::Error-Mode=any'])
  lists=root/'lists';keyring=str(root/'ondrej.sources')
 else:keyring='/usr/share/keyrings/ubuntu-archive-keyring.gpg'
 release=lists/(prefix+'_InRelease')
 if mode!='74':run(['gpgv','--status-fd','1','--keyring',keyring,str(release)])
 contents=release.read_text();suite=re.search(r'^Suite: (.+)$',contents,re.M).group(1);assert suite==('noble' if mode=='74' else 'noble-updates')
 name=f'{component}/binary-amd64/Packages'; match=re.search(r'^SHA256:\n(.*?)(?=^[^ ])',contents,re.M|re.S);assert match
 hashes={parts[2]:(parts[0],int(parts[1])) for line in match.group(1).splitlines() if len(parts:=line.split())==3};assert name in hashes
 cached=list(lists.glob(prefix+'_'+component+'_binary-amd64_Packages*'));assert len(cached)==1
 raw=subprocess.check_output(['/usr/lib/apt/apt-helper','cat-file',str(cached[0])]);assert (hashlib.sha256(raw).hexdigest(),len(raw))==hashes[name]
 package='php'+('7.4' if mode=='74' else '8.3')+'-soap'
 stanzas=[]
 for stanza in raw.decode().split('\n\n'):
  fields=dict(line.split(': ',1) for line in stanza.splitlines() if ': ' in line and not line.startswith(' '))
  if fields.get('Package')==package and fields.get('Version')==version:stanzas.append(fields)
 assert len(stanzas)==1;fields=stanzas[0];assert fields['SHA256']==want and fields['Architecture']=='amd64'
 filename=fields['Filename'];assert filename.startswith('pool/') and '..' not in filename
 run(['/usr/lib/apt/apt-helper','download-file',origin+filename,str(root/'soap.deb'),'SHA256:'+want]);assert digest('soap.deb')==want
 control=run(['dpkg-deb','-f','soap.deb','Package','Version','Architecture','Depends']);assert package in control and version in control
 run(['dpkg-deb','-x','soap.deb','extracted']);module=root/'extracted/usr/lib/php'/abi/'soap.so';assert module.is_file() and not module.is_symlink()
 elf=run(['readelf','-h','-d',str(module)]);assert 'Advanced Micro Devices X86-64' in elf
 linked=run(['ldd',str(module)]);assert 'not found' not in linked
 paths=sorted(set(re.findall(r'/[^\s()]+',linked)));libs={p:digest(p) for p in paths}
 data={'status':'EXTRACTED_NOT_LOADED','mode':mode,'suite':suite,'origin':origin,'version':version,'package_sha256':want,'signed_release_sha256':digest(release),'keyring_sha256':digest(keyring),'packages_sha256':hashes[name][0],'module':str(module),'module_sha256':digest(module),'abi_directory':abi,'linked_libraries':libs,'steps':steps,'no_install':True,'no_php_load':True,'authentication':'isolated APT existing Signed-By' if mode=='74' else 'gpgv exit0 existing Ubuntu keyring'}
 print(json.dumps(data,indent=2))
except Exception as exc:
 print(json.dumps({'status':'FAILED_RETAINED_PROVIDER','error':str(exc),'steps':steps},indent=2));sys.exit(1)

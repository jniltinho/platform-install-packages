#!/usr/bin/env python3
"""Read-only php83 lab interpreter, explicit modules and linked-library snapshot."""
import hashlib,json,pathlib,re,socket,subprocess
P=pathlib.Path
if socket.gethostname()!='kaltura-php83-lab':raise SystemExit(64)
php=P('/usr/bin/php8.3');names=['tokenizer','mbstring','xmlwriter','dom','simplexml']
args=[str(php),'-n']
for name in names:args+=['-d','extension='+name]
code="echo json_encode(['version'=>PHP_VERSION,'sapi'=>PHP_SAPI,'ini'=>php_ini_loaded_file(),'scanned_ini'=>php_ini_scanned_files(),'extension_dir'=>ini_get('extension_dir'),'extensions'=>get_loaded_extensions(),'module_versions'=>array_map('phpversion',get_loaded_extensions())]);"
configuration=json.loads(subprocess.check_output(args+['-r',code],text=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},timeout=15))
files=[php]+[P(configuration['extension_dir'])/(name+'.so') for name in names]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
libraries={};objects={}
for file in files:
 report=subprocess.check_output(['ldd',str(file)],text=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},timeout=15)
 if 'not found' in report:raise RuntimeError('Missing dynamic library')
 paths=set(re.findall(r'=> (/\S+)',report)+re.findall(r'^\s*(/\S+)',report,re.M))
 objects[str(file)]={'resolved_path':str(file.resolve()),'sha256':sha(file),'ldd':report}
 for name in sorted(paths):
  library=P(name);libraries[name]={'resolved_path':str(library.resolve()),'sha256':sha(library)}
print(json.dumps({'schema':1,'scope':'Read-only snapshot; no assertion that this predates an earlier completed run','configuration':configuration,'objects':objects,'linked_libraries':libraries},indent=2,sort_keys=True))

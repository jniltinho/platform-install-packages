import hashlib,json,pathlib,subprocess,socket,os
assert socket.gethostname()=='kaltura-php83-lab'
root=pathlib.Path('/home/vagrant/pilot83-bridge-r1')
pins={'private-argv.php':'f08566c2dfc4b7547711cb9e1f2d0e80478c676ad71e45e69b3289580edd21aa','probe-private-argv-native.py':'304960ed8061d99476c92d934221dc1ecbc2b7f0ec9f8608c1cfa8a9d1d3dc72'}
def snapshot():
 return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*(root/n for n in pins),pathlib.Path('/usr/bin/php8.3'),pathlib.Path('/etc/php/8.3/cli/php.ini')]}
for name,pin in pins.items():
 p=root/name;assert not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==pin;os.chown(p,0,0);os.chmod(p,0o444)
os.chown(root,0,0);os.chmod(root,0o555)
before=snapshot();commands=[['/usr/bin/php8.3','-l',str(root/'private-argv.php')],['python3',str(root/'probe-private-argv-native.py'),'--bridge',str(root/'private-argv.php'),'--bridge-sha256',pins['private-argv.php']]]
rows=[]
for cmd in commands:
 p=subprocess.run(cmd,capture_output=True,timeout=150)
 rows.append({'exit':p.returncode,'stderr_bytes':len(p.stderr),'stdout':p.stdout.decode()})
 if p.returncode:break
report={'status':'SYNTHETIC_NATIVE_BRIDGE_ONLY','executor':'Codex','before':before,'after':snapshot(),'commands':rows,'app_hooks_executed':False,'installed':False}
print(json.dumps(report,indent=2));assert before==report['after'] and len(rows)==2 and all(r['exit']==0 and r['stderr_bytes']==0 for r in rows)

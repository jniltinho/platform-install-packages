#!/usr/bin/env python3
"""One bounded compiler process, preserving public stdout/stderr/exit evidence."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('executor',choices=['opencode-independent','codex-repeat']);a=p.parse_args();base=Path(__file__).resolve().parent;stem=base/a.executor
paths=[stem.with_suffix(s) for s in ['.json','.stderr','.exit']]
if any(p.exists() for p in paths):raise FileExistsError('Never overwrite compiler evidence')
freeze=json.loads((base/'prep-freeze.json').read_text())
for name,pin in freeze.items():
 if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=pin:raise RuntimeError('Frozen prep drift')
sys.path.insert(0,str(Path('tools/php83/exp14-syntax').resolve()));import scan
scan.load_contract() # Fail before SSH for a pending/invalid candidate pin.
command=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83','bash /home/vagrant/php-candidate-syntax-exp14/tools/run.sh']
try:
 r=subprocess.run(command,capture_output=True,timeout=600);code=r.returncode;out=r.stdout;err=r.stderr
except subprocess.TimeoutExpired as e:
 code=124;out=e.stdout or b'';err=e.stderr or b''
for path,data in zip(paths,[out,err,str(code).encode()+b'\n']):
 with path.open('xb') as f:f.write(data)
print(json.dumps({'executor':a.executor,'exit':code,'output':str(paths[0]),'sha256':hashlib.sha256(out).hexdigest()}))
raise SystemExit(code)

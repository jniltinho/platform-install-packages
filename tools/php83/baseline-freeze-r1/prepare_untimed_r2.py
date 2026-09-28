"""Versioned settle/capture derivative; historical guest and scanner sources unchanged."""
import argparse,ast,hashlib,re
from pathlib import Path
H=Path(__file__).parent;ROOT=H.resolve().parents[2]
raw=(H/'guest_untimed.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='3f95f1ced7b530e42b90e1872b34add4f1ddea0c6da174a79bda8a324955d56c'
s=raw.decode()
anchor="  rehearsal=load('baseline_rehearsal_v2',NEW_HERE/'rehearsal.py')"
s=s.replace(anchor,anchor+"\n  need(hashlib.sha256((NEW_HERE/'settle.py').read_bytes()).hexdigest()=="+repr(hashlib.sha256((H/'settle.py').read_bytes()).hexdigest())+",'SETTLE_PIN')\n  settle=load('baseline_settle_v1',NEW_HERE/'settle.py')")
s=s.replace('media_window=None;tracked_tokens=[]',"media_window=None;tracked_tokens=[];failure_stage='PREFLIGHT'")
s=s.replace("report['phase']='untimed-protocol-rehearsal'", "report['phase']='untimed-protocol-rehearsal';failure_stage='API_ROUND'")
a="  report['media_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)"
s=s.replace(a,"""  failure_stage='QUIET_SETTLE'
  try:report['quiet_window']=settle.wait_quiet(lambda:(files.snapshot(legacy.logs()),journal.snapshot()))
  except settle.Unsettled:raise Rejected('QUIET_WINDOW_NOT_ESTABLISHED') from None
  failure_stage='MEDIA_PRIVACY'
"""+a)
s=s.replace("  report['round_privacy']=audit_all", "  failure_stage='BATCH_PRIVACY'\n  report['round_privacy']=audit_all")
s=s.replace("  need(legacy.checksum(stored)==legacy.SOURCE_PIN", "  failure_stage='POSTCHECK'\n  need(legacy.checksum(stored)==legacy.SOURCE_PIN")
codes={n.args[1].value for n in ast.walk(ast.parse(s)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='need' and len(n.args)>1 and isinstance(n.args[1],ast.Constant) and isinstance(n.args[1].value,str)}
codes.add('QUIET_WINDOW_NOT_ESTABLISHED')
for rel in ('tools/php83/baseline-rehearsal/privacy/append-window-v1/scan.py','tools/php83/baseline-rehearsal/privacy/journal-window-v1/scan.py'):
 tree=ast.parse((ROOT/rel).read_text())
 for n in ast.walk(tree):
  if isinstance(n,ast.Constant) and type(n.value) is str and re.fullmatch('[A-Z_]+',n.value):codes.update(('FILES_'+n.value,'JOURNAL_'+n.value))
s=s.replace('class Rejected(RuntimeError):pass','FIXED_FAILURE_CODES='+repr(sorted(codes))+'\nclass Rejected(RuntimeError):pass')
s=s.replace("report['failure_code']='OBSERVATION_REJECTED'", "report['failure_stage']=failure_stage;report['failure_code']=str(error) if type(error) is Rejected and str(error) in FIXED_FAILURE_CODES else 'UNEXPECTED_OR_DEPENDENCY_FAILURE'")
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
with Path(a.output).open('x') as f:f.write(s)
print(hashlib.sha256(s.encode()).hexdigest())

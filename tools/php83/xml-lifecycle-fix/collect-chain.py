import hashlib,json,subprocess,sys
from pathlib import Path
stage=Path(sys.argv[1]);out=Path(sys.argv[2]);assert not out.exists()
mb=(stage/'identities.json').read_bytes();m=json.loads(mb);pin=hashlib.sha256(mb).hexdigest()
if m['phase']!='xml-lifecycle-held-A-chain-r1':raise ValueError('Wrong chain phase')
for p,h in m['files'].items():
 if hashlib.sha256((stage/p).read_bytes()).hexdigest()!=h:raise ValueError('Local drift')
rows=[];failed=False
for variant in ['baseline','candidate']:
 cmd=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83','bash /home/vagrant/php-xml-lifecycle-fix-chain-r1/run-native.sh behavior '+variant+' callback-throw '+pin]
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=75);row={'variant':variant,'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
 try:
  if r.returncode:raise ValueError('Native process failure')
  b=json.loads(r.stdout);row['body']=b
  expected={p[len(variant)+1:]:h for p,h in m['files'].items() if p.startswith(variant+'/')}
  if b['loaded']!=expected or b['probe_sha256']!=m['files']['behavior.php']:raise ValueError('Actual source identity')
  if b['runtime']['php_id']!=80306 or b['runtime']['error_reporting']!=32767:raise ValueError('Runtime identity')
  if b['variant']!=variant or b['case']!='callback-throw':raise ValueError('Case identity')
  if b['exception'] is None or b['exception']['chain_truncated'] is not False:raise ValueError('Full native chain unavailable')
  if len(b['resolver_exceptions'])!=1 or b['resolver_exceptions'][0]['exception']['chain_truncated'] is not False:raise ValueError('Thrown resolver exception unavailable')
 except (ValueError,KeyError,TypeError) as e:row['failure']=str(e);failed=True
 rows.append(row)
out.write_text(json.dumps({'status':'CHAIN_CAPTURED_NOT_PRODUCT_ACCEPTANCE' if not failed else 'FAIL_RETAINED_CHAIN','manifest_sha256':pin,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'records':rows,'product_changed':False,'acceptance':False},indent=2)+'\n')
print(json.dumps({'records':len(rows),'failed':failed}));sys.exit(1 if failed else 0)

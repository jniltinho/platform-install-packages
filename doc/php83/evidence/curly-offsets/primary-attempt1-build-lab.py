#!/usr/bin/env python3
"""Run pinned PHPCBF only on private copies, verify tokens and PHP8.3 compile controls."""
import base64,hashlib,json,os,pathlib,shutil,socket,subprocess,tempfile
P=pathlib.Path
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert socket.gethostname()=='kaltura-php83-lab' and os.getuid()==1000
analyzer=P('/audit/analyzer'); stage=P('/audit/stage')
def identity():
 return {str(p.relative_to(analyzer)):sha(p) for p in sorted(analyzer.rglob('*')) if p.is_file() and not p.is_symlink()}
before=identity();assert before['composer.lock']=='1349200f714f39615153d319d88046b1f34b91a782954b76a7fe538c9b8b5e33'
php=['/usr/bin/php8.3','-n','-d','extension=tokenizer','-d','extension=mbstring','-d','extension=xmlwriter','-d','extension=dom','-d','extension=simplexml']
common=['--standard=PHPCompatibility','--sniffs=PHPCompatibility.Syntax.RemovedCurlyBraceArrayAccess','--runtime-set','testVersion','7.4-8.3','--extensions=php,phtml,inc,php5']
paths=json.loads((stage/'selection.json').read_text());rows=[]
with tempfile.TemporaryDirectory(prefix='php83-curly-') as temporary:
 root=P(temporary); candidate=root/'candidate'; shutil.copytree(stage/'original',candidate)
 command=php+[str(analyzer/'vendor/bin/phpcs')]+common+['--report=json',str(candidate)]
 scan=subprocess.run(command,capture_output=True,text=True,timeout=240)
 if scan.returncode not in (1,2):raise RuntimeError('Expected original targeted findings: '+scan.stderr)
 original_report=json.loads(scan.stdout)
 fix_command=php+[str(analyzer/'vendor/bin/phpcbf')]+common+[str(candidate)]
 fixed=subprocess.run(fix_command,capture_output=True,text=True,timeout=240)
 if fixed.returncode!=1:raise RuntimeError('PHPCBF did not report corrected errors: '+fixed.stdout+fixed.stderr)
 clean=subprocess.run(command,capture_output=True,text=True,timeout=240)
 if clean.returncode!=0:raise RuntimeError('Remaining targeted findings: '+clean.stdout+clean.stderr)
 for path,want in sorted(paths.items()):
  original=stage/'original'/path; output=candidate/path
  if sha(original)!=want:raise RuntimeError('Original source drift')
  record=original_report['files'][str(output)]
  messages=root/'messages.json';messages.write_text(json.dumps(record['messages']))
  token=subprocess.run(php+[str(stage/'tools/verify-tokens.php'),str(original),str(output),str(messages)],capture_output=True,text=True,timeout=30)
  if token.returncode:raise RuntimeError('Token proof failed '+path+': '+token.stderr)
  original_lint=subprocess.run(['/usr/bin/php8.3','-n','-d','short_open_tag=1','-d','error_reporting=32767','-d','display_errors=stderr','-d','log_errors=0','-l',str(original)],capture_output=True,text=True,timeout=15)
  candidate_lint=subprocess.run(['/usr/bin/php8.3','-n','-d','short_open_tag=1','-d','error_reporting=32767','-d','display_errors=stderr','-d','log_errors=0','-l',str(output)],capture_output=True,text=True,timeout=15)
  if original_lint.returncode!=255 or candidate_lint.returncode!=0:raise RuntimeError('Compile control failed '+path+': '+candidate_lint.stderr)
  rows.append({'path':path,'proof':json.loads(token.stdout),'targeted_messages':record['messages'],
   'candidate_base64':base64.b64encode(output.read_bytes()).decode(),
   'original_compile':{'exit':original_lint.returncode,'stdout':original_lint.stdout.replace(str(stage/'original'),'/original'),'stderr':original_lint.stderr.replace(str(stage/'original'),'/original')},
   'candidate_compile':{'exit':candidate_lint.returncode,'stdout':candidate_lint.stdout.replace(str(candidate),'/candidate'),'stderr':candidate_lint.stderr.replace(str(candidate),'/candidate')}})
 after=identity()
 if before!=after:raise RuntimeError('Analyzer files changed')
 print(json.dumps({'schema':1,'analyzer_before':before,'analyzer_after':after,'analyzer_unchanged':True,
  'php_binary_sha256':sha(P('/usr/bin/php8.3')),'php_version':subprocess.check_output(['/usr/bin/php8.3','-v'],text=True).splitlines()[0],
  'phpcbf_version':subprocess.check_output(php+[str(analyzer/'vendor/bin/phpcbf'),'--version'],text=True).strip(),
  'sniff':'PHPCompatibility.Syntax.RemovedCurlyBraceArrayAccess','testVersion':'7.4-8.3',
  'scan_before_exit':scan.returncode,'fix_exit':fixed.returncode,'fix_stdout':fixed.stdout.replace(str(candidate),'/candidate'),'fix_stderr':fixed.stderr.replace(str(candidate),'/candidate'),
  'scan_after_exit':clean.returncode,'scan_after_totals':json.loads(clean.stdout)['totals'],'rows':rows,
  'application_acceptance':False,'held_only':True},indent=2))

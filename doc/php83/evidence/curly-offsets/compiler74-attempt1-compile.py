#!/usr/bin/env python3
"""Fresh 43-file PHP7.4 compiler/tokenizer control; never execute source bodies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
ORIGINAL_SHA='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
ROOT=Path('/audit/curly74')
PHP='/usr/bin/php7.4'
LINT_FLAGS=['-n','-d','short_open_tag=1','-d','error_reporting=32767','-d','display_errors=stderr','-d','log_errors=0','-l']
TOKEN_FLAGS=['-n','-d','extension=/usr/lib/php/20190902/json.so','-d','extension=/usr/lib/php/20190902/tokenizer.so','-d','error_reporting=32767','-d','display_errors=stderr','-d','log_errors=0']

def require(ok,message):
 if not ok:raise RuntimeError(message)

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify_files(root,expected):
 require(root.is_dir() and not root.is_symlink(),'Invalid stage root')
 for path in root.rglob('*'):require(not path.is_symlink() and (path.is_file() or path.is_dir()),'Nonregular stage object')
 actual={str(p.relative_to(root)):digest(p) for p in root.rglob('*') if p.is_file()}
 require(actual==expected,'Stage file identity drift')
 return actual

def safe_relative(path):
 p=Path(path);require(not p.is_absolute() and '..' not in p.parts and path==str(p),'Unsafe relative source path');return p

def prepare(target):
 require(not target.exists(),'Refusing existing stage')
 manifest=REPO/'patches/php83/held/curly-offsets/manifest.json'
 lab=REPO/'doc/php83/evidence/curly-offsets/primary-lab.json'
 m=json.loads(manifest.read_text());rows=json.loads(lab.read_text())['rows']
 print('primary row keys: '+','.join(rows[0]),file=__import__('sys').stderr)
 by_path={r['path']:r for r in rows};require(len(m['files'])==43 and len(by_path)==43,'Expected43sourcefiles')
 archive=Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip');require(digest(archive)==ORIGINAL_SHA,'Original ZIP drift')
 target.mkdir(); sources=[]
 with zipfile.ZipFile(archive) as z:
  for i,entry in enumerate(m['files']):
   path=entry['path'];safe_relative(path)
   before=z.read('server-Rigel-18.20.0/'+path);after=(Path('/tmp/php83-curly-offsets-candidate')/path).read_bytes()
   require(hashlib.sha256(before).hexdigest()==entry['before_sha256'] and hashlib.sha256(after).hexdigest()==entry['after_sha256'],'Patch source drift')
   for variant,data in [('original',before),('candidate',after)]:
    dest=target/variant/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
   message_path='messages/'+str(i)+'.json';dest=target/message_path;dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(by_path[path]['targeted_messages'])+'\n')
   sources.append({**entry,'messages':message_path})
 shutil.copyfile(HERE/'verify-tokens.php',target/'verify-tokens.php');shutil.copyfile(Path(__file__),target/'compile74.py')
 metadata={'schema':1,'sources':sources,'original_zip_sha256':ORIGINAL_SHA,'held_manifest_sha256':digest(manifest),'primary83_report_sha256':digest(lab),'files':{str(p.relative_to(target)):digest(p) for p in target.rglob('*') if p.is_file()}}
 (target/'identity.json').write_text(json.dumps(metadata,indent=2)+'\n')
 print(json.dumps({'stage':str(target),'identity_sha256':digest(target/'identity.json'),'files':len(metadata['files']),'source_files_each':len(sources)}))

def runtime():
 paths=[PHP,'/usr/lib/php/20190902/json.so','/usr/lib/php/20190902/tokenizer.so']
 modules=subprocess.check_output([PHP]+TOKEN_FLAGS+['-m'],text=True)
 version=subprocess.check_output([PHP,'-n','-v'],text=True)
 require(version.startswith('PHP 7.4.'),'Wrong runtime family')
 require('\njson\n' in modules and '\ntokenizer\n' in modules,'Missing verifier modules')
 libraries={}
 for path in paths:
  listing=subprocess.check_output(['/usr/bin/ldd',path],text=True);require('not found' not in listing,'Missing linked library')
  libraries[path]={p:digest(p) for p in sorted(set(re.findall(r'/[^\s()]+',listing)))}
 return {'version':version,'file_sha256':{p:digest(p) for p in paths},'linked_library_sha256':libraries,'token_modules':modules,'ini':subprocess.check_output([PHP,'-n','--ini'],text=True)}

def command_run(command):
 try:
  r=subprocess.run(command,capture_output=True,text=True,timeout=25)
  return {'command':command,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
 except subprocess.TimeoutExpired:
  return {'command':command,'exit':124,'stdout':'','stderr':'Timeout; incomplete evidence'}

def scan():
 require(os.geteuid()==1000 and bool(os.statvfs(ROOT).f_flag & os.ST_RDONLY),'Need unprivileged readonly stage')
 metadata=json.loads((ROOT/'identity.json').read_text());pinned={**metadata['files'],'identity.json':digest(ROOT/'identity.json')}
 before=verify_files(ROOT,pinned);environment=runtime();records=[]
 require(len(metadata['sources'])==43,'Expected43sources')
 for entry in metadata['sources']:
  path=entry['path'];safe_relative(path)
  original=str(ROOT/'original'/path);candidate=str(ROOT/'candidate'/path)
  compiles={variant:command_run([PHP]+LINT_FLAGS+[filename]) for variant,filename in [('original',original),('candidate',candidate)]}
  proof=command_run([PHP]+TOKEN_FLAGS+[str(ROOT/'verify-tokens.php'),original,candidate,str(ROOT/entry['messages'])])
  parsed=None;valid=False
  if proof['exit']==0:
   parsed=json.loads(proof['stdout']);valid=parsed['before_sha256']==entry['before_sha256'] and parsed['after_sha256']==entry['after_sha256'] and len(parsed['offset_pairs'])==entry['offset_pairs'] and parsed['changed_bytes']==entry['changed_bytes'] and parsed['all_other_bytes_tokens_identical'] is True
  records.append({'path':path,'source_identity':entry,'compile':compiles,'token_command':proof['command'],'token_exit':proof['exit'],'token_stderr':proof['stderr'],'token_stdout_sha256':hashlib.sha256(proof['stdout'].encode()).hexdigest(),'token_proof':parsed,'token_proof_valid':valid})
 require(verify_files(ROOT,pinned)==before and runtime()==environment,'Post-run identity drift')
 complete=all(v['exit'] in (0,255) for r in records for v in r['compile'].values()) and all(r['token_exit'] in (0,255) for r in records)
 summary={variant:{'files':43,'accepted':sum(r['compile'][variant]['exit']==0 for r in records),'rejected':sum(r['compile'][variant]['exit']==255 for r in records),'incomplete':sum(r['compile'][variant]['exit'] not in (0,255) for r in records)} for variant in ('original','candidate')}
 passed=complete and summary['original']['accepted']==43 and summary['candidate']['accepted']==43 and all(r['token_proof_valid'] for r in records)
 print(json.dumps({'schema':1,'scope':'PHP7.4 compiler and native tokenizer controls only; no source-body execution','runtime':environment,'stage_identity':metadata,'identity_sha256':digest(ROOT/'identity.json'),'records':records,'summary':summary,'collection_complete':complete,'compiler_and_token_checks_passed':passed,'application_acceptance':False},indent=2))
 return 0 if passed else 1

class Controls(unittest.TestCase):
 def test_wrong_hash(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'a').write_text('a')
   with self.assertRaises(RuntimeError):verify_files(p,{'a':'0'*64})
 def test_extra_file(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'a').write_text('a')
   with self.assertRaises(RuntimeError):verify_files(p,{})
 def test_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'a').write_text('a');(p/'b').symlink_to('a')
   with self.assertRaises(RuntimeError):verify_files(p,{'a':digest(p/'a'),'b':digest(p/'a')})
 def test_traversal(self):
  with self.assertRaises(RuntimeError):safe_relative('../escape.php')
 def test_absolute(self):
  with self.assertRaises(RuntimeError):safe_relative('/etc/passwd')
 def test_valid(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'a').write_text('a');self.assertEqual(verify_files(p,{'a':digest(p/'a')}),{'a':digest(p/'a')})

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','scan','test']);parser.add_argument('target',nargs='?',type=Path);a=parser.parse_args()
 if a.mode=='prepare':require(a.target is not None,'Stage target required');prepare(a.target)
 elif a.mode=='scan':raise SystemExit(scan())
 else:raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls)).wasSuccessful())

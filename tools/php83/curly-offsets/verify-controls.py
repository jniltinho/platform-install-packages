#!/usr/bin/env python3
"""Actual native token-verifier negative controls, synthetic only, isolated lab."""
import json,pathlib,subprocess,tempfile
P=pathlib.Path
base='<?php\n$x="ab";\n// do not edit {0}\n$s="{literal}";\nif (true) { $out=$x{0}; }\n'
after=base.replace('$x{0}','$x[0]')
offset=base.index('$x{0}')+2
message={'source':'PHPCompatibility.Syntax.RemovedCurlyBraceArrayAccess.Removed','fixable':True,'line':base[:offset].count('\n')+1,'column':offset-base.rfind('\n',0,offset)}
cases=[('valid',base,after,[message],True),('duplicate_findings',base,after,[message,message],True),
 ('comment_change',base,after.replace('edit','EDIT'),[message],False),
 ('string_change',base,after.replace('{literal}','[literal]'),[message],False),
 ('control_block_change',base,after.replace('if (true) {','if (true) ['),[message],False),
 ('no_changes',base,base,[],False),
 ('closing_only',base,base.replace('$x{0}','$x{0]'),[message],False),
 ('other_code_change',base,after.replace('true','null'),[message],False),
 ('wrong_sniff',base,after,[{**message,'source':'Unexpected.Sniff'}],False),
 ('wrong_position',base,after,[{**message,'column':1}],False)]
# Interpolation curly-open is an array token, never eligible offset punctuation.
inter='<?php $s="{$x}";'
cases.append(('interpolation_change',inter,inter.replace('{$x}','[$x]'),[message],False))
rows=[]
with tempfile.TemporaryDirectory() as d:
 root=P(d)
 for name,b,a,m,want in cases:
  (root/'before').write_text(b);(root/'after').write_text(a);(root/'messages').write_text(json.dumps(m))
  command=['/usr/bin/php8.3','-n','-d','extension=tokenizer','/audit/tools/verify-tokens.php',str(root/'before'),str(root/'after'),str(root/'messages')]
  r=subprocess.run(command,capture_output=True,text=True,timeout=15)
  passed=(r.returncode==0)==want
  rows.append({'case':name,'expected_accept':want,'exit':r.returncode,'passed':passed,'stdout':r.stdout,'stderr':r.stderr.replace(d,'/fixture')})
report={'cases':rows,'passed':all(r['passed'] for r in rows),'synthetic_only':True}
print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)

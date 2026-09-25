#!/usr/bin/env python3
"""Extract exactly one allowlisted define statement, never execute generated scripts."""
import argparse,base64,hashlib,json,re
from pathlib import Path
REPORT_PIN='43074293abfe7a9bda134a6305a72adf66e4139b6888d13e220d93a674696a86'
def sha(b):return hashlib.sha256(b).hexdigest()
def statement(data):
 lines=[l for l in data.splitlines() if b"define('SF_DEBUG'" in l]
 if len(lines)!=1 or re.fullmatch(rb"define\('SF_DEBUG',[ \t]*(?:1)?[ \t]*\);",lines[0]) is None:raise ValueError('Not exactly one allowlisted DEBUG definition')
 return lines[0]
HEADER=b'''<?php
// Isolated native call only. No includes, eval, autoload, application or config.
$diagnostics=array();
set_error_handler(function($severity,$message,$file,$line) use (&$diagnostics){
 $diagnostics[]=array('severity'=>$severity,'message'=>$message,'line'=>$line);return false;
});
$returned=null;$exception=null;
try {
 $returned = '''
FOOTER=b'''
} catch(Throwable $e) {$exception=array('class'=>get_class($e),'message'=>$e->getMessage());}
echo json_encode(array('runtime'=>PHP_VERSION,'returned'=>$returned,'returned_type'=>gettype($returned),'defined'=>defined('SF_DEBUG'),'constant'=>defined('SF_DEBUG')?constant('SF_DEBUG'):null,'diagnostics'=>$diagnostics,'exception'=>$exception),JSON_UNESCAPED_SLASHES|JSON_THROW_ON_ERROR)."\\n";
exit($exception===null?0:10);
'''
def prepare(report_path,output):
 raw=report_path.read_bytes()
 if sha(raw)!=REPORT_PIN:raise ValueError('Generated evidence pin mismatch')
 report=json.loads(raw);selected={};provenance=[];seen=set()
 for r in report['records']:
  if r['runtime']!='83' or r['variant']!='candidate' or r['case'] not in ['default-false','default-zero','rotate-false','rotate-zero','controller-false','controller-zero','default-true']:continue
  if r['case'] in seen:raise ValueError('Duplicate selected case')
  seen.add(r['case'])
  body=json.loads(r['stdout'])
  if len(body['outputs'])!=1:raise ValueError('Unexpected output inventory')
  path,item=next(iter(body['outputs'].items()));data=base64.b64decode(item['base64'],validate=True)
  if sha(data)!=item['sha256']:raise ValueError('Generated source hash mismatch')
  stmt=statement(data);key='true' if r['case']=='default-true' else 'empty'
  if (b'1' in stmt)!=(key=='true'):raise ValueError('Case name/literal mismatch')
  if key in selected and selected[key]!=stmt:raise ValueError('DEBUG statement drift')
  selected[key]=stmt;provenance.append({'case':r['case'],'path':path,'source_sha256':sha(data),'statement':stmt.decode(),'statement_sha256':sha(stmt)})
 if set(selected)!={'empty','true'} or len(provenance)!=7:raise ValueError('Missing input cases')
 output.mkdir(exist_ok=False);files={}
 for key,stmt in selected.items():
  data=HEADER+stmt+FOOTER;(output/(key+'.php')).write_bytes(data);files[key+'.php']=sha(data)
 manifest={'status':'PREPARED_NOT_EXECUTED','source_report_sha256':REPORT_PIN,'sources':provenance,'fixture_sha256':files,'scope':'One literal native define call per process only; generated application never loaded','runtime_acceptance':False}
 (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('report',type=Path);p.add_argument('output',type=Path);a=p.parse_args();prepare(a.report,a.output)

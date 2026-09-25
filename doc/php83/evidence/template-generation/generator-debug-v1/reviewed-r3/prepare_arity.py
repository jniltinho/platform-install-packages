#!/usr/bin/env python3
"""Derive safe numeric literals only from a validated actual generation report."""
import argparse,base64,hashlib,importlib.util,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v',HERE/'validate.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def sha(b):return hashlib.sha256(b).hexdigest()
def statement(data):
 lines=[line for line in data.splitlines() if b"define('SF_DEBUG'" in line]
 if len(lines)!=1 or re.fullmatch(rb"define\('SF_DEBUG',[ \t]*[01][ \t]*\);",lines[0]) is None:raise ValueError('Not one numeric DEBUG literal')
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
def extract(report):
 selected={};provenance=[];seen=set()
 cases=['default-false','default-zero','rotate-false','rotate-zero','controller-false','controller-zero','default-true']
 for row in report['records']:
  if row['runtime']!='83' or row['variant']!='debug' or row['case'] not in cases:continue
  if row['case'] in seen:raise ValueError('Duplicate case')
  seen.add(row['case']);body=json.loads(row['stdout'])
  if len(body['outputs'])!=1:raise ValueError('Output inventory')
  path,item=next(iter(body['outputs'].items()));data=base64.b64decode(item['base64'],validate=True)
  if sha(data)!=item['sha256']:raise ValueError('Generated hash')
  stmt=statement(data);key='one' if row['case']=='default-true' else 'zero'
  if re.fullmatch(rb"define\('SF_DEBUG',[ \t]*"+(b'1' if key=='one' else b'0')+rb"[ \t]*\);",stmt) is None:raise ValueError('Case literal mismatch')
  if key in selected and selected[key]!=stmt:raise ValueError('Literal drift')
  selected[key]=stmt;provenance.append({'case':row['case'],'path':path,'generated_sha256':sha(data),'statement':stmt.decode()})
 if seen!=set(cases) or set(selected)!={'zero','one'}:raise ValueError('Missing selected cases')
 return {name+'.php':HEADER+stmt+FOOTER for name,stmt in selected.items()},provenance
def verified(report_path,pin):
 raw=report_path.read_bytes()
 if re.fullmatch('[0-9a-f]{64}',pin) is None or sha(raw)!=pin:raise ValueError('Report pin mismatch')
 report=json.loads(raw);v.validate(report);files,provenance=extract(report)
 manifest={'status':'PREPARED_NOT_EXECUTED','source_report_sha256':pin,'sources':provenance,'fixture_sha256':{n:sha(b) for n,b in files.items()},'generated_application_execution':False}
 return files,manifest
def prepare(report,pin,output):
 files,manifest=verified(report,pin);output.mkdir(exist_ok=False)
 for name,data in files.items():(output/name).write_bytes(data)
 (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('report',type=Path);p.add_argument('sha256');p.add_argument('output',type=Path);a=p.parse_args();prepare(a.report,a.sha256,a.output)

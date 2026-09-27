"""Prepared-statement display only; no installation or source artifact mutation."""
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('log_copy',HERE.parent/'prepare.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
TARGET='alpha/apps/kaltura/lib/db/KalturaStatement.php'
PIN='459feaf9caf2abe55963dce0cac51b8b593e4ff1b46d2eaf9cb7d5c3f13f62a1'
def transform(raw):
 out=old.replace_once(raw,b'\tprotected $values = array();',b'\tprotected $values = array();\n\t// Display metadata only. Never retain another copy of argument values.\n\tprotected $logValueTypes = array();')
 out=old.replace_once(out,b'\t\t$index = count($this->values) + 1;',b'\t\t$index = count($this->values) + 1;\n\t\t$this->logValueTypes[":p{$index}"] = gettype($value);')
 out=old.replace_once(out,b'\t\tKalturaLog::debug($sql);',b'''\t\t// Keep the original SQL for execution, dry-run and monitoring. Only the\n\t\t// DEBUG representation uses placeholders plus value-free type metadata.\n\t\t$logTypes = $this->logValueTypes;\n\t\tif (!is_null($input_parameters))\n\t\t{\n\t\t\t$logTypes = array();\n\t\t\t$logIndex = 1;\n\t\t\tforeach ($input_parameters as $logValue)\n\t\t\t\t$logTypes[':p' . $logIndex++] = gettype($logValue);\n\t\t}\n\t\tKalturaLog::debug($this->queryString . ' [bind-types:' . json_encode($logTypes) . ']');''')
 return out

def prepare(original,candidate,output):
 if output.exists():raise ValueError('Fresh output required')
 output.mkdir(parents=True)
 rows=[]
 for version,archive,pin in [('original',original,old.UPSTREAM),('exp14',candidate,PIN)]:
  before=old.archive(archive,pin,[TARGET])[TARGET];after=transform(before);patch=old.patch_bytes(TARGET,before,after);old.strict_replay(TARGET,before,patch,after)
  d=output/version;d.mkdir();(d/'KalturaStatement.php').write_bytes(after);(d/'original.php').write_bytes(before);(d/'display.patch').write_bytes(patch)
  rows.append({'version':version,'path':TARGET,'before_sha256':old.sha(before),'after_sha256':old.sha(after),'patch_sha256':old.sha(patch)})
 result={'status':'PREPARED_NOT_INSTALLED','targets':rows,'privacy_acceptance':False,'native_executed':False,'limit':'Prepared bound values only; SQL template literals and direct PDO logs unchanged'}
 (output/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path);a=p.parse_args();print(json.dumps(prepare(a.original,a.candidate,a.output),indent=2))

"""Sequential guarded native-policy matrix. Requires prior explicit VM ownership."""
import argparse,hashlib,itertools,json,subprocess
from pathlib import Path
POLICIES=('enabled','legacy','default','deny')
PARSERS=('dom','simplexml','xmlreader')
DOCS=('plain','internal','malformed','file','wrapper','dtd')
FLAGS=('zero','noent','dtdload','dtdvalid','nonet','noent_dtdload','noent_dtdload_nonet')
OPTIONS=(0,2,4,16,2048,6,2054)
MARKER='SYNTHETIC_XML_ENTITY_MARKER'
def validate(body,policy,parser,runtime,sources):
 if type(body) is not dict:raise ValueError('body')
 if body.get('policy')!=policy or body.get('parser')!=parser or body.get('application_coverage') is not False:raise ValueError('scope')
 if body.get('source')!=sources:raise ValueError('source pins')
 r=body.get('runtime',{})
 pid=r.get('php_id')
 if type(pid) is not int or not ((70400<=pid<70500) if runtime=='74' else (80300<=pid<80400)):raise ValueError('runtime family')
 if type(r.get('error_reporting')) is not int or r['error_reporting']!=32767 or r.get('internal_errors') is not False:raise ValueError('warning policy')
 if not isinstance(r.get('extensions'),list) or not {'libxml','dom','SimpleXML','xmlreader'}.issubset(r['extensions']):raise ValueError('modules')
 rows=body.get('records')
 if type(rows) is not list or len(rows)!=42:raise ValueError('inventory size')
 if [(x.get('document'),x.get('flag')) for x in rows]!=list(itertools.product(DOCS,FLAGS)):raise ValueError('inventory')
 for row in rows:
  if type(row.get('options')) is not int or row['options']!=OPTIONS[FLAGS.index(row['flag'])]:raise ValueError('flags')
  if type(row.get('initial_parse_return')) is not bool or type(row.get('value')) is not str:raise ValueError('value types')
  for key,token in [('marker_seen',MARKER),('internal_seen','INTERNAL')]:
   if type(row.get(key)) is not bool or row[key]!=(token in row['value']):raise ValueError('marker consistency')
  for key in ['diagnostics','loader_calls','wrapper_events']:
   if type(row.get(key)) is not list:raise ValueError('event list')
  if policy in ('legacy','deny') and row['marker_seen']:raise ValueError('external marker disclosed under blocking policy')
  if row['document']=='malformed' and not (row['diagnostics'] or row.get('exception')):raise ValueError('malformed missing diagnostic')
 by={(x['document'],x['flag']):x for x in rows}
 if by['plain','zero']['value']!='PLAIN' or by['internal','noent']['value']!='INTERNAL':raise ValueError('positive parser functionality')
 if policy=='enabled':
  for key in [('file','noent'),('wrapper','noent'),('dtd','noent_dtdload')]:
   if not by[key]['marker_seen']:raise ValueError('enabled canary did not demonstrate external read: '+str(key))
 if policy=='deny':
  for key in [('file','noent'),('wrapper','noent'),('dtd','noent_dtdload')]:
   if not by[key]['loader_calls']:raise ValueError('deny callback not reached: '+str(key))
 return {'rows':42,'markers_observed':sum(x['marker_seen'] for x in rows),'diagnostics':sum(len(x['diagnostics']) for x in rows),'policy_diagnostics':len(body.get('policy_diagnostics',[]))}
def main():
 p=argparse.ArgumentParser();p.add_argument('runtime',choices=['74','83']);p.add_argument('prepared',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 if a.output.exists():raise ValueError('Refuse existing output')
 manifest=(a.prepared/'identities.json').read_bytes();pin=hashlib.sha256(manifest).hexdigest();m=json.loads(manifest)
 if set(m['files'])!={'probe.php','run.sh','marker.txt','marker.dtd'}:raise ValueError('manifest')
 for n,h in m['files'].items():
  if hashlib.sha256((a.prepared/n).read_bytes()).hexdigest()!=h:raise ValueError('local stage drift')
 sources={k:m['files'][n] for k,n in [('probe','probe.php'),('marker','marker.txt'),('dtd','marker.dtd')]}
 config,alias=('/tmp/kaltura-php74-ssh.conf','baseline74') if a.runtime=='74' else ('/tmp/kaltura-php83-ssh.conf','php83')
 records=[];failures=[]
 for policy,parser in itertools.product(POLICIES,PARSERS):
  command=['ssh','-T','-F',config,alias,'bash /home/vagrant/php-xml-loader-r1/run.sh '+policy+' '+parser+' '+pin]
  rec={'policy':policy,'parser':parser,'command':command}
  try:
   r=subprocess.run(command,capture_output=True,text=True,timeout=75)
   rec.update({'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
   if r.returncode:raise ValueError('native process failed')
   rec['body']=json.loads(r.stdout)
   rec['validation']=validate(rec['body'],policy,parser,a.runtime,sources)
  except (ValueError,subprocess.TimeoutExpired) as e:
   rec['validation_error']=str(e);failures.append(policy+'/'+parser)
  records.append(rec)
 output={'status':'FAIL' if failures else 'PASS_BOUNDED_NATIVE_POLICY','runtime':a.runtime,
    'manifest_sha256':pin,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'records':records,'failures':failures,'application_coverage':False,
    'runtime_identity_requirement':'Coordinator must bracket this run with binary/module/linked-library snapshots; report alone does not establish unchanged runtime.'}
 a.output.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'processes':len(records),'failures':failures}))
 raise SystemExit(bool(failures))
if __name__=='__main__':main()

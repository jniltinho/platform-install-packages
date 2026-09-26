#!/usr/bin/env python3
"""88 current artifact processes; historical 74/cachefix rows explicitly not rerun."""
import argparse,base64,json,subprocess
from pathlib import Path
import common as c

def closure():return {p.name:c.sha(p.read_bytes()) for p in [Path(__file__),c.HERE/'common.py',c.HERE/'input-pins.json']}
def adjudicate(result,identity):
 try:
  c.need(not result['failures'],'Native observation failures');result['contract']=c.compare(result['records'])
  c.need(closure()==identity,'Collector closure changed');result['status']='PASS_BOUNDED_88_ARTIFACT_CONTRACT'
 except Exception as e:
  result['status']='FAIL_RETAINED_OBSERVATIONS';result['contract_error']={'type':type(e).__name__,'message':str(e)}
 return result

def run(output):
 c.need(not output.exists(),'Refuse report overwrite');c.need(Path.cwd().resolve()==c.ROOT,'Run from repository root before native execution');c.inputs();prep=c.preparation();directory=c.ROOT/prep['local'];raw=(directory/'identities.json').read_bytes();c.need(c.sha(raw)==prep['manifest_sha256'],'Stage manifest')
 manifest=json.loads(raw)
 for name,digest in manifest['files'].items():c.need(c.sha((directory/name).read_bytes())==digest,'Local source drift')
 identity=closure();oracle=c.load_oracle();collector=oracle.collector;refs=c.references();oldmanifest=json.loads((c.OLD/'r3-stage-identities.json').read_bytes());wire_reference=json.loads((c.OLD/'r3-reference-wires.json').read_bytes());wire74={r['kind']:json.loads(r['stdout'])['result']['wire'] for r in refs['74']['records'] if r['kind']!='cache' and r['operation']=='roundtrip'}
 records=[];failures=[];wires={}
 for expected in c.expected():
  variant,kind,op,writer=c.key(expected);row={'variant':variant,'kind':kind,'operation':op,'writer':writer};records.append(row)
  try:
   payload=''
   if op=='read':
    wire=wire74[kind] if writer=='original74' else wires[(writer.removesuffix('83-r2'),kind)];payload=collector.wiredata(wire)
   elif kind=='cache' and op.startswith('read-'):payload=collector.wiredata(wire_reference[('original' if op=='read-C' else 'candidate')+'/plain'])
   cmd=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83','bash '+c.REMOTE+'/run.sh '+variant+' '+kind+' '+op+' '+prep['manifest_sha256']]
   observed=collector.observe_process(cmd,payload,row);row.update(observed)
   c.need(not row.get('invalid_utf8_output'),'Invalid native UTF8; exact byte channels retained')
   body=collector.validate(row,'83',manifest)
   if kind!='cache' and op=='roundtrip':collector.remember_wire(wires,(variant,kind),body['result']['wire'])
  except (ValueError,KeyError,TypeError,AttributeError,OSError,subprocess.TimeoutExpired) as e:
   row['failure']={'type':type(e).__name__,'message':str(e)};failures.append(list(c.key(row)))
 result={'status':'OBSERVED_88_PENDING_TYPED_RECONCILIATION','records':records,'failures':failures,'artifact_pins':prep['artifact_pins'],'manifest_sha256':prep['manifest_sha256'],'collector_closure':identity,'historical74_report_sha256':c.sha((c.OLD/'r3-primary74.json').read_bytes()),'historical74_NOT_RERUN':True,'historical_cachefix_NOT_RERUN':True,'application_acceptance':False,'rollback_compatible':False}
 adjudicate(result,identity)
 output.write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('output',type=Path);r=a.parse_args();result=run(r.output);print(json.dumps({'status':result['status'],'records':len(result['records']),'failures':result['failures']}));raise SystemExit(result['status']!='PASS_BOUNDED_88_ARTIFACT_CONTRACT')

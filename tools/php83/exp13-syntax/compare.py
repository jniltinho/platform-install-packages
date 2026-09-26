#!/usr/bin/env python3
import argparse,copy,hashlib,json,pathlib
import scan

def normalize(report):
 result=copy.deepcopy(report)
 for v in result['variants'].values():
  for row in v['records']:
   t=row.pop('duration_ns');scan.require(type(t) is int and t>=0,'Bad duration')
 return result

def validate(report,contract,harness):
 scan.require(report.get('status')=='COMPLETE_BOUNDED' and report.get('application_acceptance') is False,'Incomplete/nonbounded report')
 scan.require(scan.strict_equal(report['input_contract'],contract),'Contract differs')
 scan.require(scan.strict_equal(report['runtime_before'],report['runtime_after']),'Runtime drift')
 scan.require(report['harness_before']==report['harness_after']==harness,'Harness drift')
 for name,v in report['variants'].items():
  scan.require(v['zip_sha256']==contract['pins'][name],'Artifact pin')
  scan.require(v['source_before']==v['source_after'],'Source drift')
  selected={p:h for p,h in v['source_before'].items() if pathlib.Path(p).suffix.lower() in scan.SUFFIXES}
  scan.require(selected=={r['path']:r['sha256'] for r in v['records']},'Source/record coverage mismatch')
  scan.require(scan.strict_equal(v['summary'],scan.core.summarize(v['records'])),'Summary differs')
 result=scan.compare_reports(report['variants'],contract);scan.require(scan.strict_equal(result,report['comparison']),'Derived comparison mismatch');return result

def main():
 p=argparse.ArgumentParser();p.add_argument('primary',type=pathlib.Path);p.add_argument('independent',type=pathlib.Path);p.add_argument('output',type=pathlib.Path);a=p.parse_args();scan.require(not a.output.exists(),'Output exists')
 reports=[];inputs={}
 for file in [a.primary,a.independent]:
  for suffix,value in [('.exit',b'0'),('.stderr',b'')]:
   q=file.with_suffix(suffix);b=q.read_bytes();scan.require(b.strip()==value,'Runner sidecar failed');inputs[str(q)]=hashlib.sha256(b).hexdigest()
  raw=file.read_bytes();reports.append(json.loads(raw));inputs[str(file)]=hashlib.sha256(raw).hexdigest()
 contract=scan.load_contract();harness={n:scan.sha(scan.HERE/n) for n in scan.FILES}
 for r in reports:validate(r,contract,harness)
 scan.require(scan.strict_equal(normalize(reports[0]),normalize(reports[1])),'Independent evidence differs beyond duration')
 out={'status':'INDEPENDENT_BOUNDED_COMPILER_NONREGRESSION','inputs_sha256':inputs,'logical_rows':sum(len(v['records']) for v in reports[0]['variants'].values()),'comparison':reports[0]['comparison'],'summaries':{v:r['summary'] for v,r in reports[0]['variants'].items()},'application_acceptance':False,'comparator_sha256':scan.sha(pathlib.Path(__file__))}
 with a.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 print(out['status'])
if __name__=='__main__':main()

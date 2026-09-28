"""Preferred reviewed notice census bridge; original supplement retained unchanged."""
import argparse,json
from pathlib import Path
from build import ROOT,canonical,require,sha
from join_supplements import PINS,join
INPUTS=dict(PINS)
INPUTS.pop('doc/php83/evidence/license-notice-census-r1/primary.json')
NOTICE_PATH='doc/php83/evidence/license-notice-census-r1/reviewed-r2.json'
NOTICE_PIN='180b76929ebd2b10457ef430b200eca149ed5189aeac74051ab9a430243fc160'
INPUTS[NOTICE_PATH]=NOTICE_PIN
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();values={}
 for name,pin in INPUTS.items():
  raw=(ROOT/name).read_bytes();require(sha(raw)==pin,'INPUT_PIN');values[name]=json.loads(raw)
 result=join(values[next(iter(PINS))],values[NOTICE_PATH],values[list(PINS)[2]]);result['inputs']=INPUTS
 with Path(a.output).open('xb') as f:f.write(canonical(result))
if __name__=='__main__':main()

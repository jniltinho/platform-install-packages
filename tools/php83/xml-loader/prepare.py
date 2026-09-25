"""Prepare only synthetic files in a new local directory; never execute PHP."""
import argparse,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
MARKER=b'SYNTHETIC_XML_ENTITY_MARKER\n'
DTD=b'<!ELEMENT r (#PCDATA)>\n<!ENTITY x "SYNTHETIC_XML_ENTITY_MARKER">\n'
def prepare(out):
 if out.exists():raise ValueError('Refuse existing stage')
 payload={n:(HERE/n).read_bytes() for n in ['probe.php','run.sh']}
 payload.update({'marker.txt':MARKER,'marker.dtd':DTD})
 out.mkdir(parents=True)
 hashes={}
 for n,b in payload.items():
  (out/n).write_bytes(b);hashes[n]=hashlib.sha256(b).hexdigest()
 (out/'identities.json').write_text(json.dumps({'files':hashes,'synthetic_only':True,'application_coverage':False},indent=2)+'\n')
 return {'manifest_sha256':hashlib.sha256((out/'identities.json').read_bytes()).hexdigest(),'files':4,'application_coverage':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();print(json.dumps(prepare(a.out)))

"""Pinned, curated packaging route evidence; never execute indexed commands."""
import argparse, gzip, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = 'doc/php83/evidence/entrypoint-inventory/authorized-real-r1/inventory.json.gz'
OLD_SHA = '42c3e2411c3973e1f5591d4aacd31d1af2a7a05929af935992ab2ebcdae67501'
def sha(data): return hashlib.sha256(data).hexdigest()
def build(root=ROOT, contract=None):
    spec = contract if contract is not None else json.loads((HERE/'sources.json').read_text())
    sources = {}
    for path, expected in spec['source_pins'].items():
        data = (root/path).read_bytes()
        if sha(data) != expected: raise ValueError('SOURCE_DRIFT')
        sources[path] = data.decode().splitlines()
    rows = []
    for row in spec['routes']:
        item = dict(row); proof = []
        for path, anchor in item.pop('anchors'):
            hits = [(i+1,line.strip()) for i,line in enumerate(sources[path]) if anchor in line]
            if not hits: raise ValueError('ANCHOR_MISSING')
            proof.append({'path':path,'sha256':spec['source_pins'][path], 'lines':[{'line':i,'text':s} for i,s in hits]})
        item['evidence'] = proof; rows.append(item)
    raw = gzip.decompress((root/OLD).read_bytes())
    if sha(raw) != OLD_SHA: raise ValueError('ARCHIVE_INVENTORY_DRIFT')
    old = json.loads(raw); joins=[]
    for path in spec['archive_candidate_paths']:
        found = [r for r in old['candidates'] if r['path']==path]
        if len(found)!=1: raise ValueError('CANDIDATE_CARDINALITY')
        r=found[0]
        joins.append({k:r[k] for k in ('path','sha256','owners')})
    return {'schema':1,'scope':'CURATED_SOURCE_DECLARATIONS_NOT_RUNTIME_REACHABILITY',
      'source_pins':spec['source_pins'],'routes':rows,'archive_candidates':joins,
      'archive_inventory_sha256':OLD_SHA,'full_entrypoint_inventory_complete':False,
      'runtime_activation_verified':False,'limitations':spec['limitations']}
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    data=(json.dumps(build(),sort_keys=True,indent=2)+'\n').encode()
    with a.output.open('xb') as f: f.write(data)

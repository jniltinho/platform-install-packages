"""Pure pinned supplement identity joins; no licensing/runtime completion inference."""
import argparse,json
from pathlib import Path
from build import ROOT,canonical,require,sha
PINS={
 'doc/php83/evidence/inventory-closure-r1/inventory-reviewed.json':'4cd9212e48d806ce7a5cdf852712f4f685cd32182add9a0ec0dacd46567ed162',
 'doc/php83/evidence/license-notice-census-r1/primary.json':'d9fcc34179afb31e3aa07546df278765834f37dc4d337623a5a6ef09db138409',
 'doc/php83/evidence/entrypoint-inventory-r1/inventory.json':'cab11981558027198246f05322940585bad9ed2c7ef4b4ef3126d65d0e849a50'}
def join(inventory,notices,routes):
 require(inventory['source_archive_sha256']==notices['archive_sha256'],'ARCHIVE_JOIN')
 original={r['path']:r for r in inventory['source_members']};vendor={p for p in original if p.startswith('vendor/')}
 require(len(notices['files'])==len({r['path'] for r in notices['files']}) and {r['path'] for r in notices['files']}==vendor,'VENDOR_COVERAGE')
 for r in notices['files']:require((r['sha256'],r['bytes'])==(original[r['path']]['sha256'],original[r['path']]['bytes']),'NOTICE_IDENTITY')
 packages={r['path']:r for r in inventory['packaged_php']}
 # Route candidates can include non-PHP controls/configs; compare against the
 # broader exact historical candidate registry as well, never fabricate owners.
 candidates=inventory['packaged_entrypoint_candidates']
 for r in routes['archive_candidates']:
  matches=[p for p in candidates if p['path']==r['path'] and p['sha256']==r['sha256'] and p['owners']==r['owners']]
  require(bool(matches),'ROUTE_OWNER_IDENTITY')
 require(len(routes['routes'])==len({r['id'] for r in routes['routes']}),'ROUTE_DUPLICATE')
 return {'schema':1,'inputs':PINS,'status':'SUPPLEMENT_IDENTITY_JOINS_PASS','vendor_file_identities':len(vendor),'route_declarations':len(routes['routes']),'route_archive_owner_joins':len(routes['archive_candidates']),'license_applicability':'NOT_ADJUDICATED','runtime_activation_verified':False,'task_1_1_complete':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();inputs=[]
 for name,pin in PINS.items():
  raw=(ROOT/name).read_bytes();require(sha(raw)==pin,'INPUT_PIN');inputs.append(json.loads(raw))
 with Path(a.output).open('xb') as f:f.write(canonical(join(*inputs)))
if __name__=='__main__':main()

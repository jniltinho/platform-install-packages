"""Identity-only bridge for externally reviewed MaxMind attribution, no network."""
import argparse,json
from pathlib import Path
from build import ROOT,canonical,require,sha
INPUTS={
'doc/php83/evidence/inventory-closure-r1/inventory-reviewed.json':'4cd9212e48d806ce7a5cdf852712f4f685cd32182add9a0ec0dacd46567ed162',
'doc/php83/evidence/license-notice-census-r1/maxmind-attribution.json':'ff442cc63b86a6d434cc8db8adc4a0bc29348b34e3e4da7a362298f1ea69e124'}
def join(inventory,attribution):
 require(inventory['source_archive_sha256']==attribution['original_archive_sha256'],'COHORT')
 source={r['path']:r['sha256'] for r in inventory['source_members']};rows=[];seen=set()
 for name,component in sorted(attribution['components'].items()):
  for r in component['files']:
   require(r['path'] not in seen,'DUPLICATE');seen.add(r['path'])
   require(r['equal'] is True and r['local_sha256']==r['upstream_sha256']==source.get(r['path']),'BYTE_JOIN')
  rows.append({'component':name,'files_joined':len(component['files']),'observed_tag':component['observed_tag'],'matching_commit':component['commit'],'declared_upstream_license':component['declared_upstream_license'],'license_sha256':component['license_sha256'],'bundled_license_text_present':component['bundled_license_text_present'],'unique_original_version_proven':False,'release_compliance_approved':False})
 require(seen=={p for p in source if p.startswith('vendor/MaxMind/')},'EXACT_COMPONENT_SCOPE')
 return {'schema':1,'inputs':INPUTS,'status':'MAXMIND_SOURCE_IDENTITY_JOIN_PASS','files':len(seen),'components':rows,'task_1_1_complete':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();values=[]
 for name,pin in INPUTS.items():
  raw=(ROOT/name).read_bytes();require(sha(raw)==pin,'INPUT_PIN');values.append(json.loads(raw))
 with Path(a.output).open('xb') as f:f.write(canonical(join(*values)))
if __name__=='__main__':main()

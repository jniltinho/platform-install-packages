"""Deterministic original ZIP/member-to-package inventory; no application execution.

Pinned historical reports remain provenance, not current installed/runtime claims.
Optional exclusive new-tree extraction and verification; no network, dependency change, license inference or finding adjudication.
"""
import argparse,hashlib,importlib.util,json,os,stat,zipfile
from collections import Counter
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[3]
ZIP_PIN='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
PREFIX='server-Rigel-18.20.0/'
PINS={
 'tools/php83/entrypoint-inventory/build.py':'d2ed28e1df69479a2f795861c1713966cab0d4ba2f32511afcc15dd3702b3202',
 'doc/php83/evidence/package-identities/primary.json':'9e76e1f9664527102528ea2eb46aae38a0d06d441cf270dc48724086af1515c9',
 'doc/php83/evidence/entrypoint-inventory/authorized-real-r1/primary.json':'42c3e2411c3973e1f5591d4aacd31d1af2a7a05929af935992ab2ebcdae67501',
 'doc/php83/evidence/dependency-attribution-followup/primary.json':'232ad945d54ef3bfda5a8c7777be146bf2641b0551143b166e84a4c50b843ec2'}
def sha(b):return hashlib.sha256(b).hexdigest()
def file_sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def canonical(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode()
def require(ok,code):
 if not ok:raise ValueError(code)
def scanner():
 path=ROOT/next(iter(PINS));raw=path.read_bytes();require(sha(raw)==PINS[str(path.relative_to(ROOT))],'SCANNER_PIN')
 spec=importlib.util.spec_from_file_location('inventory_existing_scanner',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def source_inventory(path,expected_pin,scan):
 require(file_sha(path)==expected_pin,'ZIP_PIN');rows=[];seen=set();invocations=[]
 with zipfile.ZipFile(path) as z:
  for member in sorted(z.infolist(),key=lambda x:x.filename):
   require(member.filename.startswith(PREFIX),'ZIP_ROOT')
   name=member.filename[len(PREFIX):];normalized=scan.normalize(name) if name else ''
   require(normalized not in seen,'DUPLICATE_MEMBER');seen.add(normalized)
   if member.is_dir():continue
   require(normalized and name==normalized,'NONCANONICAL_MEMBER')
   mode=member.external_attr>>16;kind=stat.S_IFMT(mode)
   require(kind in (0,stat.S_IFREG),'NONREGULAR_SOURCE')
   raw=z.read(member);require(len(raw)==member.file_size,'SIZE')
   classes=[]
   if scan.php_path(name):classes.append('php_family')
   if scan.is_generated_client_candidate(name):classes.append('generated_client_path_candidate')
   if mode&0o111:classes.append('executable_bit')
   if len(raw)>scan.SCAN_SIZE_LIMIT:disposition='oversize_unscanned'
   elif b'\0' in raw:disposition='binary_unscanned'
   else:
    disposition='bounded_text_scanned';lower=raw.lower()
    if b'<?php' in lower or b'<?=' in lower:classes.append('php_open_tag_candidate')
    text=scan._decode_scan_text(raw)
    if scan.SHEBANG_PHP_RE.match(text.splitlines()[0] if text else ''):classes.append('php_shebang')
    # No raw excerpts or command arguments emitted, even from public source.
    for hit in scan.scan_php_invocations(text,name,{'source_archive_sha256':expected_pin}):
     invocations.append({'source_path':name,'source_sha256':sha(raw),'line':hit['line'],'target_class':hit['target_class']})
   rows.append({'path':name,'sha256':sha(raw),'bytes':len(raw),'mode':stat.S_IMODE(mode),'classes':classes,'scan_disposition':disposition})
 require(file_sha(path)==expected_pin,'ZIP_CHANGED')
 return rows,invocations

def join(rows,package_report,entry_report):
 require(package_report['original_archive_sha256']==entry_report['original_archive_sha256']==ZIP_PIN,'SOURCE_COHORT')
 require(package_report['bundle_sha256']==entry_report['bundle_sha256'],'PACKAGE_COHORT')
 source={r['path']:r for r in rows};require(len(source)==len(rows),'SOURCE_DUPLICATE')
 owners={p['package_file']:p['package_sha256'] for p in package_report['packages']}
 require(len(owners)==len(package_report['packages']),'OWNER_DUPLICATE')
 require(owners=={p['package_file']:p['package_sha256'] for p in entry_report['packages']},'ENTRY_OWNER_JOIN')
 matched=set();package_rows=[]
 for name,row in sorted(package_report['files'].items()):
  require(name==row['path'] and row['type']=='regular','PACKAGE_ROW')
  require(row['owners'] and all(owners.get(o['package_file'])==o['package_sha256'] for o in row['owners']),'OWNER_PIN')
  candidate=name.removeprefix('opt/kaltura/app/') if name.startswith('opt/kaltura/app/') else None
  original=source.get(candidate);relation='package_only_php_overlay'
  if original:
   matched.add(candidate);relation='same_original_bytes' if row['sha256']==original['sha256'] else 'changed_original_bytes'
  package_rows.append({'path':name,'sha256':row['sha256'],'bytes':row['size'],'owners':row['owners'],'original_path':candidate if original else None,'relation':relation})
 # Inventory union: never discard original-only/non-PHP files or package owners.
 for row in rows:row['matched_in_packaged_php_index']=row['path'] in matched
 grouped=Counter(r['relation'] for r in package_rows)
 expected=package_report['source_differential']
 require(grouped['same_original_bytes']==expected['unchanged_upstream_php_files'],'UNCHANGED_JOIN')
 require(grouped['package_only_php_overlay']==expected['extra_packaged_php_files'],'OVERLAY_JOIN')
 return package_rows

def extracted_identity(tree,rows):
 tree=Path(tree);require(tree.is_dir() and not tree.is_symlink(),'EXTRACTED_ROOT')
 expected={r['path']:r for r in rows};observed=set()
 for p in tree.rglob('*'):
  require(not p.is_symlink(),'EXTRACTED_LINK')
  if p.is_dir():continue
  name=p.relative_to(tree).as_posix();require(name in expected and p.is_file(),'EXTRACTED_INVENTORY')
  require(file_sha(p)==expected[name]['sha256'] and p.stat().st_size==expected[name]['bytes'],'EXTRACTED_BYTES');observed.add(name)
 require(observed==set(expected),'EXTRACTED_MISSING')
 return {'status':'ALL_ORIGINAL_REGULAR_BYTES_VERIFIED','files':len(observed),'bytes':sum(r['bytes'] for r in rows),'manifest_sha256':sha(canonical([(r['path'],r['sha256'],r['bytes']) for r in rows]))}

def extract_new(archive,tree,rows):
 # rows were produced by fully pinned, duplicate/path/nonregular rejecting census.
 tree=Path(tree);require(not os.path.lexists(tree),'EXTRACTION_EXISTS');tree.mkdir(mode=0o700)
 with zipfile.ZipFile(archive) as z:
  for row in rows:
   p=tree/row['path'];p.parent.mkdir(parents=True,exist_ok=True)
   raw=z.read(PREFIX+row['path']);require(sha(raw)==row['sha256'],'EXTRACTION_SOURCE_DRIFT')
   with p.open('xb') as f:f.write(raw)
 return extracted_identity(tree,rows)

def build(archive,tree,create=False):
 raw={n:(ROOT/n).read_bytes() for n in PINS};require(all(sha(v)==PINS[n] for n,v in raw.items()),'INPUT_PIN')
 scan=scanner();rows,invocations=source_inventory(archive,ZIP_PIN,scan)
 extraction=extract_new(archive,tree,rows) if create else extracted_identity(tree,rows)
 reports=[json.loads(raw[n]) for n in list(PINS)[1:]];packages,entries,dependencies=reports
 package_rows=join(rows,packages,entries)
 require(dependencies['archive']['sha256']==ZIP_PIN,'DEPENDENCY_COHORT')
 return {'schema':1,'scope':'Original member coverage + historical published package join; no active-runtime, license-completeness or static-finding acceptance',
  'source_archive_sha256':ZIP_PIN,'extraction':extraction,'inputs':PINS,'source_members':rows,'original_invocation_candidates':invocations,'packaged_php':package_rows,
  'packaged_entrypoint_candidates':[{'path':r['path'],'sha256':r.get('sha256'),'class':r['candidate_class'],'owners':r['owners']} for r in entries['candidates']],
  'dependency_attribution_rows':dependencies['rows'],
  'summary':{'source_files':len(rows),'source_classes':dict(sorted(Counter(c for r in rows for c in r['classes']).items())),
   'scan_dispositions':dict(sorted(Counter(r['scan_disposition'] for r in rows).items())),
   'original_invocation_candidates':len(invocations),'packaged_php':len(package_rows),'package_relations':dict(sorted(Counter(r['relation'] for r in package_rows).items())),
   'packaged_entrypoint_candidates':len(entries['candidates']),'dependency_directory_rows':len(dependencies['rows'])},
  'remaining':['Source-backed active/historical route classification from separate reviewer','Scoped revision/license gaps from separate attribution lane','Generated-client identity/classification join beyond path heuristics; actual execution is separate runtime scope','Non-PHP packaged-file semantic coverage; exact original member registry is complete'],
  'task_1_1_complete':False,'static_findings_adjudicated':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--output',required=True);p.add_argument('--extracted-tree',required=True);p.add_argument('--create-new-tree',action='store_true');a=p.parse_args()
 result=canonical(build(a.archive,a.extracted_tree,a.create_new_tree))
 with Path(a.output).open('xb') as f:f.write(result)
 print(json.dumps({'status':'INVENTORY_BUILT_NOT_FULL_ACCEPTANCE','sha256':sha(result),'bytes':len(result)}))
if __name__=='__main__':main()

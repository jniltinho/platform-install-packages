"""Read-only local R3 stage/manifest consistency check. No SSH/PHP/writes."""
import hashlib,importlib.util,json,subprocess
from pathlib import Path
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
T=Path('tools/php83/serialization-contracts');E=Path('doc/php83/evidence/serialization-contracts');S=T/'stage-r3';R2=T/'stage-r2'
s=importlib.util.spec_from_file_location('c',T/'collect-r2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
m=json.loads((E/'r3-stage-identities.json').read_text());pin=json.loads((E/'r3-stage-pin.json').read_text());o=json.loads((E/'r2-stage-identities.json').read_text())
out={}
out['collector_closure_matches_current']=m['collector_closure']==c.collector_identity()
out['pin_matches_evidence_manifest']=H(E/'r3-stage-identities.json')==pin['manifest_sha256']
out['stage_manifest_bytes_equal_evidence']=(S/'identities.json').read_bytes()==(E/'r3-stage-identities.json').read_bytes()
actual={str(p.relative_to(S)) for p in S.rglob('*') if p.is_file() or p.is_symlink()}
out['stage_inventory_exact']=actual==set(m['files'])|{'identities.json'}
out['no_symlinks']=not any(p.is_symlink() for p in S.rglob('*'))
out['stage_hashes_match']=all(H(S/n)==d for n,d in m['files'].items())
diff=sorted(k for k in set(m['files'])|set(o['files']) if m['files'].get(k)!=o['files'].get(k))
out['files_differing_from_r2_manifest']=diff
out['changes_equal_r2']=m['changes']==o['changes'];out['runtime_files_equal_r2']=m['runtime_files']==o['runtime_files'];out['source_archives_equal_r2']=m['source_archives']==o['source_archives']
out['patch_hashes_match']=all(H(ch['patch'])==ch['patch_sha256'] for ch in m['changes'])
out['patches_git_clean']=subprocess.run(['git','status','--porcelain','--']+[ch['patch'] for ch in m['changes']],capture_output=True,text=True).stdout==''
out['candidate_after_hashes']=all(m['files'].get('candidate/'+ch['path'])==ch['after_sha256'] and m['files'].get('original/'+ch['path'])==ch['before_sha256'] for ch in m['changes'])
out['reference_wires_equal_r2']=(E/'r3-reference-wires.json').read_bytes()==(E/'r2-reference-wires.json').read_bytes()==(S/'reference-wires.json').read_bytes()
out['preparer_sha_matches_current']=m['preparer_sha256']==H(T/'prepare-r3.py')
r2=(R2/'run.sh').read_text().splitlines();r3=(S/'run.sh').read_text().splitlines()
out['runsh_changed_lines']=[[a,b] for a,b in zip(r2,r3) if a!=b]+([['len',len(r2),len(r3)]] if len(r2)!=len(r3) else [])
out['phase']=m['phase'];out['application_selected']=m['application_selected'];out['manifest_sha256']=pin['manifest_sha256'];out['collector_closure_sha256']=m['collector_closure']['sha256']
print(json.dumps(out,indent=1))

import json,hashlib,subprocess
from pathlib import Path
h=lambda b:hashlib.sha256(b).hexdigest()
P=Path('doc/php83/evidence/exp13-candidate');pr=P/'proposed-r1';se=P/'selected-r1'
raw=(pr/'manifest.json').read_bytes();p=json.loads(raw);s=json.loads((se/'manifest.json').read_bytes())
r={}
r['proposal_sha']=h(raw);r['proposal_sha_ok']=h(raw)=='b6ec7cc58a1828611d9c4558a8557eaa6fbf57ea72a40ef02e2095d9af177b17'
r['proposal_committed_equal']=h(subprocess.check_output(['git','show','fd157eb4:'+str(pr/'manifest.json')]))==h(raw)
r['proposal_worktree_clean']=subprocess.run(['git','diff','--quiet','HEAD','--',str(pr)]).returncode==0
r['patch_rows_equal']=s['patches']==p['patches'];r['patch_count']=len(s['patches'])
bad=[x['patch'] for x in s['patches'] if h((se/x['patch']).read_bytes())!=x['sha256'] or (se/x['patch']).read_bytes()!=(pr/x['patch']).read_bytes()]
r['patch_bytes_mismatch']=bad
r['selected_files_extra']=sorted({f.name for f in se.iterdir()}-{x['patch'] for x in s['patches']}-{'manifest.json'})
diff={k for k in set(p)|set(s) if p.get(k)!=s.get(k)};r['changed_keys']=sorted(diff)
r['proposal_status']=p['status'];r['proposal_pending']=p['pending'];r['selected_pending']=s['pending'];r['proposal_conditional']=p['conditional_families']
pins=json.load(open('tools/php83/exp13-candidate/sql-pins.json'))
r['sql_pins_ok']={k:h(Path(k).read_bytes())==v for k,v in pins.items()}
r['sql_pins_committed_004b75da']={k:(h(subprocess.check_output(['git','show','004b75da:'+k]))==v) if subprocess.run(['git','cat-file','-e','004b75da:'+k]).returncode==0 else 'absent' for k,v in pins.items()}
r['sql_pins_head_clean']=subprocess.run(['git','diff','--quiet','HEAD','--',*pins]).returncode==0
r['comparison']=json.load(open('doc/php83/evidence/return-contracts-sql/comparison-r2.json'))
r['auth']=s['selection_authorization']
print(json.dumps(r,indent=1))

"""Finite retained-evidence join only. No subprocess, PHP, VM or semantic PASS inference."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
MANIFEST=ROOT/'doc/php83/evidence/exp14-candidate/selected-r1/manifest.json'
ZIP=ROOT.parent/'platform-install-packages-php83-artifacts/exp14/Rigel-18.20.0-php83-experimental.exp14.zip'
PIN='459feaf9caf2abe55963dce0cac51b8b593e4ff1b46d2eaf9cb7d5c3f13f62a1'
REPORTS=['exp14-runtime/cli74-primary.json','exp14-runtime/cli83-primary.json','exp14-runtime/api-primary.json','exp13-xml/primary.json','exp13-serialization/primary.json','exp12-runtime/generator-primary.json','exp12-runtime/criteria-primary.json','exp12-runtime/additions-primary-revalidated.json','exp12-runtime/curly-primary.json','curly-offsets/behavior-primary.json','base-object-ternary/primary-r2.json','autoload83/primary-r3.json','autoload83/composition-primary-r2.json','return-contracts/native-primary.json','return-contracts-sql/primary-r1.json','dispatch-rank/native-primary.json','dispatch-rank/baseline74-authorized-primary.json','rank-signature-repair/primary-r2.json','criteria-selection/composition-primary.json']
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(path):return json.loads(path.read_text())
def family(path):
 if '/curly-offsets/' in path['source_patch']:return 'curly'
 p=path['path']
 if p.startswith('vendor/aws/'):return 'aws'
 if p in ['alpha/config/kConf.php','infra/general/kSoapClient.php','infra/general/kXmlEntityLoaderPolicy.php']:return 'xml'
 if p.endswith(('KalturaPDO.php','PropelPDO.php','PropelConfiguration.php','KalturaAPIException.php','DebugPDO.php')):return 'return-family'
 if p.endswith('KalturaStatement.php'):return 'statement-bool'
 if p.endswith('Criteria.php'):return 'criteria'
 if p.endswith(('pakeApp.class.php','sfPakeGenerator.php')):return 'generator'
 if p.endswith(('HTMLPurifier.autoload.php','symfony.php','sfCore.class.php')):return 'autoload'
 if p.endswith('baseObjectUtils.class.php'):return 'ternary'
 if p.endswith('KalturaEntryService.php'):return 'rank'
 if p.endswith('KalturaFrontController.php'):return 'dispatcher'
 if p.endswith('KalturaActionReflector.php'):return 'reflection'
 if p.endswith('/Config.php'):return 'config'
 if p.endswith(('Services_JSON.class.php','/Encoder.php','/Decoder.php')):return 'json'
 if p.endswith('dateUtils.class.php'):return 'date'
 if p.endswith('KalturaDocCommentParser.php'):return 'doccomment'
 return 'null-input'
def main():
 out=OUT/'ledger.json'
 if out.exists():raise ValueError('Never overwrite')
 m=load(MANIFEST);entries=m['patches'];assert len(entries)==len({p['path'] for p in entries})==76
 assert sha(ZIP.read_bytes())==PIN
 with zipfile.ZipFile(ZIP) as z:
  names=z.namelist();assert len(names)==len(set(names))
  for e in entries:
   matches=[n for n in names if n.endswith('/'+e['path'])];assert len(matches)==1
   assert sha(z.read(matches[0]))==e['after_sha256']
   assert sha((ROOT/e['source_patch']).read_bytes())==e['sha256']
 compiler_path=ROOT/'doc/php83/evidence/exp14-syntax/opencode-independent.json';compiler=load(compiler_path)
 records=compiler['variants']['exp14']['records'];by_path={r['path']:r for r in records};assert len(by_path)==len(records)==11785
 refs={e['path']:{'before':[],'after':[]} for e in entries};inputs={str(MANIFEST.relative_to(ROOT)):sha(MANIFEST.read_bytes()),str(compiler_path.relative_to(ROOT)):sha(compiler_path.read_bytes())}
 def record_ref(path,h,report,pointer,context):
  for e in entries:
   if path==e['path'] or path.endswith('/'+e['path']):
    for phase,expected in [('before',e.get('before_sha256')),('after',e['after_sha256'])]:
     if h==expected:refs[e['path']][phase].append({'report':report,'pointer':pointer,'case_context':context})
 def walk(value,report,pointer='',context=None):
  if isinstance(value,dict):
   context=dict(context or {})
   for k in ['case','mode','variant','runtime','source','tree','kind','operation']:
    if isinstance(value.get(k),(str,int)):context[k]=value[k]
   # Only explicit loaded maps or source_path/source_sha256 pairs: not arbitrary metadata hashes.
   for k in ['loaded','loaded_sources']:
    if isinstance(value.get(k),dict):
     for path,h in value[k].items():
      if isinstance(h,str):record_ref(path,h,report,pointer+'/'+k+'/'+path,context)
   if isinstance(value.get('source_path'),str) and isinstance(value.get('source_sha256'),str):record_ref(value['source_path'],value['source_sha256'],report,pointer,context)
   for k,v in value.items():
    if k=='stdout' and isinstance(v,str):
     try:walk(json.loads(v),report,pointer+'/stdout:json',context)
     except (ValueError,TypeError):pass
    elif isinstance(v,(dict,list)):walk(v,report,pointer+'/'+k,context)
  elif isinstance(value,list):
   for i,v in enumerate(value):walk(v,report,pointer+'/'+str(i),context)
 for name in REPORTS:
  p=ROOT/'doc/php83/evidence'/name;assert p.exists(),name
  inputs[str(p.relative_to(ROOT))]=sha(p.read_bytes());walk(load(p),str(p.relative_to(ROOT)))
 curly_path=ROOT/'doc/php83/evidence/curly-offsets/primary-lab.json';curly={r['path']:r for r in load(curly_path)['rows']};inputs[str(curly_path.relative_to(ROOT))]=sha(curly_path.read_bytes())
 rows=[]
 for e in entries:
  cr=by_path[e['path']];assert cr['sha256']==e['after_sha256'] and type(cr['exit']) is int and cr['exit']==0
  r={'path':e['path'],'family':family(e),'upstream_sha256':e.get('before_sha256'),'selected_sha256':e['after_sha256'],'patch':e['source_patch'],'patch_sha256':e['sha256'],'zip_member_hash_verified':True,'compiler83':{'report':str(compiler_path.relative_to(ROOT)),'path':e['path'],'exit':cr['exit']},'retained_loaded_source_hash_matches':refs[e['path']],'behavior_acceptance':False,'proof_gap':'Loaded-source matches locate executed corpus; changed-behavior contract/independent-review attribution must be reconciled, never inferred from load alone.'}
  if e['path'] in curly:
   c=curly[e['path']];assert c['proof']['before_sha256']==e['before_sha256'] and c['proof']['after_sha256']==e['after_sha256'] and c['proof']['all_other_bytes_tokens_identical'] is True
   r['paired_token_proof']={'report':str(curly_path.relative_to(ROOT)),'path':e['path'],'offset_pairs':len(c['proof']['offset_pairs']),'all_other_bytes_tokens_identical':True}
  rows.append(r)
 summary={'targets':76,'families':{},'with_exact_after_loaded_match':sum(bool(r['retained_loaded_source_hash_matches']['after']) for r in rows),'with_exact_upstream_loaded_match':sum(bool(r['retained_loaded_source_hash_matches']['before']) for r in rows),'paired_token_proof_targets':sum('paired_token_proof' in r for r in rows),'compiler83_accepted_targets':76,'semantic_acceptance_rows':0}
 for r in rows:summary['families'][r['family']]=summary['families'].get(r['family'],0)+1
 result={'status':'SOURCE_IDENTITY_AND_EXECUTED_CORPUS_JOIN_NOT_TASK_ACCEPTANCE','artifact_sha256':PIN,'input_sha256':inputs,'join_script_sha256':sha(Path(__file__).read_bytes()),'summary':summary,'rows':rows,'scope':'Only named retained reports searched. No missing-load match proves absence elsewhere. No VM/compiler rerun. Task checkboxes unchanged.'}
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()

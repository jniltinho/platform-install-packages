#!/usr/bin/env python3
"""Repo-local comparison variants, no rank repair and no source execution."""
import argparse,hashlib,json,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
PIN='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
PATHS=['api_v3/lib/KalturaFrontController.php','api_v3/lib/KalturaEntryService.php','api_v3/lib/KalturaBaseService.php','api_v3/services/BaseEntryService.php','api_v3/services/MediaService.php','api_v3/services/MixingService.php','api_v3/lib/KalturaDispatcher.php','alpha/apps/kaltura/lib/requestUtils.class.php','alpha/apps/kaltura/lib/request/infraRequestUtils.class.php','alpha/apps/kaltura/lib/kCurrentContext.class.php','infra/general/kString.class.php']
sha=lambda b:hashlib.sha256(b).hexdigest()
def variants(raw):
 old=b'class KalturaFrontController\n'
 if raw.count(old)!=1:raise ValueError('Exact class declaration required')
 slot=b'\tprivate $disptacher = null;\n'
 if raw.count(slot)!=1:raise ValueError('Exact historical typo required')
 return {'original':raw,'public-comparison':raw.replace(slot,slot+b'\tpublic $dispatcher = null;\n'),'attribute-comparison':raw.replace(old,b'#[\\AllowDynamicProperties]\n'+old)}
def prepare(archive,out):
 out=pathlib.Path(out)
 if out.exists():raise ValueError('Output exists')
 # New preparations are repository-local; never relocate previously denied stages.
 if not out.resolve().is_relative_to(ROOT/'doc/php83/evidence/dispatch-rank'):raise ValueError('New stage must be in owned repository evidence scope')
 if sha(pathlib.Path(archive).read_bytes())!=PIN:raise ValueError('Wrong ZIP')
 with zipfile.ZipFile(archive) as z:files={p:z.read('server-Rigel-18.20.0/'+p) for p in PATHS}
 mp=ROOT/'doc/php83/evidence/exp12-candidate/selected-manifest.json';selected=json.loads(mp.read_bytes());mapped={x['path']:x for x in selected['patches']}
 target=PATHS[0]
 if sha(files[target])!=mapped[target]['after_sha256']:raise ValueError('Selected target mismatch')
 out.mkdir(parents=True)
 ids={}
 for variant,data in variants(files[target]).items():
  p=out/(variant+'.php');p.write_bytes(data);ids[p.name]=sha(data)
 # Preserve complete real classes for review, not extracted replacement methods.
 for p,data in files.items():
  dest=out/'source'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);ids[str(dest.relative_to(out))]=sha(data)
 report={'status':'COMPARISON_ONLY_NO_PATCH_SELECTED','zip_sha256':PIN,'files':ids,'rank_repair_created':False,'variants':['original','public-comparison','attribute-comparison'],'rank_call_shapes':{'BaseEntryService':['entryId',None,'rank'],'MediaService':['entryId','KalturaEntryType::MEDIA_CLIP','rank'],'MixingService':['entryId','KalturaEntryType::MIX','rank']},'limitations':['Three positive graph callers, not dynamic caller completeness.','No PHP/VM execution. Public and attribute are alternatives with explicit different object contracts.']}
 (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zip',required=True);p.add_argument('--output',required=True);a=p.parse_args();print(json.dumps(prepare(a.zip,a.output),indent=2))

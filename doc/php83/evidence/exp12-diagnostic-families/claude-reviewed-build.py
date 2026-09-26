#!/usr/bin/env python3
"""Read-only pinned archive/report classification; never executes source or patches."""
import collections, hashlib, json, pathlib, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[4]
BASE = pathlib.Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
def pinned(p, expected):
    data = pathlib.Path(p).read_bytes()
    if sha(data) != expected: raise ValueError('input hash mismatch: '+str(p))
    return data

def build():
    ap = ROOT/'doc/php83/evidence/exp12-runtime/api-primary.json'
    report = json.loads(ap.read_bytes())
    record = [r for r in report['records'] if r['tree']=='exp12' and r['runtime']=='83']
    if len(record)!=1: raise ValueError('exact exp12 record required')
    groups=record[0]['diagnostics']
    if len(groups)!=17 or sum(r['count'] for r in groups)!=371: raise ValueError('diagnostic denominator drift')
    zp=ROOT.parent/'platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip'
    pin='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
    pinned(zp,pin)
    op=pathlib.Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip')
    opin='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28';pinned(op,opin)
    mp=ROOT/'doc/php83/evidence/exp12-candidate/selected-manifest.json'
    manifest=json.loads(pinned(mp,'593ff6e826978c09704cf89f8cdf099452efdcf74a4c058bc88ee57ca16e74d6'))
    selected={r['path']:r for r in manifest['patches']}
    families={
      'tentative-return-contracts': {'status':'new repair required; existing same-file patches are not this repair','contract':'Preserve exact typed values, errors, PDO transactions/prepared cache, ArrayAccess quirks and exception serialization; native return declarations only after observed values and override compatibility are proved.'},
      'dispatcher-dynamic-property': {'status':'new repair required; selected null-user patch is unrelated','contract':'Preserve public dynamic dispatcher access, singleton dispatch and serialized/reflection shape; adding private dispatcher is not automatically equivalent.'},
      'xml-loader-lifecycle': {'status':'held repair owned by XML worker; do not duplicate','contract':'Security/lifecycle tests, resolver state and external entity rejection; do not merely delete deprecated security call.'},
      'aws-legacy-serialization': {'status':'new repair design required; no backend acceptance','contract':'Legacy C-format import/export, role private fields, expiration refresh and decorators; adding magic methods can change wire format and requires explicit compatibility design.'},
      'rank-required-parameter-order': {'status':'new repair required after caller inventory','contract':'Preserve positional and named arguments, omitted/null entryType, reflection and errors; do not reorder parameters without complete caller evidence.'}}
    rows=[]; sources={}
    with zipfile.ZipFile(zp) as z, zipfile.ZipFile(op) as o:
      paths={r['path'].removeprefix('/audit/app/') for r in groups}
      paths.update(['vendor/aws/Aws/Common/Credentials/CredentialsInterface.php','vendor/aws/Aws/Common/Credentials/AbstractRefreshableCredentials.php'])
      for p in sorted(paths):
        raw=z.read('server-Rigel-18.20.0/'+p); original=o.read('server-Rigel-18.20.0/'+p)
        sourcehash=sha(raw)
        if p in selected and sourcehash!=selected[p]['after_sha256']: raise ValueError('selected hash mismatch')
        if p not in selected and raw!=original: raise ValueError('unselected source drift')
        matching=[]
        for patch in sorted((ROOT/'patches/php83').rglob('*.patch')):
          data=patch.read_bytes()
          if ('+++ b/'+p+'\n').encode() in data:
            matching.append({'path':str(patch.relative_to(ROOT)),'sha256':sha(data),'claim':'same target only; no implied applicability or selection'})
        sources[p]={'original_sha256':sha(original),'exp12_sha256':sourcehash,'selected_patch':selected.get(p),'same_target_patch_files':matching}
      for r in groups:
        p=r['path'].removeprefix('/audit/app/'); line=r['line']; name=p.split('/')[-1]
        if name in ('KalturaPDO.php','PropelPDO.php','PropelConfiguration.php','KalturaAPIException.php'): family='tentative-return-contracts'
        elif name=='kConf.php':family='xml-loader-lifecycle'
        elif name=='KalturaFrontController.php':family='dispatcher-dynamic-property'
        elif name=='KalturaEntryService.php':family='rank-required-parameter-order'
        else:family='aws-legacy-serialization'
        lines=z.read('server-Rigel-18.20.0/'+p).decode().splitlines()
        rows.append(dict(r,source_path=p,source_sha256=sources[p]['exp12_sha256'],family=family,attribution='SOURCE_SUPPORTED_INFERENCE_NOT_RETAINED_NATIVE_MESSAGE',excerpt=[{'line':i+1,'text':lines[i]} for i in range(max(0,line-3),min(len(lines),line+3))]))
    counts=collections.Counter(); events=collections.Counter()
    for r in rows:counts[r['family']]+=1;events[r['family']]+=r['count']
    for k,v in families.items(): v.update(groups=counts[k],events=events[k])
    return {'status':'PLANNING_CLASSIFICATION_NOT_REPAIR_ACCEPTANCE','api_report':str(ap.relative_to(ROOT)),'api_report_sha256':sha(ap.read_bytes()),'exp12_zip_sha256':pin,'original_zip_sha256':opin,'groups':17,'events':371,'native_message_attributions_confirmed':0,'source_supported_inferences':17,'families':families,'sources':sources,'rows':rows,'limits':['Raw KS-bearing API stderr was not retained. Source lines support hypotheses, not recovered exact messages.','No new PHP execution, VM access, patches, package acceptance or caller-completeness claim.','Same-target held patch inventory is not proof of compatibility. Exact selected metadata is retained separately.']}
if __name__=='__main__':
    import sys
    result=json.dumps(build(),indent=2,sort_keys=True)+'\n'
    if '--check' in sys.argv:
        if (BASE/'classification.json').read_text()!=result:raise SystemExit('classification drift')
        print('PASS: 17 groups / 371 events, 11 source identities, exact archive and selection joins')
    else: print(result,end='')

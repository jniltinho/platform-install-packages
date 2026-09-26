#!/usr/bin/env python3
"""Read-only source-pinned composition corpus preparation; never selects a patch."""
import hashlib,importlib.util,io,json,zipfile
from pathlib import Path
import prepare
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
MARKER=HERE.parent/'criteria-marker'/'attribute'
SOURCES={'criteriaFilter.php':'alpha/apps/kaltura/lib/criteriaFilter.class.php','myCriteria.php':'alpha/apps/kaltura/lib/myCriteria.class.php','IKalturaDbQuery.php':'alpha/apps/kaltura/lib/model/objectfilters/IKalturaDbQuery.php','KalturaCriteria.php':'alpha/apps/kaltura/lib/model/objectfilters/KalturaCriteria.php'}
def replace_exact(raw,old,new):
    if raw.count(old)!=1:raise ValueError('Probe adaptation anchor drift')
    return raw.replace(old,new,1)
def build(original,exp11,output):
    if output.exists():raise ValueError('Existing fixture')
    base=prepare.read_pinned(original,prepare.UPSTREAM,prepare.BEFORE)
    prior=prepare.read_pinned(exp11,prepare.EXP11,prepare.PRIOR)
    raw=exp11.read_bytes()
    if prepare.sha(raw)!=prepare.EXP11:raise ValueError('Archive drift')
    pins=json.loads((MARKER/'source-pins.json').read_text())
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files={name:z.read('server-Rigel-18.20.0/'+path) for name,path in SOURCES.items()}
    if any(prepare.sha(data)!=pins[name] for name,data in files.items()):raise ValueError('Dependency drift')
    files.update({'prior.php':prior,'candidate.php':prepare.transform(prior),'legacy.json':b'{}\n'})
    marker=(MARKER/'probe.php').read_bytes()
    returns=(HERE.parent/'criteria-return'/'probe.php').read_bytes()
    # Retain real corpus assertions; restore native warning visibility.
    returns=replace_exact(returns,b'return true;',b'return false;')
    for path,name in [('alpha/apps/kaltura/lib/myCriteria.class.php','myCriteria.php'),('alpha/apps/kaltura/lib/model/objectfilters/IKalturaDbQuery.php','IKalturaDbQuery.php'),('alpha/apps/kaltura/lib/model/objectfilters/KalturaCriteria.php','KalturaCriteria.php')]:
        returns=replace_exact(returns,('/audit/app/'+path).encode(),('/audit/probe/'+name).encode())
    returns=replace_exact(returns,b"['php'=>PHP_VERSION,'rows'",b"['source_sha256'=>['criteria'=>hash_file('sha256',$argv[1])],'variant'=>basename($argv[1],'.php'),'php'=>PHP_VERSION,'rows'")
    files['filter.php']=marker;files['returns.php']=returns
    for name in ['run.sh','verify.py']:files[name]=(HERE/name).read_bytes()
    identities={'status':'PREPARED_COMPOSITION_NATIVE83_ONLY_NOT_SELECTED','upstream_sha256':prepare.UPSTREAM,'exp11_sha256':prepare.EXP11,'files':{n:prepare.sha(d) for n,d in files.items()},'adapted_probes':{'filter_original_sha256':prepare.sha(marker),'returns_original_sha256':prepare.sha((HERE.parent/'criteria-return'/'probe.php').read_bytes())},'strict_cross_engine_layout':'FAIL_RETAINED','cache_acceptance':False}
    output.mkdir(parents=True,exist_ok=False)
    for n,d in files.items():(output/n).write_bytes(d)
    (output/'identities.json').write_text(json.dumps(identities,indent=2)+'\n')
    return identities

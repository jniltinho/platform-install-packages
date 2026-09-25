#!/usr/bin/env python3
"""Prepare a separate unselected class-hierarchy attribute experiment."""
import argparse,hashlib,io,json
from pathlib import Path
import zipfile
HERE=Path(__file__).resolve().parent
ORIGINAL='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
ROOT='server-Rigel-18.20.0/'
SOURCES={'original.php':'vendor/propel/util/Criteria.php','criteriaFilter.php':'alpha/apps/kaltura/lib/criteriaFilter.class.php','myCriteria.php':'alpha/apps/kaltura/lib/myCriteria.class.php','IKalturaDbQuery.php':'alpha/apps/kaltura/lib/model/objectfilters/IKalturaDbQuery.php','KalturaCriteria.php':'alpha/apps/kaltura/lib/model/objectfilters/KalturaCriteria.php'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def attribute(data):
    anchor=b'class Criteria implements IteratorAggregate {'
    if data.count(anchor)!=1 or data.splitlines()[37]!=anchor or b'AllowDynamicProperties' in data:raise ValueError('Unexpected original source')
    return data.replace(anchor,b'#[\\AllowDynamicProperties]\n'+anchor,1)
def build(archive,output,payloads=None):
    if output.exists():raise ValueError('Refuse existing output')
    raw=archive.read_bytes()
    if sha(raw)!=ORIGINAL:raise ValueError('Upstream ZIP drift')
    pins=json.loads((HERE/'source-pins.json').read_text())
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Duplicate ZIP members')
        files={n:z.read(ROOT+p) for n,p in SOURCES.items()}
    if {n:sha(b) for n,b in files.items()}!=pins:raise ValueError('Source drift')
    files['attribute.php']=attribute(files['original.php'])
    for n in ['probe.php','run.sh','verify.py']:files[n]=(HERE/n).read_bytes()
    if payloads is None:payloads={}
    if not isinstance(payloads,dict):raise ValueError('Bad payload map')
    files['legacy.json']=(json.dumps(payloads,sort_keys=True,indent=2)+'\n').encode()
    result={'status':'UNSELECTED_ATTRIBUTE_HIERARCHY_EXPERIMENT','upstream_sha256':ORIGINAL,'original_sources':pins,'files':{n:sha(b) for n,b in files.items()},'patch_selected':False}
    output.mkdir(parents=True,exist_ok=False)
    for n,b in files.items():(output/n).write_bytes(b)
    (output/'identities.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('output',type=Path);a=p.parse_args();print(json.dumps(build(a.archive,a.output),indent=2))

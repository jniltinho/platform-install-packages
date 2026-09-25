#!/usr/bin/env python3
"""Prepare an unselected marker experiment from the pinned original ZIP, no execution."""
import argparse, hashlib, io, json
from pathlib import Path
import zipfile
ORIGINAL = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
ROOT = 'server-Rigel-18.20.0/'
CRITERIA = 'vendor/propel/util/Criteria.php'
FILTER = 'alpha/apps/kaltura/lib/criteriaFilter.class.php'
sha = lambda b: hashlib.sha256(b).hexdigest()
def propose(data):
    anchor=b'class Criteria implements IteratorAggregate {'
    if data.count(anchor)!=1 or b'$creteria_filter_attached' in data: raise ValueError('Unexpected declaration source')
    return data.replace(anchor,anchor+b'\n\tpublic $creteria_filter_attached = null;',1)
def assert_source_lines(sources):
    if sources[CRITERIA].splitlines()[37] != b'class Criteria implements IteratorAggregate {': raise ValueError('Criteria declaration line drift')
    if sources[FILTER].splitlines()[50].strip() != b'$criteria_to_filter->creteria_filter_attached = true;': raise ValueError('Filter marker line drift')
def prepare(archive, output):
    if output.exists(): raise ValueError('Refuse existing output')
    data=archive.read_bytes()
    if sha(data)!=ORIGINAL: raise ValueError('Original ZIP drift')
    pins=json.loads(Path(__file__).with_name('source-pins.json').read_text())
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if len(z.namelist())!=len(set(z.namelist())): raise ValueError('Duplicate members')
        sources={name:z.read(ROOT+name) for name in (CRITERIA,FILTER)}
    if any(sha(sources[k])!=pins[k] for k in sources): raise ValueError('Source hash drift')
    assert_source_lines(sources)
    files={'original.php':sources[CRITERIA],'declaration.php':propose(sources[CRITERIA]),'criteriaFilter.php':sources[FILTER]}
    for name in ('probe.php','run.sh','verify.py'): files[name]=Path(__file__).with_name(name).read_bytes()
    output.mkdir(parents=True,exist_ok=False)
    for name,body in files.items(): (output/name).write_bytes(body)
    result={'status':'UNSELECTED_REPRESENTATION_EXPERIMENT','upstream_sha256':ORIGINAL,'source_hashes':pins,'files':{n:sha(b) for n,b in files.items()},'php_executed':False,'patch_selected':False}
    (output/'identities.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('output',type=Path);a=p.parse_args();print(json.dumps(prepare(a.archive,a.output),indent=2))

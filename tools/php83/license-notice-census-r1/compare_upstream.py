"""Offline byte comparison with two separately fetched official upstream archives."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ORIGINAL_PIN='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
SPECS={
 'geoip2':{'file':'geoip2-b28a0ed.zip','repository':'GeoIP2-php','tag':'v2.4.5','commit':'b28a0ed0190cd76c878ed7002a5d1bb8c5f4c175','archive_sha256':'0ab21a12ed067a3969203b73dd0c45e4d2a7256a2bdc3cc566b08a60b6fc7ec9','local_prefix':'vendor/MaxMind/GeoIP2/','upstream_prefix':'src/','count':30},
 'reader':{'file':'reader-7eeccf6.zip','repository':'MaxMind-DB-Reader-php','tag':'v1.1.3','commit':'7eeccf61b078bb23bb07b1a151a7e5db52871e65','archive_sha256':'6529c8b5956b700a604866904ec7fc9f6a00a2b12da3d0d2383e976907751ccf','local_prefix':'vendor/MaxMind/MaxMind/','upstream_prefix':'src/MaxMind/','count':5}}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def verified(path,pin):
    raw=Path(path).read_bytes()
    if sha(raw)!=pin:raise ValueError('ARCHIVE_PIN')
    return raw

def compare(original,upstream_dir):
    verified(original,ORIGINAL_PIN);result={}
    with zipfile.ZipFile(original) as local:
        for key,spec in SPECS.items():
            path=Path(upstream_dir)/spec['file'];verified(path,spec['archive_sha256'])
            root=spec['repository']+'-'+spec['commit']+'/'
            local_prefix='server-Rigel-18.20.0/'+spec['local_prefix'];rows=[]
            with zipfile.ZipFile(path) as upstream:
                license_bytes=upstream.read(root+'LICENSE')
                if b'Apache License' not in license_bytes[:100] or b'Version 2.0' not in license_bytes[:150]:raise ValueError('LICENSE_DECLARATION')
                for n in sorted(local.namelist()):
                    if not n.startswith(local_prefix) or n.endswith('/'):continue
                    target=spec['upstream_prefix']+n[len(local_prefix):]
                    a=local.read(n);b=upstream.read(root+target)
                    rows.append({'path':n.removeprefix('server-Rigel-18.20.0/'),'upstream_path':target,'local_sha256':sha(a),'upstream_sha256':sha(b),'equal':a==b})
                if len(rows)!=spec['count'] or not all(r['equal'] for r in rows):raise ValueError('SOURCE_DIFFERENCE')
            result[key]={'repository':'https://github.com/maxmind/'+spec['repository'],'observed_tag':spec['tag'],'commit':spec['commit'],'archive_sha256':spec['archive_sha256'],'declared_upstream_license':'Apache-2.0','license_sha256':sha(license_bytes),'license_url':'https://raw.githubusercontent.com/maxmind/'+spec['repository']+'/'+spec['commit']+'/LICENSE','files':rows,'unique_original_version_proven':False,'bundled_license_text_present':False,'release_compliance_approved':False}
    return {'schema':1,'original_archive_sha256':ORIGINAL_PIN,'scope':'35 byte-identical source files joined to official pinned upstream license declarations; no claim of unique original provenance or redistribution compliance.','components':result}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--upstream-dir',required=True);p.add_argument('--output',required=True);a=p.parse_args();report=compare(a.original,a.upstream_dir)
    with Path(a.output).open('x') as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'components':len(report['components']),'matched_files':sum(len(r['files']) for r in report['components'].values()),'sha256':sha(Path(a.output).read_bytes())}))

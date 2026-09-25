"""Synthetic selection validation; no experimental archive build or patch execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec=importlib.util.spec_from_file_location('exp10_stage',Path(__file__).with_name('stage.py'))
stage=importlib.util.module_from_spec(spec);spec.loader.exec_module(stage)
sha=lambda data:hashlib.sha256(data).hexdigest()

class SelectionTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.repo=Path(temporary.name);self.archive=self.repo/'original.zip'
        self.prior={'patches':[]};self.held={'files':[]}
        with zipfile.ZipFile(self.archive,'w') as source:
            for index in range(59):
                path=f'src/file{index:02}.php';data=f'<?php /* original {index} */'.encode()
                source.writestr('server-Rigel-18.20.0/'+path,data)
                patch_path=f'patches/patch{index:02}.patch'
                patch_bytes=f'synthetic non-executed patch identity {index}'.encode()
                file=self.repo/patch_path;file.parent.mkdir(exist_ok=True);file.write_bytes(patch_bytes)
                row={'patch':Path(patch_path).name,'sha256':sha(patch_bytes),'path':path,
                    'before_sha256':sha(data),'after_sha256':sha(b'candidate'+data),'source_patch':patch_path}
                if index<16:self.prior['patches'].append(row)
                else:self.held['files'].append({'patch':patch_path,'patch_sha256':row['sha256'],
                    'path':path,'before_sha256':row['before_sha256'],'after_sha256':row['after_sha256']})
        self.manifest_path=self.repo/'manifest.json';self.write_manifest()
        for name,value in [('REPO',self.repo),('MANIFEST',self.manifest_path),('ORIGINAL',sha(self.archive.read_bytes()))]:
            patched=patch.object(stage,name,value);patched.start();self.addCleanup(patched.stop)

    def write_manifest(self):
        prior_bytes=json.dumps(self.prior).encode();held_bytes=json.dumps(self.held).encode()
        (self.repo/'prior.json').write_bytes(prior_bytes);(self.repo/'held.json').write_bytes(held_bytes)
        expected=list(self.prior['patches'])+[{'patch':Path(r['patch']).name,'sha256':r['patch_sha256'],
            'path':r['path'],'before_sha256':r['before_sha256'],'after_sha256':r['after_sha256'],'source_patch':r['patch']} for r in self.held['files']]
        self.manifest={'revision':'exp10','target_php':'8.3','upstream_root':'server-Rigel-18.20.0',
            'upstream_sha256':sha(self.archive.read_bytes()),'patches':expected,
            'selection_provenance':{'prior_manifest':'prior.json','prior_manifest_sha256':sha(prior_bytes),
                'additional_held_manifest':'held.json','additional_held_manifest_sha256':sha(held_bytes)}}
        self.manifest_path.write_text(json.dumps(self.manifest))

    def test_full16_plus43_inputs(self):
        manifest,patches=stage.validate(self.archive)
        self.assertEqual(len(patches),59)
        self.assertEqual(json.loads(manifest)['patches'][:16],self.prior['patches'])

    def test_cumulative_omission_rejected(self):
        self.manifest['patches'].pop();self.manifest_path.write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError,'Cumulative selection'):stage.validate(self.archive)

    def test_reordering_prior_entries_rejected(self):
        self.manifest['patches'][0],self.manifest['patches'][1]=self.manifest['patches'][1],self.manifest['patches'][0]
        self.manifest_path.write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError,'Cumulative selection'):stage.validate(self.archive)

    def test_source_overlap_rejected(self):
        self.held['files'][0]['path']=self.prior['patches'][0]['path'];self.write_manifest()
        with self.assertRaisesRegex(ValueError,'collision'):stage.validate(self.archive)

    def test_patch_leaf_collision_rejected(self):
        self.held['files'][0]['patch']='other/'+self.prior['patches'][0]['patch'];self.write_manifest()
        with self.assertRaisesRegex(ValueError,'collision'):stage.validate(self.archive)

    def test_patch_byte_drift_rejected(self):
        (self.repo/self.prior['patches'][0]['source_patch']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Patch bytes drift'):stage.validate(self.archive)

    def test_upstream_target_hash_drift_rejected(self):
        self.prior['patches'][0]['before_sha256']='0'*64;self.write_manifest()
        with self.assertRaisesRegex(ValueError,'Original target identity'):stage.validate(self.archive)

    def test_provenance_drift_rejected(self):
        (self.repo/'held.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'Selection provenance drift'):stage.validate(self.archive)

    def test_archive_drift_rejected(self):
        self.archive.write_bytes(b'changed archive')
        with self.assertRaisesRegex(ValueError,'Original archive identity'):stage.validate(self.archive)

    def test_unsafe_patch_source_rejected(self):
        self.prior['patches'][0]['source_patch']='../escape.patch';self.write_manifest()
        with self.assertRaisesRegex(ValueError,'Unsafe input path'):stage.validate(self.archive)

if __name__=='__main__':unittest.main()

"""Synthetic archive/identity negative controls. No dpkg scripts, network or VMs."""
import importlib.util
import io
import hashlib
import json
import subprocess
import tempfile
import zipfile
from contextlib import ExitStack
from unittest.mock import patch
from pathlib import Path
import tarfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('package_builder', HERE / 'build.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OWNER = {'package_file': 'a.deb', 'package_sha256': 'a' * 64}


def archive(entries):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode='w') as tar:
        for path, kind, value in entries:
            item = tarfile.TarInfo(path)
            item.type = kind
            if kind == tarfile.REGTYPE:
                item.size = len(value)
                tar.addfile(item, io.BytesIO(value))
            else:
                item.linkname = value
                tar.addfile(item)
    output.seek(0)
    return output


def regular(path='opt/kaltura/app/a.php', value=b'bytes'):
    return b.payload_inventory(archive([(path, tarfile.REGTYPE, value)]), OWNER)[0]


class PackageIdentityTests(unittest.TestCase):
    def test_php_family_and_case(self):
        for path in ['x.php','x.PHP','x.phtml','x.inc','x.php5']:
            self.assertTrue(b.php_path(path))
        for path in ['x.sh','x.php4','php-script']:
            self.assertFalse(b.php_path(path))

    def test_path_guards(self):
        for path in ['/etc/a.php', './a/../b.php', '../b.php', 'a\\b.php', '']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                b.normalize(path)
        self.assertEqual(b.normalize('./opt/kaltura/app/a.php'), 'opt/kaltura/app/a.php')

    def test_inner_manifest_normalization(self):
        self.assertEqual(b.checksum_manifest('a' * 64 + '  ./a.deb\n'), {'a.deb': 'a' * 64})
        self.assertEqual(b.checksum_manifest('b' * 64 + ' *b.deb\n'), {'b.deb': 'b' * 64})

    def test_duplicate_manifest_path_rejected(self):
        with self.assertRaises(ValueError):
            b.checksum_manifest('a' * 64 + '  ./a.deb\n' + 'b' * 64 + '  a.deb\n')

    def test_invalid_manifests_rejected(self):
        for value in ['', 'nothash  a.deb', 'a' * 64 + '  ../a.deb', 'a' * 64 + '  nested/a.deb', 'a' * 64 + '  a.txt']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                b.checksum_manifest(value)

    def test_regular_payload(self):
        row = regular()
        self.assertEqual(row['type'], 'regular')
        self.assertEqual(row['size'], 5)
        self.assertEqual(row['owners'], [OWNER])

    def test_php_links_and_special_files_rejected(self):
        for kind in [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE, tarfile.DIRTYPE]:
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'Non-regular PHP'):
                b.payload_inventory(archive([('x.php', kind, '../target')]), OWNER)

    def test_payload_traversal_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Traversal'):
            regular('../x.php')

    def test_duplicate_within_package_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate path'):
            b.payload_inventory(archive([('x.php', tarfile.REGTYPE, b'a'),('./x.php',tarfile.REGTYPE,b'a')]),OWNER)

    def test_cross_package_identical_owners_retained(self):
        one = regular(); two = regular()
        two['owners'] = [{'package_file':'b.deb','package_sha256':'b'*64}]
        merged = b.merge_payloads([one,two])
        self.assertEqual(len(merged[one['path']]['owners']),2)

    def test_cross_package_content_conflict_rejected(self):
        with self.assertRaisesRegex(ValueError,'Conflicting package payload'):
            b.merge_payloads([regular(value=b'one'),regular(value=b'two')])

    def test_cross_package_metadata_conflict_rejected(self):
        one=regular(); two=regular(); two['mode']=0o777
        with self.assertRaisesRegex(ValueError,'Conflicting package payload'):
            b.merge_payloads([one,two])

    def test_missing_and_known_hash_join(self):
        row=regular();files={row['path']:row}
        ledger={'files':{'unknown':{'scope':'packaged','path':row['path'],'source_sha256':None},'known':{'scope':'packaged','path':row['path'],'source_sha256':row['sha256']}}}
        joined=b.join_ledger(ledger,files)
        self.assertEqual({r['status'] for r in joined},{'missing_identity_resolved','known_identity_preserved'})

    def test_known_hash_conflict_rejected(self):
        row=regular()
        with self.assertRaisesRegex(ValueError,'Known ledger identity conflict'):
            b.join_ledger({'files':{'known':{'scope':'packaged','path':row['path'],'source_sha256':'0'*64}}},{row['path']:row})

    def test_missing_package_path_rejected(self):
        with self.assertRaisesRegex(ValueError,'Ledger packaged path missing'):
            b.join_ledger({'files':{'unknown':{'scope':'packaged','path':'missing.php','source_sha256':None}}},{})

    def test_exclusions_counted_without_following_links(self):
        counts={}
        records=b.payload_inventory(archive([('a.sh',tarfile.REGTYPE,b'script'),('bin/tool',tarfile.SYMTYPE,'/protected')]),OWNER,counts)
        self.assertEqual(records,[])
        self.assertEqual(counts,{'.sh':1,'(extensionless)':1})

    def test_historical_map_conflict_rejected(self):
        row=regular()
        prior={'unchanged_upstream_php_files':1,'changed_upstream_php_files':[], 'upstream_php_not_at_expected_package_path':[], 'extra_packaged_php_files':0,'extra_path_groups':{}}
        with self.assertRaisesRegex(ValueError,'Published source/package map mismatch'):
            b.reconcile({row['path']:row},{'a.php':'0'*64},prior)

    def test_extra_path_partition_required(self):
        row=regular('opt/kaltura/bin/extra.php')
        prior={'unchanged_upstream_php_files':0,'changed_upstream_php_files':[], 'upstream_php_not_at_expected_package_path':[], 'extra_packaged_php_files':1,'extra_path_groups':{}}
        with self.assertRaisesRegex(ValueError,'exact partition'):
            b.reconcile({row['path']:row},{},prior)



class BuildOrchestrationTests(unittest.TestCase):
    """Pin synthetic archives while mocking only the external dpkg executable."""
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='package-identity-test-')
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.original = self.repo / 'source.zip'
        self.bundle = self.repo / 'bundle.tar.gz'
        self.binary = self.repo / 'mock-dpkg-deb'
        self.binary.write_bytes(b'never executed')
        self.content = {'a.php': b'<?php echo 1;', 'b.phtml': b'<?php echo 2;'}
        with zipfile.ZipFile(self.original, 'w') as z:
            for name, content in self.content.items():
                z.writestr(b.SOURCE_ROOT + name, content)
        self.deb = b'synthetic opaque DEB; decoder is mocked'
        self.deb_sha = hashlib.sha256(self.deb).hexdigest()
        self.write_bundle()
        evidence = self.repo / 'doc/php83/evidence'
        (evidence / 'inventory-ledger').mkdir(parents=True)
        (evidence / 'source-audit').mkdir()
        ledger = {'files': {
            'missing': {'scope':'packaged', 'path':'opt/kaltura/app/a.php', 'source_sha256':None},
            'known': {'scope':'packaged', 'path':'opt/kaltura/app/b.phtml',
                'source_sha256':hashlib.sha256(self.content['b.phtml']).hexdigest()}},
            'summary':{'missing_file_hashes_by_scope':{'packaged':1}}}
        prior = {'unchanged_upstream_php_files':2, 'changed_upstream_php_files':[],
            'upstream_php_not_at_expected_package_path':[], 'extra_packaged_php_files':0,
            'extra_path_groups':{}}
        (evidence / 'inventory-ledger/ledger.json').write_text(json.dumps(ledger))
        (evidence / 'source-audit/source-to-package-map.json').write_text(json.dumps(prior))
        self.payload = archive([('opt/kaltura/app/' + name, tarfile.REGTYPE, content)
            for name, content in self.content.items()]).getvalue()
        self.temp_paths = []

    def write_bundle(self, checksum=None, kind=tarfile.REGTYPE, checksum_name='a.deb'):
        checksum = checksum or self.deb_sha
        with tarfile.open(self.bundle, 'w:gz') as t:
            data = (checksum + '  ' + checksum_name + '\n').encode()
            sums = tarfile.TarInfo('./SHA256SUMS'); sums.size = len(data)
            t.addfile(sums, io.BytesIO(data))
            package = tarfile.TarInfo('./a.deb'); package.type = kind
            if kind == tarfile.REGTYPE:
                package.size = len(self.deb)
                t.addfile(package, io.BytesIO(self.deb))
            else:
                package.linkname = '/must/not/be/followed'
                t.addfile(package)

    def execute(self, *, bundle_sha=None, source_sha=None, dpkg_exit=0):
        def decode(command, *, stdout, stderr, timeout):
            self.assertEqual(command[:2], [str(self.binary), '--fsys-tarfile'])
            self.assertEqual(timeout, 180)
            self.assertEqual(stderr, subprocess.PIPE)
            opaque = Path(command[2])
            self.assertEqual(opaque.read_bytes(), self.deb)
            self.temp_paths.append(opaque.parent)
            if not dpkg_exit:
                stdout.write(self.payload)
            return subprocess.CompletedProcess(command, dpkg_exit, stderr=b'synthetic error' if dpkg_exit else b'')
        with ExitStack() as stack:
            stack.enter_context(patch.object(b, 'BUNDLE_SHA', bundle_sha or b.hash_file(self.bundle)))
            stack.enter_context(patch.object(b, 'SOURCE_SHA', source_sha or b.hash_file(self.original)))
            stack.enter_context(patch.object(b.shutil, 'which', return_value=str(self.binary)))
            version = stack.enter_context(patch.object(b.subprocess, 'check_output', return_value='synthetic dpkg-deb version\n'))
            decoder = stack.enter_context(patch.object(b.subprocess, 'run', side_effect=decode))
            try:
                report = b.build(self.repo, self.bundle, self.original)
            finally:
                self.assertTrue(all(not p.exists() for p in self.temp_paths), 'Private DEB/tar state leaked')
            version.assert_called_once_with([str(self.binary),'--version'], text=True, timeout=15)
            decoder.assert_called_once()
            return report

    def test_successful_synthetic_build_preserves_and_resolves_joins(self):
        report = self.execute()
        self.assertEqual(report['summary']['packages'], 1)
        self.assertEqual(report['summary']['unique_php_paths'], 2)
        self.assertEqual(report['summary']['known_ledger_hashes_preserved'], 1)
        self.assertEqual(report['summary']['missing_ledger_hashes_resolved'], 1)
        self.assertTrue(report['source_differential']['matches_historical_map'])
        self.assertEqual(report['files']['opt/kaltura/app/a.php']['owners'],
            [{'package_file':'a.deb','package_sha256':self.deb_sha}])
        self.assertFalse(report['t0_04_complete'])

    def test_outer_bundle_hash_mismatch(self):
        with self.assertRaisesRegex(ValueError, 'Published bundle hash mismatch'):
            self.execute(bundle_sha='0' * 64)

    def test_inner_checksum_mismatch(self):
        self.write_bundle(checksum='0' * 64)
        with self.assertRaisesRegex(ValueError, 'Inner package hash mismatch'):
            self.execute()

    def test_original_zip_hash_mismatch(self):
        with self.assertRaisesRegex(ValueError, 'Original archive hash mismatch'):
            self.execute(source_sha='0' * 64)

    def test_nonregular_deb_rejected(self):
        self.write_bundle(kind=tarfile.SYMTYPE)
        with self.assertRaisesRegex(ValueError, 'Non-regular DEB member'):
            self.execute()

    def test_checksum_deb_set_mismatch(self):
        self.write_bundle(checksum_name='different.deb')
        with self.assertRaisesRegex(ValueError, 'Checksum/package set mismatch'):
            self.execute()

    def test_dpkg_failure(self):
        with self.assertRaisesRegex(ValueError, 'dpkg-deb payload read failed'):
            self.execute(dpkg_exit=2)


if __name__=='__main__':unittest.main()

"""Synthetic archive/identity negative controls. No dpkg scripts, network or VMs."""
import importlib.util
import io
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

if __name__=='__main__':unittest.main()

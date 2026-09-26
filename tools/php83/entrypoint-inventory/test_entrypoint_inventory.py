"""Synthetic entrypoint-inventory controls. No real archives, no /tmp, no network/VM."""
import hashlib
import importlib.util
import io
import json
import subprocess
import tarfile
import unittest
import zipfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('entrypoint_builder', HERE / 'build.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OWNER = {'package_file': 'a.deb', 'package_sha256': 'a' * 64}

SCOPE = HERE / '.tmp-test-scope'


def tar_bytes(entries):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode='w') as tar:
        for row in entries:
            item = tarfile.TarInfo(row['name'])
            item.size = len(row.get('data', b''))
            item.mode = row.get('mode', 0o644)
            item.mtime = 0
            kind = row.get('kind', 'file')
            if kind == 'dir':
                item.type = tarfile.DIRTYPE
                item.size = 0
                tar.addfile(item)
            elif kind == 'symlink':
                item.type = tarfile.SYMTYPE
                item.linkname = row['linkname']
                item.size = 0
                tar.addfile(item)
            elif kind == 'hardlink':
                item.type = tarfile.LNKTYPE
                item.linkname = row['linkname']
                item.size = 0
                tar.addfile(item)
            else:
                item.type = tarfile.REGTYPE
                tar.addfile(item, io.BytesIO(row.get('data', b'')))
    output.seek(0)
    return output


def stream(data):
    data.seek(0)
    return data


class EntrypointUnitTests(unittest.TestCase):
    def test_path_guards(self):
        for bad in ['/etc/a.php', '../x.php', 'a\\b.php', '', './']:
            if bad == './':
                self.assertEqual(b.normalize(bad), '')
                continue
            with self.subTest(path=bad), self.assertRaises(ValueError):
                b.normalize(bad)
        self.assertEqual(b.normalize('./opt/a.php'), 'opt/a.php')
        self.assertEqual(b.normalize('opt/./a.php'), 'opt/a.php')

    def test_traversal_rejected_in_control_and_data(self):
        with self.assertRaisesRegex(ValueError, 'Traversal'):
            b.parse_control_stream(stream(tar_bytes([{'name': '../postinst', 'data': b'x'}])), OWNER)
        with self.assertRaisesRegex(ValueError, 'Traversal'):
            b.parse_data_stream(stream(tar_bytes([{'name': 'opt/../../x.php', 'data': b'x'}])), OWNER)

    def test_duplicate_rejected(self):
        entries = [{'name': 'postinst', 'data': b'a'}, {'name': './postinst', 'data': b'a'}]
        with self.assertRaisesRegex(ValueError, 'Duplicate control path'):
            b.parse_control_stream(stream(tar_bytes(entries)), OWNER)
        with self.assertRaisesRegex(ValueError, 'Duplicate data path'):
            b.parse_data_stream(stream(tar_bytes(entries)), OWNER)

    def test_links_recorded_never_followed(self):
        entries = [{'name': 'run.php', 'kind': 'symlink', 'linkname': '/etc/passwd'},
                   {'name': 'hard.php', 'kind': 'hardlink', 'linkname': 'run.php'}]
        _, candidates, _, _ = b.parse_data_stream(stream(tar_bytes(entries)), OWNER)
        self.assertEqual(len(candidates), 2)
        self.assertTrue(all(c['candidate_class'] == 'php_link_candidate' for c in candidates))
        self.assertEqual(candidates[0]['linkname'], '/etc/passwd')

    def test_maintainer_scripts_scanned_with_owner_line(self):
        body = b'#!/bin/sh\n/usr/bin/php /opt/kaltura/app/start.php\n'
        records, scripts, invocations, _ = b.parse_control_stream(
            stream(tar_bytes([{'name': './postinst', 'data': body}])), OWNER)
        self.assertEqual([r['path'] for r in scripts], ['postinst'])
        self.assertTrue(records[0]['sha256'])
        self.assertEqual(len(invocations), 1)
        self.assertEqual(invocations[0]['target_class'], 'literal_php')
        self.assertEqual(invocations[0]['line'], 2)
        self.assertEqual(invocations[0]['owners'], [OWNER])

    def test_literal_and_dynamic_interpreter_targets(self):
        body = ('* * * * * root /usr/bin/php /opt/kaltura/app/cron.php\n'
                '0 * * * * root php $APP_DIR/cron.php\n'
                '@reboot root /usr/bin/php8.3 /opt/x/*.php\n')
        _, _, invocations, _ = b.parse_data_stream(
            stream(tar_bytes([{'name': 'etc/cron.d/kaltura',
                               'data': body.encode()}])), OWNER)
        classes = [f['target_class'] for f in invocations]
        self.assertEqual(classes.count('literal_php'), 1)
        self.assertEqual(classes.count('unresolved_dynamic'), 2)

    def test_executable_shebang_extensionless_and_generated_client(self):
        entries = [{'name': 'usr/bin/tool', 'mode': 0o755,
                    'data': b'#!/usr/bin/php\n<?php echo 1;'},
                   {'name': 'opt/kaltura/app/generated/client.php',
                    'data': b'<?php echo 2;'},
                   {'name': 'var/www/app.js', 'data': b'var x = 1;'}]
        excluded = {}
        _, candidates, _, _ = b.parse_data_stream(
            stream(tar_bytes(entries)), OWNER, excluded)
        by_path = {c['path']: c['candidate_class'] for c in candidates}
        self.assertIn('shebang_php', by_path['usr/bin/tool'])
        self.assertIn('extensionless_php_candidate', by_path['usr/bin/tool'])
        self.assertIn('generated_client_candidate',
                      by_path['opt/kaltura/app/generated/client.php'])
        self.assertEqual(excluded.get('.js'), 1)

    def test_denominator_and_exclusion_counts(self):
        entries = [{'name': 'opt/a.php', 'data': b'<?php 1;'},
                   {'name': 'opt/b.txt', 'data': b'text'},
                   {'name': 'opt/bin/run', 'mode': 0o755, 'data': b'#!/bin/sh\necho hi\n'},
                   {'name': 'opt/empty', 'kind': 'dir'},
                   {'name': 'opt/link', 'kind': 'symlink', 'linkname': 'opt/a.php'}]
        excluded = {}
        records, candidates, _, skipped = b.parse_data_stream(
            stream(tar_bytes(entries)), OWNER, excluded)
        self.assertEqual(len(records), 5)
        self.assertEqual(skipped, 0)
        self.assertEqual(excluded.get('.txt'), 1)
        kinds = sorted(r['type'] for r in records)
        self.assertIn('dir', kinds)
        self.assertIn('symlink', kinds)
        self.assertTrue(any('php_family' in c['candidate_class'] for c in candidates))

    def test_oversize_unscanned_counted(self):
        big = b'x' * 16
        with patch.object(b, 'SCAN_SIZE_LIMIT', 4):
            excluded = {}
            _, candidates, _, skipped = b.parse_data_stream(
                stream(tar_bytes([{'name': 'opt/big.php', 'data': big}])), OWNER, excluded)
        self.assertEqual(skipped, 1)
        self.assertEqual(candidates[0]['candidate_class'], 'oversize_unscanned')
        self.assertEqual(excluded.get('oversize_skipped'), 1)

    def test_shell_and_application_template_invocations(self):
        paths = ['opt/kaltura/bin/run.sh', 'opt/kaltura/bin/lib.sh',
                 'opt/kaltura/app/configurations/cron/api']
        for path in paths:
            records, candidates, invocations, _ = b.parse_data_stream(stream(tar_bytes([
                {'name': path, 'data': b'php /opt/a.php\n'}])), OWNER)
            self.assertEqual(len(invocations), 1)
            self.assertEqual(invocations[0]['source_sha256'], records[0]['sha256'])
            self.assertTrue(candidates)
            self.assertEqual(records[0]['scan_disposition'], 'candidate_scanned')

    def test_variable_interpreters_and_nonliteral_targets(self):
        rows = b.scan_php_invocations('$PHP_BIN /opt/x.php\n${PHP} /opt/y.php\n'
                                      'php -f /opt/z.php\nphp install.php', 'script', OWNER)
        self.assertEqual([r['target_class'] for r in rows],
                         ['unresolved_dynamic', 'unresolved_dynamic',
                          'unresolved_option', 'relative_unresolved'])

    def test_nested_shell_variable_interpreter_not_consumed_by_prior_var(self):
        body = 'su $OS_KALTURA_USER -c "nohup $PHP_BIN $BATCHEXE >$LOG 2>&1"'
        rows = b.scan_php_invocations(body, 'etc/init.d/kaltura-batch', OWNER)
        self.assertTrue(any(row['interpreter'] == '$PHP_BIN' and
                            row['target_class'] == 'unresolved_dynamic' for row in rows))
        for body in ['"$PHP" /opt/x.php', '${PHP:-php} /opt/y.php']:
            rows = b.scan_php_invocations(body, 'script', OWNER)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['target_class'], 'unresolved_dynamic')

    def test_executable_binary_not_labeled_php(self):
        _, rows, _, _ = b.parse_data_stream(stream(tar_bytes([
            {'name': 'usr/bin/blob', 'mode': 0o755, 'data': b'\x7fELF'}])), OWNER)
        self.assertEqual(rows[0]['candidate_class'], 'executable')

    def test_control_script_exact_hash_retained(self):
        records, scripts, invocations, _ = b.parse_control_stream(stream(tar_bytes([
            {'name': 'postinst', 'data': b'php /opt/a.php'}])), OWNER)
        self.assertEqual(invocations[0]['source_sha256'], scripts[0]['sha256'])
        self.assertEqual(records[0]['sha256'], scripts[0]['sha256'])

    def test_scratch_must_stay_inside_repo(self):
        with self.assertRaisesRegex(ValueError, 'inside the repository'):
            b._ensure_repo_scratch(HERE.parents[3], '/definitely/outside/repo')


class BuildOrchestrationTests(unittest.TestCase):
    def setUp(self):
        SCOPE.mkdir(parents=True, exist_ok=True)
        self.scope = SCOPE / ('case-' + self._testMethodName)
        if self.scope.exists():
            for child in sorted(self.scope.rglob('*'), reverse=True):
                if child.is_file() or child.is_symlink():
                    child.unlink()
        self.scope.mkdir(parents=True, exist_ok=True)
        self.repo = self.scope / 'repo'
        (self.repo / 'doc/php83/evidence/inventory-ledger').mkdir(parents=True, exist_ok=True)
        (self.repo / 'doc/php83/evidence/source-audit').mkdir(parents=True, exist_ok=True)
        (self.repo / 'doc/php83/evidence/package-identities').mkdir(parents=True, exist_ok=True)
        for name in ('inventory-ledger/ledger.json',
                     'source-audit/source-to-package-map.json',
                     'package-identities/primary.json'):
            (self.repo / 'doc/php83/evidence' / name).write_text('{}')
        self.original = self.scope / 'source.zip'
        self.bundle = self.scope / 'bundle.tar.gz'
        self.binary = self.scope / 'mock-dpkg-deb'
        self.binary.write_bytes(b'never executed')
        with zipfile.ZipFile(self.original, 'w') as archive:
            archive.writestr(b.SOURCE_ROOT + 'a.php', b'<?php 1;')
        self.deb = b'synthetic opaque DEB; decoders are mocked'
        self.deb_sha = hashlib.sha256(self.deb).hexdigest()
        self.ctrl = tar_bytes([{'name': './postinst',
                                'data': b'#!/bin/sh\n/usr/bin/php /opt/kaltura/app/a.php\n'}]).getvalue()
        self.data = tar_bytes(
            [{'name': 'opt/kaltura/app/a.php', 'data': b'<?php 1;'},
             {'name': 'etc/cron.d/kaltura', 'data': b'* * * * * root php $DIR/x.php\n'},
             {'name': 'usr/bin/tool', 'mode': 0o755,
              'data': b'#!/usr/bin/php\n<?php 1;'},
             {'name': 'var/www/note.txt', 'data': b'text'}]).getvalue()
        manifest = (self.deb_sha + '  a.deb\n').encode()
        with tarfile.open(self.bundle, 'w:gz') as tar:
            info = tarfile.TarInfo('./SHA256SUMS')
            info.size = len(manifest)
            tar.addfile(info, io.BytesIO(manifest))
            pkg = tarfile.TarInfo('./a.deb')
            pkg.size = len(self.deb)
            tar.addfile(pkg, io.BytesIO(self.deb))

    def execute(self):
        def fake_run(command, *, stdout, stderr, timeout):
            self.assertEqual(command[0], str(self.binary))
            self.assertEqual(timeout, 180)
            self.assertEqual(stderr, subprocess.PIPE)
            self.assertEqual(Path(command[2]).read_bytes(), self.deb)
            if command[1] == '--ctrl-tarfile':
                stdout.write(self.ctrl)
            elif command[1] == '--fsys-tarfile':
                stdout.write(self.data)
            else:
                raise AssertionError(command[1])
            return subprocess.CompletedProcess(command, 0, stderr=b'')
        with ExitStack() as stack:
            stack.enter_context(patch.object(b, 'BUNDLE_SHA', b.hash_file(self.bundle)))
            stack.enter_context(patch.object(b, 'SOURCE_SHA', b.hash_file(self.original)))
            stack.enter_context(patch.object(b.shutil, 'which', return_value=str(self.binary)))
            stack.enter_context(patch.object(
                b.subprocess, 'check_output', return_value='synthetic dpkg-deb version\n'))
            stack.enter_context(patch.object(b.subprocess, 'run', side_effect=fake_run))
            report = b.build(self.repo, self.bundle, self.original,
                             work_dir=self.repo / 'scratch')
        self.assertFalse((self.repo / 'scratch').exists()
                         and any((self.repo / 'scratch').iterdir()),
                         'Private DEB/tar state leaked')
        return report

    def test_synthetic_build_denominators_and_evidence(self):
        report = self.execute()
        summary = report['summary']
        self.assertEqual(summary['packages'], 1)
        self.assertEqual(summary['control_members_total'], 1)
        self.assertEqual(summary['data_members_total'], 4)
        self.assertEqual(summary['data_regular'], 4)
        self.assertEqual(sum(summary['regular_dispositions'].values()), summary['data_regular'])
        self.assertEqual(summary['php_invocations_literal'], 1)
        self.assertEqual(summary['php_invocations_unresolved'], 1)
        self.assertEqual(summary['excluded_suffix_counts'].get('.txt'), 1)
        self.assertEqual(summary['upstream_php_files'], 1)
        self.assertTrue(report['no_package_hooks_installation_or_vm'])
        self.assertTrue(report['no_runtime_or_reachability_claim'])
        self.assertFalse(report['t0_04_complete'])
        package = report['packages'][0]
        self.assertEqual(package['maintainer_scripts'], ['postinst'])
        invocation = report['php_invocations'][0]
        self.assertIn('owners', invocation)
        self.assertIn('line', invocation)

    def test_inner_hash_mismatch_fail_closed(self):
        with tarfile.open(self.bundle, 'r:gz') as tar:
            names = tar.getnames()
        self.assertIn('./a.deb', names)
        bad = self.scope / 'bad.tar.gz'
        with tarfile.open(self.bundle, 'r:gz') as src, tarfile.open(bad, 'w:gz') as dst:
            for member in src.getmembers():
                stream_in = src.extractfile(member)
                data = stream_in.read() if stream_in else None
                if member.name == './SHA256SUMS':
                    data = ('0' * 64 + '  a.deb\n').encode()
                    member.size = len(data)
                dst.addfile(member, io.BytesIO(data) if data is not None else None)
        with ExitStack() as stack:
            stack.enter_context(patch.object(b, 'BUNDLE_SHA', b.hash_file(bad)))
            stack.enter_context(patch.object(b, 'SOURCE_SHA', b.hash_file(self.original)))
            stack.enter_context(patch.object(b.shutil, 'which', return_value=str(self.binary)))
            stack.enter_context(patch.object(
                b.subprocess, 'check_output', return_value='synthetic dpkg-deb version\n'))
            with self.assertRaisesRegex(ValueError, 'Inner package hash mismatch'):
                b.build(self.repo, bad, self.original, work_dir=self.repo / 'scratch2')


if __name__ == '__main__':
    unittest.main()

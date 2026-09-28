"""Root-only synthetic bridge probe; no application or database invocation."""
import argparse, hashlib, json, os, pathlib, secrets, shutil, subprocess, tempfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bridge', required=True, type=pathlib.Path)
    ap.add_argument('--bridge-sha256', required=True)
    args = ap.parse_args()
    assert os.geteuid() == 0
    assert hashlib.sha256(args.bridge.read_bytes()).hexdigest() == args.bridge_sha256
    base = pathlib.Path('/opt/kaltura')
    made_base = not base.exists()
    if made_base:
        base.mkdir(mode=0o755)
    target_dir = base / '.pilot83-bridge-probe'
    # Never replace a real application file or an earlier probe.
    target_dir.mkdir(mode=0o700)
    private = pathlib.Path(tempfile.mkdtemp(prefix='pilot83-bridge-probe-', dir='/run'))
    cases = []
    try:
        target = target_dir / 'create_playkit_uiconf.php'
        expected = private / 'expected.json'
        values = [str(target), 'Synthetic-private-' + secrets.token_hex(24), '', 'line1\nlinha-ç']
        expected.write_text(json.dumps(values)); expected.chmod(0o600)
        php = '''<?php
$expected = json_decode(file_get_contents(EXPECTED), true);
$cmdline = file_get_contents('/proc/self/cmdline');
$ok = $argv === $expected && $argc === count($expected)
    && $_SERVER['argv'] === $expected && $_SERVER['argc'] === count($expected)
    && $_SERVER['SCRIPT_FILENAME'] === __FILE__ && $_SERVER['PHP_SELF'] === __FILE__
    && strpos($cmdline, $expected[1]) === false && !file_exists(ARGUMENTS);
echo json_encode(['contract_preserved' => $ok, 'secret_absent_exec_argv' => strpos($cmdline, $expected[1]) === false]), "\\n";
exit($ok ? 0 : 90);
'''
        argument_file = private / 'arguments'
        target.write_text(php.replace('EXPECTED', json.dumps(str(expected))).replace('ARGUMENTS', json.dumps(str(argument_file))))
        target.chmod(0o600)
        for name in ['valid', 'file_mode', 'parent_mode', 'symlink', 'missing_nul', 'wrong_basename', 'outside_root', 'valid_repeat']:
            private.chmod(0o700)
            if argument_file.exists() or argument_file.is_symlink(): argument_file.unlink()
            raw = '\0'.join(values).encode() + b'\0'
            if name == 'missing_nul': raw = raw[:-1]
            if name == 'wrong_basename': raw = raw.replace(str(target).encode(), str(expected).encode(), 1)
            if name == 'outside_root': raw = raw.replace(str(target).encode(), b'/etc/passwd', 1)
            argument_file.write_bytes(raw); argument_file.chmod(0o600)
            if name == 'file_mode': argument_file.chmod(0o644)
            if name == 'parent_mode': private.chmod(0o755)
            if name == 'symlink':
                backing = private / 'backing'
                argument_file.rename(backing)
                argument_file.symlink_to(backing)
            p = subprocess.run(['/usr/bin/php8.3', str(args.bridge), str(argument_file)], capture_output=True, timeout=15)
            valid = name.startswith('valid')
            stdout_ok = (json.loads(p.stdout) == {'contract_preserved': True, 'secret_absent_exec_argv': True}) if valid and p.stdout else p.stdout == b'' and not valid
            ok = p.returncode == (0 if valid else 92) and stdout_ok and p.stderr == b''
            cases.append({'case': name, 'exit': p.returncode, 'stdout_contract': stdout_ok, 'stderr_bytes': len(p.stderr), 'passed': ok})
            if not ok: break
    finally:
        private.chmod(0o700)
        shutil.rmtree(private)
        shutil.rmtree(target_dir)
        if made_base: base.rmdir()
    result = {'cases': cases, 'cleanup_complete': not private.exists() and not target_dir.exists(), 'application_invoked': False, 'secret_exported': False}
    print(json.dumps(result, indent=2))
    assert len(cases) == 8 and all(c['passed'] for c in cases) and result['cleanup_complete']

if __name__ == '__main__':
    main()

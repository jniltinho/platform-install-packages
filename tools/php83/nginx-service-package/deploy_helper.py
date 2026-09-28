"""Fresh .83 lab post-render overlay; bundle filled by reviewed local assembler.

No application start here. The original hook's final restart enters the new unit.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile

BUNDLE = None
RENDER_PINS = {'http.conf': '99a84b9bb8d0c38a2be7743fa0caed602e275e86257d49f9a7ba43e3b3c0214d', 'kaltura-nginx.conf': 'a15901610e9e7a2ec3d3ced0a4ad9fbe666fd1716d9fec9ed2f8482b1a2f69c2', 'kaltura.conf': 'c210cb31fc8c6aa4d498fe425a04ebc0432721be423767e8a49ff1c6b418aac9', 'main.conf': '52910b5a2a3412d4150a2eab49540186ea5a8fc6cd9f24694d4eda75c1284913', 'ssl.conf': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'vod-local-nginx.conf': 'abaad9f98b40ab463da18f5361f298b23f4e4745da8c770755319e4a718175b9', 'vod-local.conf': '18c327beec422e6092187b458980f38e8337592790662ce5de4738858b9fb62a', 'vod-remote-nginx.conf': '30407ca8e619e754e894d248bc638c24484d0120884748fcd17a5b3320f8ba85', 'vod-remote.conf': 'dd64e16f31eeae6b4865da6eb41a5ddfa6ee2b65cee62853ff7b875e9f2637c3'}
MODULE_PINS = {'service.py': '1122d48c325e1eda5296f4580d7a3b0da1801db86307ca24d6ccfe816a3a5f51', 'lab_adapter.py': '090c5e8faaf9a0fc468ad31994b2077cc8b50858b3577a0d1c7e327433be1af5', 'sanitizer.py': 'b44f3cdc8c38c6c00a1ef099c0a4742650b3b209e70814924115c1c5f146fffb'}
INIT_PIN = 'fc0b3d8be95aaf701d7ade53a120b585ee5f6f77187d0d90984112e95453ea6c'
UNIT_PIN = 'bfa9c6109abb3fcaaa2e1a825496c0ac9108c271daab75207e811d0ab8725b5e'


def need(value):
    if not value:
        raise ValueError('LAB_OVERLAY_REJECTED')


def write(path, raw, mode=0o644, previous=None):
    path = Path(path)
    if previous is None:
        need(not os.path.lexists(path))
    else:
        need(path.is_file() and not path.is_symlink() and path.read_bytes() == previous)
    fd, tmp = tempfile.mkstemp(prefix='.lab-overlay-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), mode)
            os.fchown(stream.fileno(), 0, 0)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if previous is None:
            os.link(tmp, path, follow_symlinks=False)
        else:
            need(path.read_bytes() == previous)
            os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def decode(encoded, pin):
    raw = base64.b64decode(encoded, validate=True)
    need(hashlib.sha256(raw).hexdigest() == pin)
    return raw


def deploy(bundle):
    need(type(bundle) is dict and set(bundle) == {'old_helper', 'rendered', 'modules', 'init', 'unit'})
    need(type(bundle['rendered']) is dict and set(bundle['rendered']) == set(RENDER_PINS))
    need(type(bundle['modules']) is dict and set(bundle['modules']) == set(MODULE_PINS))
    rendered = {n: decode(v, RENDER_PINS[n]) for n, v in bundle['rendered'].items()}
    modules = {n: decode(v, MODULE_PINS[n]) for n, v in bundle['modules'].items()}
    init_data = decode(bundle['init'], INIT_PIN)
    unit_data = decode(bundle['unit'], UNIT_PIN)
    old = {'__name__': 'frozen_nginx_guard'}
    source = base64.b64decode(bundle['old_helper'], validate=True)
    need(hashlib.sha256(source).hexdigest() == 'f4cd76e8da7b8f3b388217424310ec26d0f52f54f0be9394ea17a533de59a9d6')
    exec(compile(source, '<pinned-old-guard>', 'exec'), old)
    old['context']()
    original = old['templates']()
    expected = old['expected_rendered'](original)
    old['symlinks']()
    old['inventory'](set(old['source_files']()) | set(expected) | {'server.conf'})
    conf = old['CONF']
    for name, raw in expected.items():
        need(old['read'](conf/name) == raw)
    need(set(rendered) == set(expected))
    # Root-exclusive parents verified before creating new lab-only directories.
    roots = ('/usr/local/lib/kaltura-nginx-lab', '/etc/kaltura-nginx-lab',
             '/var/lib/kaltura-php83-nginx-log-sink', '/var/lib/kaltura-php83-nginx-access')
    for path in (*roots, str(conf/'kaltura-nginx.conf'), '/etc/systemd/system/kaltura-nginx.service'):
        for parent in Path(path).parents:
            need(not parent.lstat().st_mode & 0o022)
    for name in roots:
        old['parents'](name)
        old['absent'](name)
    old['parents']('/etc/systemd/system/kaltura-nginx.service')
    for name in roots:
        Path(name).mkdir(mode=0o700)
    for name, raw in rendered.items():
        need(name in expected and '/' not in name)
        write(conf/name, raw, previous=expected[name])
    init = Path('/etc/init.d/kaltura-nginx')
    previous = old['read'](init)
    need(hashlib.sha256(previous).hexdigest() == old['PINS']['etc/init.d/kaltura-nginx'])
    write(init, init_data, mode=0o755, previous=previous)
    for name, raw in modules.items():
        need(name in ('service.py', 'lab_adapter.py', 'sanitizer.py'))
        write(Path(roots[0])/name, raw)
    write('/etc/systemd/system/kaltura-nginx.service', unit_data)
    write('/var/lib/kaltura-php83-nginx-access/access.log', b'', mode=0o600)
    # Pin every concrete config file, not just recursively selected includes.
    files = {}
    for path in conf.iterdir():
        if path.name in ('nginx.conf', 'server.conf'):
            continue
        files[str(path)] = hashlib.sha256(old['read'](path)).hexdigest()
    for name in ('lab_adapter.py', 'sanitizer.py'):
        path = Path(roots[0])/name
        files[str(path)] = hashlib.sha256(old['read'](path)).hexdigest()
    binary = old['BINARY']
    files[str(binary)] = hashlib.sha256(old['read'](binary)).hexdigest()
    manifest = {'schema': 1, 'seconds': 120, 'socket_gid': 7373, 'files': files}
    write('/etc/kaltura-nginx-lab/manifest.json', (json.dumps(manifest, sort_keys=True)+'\n').encode(), mode=0o600)
    old['symlinks']()
    p = subprocess.run(['/usr/bin/systemctl', 'daemon-reload'], capture_output=True,
                       timeout=20, env=old['ENV'])
    need(p.returncode == 0)


if __name__ == '__main__':
    try:
        need(type(BUNDLE) is dict)
        deploy(BUNDLE)
    except BaseException:
        raise SystemExit(92)

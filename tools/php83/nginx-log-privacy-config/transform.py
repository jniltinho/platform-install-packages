"""Pure, pinned lab-template transform; does not install or start nginx.

Requires the separately reviewed guardian: syslog alone does not contain stderr.
Rotation and service integration are deliberately outside this pure transform.
"""
import hashlib
import re

PINS = {
    'main.conf.template': '6fe8a74f49d870911b2c0b9cdaf108eafc587b0d5e229015e35b0d0eb733e600',
    'http.conf.template': '4253af1e939f5f64dd5c6a52c106b2602b012a9afdeb5e3b999152b5068c2df5',
    'nginx.conf.template': 'fc85c42a733c3090ac72bf02c910c89228930acad4965f2087ad2ba5622926a0',
}
ERROR = 'error_log syslog:server=unix:/run/kaltura-php83-nginx-log/error.sock,tag=kaltura_nginx,nohostname error;'
ACCESS = '''map $request_method $privacy_method {
    default OTHER;
    GET GET;
    POST POST;
    HEAD HEAD;
    OPTIONS OPTIONS;
}
log_format main '$status $bytes_sent $request_time $request_length $connection $privacy_method';'''
ACCESS_DEST = 'access_log /var/lib/kaltura-php83-nginx-access/access.log main;'


def replace_once(text, pattern, replacement):
    result, count = re.subn(pattern, lambda _: replacement, text, flags=re.M)
    if count != 1:
        raise ValueError('template structure drift')
    return result


def transform(name, source):
    if name not in PINS or hashlib.sha256(source).hexdigest() != PINS[name]:
        raise ValueError('source identity mismatch')
    text = source.decode('ascii')
    if name in ('main.conf.template', 'nginx.conf.template'):
        text = replace_once(text, r'^error_log[^;]*;', ERROR)
    if name in ('http.conf.template', 'nginx.conf.template'):
        text = replace_once(text, r'^\s*log_format\s+main\s+[^;]*;', '\n' + ACCESS)
        text = replace_once(text, r'^\s*access_log[^;]*;', '\n' + ACCESS_DEST)
    if name == 'nginx.conf.template':
        text = replace_once(text, r'^#user  nobody;', 'user kaltura;')
    return text.encode('ascii')

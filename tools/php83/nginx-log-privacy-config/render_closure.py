"""Pure .83 bounded-lab configuration renderer. Never installs or runs a service."""
import hashlib
import json
from pathlib import Path
from transform import transform

CONF = '/opt/kaltura/nginx/conf'
PINS = json.loads(Path(__file__).with_name('source-pins.json').read_text())
SOCKET = '/run/kaltura-php83-nginx-log/syslog'


def render(source):
    if set(source) != set(PINS):
        raise ValueError('SOURCE_INVENTORY')
    for name, raw in source.items():
        if hashlib.sha256(raw).hexdigest() != PINS[name]:
            raise ValueError('SOURCE_PIN')
    replacements = {
        b'@NGINX_CONF_PATH@': CONF.encode(),
        b'@LOG_DIR@': b'/opt/kaltura/log/nginx',
        b'@PID_FILE_PATH@': b'/opt/kaltura/nginx/logs/nginx.pid',
        b'@VOD_PACKAGER_PORT@': b'88',
        b'@VOD_PACKAGER_HOST@': b'192.168.56.83',
        b'@RTMP_PORT@': b'1935',
    }
    result = {}
    for name, raw in source.items():
        if not name.endswith('.template'):
            continue
        if name == 'ssl.conf.template':
            result['ssl.conf'] = b''
            continue
        if name in ('main.conf.template', 'http.conf.template', 'nginx.conf.template'):
            raw = transform(name, raw)
            raw = raw.replace(b'/run/kaltura-php83-nginx-log/error.sock', SOCKET.encode())
        for old, new in replacements.items():
            raw = raw.replace(old, new)
        if name in ('kaltura-nginx.conf.template', 'kaltura.conf.template'):
            for old, new in {b'@STATIC_FILES_PATH@': b'/opt/kaltura/nginx/static', b'@PROTOCOL@': b'http', b'@WWW_HOST@': b'192.168.56.83'}.items():
                raw = raw.replace(old, new)
        result[name.removesuffix('.template')] = raw
    # Package's public symlink remains nginx.conf -> kaltura-nginx.conf; service
    # uses the concrete config and concrete server include for a regular-file pin.
    result.pop('nginx.conf')
    active = result['kaltura-nginx.conf']
    for old, new in ((b'\t\tlisten 88;', b'\t\tlisten 192.168.56.83:88;'),
                     (b'        listen 1935;', b'        listen 192.168.56.83:1935;'),
                     (b'/server.conf;', b'/kaltura.conf;')):
        if active.count(old) != 1:
            raise ValueError('RENDER_ANCHOR')
        active = active.replace(old, new)
    result['kaltura-nginx.conf'] = b'daemon off;\nmaster_process on;\n' + active
    return result

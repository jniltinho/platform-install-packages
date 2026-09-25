#!/usr/bin/env python3
"""Serial, strict loopback-only client for the original kApcConf web fixture."""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

SOURCE_HASHES = {
    'kApcConf.php': 'b866a78b84862006c5f4fa3a2b4fdeb7b30f5627dedb25d177465c728c7882a0',
    'kBaseConfCache.php': '44c267219c51d2745c78c46ae2793903d542a19f6d8a9982da64580ba8a47f88',
    'kMapCacheInterface.php': '4e6053e9d2266317aab80db1c968333c364acb9a9084e111756ab3928300ff80',
    'kKeyCacheInterface.php': 'a1ee7ae48df49a7c29345f65af05242c4d694863fd762aa6c4ba1a685c832dcc',
}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Redirect prohibited')


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def exact(actual, expected, label):
    # JSON booleans and integers must not compare as equivalent Python values.
    if type(actual) is not type(expected):
        raise ValueError(label + ': type mismatch')
    if isinstance(expected, dict):
        if actual.keys() != expected.keys():
            raise ValueError(label + ': keys mismatch')
        for key in expected:
            exact(actual[key], expected[key], label + '.' + key)
    elif actual != expected:
        raise ValueError(label + ': value mismatch')


def main():
    nonce = os.environ['PHP83_HTTP_NONCE']
    runtime = os.environ['PHP83_EXPECTED_RUNTIME']
    mode = os.environ['PHP83_EXPECTED_MODE']
    expected_ini = os.environ['PHP83_EXPECTED_INI']
    if not re.fullmatch('[a-f0-9]{32}', nonce) or runtime not in ('74', '83') or mode not in ('original', 'aliases'):
        raise ValueError('Invalid client environment')
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    responses = []

    def request(phase, given_nonce=nonce, expected_status=200):
        query = urllib.parse.urlencode({'phase': phase, 'nonce': given_nonce})
        url = 'http://127.0.0.1:18383/probe?' + query
        try:
            response = opener.open(url, timeout=10)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            if response.status != expected_status:
                raise ValueError('Unexpected HTTP status ' + str(response.status) + ': ' + response.read(65536).decode())
            if response.headers.get_content_type() != 'application/json':
                raise ValueError('Response is not JSON')
            raw = response.read(65537)
            if len(raw) > 65536:
                raise ValueError('Response too large')
            value = json.loads(raw, object_pairs_hook=pairs)
        responses.append(value)
        return value

    exact(request('read', '0' * 32 if nonce != '0' * 32 else '1' * 32, 403), {'ok': False, 'error': 'nonce'}, 'bad nonce')
    exact(request('unknown', expected_status=400), {'ok': False, 'error': 'phase'}, 'bad phase')
    version = 'version-1-' + nonce
    new_version = 'version-2-' + nonce
    payload = {'nonce': nonce, 'revision': 1, 'nested': {'enabled': True, 'number': 17}}
    new_payload = dict(payload, revision=2)
    enabled = mode == 'aliases'
    cases = [
        ('store', {'storeKey': True if enabled else None, 'store': enabled}),
        ('read', {'loadKey': version if enabled else None, 'load': payload if enabled else None}),
        ('mismatch', {'load': None}),
        ('read-after-mismatch', {'loadKey': version if enabled else None, 'load': payload if enabled else None}),
        ('delete', {'delete': True if enabled else None}),
        ('miss', {'load': None}),
        ('replace', {'storeKey': True if enabled else None, 'store': enabled}),
        ('read-new', {'loadKey': new_version if enabled else None, 'load': new_payload if enabled else None}),
    ]
    invariant = None
    keys = {'schema', 'ok', 'php', 'sapi', 'apcu_enabled', 'apcu_version', 'source_hashes', 'ini', 'scanned_ini', 'pid', 'nonce', 'phase', 'mode', 'result'}
    for phase, expected in cases:
        value = request(phase)
        if not isinstance(value, dict) or value.keys() != keys:
            raise ValueError('Response schema mismatch')
        for key, expected_value in {'schema': 1, 'ok': True, 'sapi': 'apache2handler', 'apcu_enabled': True,
                                    'nonce': nonce, 'phase': phase, 'mode': mode, 'source_hashes': SOURCE_HASHES}.items():
            exact(value[key], expected_value, key)
        if not isinstance(value['php'], str) or not re.fullmatch((r'7\.4' if runtime == '74' else r'8\.3') + r'\.\d+(?:[-+].*)?', value['php']):
            raise ValueError('Wrong PHP version')
        if type(value['pid']) is not int or value['pid'] <= 0:
            raise ValueError('Invalid Apache PID')
        exact(value['ini'], expected_ini, 'loaded ini')
        exact(value['scanned_ini'], False, 'no scanned ini')
        for key in ('ini', 'apcu_version'):
            if not isinstance(value[key], str) or not value[key]:
                raise ValueError('Missing runtime identity: ' + key)
        current = {key: value[key] for key in ('php', 'sapi', 'apcu_version', 'source_hashes', 'ini', 'scanned_ini', 'nonce', 'mode', 'pid')}
        if invariant is not None:
            exact(current, invariant, 'runtime identity changed')
        invariant = current
        exact(value['result'], expected, phase)
    print(json.dumps({'schema': 1, 'ok': True, 'scope': 'synthetic-kApcConf-serial-web-only',
                      'runtime': runtime, 'mode': mode, 'responses': responses}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        sys.exit(1)

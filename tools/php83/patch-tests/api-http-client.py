#!/usr/bin/env python3
"""Loopback-only HTTP client; no proxies, DNS, redirects, or token output."""
import http.client
import json
import os
import ssl
import time
import urllib.parse


def request(params, method='POST'):
    body = urllib.parse.urlencode(dict(format=1, **params))
    if os.environ.get('PHP83_HTTP_TLS') == '1':
        context = ssl.create_default_context(cafile=os.environ['PHP83_HTTP_CA'])
        connection = http.client.HTTPSConnection('127.0.0.1', 18443, timeout=15, context=context)
    else:
        connection = http.client.HTTPConnection('127.0.0.1', 18383, timeout=15)
    path = '/probe' + ('?' + body if method == 'GET' else '')
    connection.request(method, path, body if method == 'POST' else None,
                       {'Content-Type': 'application/x-www-form-urlencoded'})
    response = connection.getresponse()
    data = response.read(1024 * 1024)
    content_type = response.getheader('Content-Type', '')
    runtime = response.getheader('X-Probe-PHP', '')
    sapi = response.getheader('X-Probe-SAPI', '')
    nonce = response.getheader('X-Probe-Nonce', '')
    connection.close()
    if response.status != 200:
        raise RuntimeError('Unexpected HTTP status: ' + str(response.status))
    expected_runtime = {'74': '7.4.', '83': '8.3.'}.get(os.environ.get('PHP83_EXPECTED_RUNTIME'))
    if not expected_runtime or not runtime.startswith(expected_runtime) or sapi != os.environ.get('PHP83_EXPECTED_SAPI', 'cli-server'):
        raise RuntimeError('Unexpected HTTP runtime/SAPI')
    if os.environ.get('PHP83_HTTP_NONCE') and nonce != os.environ['PHP83_HTTP_NONCE']:
        raise RuntimeError('Unexpected HTTP server nonce')
    if 'json' not in content_type.lower():
        raise RuntimeError('Unexpected content type')
    return json.loads(data)


def main():
    out = []
    for kind, secret in [(0, 'synthetic-user-only'), (2, 'synthetic-admin-only')]:
        token = request(dict(service='session', action='start', partnerId=83001,
                             userId='synthetic-user', type=kind, expiry=60, secret=secret))
        if not isinstance(token, str) or not token:
            raise RuntimeError('Session start did not return a token')
        out.append(['http-session-start', kind, True])
        for method in ['GET', 'POST']:
            info = request(dict(service='session', action='get', ks=token), method)
            if not isinstance(info, dict) or info.get('objectType') != 'KalturaSessionInfo' or info.get('partnerId') != '83001' or info.get('userId') != 'synthetic-user' or info.get('sessionType') != str(kind):
                raise RuntimeError('Session JSON contract mismatch')
            if not isinstance(info.get('expiry'), str) or not info['expiry'].isdigit() or abs(int(info['expiry']) - time.time() - 60) > 15:
                raise RuntimeError('Session expiry contract mismatch')
            out.append(['http-session-get', kind, method, True])
    expired = request(dict(service='session', action='start', partnerId=83001,
                           userId='synthetic-user', type=0, expiry=-60, secret='synthetic-user-only'))
    if not isinstance(expired, str) or not expired:
        raise RuntimeError('Expired fixture creation failed')
    negatives = [
        ('missing', dict(service='session', action='get', partnerId=83001), 'SERVICE_FORBIDDEN'),
        ('malformed', dict(service='session', action='get', ks='not-a-valid-session'), 'INVALID_KS'),
        ('expired', dict(service='session', action='get', ks=expired), 'INVALID_KS'),
        ('wrong-secret', dict(service='session', action='start', partnerId=83001,
                              secret='synthetic-wrong', type=0), 'START_SESSION_ERROR'),
        ('escalation', dict(service='session', action='start', partnerId=83001,
                            secret='synthetic-user-only', type=2), 'START_SESSION_ERROR'),
    ]
    for label, params, code in negatives:
        result = request(params)
        if not isinstance(result, dict) or result.get('objectType') != 'KalturaAPIException' or result.get('code') != code:
            raise RuntimeError('HTTP negative contract mismatch: ' + label)
        if label == 'expired' and 'EXPIRED' not in result.get('message', ''):
            raise RuntimeError('Expired KS rejected for unexpected reason')
        out.append(['http-rejected', label, code])
    print(json.dumps(out))


if __name__ == '__main__':
    main()

"""Fail-closed target boundary for future synthetic lab HTTP workloads."""
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, build_opener, Request

LAB_IPS = frozenset({'192.168.56.74', '192.168.56.83'})
LAB_PORTS = frozenset({80, 443, 88, 8443, 8080})


def validate_target(url, expected_ip):
    """Use literal lab IPs only: no DNS resolution/rebinding or userinfo allowed."""
    if expected_ip not in LAB_IPS:
        raise ValueError('Unknown lab identity')
    parts = urlsplit(url)
    if (parts.scheme not in {'http', 'https'} or parts.hostname != expected_ip
            or parts.username is not None or parts.password is not None
            or parts.fragment or parts.port not in LAB_PORTS | {None}
            or any(c in url for c in '\r\n\t')):
        raise ValueError('Refusing non-lab target')
    return url


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never follow even a same-host redirect implicitly with credentials.
        raise ValueError('Lab client refuses redirects')


def request(url, expected_ip, data=None, headers=None):
    """Return an HTTP response; normal TLS verification remains enabled."""
    validate_target(url, expected_ip)
    # Disable ambient proxies, which could forward credentials to another host.
    from urllib.request import ProxyHandler
    opener = build_opener(ProxyHandler({}), NoRedirects())
    return opener.open(Request(url, data=data, headers=headers or {}), timeout=30)

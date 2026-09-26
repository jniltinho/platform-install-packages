"""Local preparation: bounded, fixed-origin lab HTTP; not full baseline acceptance."""
from dataclasses import dataclass
import hashlib
import ssl
from urllib.parse import urljoin, urlsplit
from urllib.request import (HTTPRedirectHandler, HTTPSHandler, ProxyHandler,
                            Request, build_opener)
from urllib.error import HTTPError, URLError

class BoundaryError(ValueError):
    """Deliberately omit credential-bearing request URLs from error messages."""

@dataclass(frozen=True)
class Origin:
    ip: str
    scheme: str
    port: int

    def __post_init__(self):
        if self.ip not in {'192.168.56.74', '192.168.56.83'}:
            raise BoundaryError('Unknown lab identity')
        if self.scheme not in {'http', 'https'}:
            raise BoundaryError('Unsupported transport')
        if type(self.port) is not int or self.port not in {80, 443, 88, 8443, 8080}:
            raise BoundaryError('Unsupported lab port')

    def validate(self, url):
        # urlsplit strips some controls; reject them BEFORE parsing.
        if not isinstance(url, str) or not url or any(ord(c) <= 32 or ord(c) == 127 for c in url) or '\\' in url:
            raise BoundaryError('Invalid URL characters')
        try:
            p = urlsplit(url)
            port = p.port if p.port is not None else (443 if p.scheme == 'https' else 80)
            if (p.scheme != self.scheme or p.hostname != self.ip or port != self.port
                    or p.username is not None or p.password is not None or p.fragment):
                raise BoundaryError('Refusing non-origin target')
        except ValueError:
            raise BoundaryError('Refusing malformed or non-origin target') from None
        return url

    def resolve(self, parent, reference):
        self.validate(parent)
        if not isinstance(reference, str) or not reference or any(ord(c) <= 32 or ord(c) == 127 for c in reference) or '\\' in reference:
            raise BoundaryError('Invalid nested reference')
        return self.validate(urljoin(parent, reference))

class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise BoundaryError('Redirect refused')

def trusted_context(ca_pem, expected_sha256):
    if not isinstance(ca_pem, bytes) or hashlib.sha256(ca_pem).hexdigest() != expected_sha256:
        raise BoundaryError('Private CA identity mismatch')
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_verify_locations(cadata=ca_pem.decode('ascii'))
    return ctx

def read_bounded(response, limit):
    if type(limit) is not int or not 0 < limit <= 64 * 1024 * 1024:
        raise BoundaryError('Invalid body limit')
    size = response.headers.get('Content-Length')
    if size is not None:
        if not size.isascii() or not size.isdecimal() or int(size) > limit:
            raise BoundaryError('Invalid or excessive declared response length')
    data = response.read(limit + 1)
    if len(data) > limit:
        raise BoundaryError('Response body limit exceeded')
    if size is not None and len(data) != int(size):
        raise BoundaryError('Incomplete response body')
    return data

class Client:
    def __init__(self, origin, ca_pem=None, ca_sha256=None):
        self.origin = origin
        handlers = [ProxyHandler({}), NoRedirects()]
        if origin.scheme == 'https':
            if ca_pem is None or ca_sha256 is None:
                raise BoundaryError('Explicit pinned private CA required')
            handlers.append(HTTPSHandler(context=trusted_context(ca_pem, ca_sha256)))
        elif ca_pem is not None or ca_sha256 is not None:
            raise BoundaryError('Unexpected CA on plaintext transport')
        self.opener = build_opener(*handlers)

    def get(self, url, *, limit=1024 * 1024, timeout=30):
        self.origin.validate(url)
        if type(limit) is not int or not 0 < limit <= 64 * 1024 * 1024:
            raise BoundaryError('Invalid body limit')
        if type(timeout) not in {int, float} or not 0 < timeout <= 30:
            raise BoundaryError('Invalid socket timeout')
        try:
            with self.opener.open(Request(url, method='GET'), timeout=timeout) as response:
                if response.status != 200:
                    raise BoundaryError('Unexpected HTTP status')
                self.origin.validate(response.geturl())
                return read_bounded(response, limit)
        except HTTPError as exc:
            exc.close()
            raise BoundaryError('HTTP request rejected') from None
        except (URLError, OSError):
            raise BoundaryError('Transport request failed') from None

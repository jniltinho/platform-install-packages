import io
import unittest
from unittest.mock import Mock, patch
from guarded_http import Origin, Client, BoundaryError, NoRedirects, read_bounded, trusted_context

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.origin = Origin('192.168.56.74', 'http', 80)
    def test_literal(self):
        self.assertEqual(self.origin.validate('http://192.168.56.74/path?a=1'), 'http://192.168.56.74/path?a=1')
    def test_bad_targets(self):
        urls=['http://192.168.56.20/', 'http://192.168.56.83/', 'http://localhost/',
              'http://192.168.56.74.evil/', 'http://user:secret@192.168.56.74/',
              'http://[::1]/', 'https://192.168.56.74/', 'http://192.168.56.74:8080/',
              'http://192.168.56.74:bad/', 'http://192.168.56.74/#x',
              ' http://192.168.56.74/', '\x00http://192.168.56.74/',
              'http://192.168.56.74/\n', 'http://192.168.56.74/\\x']
        for u in urls:
            with self.subTest(url=u), self.assertRaises(BoundaryError):self.origin.validate(u)
    def test_invalid_origin(self):
        for args in [('192.168.56.20','http',80),('192.168.56.74','file',80),('192.168.56.74','http',True)]:
            with self.assertRaises(BoundaryError):Origin(*args)
    def test_nested_good(self):
        self.assertEqual(self.origin.resolve('http://192.168.56.74/hls/a.m3u8','seg.ts'),'http://192.168.56.74/hls/seg.ts')
    def test_nested_bad(self):
        for ref in ['//192.168.56.20/a', 'https://192.168.56.74/a', '\t//192.168.56.20/a', 'file:///tmp/a']:
            with self.assertRaises(BoundaryError):self.origin.resolve('http://192.168.56.74/a',ref)
    def test_all_redirects_refused(self):
        for code in [301,302,303,307,308]:
            with self.assertRaises(BoundaryError):NoRedirects().redirect_request(None,None,code,'',{},'http://192.168.56.74/')
    def response(self, data, length=None):
        r=io.BytesIO(data);r.headers={} if length is None else {'Content-Length':length};return r
    def test_bounded_body(self):
        self.assertEqual(read_bounded(self.response(b'abc','3'),3), b'abc')
        self.assertEqual(read_bounded(self.response(b'abc'),3), b'abc')
    def test_bad_lengths(self):
        for n in ['4','-1','x','2','9999999999999999999999999999999','３']:
            with self.subTest(n=n), self.assertRaises(BoundaryError):read_bounded(self.response(b'abc',n),3)
        with self.assertRaises(BoundaryError):read_bounded(self.response(b'abcd'),3)
    def test_limit_types(self):
        for n in [True,0,-1,1.5,64*1024*1024+1]:
            with self.assertRaises(BoundaryError):read_bounded(self.response(b''),n)
    def test_ca_must_be_explicit_and_pinned(self):
        with self.assertRaises(BoundaryError):Client(Origin('192.168.56.74','https',443))
        with self.assertRaises(BoundaryError):trusted_context(b'not certificate','wrong')
        with self.assertRaises(BoundaryError):Client(self.origin,b'bad','bad')
    @patch('guarded_http.build_opener')
    def test_rejected_before_connection(self, build):
        client=Client(self.origin)
        with self.assertRaises(BoundaryError):client.get('http://192.168.56.20/?secret=not-real')
        client.opener.open.assert_not_called()
    @patch('guarded_http.build_opener')
    def test_proxy_disabled(self, build):
        Client(self.origin)
        self.assertEqual(build.call_args.args[0].proxies,{})
    @patch('guarded_http.build_opener')
    def test_transport_error_redacted(self, build):
        client=Client(self.origin);client.opener.open.side_effect=OSError('secret-value')
        with self.assertRaises(BoundaryError) as caught:client.get('http://192.168.56.74/?ks=secret-value')
        self.assertNotIn('secret-value',str(caught.exception))

if __name__=='__main__':unittest.main()

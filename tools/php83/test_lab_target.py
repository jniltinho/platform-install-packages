import unittest
from lab_target import NoRedirects, validate_target


class TargetBoundaryTests(unittest.TestCase):
    def test_literal_lab(self):
        for ip in ('192.168.56.74', '192.168.56.83'):
            for scheme in ('http', 'https'):
                url = f'{scheme}://{ip}:8080/api_v3'
                self.assertEqual(validate_target(url, ip), url)

    def test_rejected_before_network(self):
        for url in ('http://192.168.56.20/api_v3', 'http://localhost/',
                    'http://kaltura.local/', 'http://192.168.56.83/',
                    'http://192.168.56.74.evil.example/',
                    'http://user:secret@192.168.56.74/', 'file:///tmp/test',
                    'http://192.168.56.74:22/', 'http://192.168.56.74/#x',
                    'http://192.168.56.74/\n', 'http://192.168.56.74:bad/'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_target(url, '192.168.56.74')

    def test_protected_identity_cannot_be_allowed(self):
        with self.assertRaises(ValueError):
            validate_target('http://192.168.56.20/', '192.168.56.20')

    def test_redirects_never_followed(self):
        with self.assertRaises(ValueError):
            NoRedirects().redirect_request(None, None, 302, '', {},
                                           'http://192.168.56.20/')


if __name__ == '__main__':
    unittest.main()

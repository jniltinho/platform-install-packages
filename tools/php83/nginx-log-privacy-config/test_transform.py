import hashlib
from pathlib import Path
import re
import unittest
from transform import ACCESS_DEST, ERROR, PINS, transform

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'doc/php83/evidence/nginx-r3-privacy/sources/opt/kaltura/nginx/conf'


class TransformTest(unittest.TestCase):
    def test_all_exact_sources(self):
        for name, pin in PINS.items():
            data = (SOURCE / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), pin)
            self.assertNotEqual(data, transform(name, data))

    def test_rejects_drift(self):
        for name in PINS:
            with self.assertRaises(ValueError):
                transform(name, (SOURCE / name).read_bytes() + b'\n')

    def test_rejects_unknown(self):
        with self.assertRaises(ValueError):
            transform('other', b'')

    def test_only_closed_access_fields(self):
        for name in ('http.conf.template', 'nginx.conf.template'):
            result = transform(name, (SOURCE / name).read_bytes()).decode()
            fmt = re.search(r'log_format main ([^;]*);', result).group(1)
            self.assertEqual(re.findall(r'\$\w+', fmt), ['$status', '$bytes_sent', '$request_time', '$request_length', '$connection', '$privacy_method'])
            self.assertEqual(result.count(ACCESS_DEST), 1)
            self.assertIn('default OTHER;', result)

    def test_error_and_fallback_user(self):
        for name in ('main.conf.template', 'nginx.conf.template'):
            result = transform(name, (SOURCE / name).read_bytes()).decode()
            self.assertEqual(result.count(ERROR), 1)
            self.assertNotIn('@LOG_DIR@', result)
            self.assertRegex(result, r'user\s+kaltura;')

    def test_preserves_nonlogging_rtmp_and_http_settings(self):
        name = 'nginx.conf.template'
        source = (SOURCE / name).read_bytes()
        self.assertEqual(source.split(b'# RTMP configuration')[1], transform(name, source).split(b'# RTMP configuration')[1])
        name = 'http.conf.template'
        source = (SOURCE / name).read_bytes()
        self.assertEqual(source.split(b'# general nginx tuning')[1], transform(name, source).split(b'# general nginx tuning')[1])


if __name__ == '__main__':
    unittest.main()

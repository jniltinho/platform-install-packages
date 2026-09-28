from pathlib import Path
import unittest
from render_closure import PINS, render

SOURCE = Path(__file__).resolve().parents[3] / 'doc/php83/evidence/nginx-r3-privacy/sources/opt/kaltura/nginx/conf'

class RenderTests(unittest.TestCase):
    def source(self):
        return {n:(SOURCE/n).read_bytes() for n in PINS}
    def test_exact_active_render(self):
        r=render(self.source()); c=r['kaltura-nginx.conf']
        self.assertTrue(c.startswith(b'daemon off;\nmaster_process on;\n'))
        self.assertIn(b'listen 192.168.56.83:88;',c)
        self.assertIn(b'listen 192.168.56.83:1935;',c)
        self.assertNotIn(b'/server.conf;',c)
        self.assertIn(b'/kaltura.conf;',c)
        self.assertEqual(r['ssl.conf'],b'')
        self.assertIn(b'/run/kaltura-php83-nginx-log/syslog',r['main.conf'])
        self.assertNotIn(b'$request"',r['http.conf'])
    def test_source_drift(self):
        s=self.source();s['main.conf.template']+=b'\n'
        with self.assertRaises(ValueError):render(s)
    def test_unexpected_source(self):
        s=self.source();s['evil.conf']=b''
        with self.assertRaises(ValueError):render(s)
    def test_missing_source(self):
        s=self.source();s.pop('base.conf')
        with self.assertRaises(ValueError):render(s)

if __name__=='__main__':unittest.main()

"""Real loopback transport tests. Test origin injection is private, not public."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import multiprocessing
import os
from pathlib import Path
import signal
import ssl
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch, Mock

import deadline_transport as d
from guarded_http import BoundaryError, Client, Origin

class FixtureOrigin(Origin):
    def __post_init__(self):
        if self.ip != '127.0.0.1' or self.scheme not in {'http', 'https'} or not 0 < self.port < 65536:
            raise ValueError('Invalid isolated fixture')

def fixture_worker(origin_fields, ca, pin, url, limit, timeout, buffer, state):
    try:
        body = Client(FixtureOrigin(*origin_fields), ca, pin).get(url, limit=limit, timeout=timeout)
        memoryview(buffer).cast('B')[:len(body)] = body
        state.value = len(body)
    except Exception:
        state.value = -2

def resistant_worker(ready, buffer, state):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    ready.value = 1
    time.sleep(20)

class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    hits = []
    def log_message(self, *args): pass
    def do_GET(self):
        type(self).hits.append(self.path)
        try:
            if self.path.startswith('/redirect'):
                self.send_response(302)
                self.send_header('Location', '/destination?fixture-secret')
                self.send_header('Content-Length', '0')
                self.end_headers()
            elif self.path.startswith('/unframed'):
                self.send_response(200)
                self.send_header('Connection', 'close')
                self.end_headers()
                self.close_connection = True
                self.wfile.write(b'0123456789')
            elif self.path.startswith('/drip'):
                self.send_response(200)
                self.send_header('Content-Length', '40')
                self.end_headers()
                for _ in range(40):
                    self.wfile.write(b'x'); self.wfile.flush(); time.sleep(.08)
            else:
                body = b'synthetic-response'
                self.send_response(200)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers(); self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, ssl.SSLError): pass

class DeadlineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='baseline-transport-')
        cls.root = Path(cls.temp.name)
        for name in ['trusted', 'wrong']:
            cmd = ['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                   '-days', '1', '-subj', '/CN=synthetic-loopback',
                   '-addext', 'subjectAltName=IP:127.0.0.1',
                   '-keyout', str(cls.root/(name+'.key')),
                   '-out', str(cls.root/(name+'.pem'))]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        cls.ca = (cls.root/'trusted.pem').read_bytes()
        cls.wrong = (cls.root/'wrong.pem').read_bytes()
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def setUp(self):
        self.before = {p.pid for p in multiprocessing.active_children()}
        Handler.hits = []
        self.servers = []
    def tearDown(self):
        for server, thread in self.servers:
            server.shutdown(); server.server_close(); thread.join(2)
            self.assertFalse(thread.is_alive())
        self.assertEqual({p.pid for p in multiprocessing.active_children()}, self.before)
    def server(self, tls=False):
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        server.daemon_threads = True
        if tls:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(str(self.root/'trusted.pem'), str(self.root/'trusted.key'))
            server.socket = ctx.wrap_socket(server.socket, server_side=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start(); self.servers.append((server, thread))
        return FixtureOrigin('127.0.0.1', 'https' if tls else 'http', server.server_port)
    def request(self, origin, path='/', ca=None, deadline=3, limit=100):
        pin = hashlib.sha256(ca).hexdigest() if ca else None
        url = f'{origin.scheme}://{origin.ip}:{origin.port}{path}'
        return d._bounded(fixture_worker, ((origin.ip, origin.scheme, origin.port), ca, pin, url, limit, 1),
                          limit=limit, deadline=deadline)
    def test_http_success_proxy_environment_ignored(self):
        origin = self.server()
        with patch.dict(os.environ, {'http_proxy':'http://127.0.0.1:1', 'HTTP_PROXY':'http://127.0.0.1:1', 'ALL_PROXY':'http://127.0.0.1:1'}):
            self.assertEqual(self.request(origin), b'synthetic-response')
    def test_actual_tls_success(self):
        self.assertEqual(self.request(self.server(True), ca=self.ca), b'synthetic-response')
    def test_actual_wrong_ca_rejected(self):
        with self.assertRaisesRegex(BoundaryError, '^Transport request failed$'):
            self.request(self.server(True), '/?fixture-secret', ca=self.wrong)
    def test_redirect_not_forwarded(self):
        with self.assertRaises(BoundaryError):
            self.request(self.server(), '/redirect?fixture-secret')
        self.assertEqual(Handler.hits, ['/redirect?fixture-secret'])
    def test_slow_drip_total_deadline_and_reap(self):
        origin=self.server(); started=time.monotonic()
        with self.assertRaisesRegex(BoundaryError, '^Total deadline exceeded$'):
            self.request(origin, '/drip', deadline=.7)
        self.assertLess(time.monotonic()-started, 1.8)
        self.assertEqual({p.pid for p in multiprocessing.active_children()}, self.before)
        self.assertEqual(Handler.hits, ['/drip'])
    def test_kill_fallback_reaps_sigterm_resistant_worker(self):
        started=time.monotonic()
        ready=multiprocessing.get_context('spawn').RawValue('i',0)
        with self.assertRaisesRegex(BoundaryError, '^Total deadline exceeded$'):
            d._bounded(resistant_worker, (ready,), limit=10, deadline=.7)
        self.assertEqual(ready.value,1, 'SIGTERM ignore handler must actually be installed')
        self.assertLess(time.monotonic()-started, 1.8)
    def test_real_body_limit(self):
        with self.assertRaises(BoundaryError): self.request(self.server(), limit=3)
    def test_public_entry_rejects_loopback_subclass(self):
        with self.assertRaises(BoundaryError):
            d.get(FixtureOrigin('127.0.0.1','http',80), 'http://127.0.0.1/')
    def test_public_origin_remains_fixed(self):
        with self.assertRaises(BoundaryError): Origin('127.0.0.1','http',80)
    def test_invalid_deadlines(self):
        for value in [True,0,-1,31,float('inf'),float('nan')]:
            with self.subTest(value=value), self.assertRaises(BoundaryError):
                d._bounded(resistant_worker, (), limit=10, deadline=value)
    def test_invalid_limits(self):
        for value in [True,0,-1,64*1024*1024+1]:
            with self.subTest(value=value), self.assertRaises(BoundaryError):
                d._bounded(resistant_worker, (), limit=value, deadline=1)
    def test_real_unframed_body_limit(self):
        with self.assertRaises(BoundaryError): self.request(self.server(), '/unframed', limit=3)
    def test_public_socket_timeout_rejection(self):
        for value in [True, 0, -1, 31, float('nan'), float('inf')]:
            with self.subTest(value=value), self.assertRaises(BoundaryError):
                d.get(Origin('192.168.56.74','http',80), 'http://192.168.56.74/', socket_timeout=value)
    def test_public_cross_origin_rejection(self):
        with self.assertRaises(BoundaryError):
            d.get(Origin('192.168.56.74','http',80), 'http://192.168.56.83/')
    def test_public_ca_pin_rejection(self):
        with self.assertRaises(BoundaryError):
            d.get(Origin('192.168.56.74','https',443), 'https://192.168.56.74/', ca_pem=self.ca, ca_sha256='bad')
    def test_public_plaintext_ca_rejection(self):
        with self.assertRaises(BoundaryError):
            d.get(Origin('192.168.56.74','http',80), 'http://192.168.56.74/', ca_pem=self.ca, ca_sha256=hashlib.sha256(self.ca).hexdigest())
    def test_actual_production_worker_success_private_buffer(self):
        ctx=multiprocessing.get_context('spawn');buffer=ctx.RawArray('B',16);state=ctx.RawValue('q',-1)
        client=Mock();client.get.return_value=b'actual-worker'
        with patch.object(d,'Client',return_value=client):
            d._worker(('192.168.56.74','http',80),None,None,'http://192.168.56.74/',16,1,buffer,state)
        self.assertEqual(state.value,13)
        self.assertEqual(bytes(memoryview(buffer).cast('B')[:state.value]),b'actual-worker')
    def test_actual_production_worker_rejects_invalid_body(self):
        for body in ['not-bytes',b'too-long']:
            ctx=multiprocessing.get_context('spawn');buffer=ctx.RawArray('B',2);state=ctx.RawValue('q',-1)
            client=Mock();client.get.return_value=body
            with patch.object(d,'Client',return_value=client):
                d._worker(('192.168.56.74','http',80),None,None,'http://192.168.56.74/',2,1,buffer,state)
            self.assertEqual(state.value,-2)
    def test_actual_production_worker_origin_reconstructed(self):
        ctx=multiprocessing.get_context('spawn');buffer=ctx.RawArray('B',2);state=ctx.RawValue('q',-1)
        with patch.object(d,'Client') as client:
            d._worker(('127.0.0.1','http',80),None,None,'http://127.0.0.1/',2,1,buffer,state)
        self.assertEqual(state.value,-2);client.assert_not_called()
if __name__=='__main__': unittest.main()

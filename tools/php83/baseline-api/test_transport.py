import base64
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import ssl
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs
import transport as t

class FixtureOrigin(t.Origin):
    def __post_init__(self):
        if self.ip!='127.0.0.1' or not 0<self.port<65536:raise ValueError('Fixture origin')
def fixture_spawn_worker(fields,ca,pin,params,buffer,state):
    try:
        origin=FixtureOrigin(*fields);client=t.Client(origin,ca,pin)
        t._pack_post(client,f'{origin.scheme}://{origin.ip}:{origin.port}{t.API_PATH}',params,buffer,state)
    except Exception:state.value=-2

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        body=self.rfile.read(int(self.headers['Content-Length']))
        self.server.observed.append((self.path,parse_qs(body.decode()),self.command))
        mode=self.server.mode
        if mode=='redirect':
            self.send_response(302);self.send_header('Location','/forward');self.end_headers();return
        self.send_response(200);self.send_header('Content-Type','text/html' if mode=='html' else 'application/json');self.end_headers()
        try:
            if mode=='oversize':self.wfile.write(b'x'*(t.RESPONSE_LIMIT+1))
            else:
                time.sleep(.025);self.wfile.write(b'"synthetic-session-token-123456789"')
        except (BrokenPipeError,ConnectionResetError,ssl.SSLError):pass
class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='baseline-api-tls-');cls.root=Path(cls.temp.name)
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj','/CN=synthetic','-addext','subjectAltName=IP:127.0.0.1','-keyout',str(cls.root/'key'),'-out',str(cls.root/'cert')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=20)
        cls.ca=(cls.root/'cert').read_bytes()
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):self.servers=[]
    def tearDown(self):
        for server,thread in self.servers:
            server.shutdown();server.server_close();thread.join(2);self.assertFalse(thread.is_alive())
    def setup_server(self,tls=False,mode='normal'):
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.daemon_threads=True;server.mode=mode;server.observed=[]
        if tls:
            ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.load_cert_chain(str(self.root/'cert'),str(self.root/'key'));server.socket=ctx.wrap_socket(server.socket,server_side=True)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();self.servers.append((server,thread))
        origin=FixtureOrigin('127.0.0.1','https' if tls else 'http',server.server_port)
        client=t.Client(origin,self.ca if tls else None,hashlib.sha256(self.ca).hexdigest() if tls else None)
        url=f'{origin.scheme}://{origin.ip}:{origin.port}{t.API_PATH}'
        return server,client,url
    def test_real_post_auth_body_not_url(self):
        server,client,url=self.setup_server()
        data,ns=t._post(client,url,{'service':'session','action':'start','secret':'synthetic-private-secret','format':1},2)
        self.assertGreaterEqual(ns,20_000_000);self.assertIsInstance(t.strict_json(data),str)
        self.assertEqual(server.observed[0][0],t.API_PATH);self.assertEqual(server.observed[0][2],'POST')
        self.assertEqual(server.observed[0][1]['secret'],['synthetic-private-secret'])
    def test_real_tls_post(self):
        server,client,url=self.setup_server(True)
        self.assertIsInstance(t.strict_json(t._post(client,url,{'ks':'synthetic-ks'},2)[0]),str)
        self.assertNotIn('synthetic-ks',server.observed[0][0])
    def test_post_redirect_refused_without_forward(self):
        server,client,url=self.setup_server(mode='redirect')
        with self.assertRaises(Exception):t._post(client,url,{'ks':'synthetic-ks'},2)
        self.assertEqual([x[0] for x in server.observed],[t.API_PATH])
    def test_html_even_http200_rejected(self):
        _,client,url=self.setup_server(mode='html')
        with self.assertRaises(t.BoundaryError):t._post(client,url,{},2)
    def test_unframed_oversize(self):
        _,client,url=self.setup_server(mode='oversize')
        with self.assertRaises(t.BoundaryError):t._post(client,url,{},2)
    def test_production_rejects83_and_fixture(self):
        for origin in [t.Origin('192.168.56.83','http',80),FixtureOrigin('127.0.0.1','http',80)]:
            with self.assertRaises(t.BoundaryError):t.PostTransport(origin)
    def test_production_worker_rejects_loopback(self):
        ctx=t.deadline.multiprocessing.get_context('spawn');buf=ctx.RawArray('B',100);state=ctx.RawValue('q',-1)
        with patch.object(t,'Client') as client:
            t._post_worker(('127.0.0.1','http',80),None,None,{},buf,state)
        self.assertEqual(state.value,-2);client.assert_not_called()
    def test_private_envelope_timing_and_decoding(self):
        envelope=json.dumps({'response':base64.b64encode(b'"synthetic-session-token"').decode(),'http_ns':1}).encode()
        with patch.object(t.deadline,'_bounded',return_value=envelope):
            reply=t.PostTransport(t.Origin('192.168.56.74','http',80)).request({'secret':'synthetic-secret'})
        self.assertEqual(reply.child_http_ns,1);self.assertGreaterEqual(reply.parent_ns,1);self.assertNotIn('synthetic-session-token',repr(reply))
    def test_bad_json_envelope_redacted(self):
        with patch.object(t.deadline,'_bounded',return_value=b'synthetic-secret'),self.assertRaises(t.BoundaryError) as caught:
            t.PostTransport(t.Origin('192.168.56.74','http',80)).request({})
        self.assertNotIn('synthetic-secret',str(caught.exception))
    def test_real_spawn_http_envelope_and_timing(self):
        server,client,url=self.setup_server()
        original=t.deadline._bounded
        def bridge(worker,args,**kwargs):
            self.assertIs(worker,t._post_worker)
            fields,ca,pin,params=args
            self.assertEqual(fields[0],'192.168.56.74')
            return original(fixture_spawn_worker,(('127.0.0.1','http',server.server_port),ca,pin,params),**kwargs)
        with patch.object(t.deadline,'_bounded',side_effect=bridge):
            reply=t.PostTransport(t.Origin('192.168.56.74','http',80)).request({'secret':'synthetic-private-secret'})
        self.assertEqual(reply.value,'synthetic-session-token-123456789')
        self.assertGreaterEqual(reply.child_http_ns,20_000_000)
        self.assertGreater(reply.parent_ns,reply.child_http_ns)
        self.assertEqual(server.observed[0][0],t.API_PATH)
    def test_production_worker_success_and83_rejection(self):
        ctx=t.deadline.multiprocessing.get_context('spawn');buf=ctx.RawArray('B',1000);state=ctx.RawValue('q',-1)
        with patch.object(t,'_post',return_value=(b'"synthetic-token"',5)):
            t._post_worker(('192.168.56.74','http',80),None,None,{'secret':'synthetic-secret'},buf,state)
        result=t.strict_json(bytes(memoryview(buf).cast('B')[:state.value]))
        self.assertEqual(result['http_ns'],5)
        self.assertEqual(base64.b64decode(result['response']),b'"synthetic-token"')
        with patch.object(t,'Client') as client:
            t._post_worker(('192.168.56.83','http',80),None,None,{},buf,state)
        self.assertEqual(state.value,-2);client.assert_not_called()
    def test_cleanup_failure_typed_as_fatal(self):
        with patch.object(t.deadline,'_bounded',side_effect=t.BoundaryError('Transport worker cleanup failed')):
            with self.assertRaises(t.WorkerCleanupError):
                t.PostTransport(t.Origin('192.168.56.74','http',80)).request({})
if __name__=='__main__':unittest.main()

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parent / 'patch-tests' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


client = load('api-http-client')
collector = load('collect-api-http')


class HTTPProbeTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict(client.os.environ, {'PHP83_EXPECTED_RUNTIME': '74'})
        patcher.start()
        self.addCleanup(patcher.stop)

    def response(self, status=200, content_type='application/json', body=b'true'):
        response = MagicMock(status=status)
        response.getheader.side_effect = lambda name, default='': {'Content-Type': content_type, 'X-Probe-PHP': '7.4.33', 'X-Probe-SAPI': 'cli-server'}.get(name, default)
        response.read.return_value = body
        return response

    def test_post_uses_only_fixed_loopback(self):
        with patch.object(client.http.client, 'HTTPConnection') as connection:
            connection.return_value.getresponse.return_value = self.response()
            self.assertTrue(client.request({'service': 'session', 'action': 'get'}))
            connection.assert_called_once_with('127.0.0.1', 18383, timeout=15)
            args = connection.return_value.request.call_args.args
            self.assertEqual(args[:2], ('POST', '/probe'))
            self.assertIn('format=1', args[2])
            connection.return_value.close.assert_called_once()

    def test_get_encodes_query(self):
        with patch.object(client.http.client, 'HTTPConnection') as connection:
            connection.return_value.getresponse.return_value = self.response()
            client.request({'ks': 'test +/'}, 'GET')
            args = connection.return_value.request.call_args.args
            self.assertTrue(args[1].startswith('/probe?'))
            self.assertIn('ks=test+%2B%2F', args[1])
            self.assertIsNone(args[2])

    def test_redirect_or_error_rejected_without_following(self):
        for code in (301, 302, 307, 500):
            with patch.object(client.http.client, 'HTTPConnection') as connection:
                connection.return_value.getresponse.return_value = self.response(status=code)
                with self.assertRaisesRegex(RuntimeError, 'HTTP status'):
                    client.request({})
                self.assertEqual(connection.call_count, 1)

    def test_non_json_content_type_rejected(self):
        with patch.object(client.http.client, 'HTTPConnection') as connection:
            connection.return_value.getresponse.return_value = self.response(content_type='text/html')
            with self.assertRaisesRegex(RuntimeError, 'content type'):
                client.request({})

    def test_https_uses_explicit_ca_and_fixed_loopback(self):
        with patch.dict(client.os.environ, {'PHP83_HTTP_TLS': '1', 'PHP83_HTTP_CA': '/private/test-ca.crt'}), \
             patch.object(client.ssl, 'create_default_context') as context, \
             patch.object(client.http.client, 'HTTPSConnection') as connection:
            connection.return_value.getresponse.return_value = self.response()
            self.assertTrue(client.request({}))
            context.assert_called_once_with(cafile='/private/test-ca.crt')
            connection.assert_called_once_with('127.0.0.1', 18443, timeout=15, context=context.return_value)

    def test_wrong_runtime_or_sapi_rejected(self):
        for expectation in [{'PHP83_EXPECTED_RUNTIME': '83'}, {'PHP83_EXPECTED_SAPI': 'apache2handler'}]:
            with patch.dict(client.os.environ, expectation), patch.object(client.http.client, 'HTTPConnection') as connection:
                connection.return_value.getresponse.return_value = self.response()
                with self.assertRaisesRegex(RuntimeError, 'runtime/SAPI'):
                    client.request({})

    def test_missing_tls_ca_fails_closed(self):
        with patch.dict(client.os.environ, {'PHP83_HTTP_TLS': '1'}):
            client.os.environ.pop('PHP83_HTTP_CA', None)
            with self.assertRaises(KeyError):
                client.request({})

    def test_wrong_server_nonce_rejected(self):
        with patch.dict(client.os.environ, {'PHP83_HTTP_NONCE': 'expected-run'}), patch.object(client.http.client, 'HTTPConnection') as connection:
            connection.return_value.getresponse.return_value = self.response()
            with self.assertRaisesRegex(RuntimeError, 'server nonce'):
                client.request({})

    def test_log_formats_record_locations_not_secret_text(self):
        log = '[25-Sep] PHP Deprecated: sensitive text in /audit/app/a.php on line 2\n'
        log += '/audit/app/b.php line 4 - sensitive text\nSQL token\n'
        self.assertEqual(collector.diagnostics(log), [
            dict(severity='ApplicationDiagnostic', path='/audit/app/b.php', line=4, count=1),
            dict(severity='Deprecated', path='/audit/app/a.php', line=2, count=1)])

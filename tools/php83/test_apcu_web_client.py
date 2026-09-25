"""Offline negative checks; mocks do not establish Apache/APCu acceptance."""
import contextlib
import copy
import email.message
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('apcu_web_client', Path(__file__).parent / 'apcu-web/client.py')
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class Response:
    def __init__(self, value, status):
        self.status = status
        self.headers = email.message.Message()
        self.headers['Content-Type'] = 'application/json'
        self.raw = json.dumps(value).encode()
    def read(self, size):
        return self.raw[:size]
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


class ClientTests(unittest.TestCase):
    def setUp(self):
        record = json.loads((ROOT / 'doc/php83/evidence/apcu-web/codex-83-aliases.json').read_text())
        self.responses = copy.deepcopy(record['responses'])
        self.env = {'PHP83_HTTP_NONCE': self.responses[2]['nonce'], 'PHP83_EXPECTED_RUNTIME': '83',
                    'PHP83_EXPECTED_MODE': 'aliases', 'PHP83_EXPECTED_INI': self.responses[2]['ini']}

    def run_client(self):
        responses = [Response(value, 403 if index == 0 else 400 if index == 1 else 200)
                     for index, value in enumerate(self.responses)]
        def opened(url, timeout):
            self.assertTrue(url.startswith('http://127.0.0.1:18383/probe?'))
            self.assertEqual(timeout, 10)
            return responses.pop(0)
        with patch.dict(client.os.environ, self.env, clear=True), patch.object(client.urllib.request, 'build_opener') as build, contextlib.redirect_stdout(io.StringIO()) as out:
            build.return_value.open.side_effect = opened
            client.main()
            self.assertEqual(responses, [])
            self.assertTrue(json.loads(out.getvalue())['ok'])
            handlers = build.call_args.args
            self.assertEqual(handlers[0].proxies, {})
            self.assertIsInstance(handlers[1], client.NoRedirect)

    def test_complete_positive_record(self):
        self.run_client()

    def test_reject_runtime_identity_mutations(self):
        mutations = {'schema': True, 'ok': 1, 'php': '8.4.1', 'sapi': 'cli', 'apcu_enabled': False,
                     'apcu_version': '', 'pid': False, 'nonce': '0'*32, 'ini': '/wrong',
                     'scanned_ini': '', 'source_hashes': {}, 'phase': 'other', 'mode': 'original'}
        for key, value in mutations.items():
            with self.subTest(key=key):
                original = self.responses[2][key]
                self.responses[2][key] = value
                with self.assertRaises(ValueError):
                    self.run_client()
                self.responses[2][key] = original

    def test_reject_pid_change(self):
        self.responses[3]['pid'] += 1
        with self.assertRaises(ValueError): self.run_client()

    def test_reject_missing_persistence(self):
        self.responses[3]['result']['load'] = None
        with self.assertRaises(ValueError): self.run_client()

    def test_reject_boolean_as_integer(self):
        self.responses[3]['result']['load']['nested']['enabled'] = 1
        with self.assertRaises(ValueError): self.run_client()

    def test_reject_added_schema_field(self):
        self.responses[2]['ignored'] = 'not allowed'
        with self.assertRaises(ValueError): self.run_client()

    def test_reject_bad_negative_control(self):
        self.responses[0]['ok'] = True
        with self.assertRaises(ValueError): self.run_client()

    def test_reject_duplicate_json(self):
        with self.assertRaises(ValueError):
            json.loads('{"ok": true, "ok": false}', object_pairs_hook=client.pairs)

    def test_redirect_prohibited(self):
        with self.assertRaises(ValueError):
            client.NoRedirect().redirect_request(None, None, 302, '', {}, 'http://192.168.56.20/')

    def test_invalid_environment(self):
        self.env['PHP83_EXPECTED_RUNTIME'] = '84'
        with self.assertRaises(ValueError): self.run_client()


if __name__ == '__main__':
    unittest.main()

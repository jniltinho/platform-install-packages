import base64
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tools/php83/patch-tests/doc-comment-legacy-cache.json'


class LegacyParserFixtureTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text())

    def test_original_php74_source_identity(self):
        metadata = json.loads((ROOT / 'patches/php83/held/doc-comment-property.json').read_text())
        self.assertTrue(self.fixture['producer_php'].startswith('7.4.'))
        self.assertEqual(self.fixture['source_sha256'], metadata['before_sha256'])
        self.assertEqual(len(self.fixture['entries']), 6)

    def test_payload_identities_and_public_property(self):
        for entry in self.fixture['entries']:
            payload = base64.b64decode(entry['payload_base64'], validate=True)
            self.assertEqual(hashlib.sha256(payload).hexdigest(), entry['sha256'])
            self.assertTrue(payload.startswith(b'O:23:"KalturaDocCommentParser":'))
            self.assertIn(b's:25:"disableRelativeTimeParams";', payload)

    def test_empty_original_comment_already_contains_empty_array(self):
        entry = next(e for e in self.fixture['entries'] if e['comment'] == '/** Empty */')
        self.assertIn(b's:25:"disableRelativeTimeParams";a:0:{}', base64.b64decode(entry['payload_base64']))

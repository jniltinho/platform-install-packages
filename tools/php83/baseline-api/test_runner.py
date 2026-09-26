import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import run
from test_protocol import FIXTURE,CREDS,Fake

class RunnerTests(unittest.TestCase):
    def execute(self,drift=False):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);cred=root/'credentials';fixture=root/'fixture'
            cred.write_text(json.dumps({'partner_id':CREDS.partner_id,'user_id':CREDS.user_id,'secret':CREDS.secret}));cred.chmod(0o600)
            fixture.write_text(json.dumps(FIXTURE));pin=hashlib.sha256(fixture.read_bytes()).hexdigest()
            class Transport(Fake):
                def request(self,params):
                    value=super().request(params)
                    if drift and len(self.calls)==100:fixture.write_text('{}')
                    return value
            args=['run.py','--credentials',str(cred),'--fixture',str(fixture),'--fixture-sha256',pin,'--scheme','http','--port','80','--phase','warmup','--round-index','1']
            output=io.StringIO()
            with patch.object(sys,'argv',args),patch.object(run.socket,'gethostname',return_value='kaltura-php74-baseline'),patch.object(run,'PostTransport',return_value=Transport()),contextlib.redirect_stdout(output):
                code=run.main()
            return code,json.loads(output.getvalue())
    def test_report_identifies_transport_harness_and_preserves_privacy(self):
        code,r=self.execute()
        self.assertEqual(code,0);self.assertEqual(r['scheme'],'http');self.assertEqual(r['port'],80)
        self.assertIsNone(r['ca_sha256']);self.assertTrue(r['harness_unchanged']);self.assertTrue(r['fixture_unchanged'])
        self.assertEqual(len(r['harness_sha256']),5);self.assertIn('+00:00',r['started_at_utc'])
        self.assertNotIn(CREDS.secret,json.dumps(r));self.assertFalse(r['baseline_acceptance'])
    def test_post_identity_drift_retains100_rows_and_fails(self):
        code,r=self.execute(drift=True)
        self.assertEqual(code,1);self.assertFalse(r['functional_round_pass']);self.assertFalse(r['fixture_unchanged'])
        self.assertEqual(len(r['records']),100);self.assertEqual(r['attempted'],100)
if __name__=='__main__':unittest.main()

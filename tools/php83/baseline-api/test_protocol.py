import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from protocol import *
from transport import Reply

FIXTURE={'version':1,'entry':{'objectType':'KalturaMediaEntry','id':'0_abcdefgh','partnerId':'101','status':2,'mediaType':1},'list_total_count':1,'page_size':1,'page_index':1,'order_by':'+createdAt','entry_version':1,'source_media_sha256':'0'*64}
CREDS=Credentials(101,'synthetic-user','synthetic-private-secret')
TOKEN='synthetic-session-token-123456789'
class Fake:
    def __init__(self,fail=None,last_bad=False):self.calls=[];self.fail=fail;self.last_bad=last_bad
    def request(self,params):
        self.calls.append(params)
        if len(self.calls)==self.fail:raise RuntimeError('SECRET:'+CREDS.secret)
        if params['service']=='session':
            value={'objectType':'KalturaAPIException','message':CREDS.secret} if self.last_bad and len(self.calls)==34 else TOKEN
        elif params['action']=='list':
            value={'objectType':'KalturaMediaListResponse','totalCount':1,'objects':[copy.deepcopy(FIXTURE['entry'])]}
        else:value=copy.deepcopy(FIXTURE['entry'])
        return Reply(value,100,200)
class ProtocolTests(unittest.TestCase):
    def test_full_100_and_exact_operation_counts(self):
        t=Fake();r=run_round(t,CREDS,FIXTURE)
        self.assertTrue(r['functional_round_pass']);self.assertEqual(r['planned'],100);self.assertEqual(r['attempted'],100)
        self.assertEqual([x['operation'] for x in r['records']],OPERATIONS)
        self.assertEqual(len(t.calls),100)
        self.assertTrue(all(p.get('type')==0 for p in t.calls[:34]))
        self.assertTrue(all(p.get('ks')==TOKEN for p in t.calls[34:]))
    def test_failed_call_not_removed_from_denominator(self):
        r=run_round(Fake(fail=56),CREDS,FIXTURE)
        self.assertEqual((r['planned'],r['attempted'],r['passed'],r['failed']),(100,100,99,1));self.assertFalse(r['functional_round_pass'])
    def test_last_session_failure_blocks_all_66_with_explicit_rows(self):
        t=Fake(last_bad=True);r=run_round(t,CREDS,FIXTURE)
        self.assertEqual((r['planned'],r['attempted'],r['failed'],r['not_executed']),(100,34,1,66))
        self.assertEqual(len(r['records']),100);self.assertEqual(len(t.calls),34)
    def test_prior_session_failure_still_invalidates_round(self):
        r=run_round(Fake(fail=1),CREDS,FIXTURE)
        self.assertEqual(r['attempted'],100);self.assertFalse(r['functional_round_pass'])
    def test_report_has_no_secret_or_token_or_error_message(self):
        for t in [Fake(),Fake(fail=4),Fake(last_bad=True)]:
            text=json.dumps(run_round(t,CREDS,FIXTURE))
            self.assertNotIn(CREDS.secret,text);self.assertNotIn(TOKEN,text);self.assertNotIn('SECRET:',text)
        self.assertNotIn(CREDS.secret,repr(CREDS));self.assertNotIn(TOKEN,repr(Reply(TOKEN,1,2)))
    def test_immutable_exact_filter_and_pagination(self):
        t=Fake();before=copy.deepcopy(FIXTURE);run_round(t,CREDS,FIXTURE)
        self.assertEqual(FIXTURE,before)
        for p in t.calls[34:67]:
            self.assertEqual(p['filter:idEqual'],FIXTURE['entry']['id'])
            self.assertEqual((p['pager:pageSize'],p['pager:pageIndex'],p['filter:orderBy']),(1,1,'+createdAt'))
    def test_typed_media_not_numeric_coercion(self):
        wrong=copy.deepcopy(FIXTURE['entry']);wrong['partnerId']=101
        with self.assertRaises(ContractError):validate_response('media.get',wrong,FIXTURE)
    def test_api_error_rejected_as_media(self):
        with self.assertRaises(ContractError):validate_response('media.get',{'objectType':'KalturaAPIException','message':CREDS.secret},FIXTURE)
    def test_list_total_count_type_frozen(self):
        with self.assertRaises(ContractError):validate_response('media.list',{'objectType':'KalturaMediaListResponse','totalCount':'1','objects':[FIXTURE['entry']]},FIXTURE)
    def test_false_count_not_integer(self):
        f=copy.deepcopy(FIXTURE);f['list_total_count']=True
        with self.assertRaises(ContractError):validate_fixture(f,101)
    def test_wrong_partner_fixture(self):
        with self.assertRaises(ContractError):validate_fixture(FIXTURE,102)
    def test_status_not_ready(self):
        f=copy.deepcopy(FIXTURE);f['entry']['status']=1
        with self.assertRaises(ContractError):validate_fixture(f,101)
    def test_json_duplicates_and_nan(self):
        for raw in ['{"a":1,"a":2}','{"a":NaN}']:
            with self.assertRaises(ValueError):strict_json(raw)
    def test_bad_token(self):
        for value in ['',False,{'objectType':'KalturaAPIException'},'x'*19,'token with spaces '+'x'*30]:
            with self.assertRaises(ContractError):validate_response('session.start',value,FIXTURE)
    def test_private_file_modes_and_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'credentials.json';p.write_text(json.dumps({'partner_id':101,'user_id':'synthetic-user','secret':CREDS.secret}));p.chmod(0o600)
            self.assertEqual(private_credentials(p),CREDS)
            p.chmod(0o644)
            with self.assertRaises(ContractError):private_credentials(p)
            p.chmod(0o600);link=Path(td)/'link';link.symlink_to(p)
            with self.assertRaises(ContractError):private_credentials(link)
    def test_private_file_errors_redacted(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x';p.write_text(CREDS.secret);p.chmod(0o600)
            with self.assertRaises(ContractError) as caught:private_credentials(p)
            self.assertNotIn(CREDS.secret,str(caught.exception))
    def test_cleanup_failure_aborts_but_preserves100_rows(self):
        class Broken(Fake):
            def request(self,params):
                if len(self.calls)==6:raise WorkerCleanupError('Request worker cleanup failed')
                return super().request(params)
        r=run_round(Broken(),CREDS,FIXTURE)
        self.assertEqual((r['planned'],r['attempted'],r['passed'],r['failed'],r['not_executed']),(100,7,6,1,93))
        self.assertTrue(r['aborted']);self.assertEqual(len(r['records']),100)
        self.assertEqual(r['records'][7]['status'],'NOT_EXECUTED_ABORT')
    def test_fixed_version_not_latest(self):
        t=Fake();run_round(t,CREDS,FIXTURE)
        self.assertTrue(all(p['version']==1 for p in t.calls[67:]))
        f=copy.deepcopy(FIXTURE);f['entry_version']=-1
        with self.assertRaises(ContractError):validate_fixture(f,101)
    def test_media_hash_required(self):
        f=copy.deepcopy(FIXTURE);f['source_media_sha256']='not-a-pin'
        with self.assertRaises(ContractError):validate_fixture(f,101)
    def test_private_hardlink_and_parent_mode(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'credentials';p.write_text(json.dumps({'partner_id':101,'user_id':'synthetic-user','secret':CREDS.secret}));p.chmod(0o600)
            link=Path(td)/'hard';os.link(p,link)
            with self.assertRaises(ContractError):private_credentials(p)
            link.unlink();Path(td).chmod(0o755)
            with self.assertRaises(ContractError):private_credentials(p)
            Path(td).chmod(0o700)
    def test_public_file_symlink_fifo_and_bound(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'plain';p.write_bytes(b'1234');link=Path(td)/'link';link.symlink_to(p)
            for name in [link,p]:
                with self.assertRaises(ContractError):read_file(name,2)
            fifo=Path(td)/'fifo';os.mkfifo(fifo)
            with self.assertRaises(ContractError):read_file(fifo,10)
    def test_timing_boundaries_remain_separate(self):
        r=run_round(Fake(fail=56),CREDS,FIXTURE)
        self.assertEqual(r['records'][0]['parent_overhead_ns'],100)
        self.assertIsNotNone(r['records'][0]['attempt_wall_ns'])
        self.assertIsNone(r['records'][55]['parent_ns'])
        self.assertIsNotNone(r['records'][55]['attempt_wall_ns'])
if __name__=='__main__':unittest.main()

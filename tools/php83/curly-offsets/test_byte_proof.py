import hashlib
import copy
import json
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('verify_bytes',Path(__file__).with_name('verify-bytes.py'))
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
sha=lambda x:hashlib.sha256(x).hexdigest()

def fixture():
    before=b'<?php\n$x=$a{0}; // {comment}\n';after=b'<?php\n$x=$a[0]; // {comment}\n'
    opening=before.index(b'{');closing=before.index(b'}')
    point=lambda i,a,b:{'offset':i,'line':2,'column':i-before.rfind(b'\n',0,i),'before':a,'after':b}
    proof={'before_sha256':sha(before),'after_sha256':sha(after),'offset_pairs':[{'open':point(opening,'{','['),'close':point(closing,'}',']')}], 'changed_bytes':2,'all_other_bytes_tokens_identical':True}
    return before,after,proof

class ByteProofTests(unittest.TestCase):
    def test_exact_substitution(self):
        self.assertEqual(v.verify(*fixture()),2)
    def test_extra_comment_change_rejected(self):
        before,after,p=fixture();after=after.replace(b'comment',b'COMMENT');p['after_sha256']=sha(after)
        with self.assertRaisesRegex(ValueError,'Unexpected non-offset'):v.verify(before,after,p)
    def test_missing_pair_rejected(self):
        before,after,p=fixture();p['offset_pairs']=[]
        with self.assertRaises(ValueError):v.verify(before,after,p)
    def test_duplicate_offsets_rejected(self):
        before,after,p=fixture();p['offset_pairs']*=2
        with self.assertRaises(ValueError):v.verify(before,after,p)
    def test_reversed_offsets_rejected(self):
        before,after,p=fixture();pair=p['offset_pairs'][0];pair['open']['offset'],pair['close']['offset']=pair['close']['offset'],pair['open']['offset']
        with self.assertRaises(ValueError):v.verify(before,after,p)
    def test_boolean_offset_rejected(self):
        before,after,p=fixture();p['offset_pairs'][0]['open']['offset']=True
        with self.assertRaises(ValueError):v.verify(before,after,p)
    def test_bad_location_rejected(self):
        before,after,p=fixture();p['offset_pairs'][0]['open']['line']=1
        with self.assertRaises(ValueError):v.verify(before,after,p)
    def test_extra_whitespace_rejected(self):
        before,after,p=fixture()
        with self.assertRaises(ValueError):v.verify(before,after+b' ',p)
    def test_wrong_hash_rejected(self):
        before,after,p=fixture();p['before_sha256']='0'*64
        with self.assertRaises(ValueError):v.verify(before,after,p)
    def test_missing_native_proof_rejected(self):
        before,after,p=fixture();p['all_other_bytes_tokens_identical']=False
        with self.assertRaises(ValueError):v.verify(before,after,p)



class ReportPolicyTests(unittest.TestCase):
    def setUp(self):
        repo=Path(__file__).resolve().parents[3]
        self.report=json.loads((repo/'doc/php83/evidence/curly-offsets/primary-lab.json').read_text())
    def test_actual_report_accepted(self):
        v.validate_report(self.report)
    def test_exit_types_and_failure_status_rejected(self):
        for field in ['scan_before_exit','fix_exit','scan_after_exit']:
            for value in [False,True,0.0,1.0,124,-9,'0',None]:
                with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                    v.validate_report({**self.report,field:value})
    def test_identity_maps_and_claim_rejected(self):
        for value in [1,'true',False,None]:
            with self.assertRaises(ValueError):v.validate_report({**self.report,'analyzer_unchanged':value})
        for value in [{},[],None,{'composer.lock':'wrong'}]:
            with self.assertRaises(ValueError):v.validate_report({**self.report,'analyzer_before':value,'analyzer_after':value})
    def test_policy_drift_rejected(self):
        for field in ['phpcbf_version','sniff','testVersion']:
            with self.assertRaises(ValueError):v.validate_report({**self.report,field:'wrong'})
    def test_targeted_totals_strict(self):
        for value in [False,0.0,1,None]:
            with self.assertRaises(ValueError):v.validate_report({**self.report,'scan_after_totals':{'errors':value,'warnings':0,'fixable':0}})

if __name__=='__main__':unittest.main()

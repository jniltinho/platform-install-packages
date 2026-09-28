import unittest,ast
import thumb_ks_reason as k
OK=lambda rows:None
def raw(entry='1\t0\t0\t0\t0',acl='1\t1\t1\t1',perm=''):
 return ('IDENTITY\th\n'+'ENTRY\t'+entry+'\nACL\t'+acl+'\n'+perm).encode()
class T(unittest.TestCase):
 def test_guest_code_compiles_without_main(self):
  c=k.guest_code().replace('def parse(raw,identity):','def reason_parse(raw,identity):',1);ast.parse(c)
  self.assertNotIn("raise SystemExit(main())",c);self.assertIn('START TRANSACTION READ ONLY',c);self.assertNotRegex(k.SQL,r'(?i)\b(insert|update|delete|replace|alter|drop|create)\b')
 def test_acl_rules_make_ks_needed(self):
  v=k.parse(raw(),OK);self.assertTrue(v['access_control_rules_nonempty']);self.assertTrue(v['derived_ks_needed'])
 def test_plain_entry_no_ks(self):
  v=k.parse(raw(acl='1\t1\t0\t1'),OK);self.assertFalse(v['derived_secured_entry']);self.assertFalse(v['derived_ks_needed'])
 def test_entitlement(self):
  v=k.parse(raw(acl='1\t1\t0\t1',perm='PERM\t102\t1\t1\n'),OK);self.assertTrue(v['feature_entitlement_active_status1']);self.assertTrue(v['derived_ks_needed'])
 def test_rejects(self):
  for r in [raw(entry='2\t0\t0\t0\t0'),raw(acl='1\t1\tx\t1'),raw(perm='PERM\t5\t1\t1\n'),raw()+b'OTHER\t1\n']:self.assertRaises(k.Rejected,k.parse,r,OK)
if __name__=='__main__':unittest.main()

import ast,pathlib,unittest
from unittest import mock
import profile_socket as p
class ProfileTests(unittest.TestCase):
 def good(self):return ('IDENTITY\tkaltura-php74-baseline\t/run/mysqld/mysqld.sock\t/var/lib/mysql/\troot@localhost\tkaltura\nENTRY\t0_wzmt2sfy\t102\t14\nPROFILE\t14\t102\t2\t1\t1\nFLAVOR\t14\t0\nFLAVOR\t14\t1\n').encode()
 def test_positive_scoped(self):
  v=p.parse(self.good());self.assertEqual(v['configured_flavor_ids'],[0,1]);self.assertEqual(v['select_count'],5);self.assertFalse(v['api_authorization_verified'])
 def test_target_db_identity(self):
  for old,new in [(b'kaltura-php74-baseline',b'kaltura-php83'),(b'/var/lib/mysql/',b'/tmp/db/'),(b'root@localhost',b'root@remote'),(b'\tkaltura\n',b'\tother\n')]:self.assertRaises(Exception,p.parse,self.good().replace(old,new))
 def test_known_socket_alias(self):self.assertTrue(p.parse(self.good().replace(b'/run/mysqld/',b'/var/run/mysqld/'))['db_identity_verified'])
 def test_relation_cardinality_overflow_and_owner(self):
  for raw in [self.good()+b'PROFILE\t14\t102\t2\t1\t1\n',self.good().replace(b'PROFILE\t14\t102',b'PROFILE\t14\t999'),self.good()+b'FLAVOR\t14\t1\n',self.good()+b'FLAVOR\t14\t2\n'*130]:self.assertRaises(Exception,p.parse,raw)
 def test_empty_configuration_is_explicit(self):
  raw=self.good().split(b'FLAVOR')[0];self.assertEqual(p.parse(raw)['configured_flavor_ids'],[])
 def test_arbitrary_text_rejected(self):
  self.assertRaises(Exception,p.parse,self.good().replace(b'PROFILE\t14\t102\t2',b'PROFILE\t14\t102\tSYNTHETIC_SECRET'))
 def test_sql_fixed_and_no_modification(self):
  self.assertIn('START TRANSACTION READ ONLY',p.SQL);self.assertIn('max_statement_time=3',p.SQL)
  for word in ('UPDATE ','INSERT ','DELETE ','GRANT ','CALL '):self.assertNotIn(word,p.SQL)
  self.assertEqual(p.SQL.count('SELECT '),4);self.assertIn('LIMIT 129',p.SQL)
 def test_identity_before_relation_query(self):
  with mock.patch.object(p,'guard'),mock.patch.object(p,'secret_read',return_value='a'*48),mock.patch.object(p,'query',return_value=b'IDENTITY\tWRONG\t/run/mysqld/mysqld.sock\t/var/lib/mysql/\troot@localhost\tkaltura\n') as query,mock.patch('builtins.print') as output:
   self.assertEqual(p.main(),2);self.assertEqual(query.call_count,1);self.assertNotIn('a'*48,str(output.call_args))
if __name__=='__main__':unittest.main()

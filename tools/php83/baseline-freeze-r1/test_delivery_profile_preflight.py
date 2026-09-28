import unittest
import delivery_profile_preflight as m
class Tests(unittest.TestCase):
 def row(self):return ['1001','0','61','0','1','0','NULL','applehttp','1','1','0','1','1','0','1','0','0','34']
 def raw(self,row=None):return ('IDENTITY\thost\nPROFILE\t'+'\t'.join(self.row() if row is None else row)+'\n').encode()
 def identity(self,rows):self.assertEqual(rows,[['host']])
 def test_positive(self):
  r=m.parse(self.raw(),self.identity);self.assertFalse(r['mutation_ready']);self.assertEqual(r['opaque_fields']['custom_data'],{'is_null':False,'byte_length':34});self.assertIsNone(r['priority'])
 def test_nullable_parent_priority_host(self):
  row=self.row();row[5]='NULL';row[6]='-1';row[10]='1';row[11]='NULL'
  r=m.parse(self.raw(row),self.identity);self.assertIsNone(r['parent_id']);self.assertEqual(r['priority'],-1);self.assertIsNone(r['host_name_owned'])
 def test_wrong_identity_or_cardinality(self):
  for i in range(5):
   row=self.row();row[i]='99'
   with self.assertRaises(m.Rejected):m.parse(self.raw(row),self.identity)
  with self.assertRaises(m.Rejected):m.parse(self.raw()+b'PROFILE\tx\n',self.identity)
 def test_opaque_values_not_exported(self):
  row=self.row();row[13]='SYNTHETIC_SECRET'
  with self.assertRaises(m.Rejected):m.parse(self.raw(row),self.identity)
  self.assertNotIn('SYNTHETIC_SECRET',str(m.parse(self.raw(),self.identity)))
 def test_invalid_null_length_and_flags(self):
  for i,v in ((13,'1'),(15,'-1'),(17,'1048577'),(8,'true'),(11,'NULL'),(5,'00')):
   row=self.row();row[i]=v
   with self.assertRaises(m.Rejected):m.parse(self.raw(row),self.identity)
 def test_fixed_queries(self):
  self.assertEqual(m.SQL.count('SELECT '),2);self.assertIn('WHERE id=1001 LIMIT 2',m.SQL);self.assertIn('START TRANSACTION READ ONLY',m.SQL)
  for s in ('HEX(', 'SELECT *', 'UPDATE ', 'INSERT ', 'DELETE '):self.assertNotIn(s,m.SQL)
if __name__=='__main__':unittest.main()

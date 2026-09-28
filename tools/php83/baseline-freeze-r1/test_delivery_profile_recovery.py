import unittest,json
import delivery_profile_recovery as m
class Tests(unittest.TestCase):
 def before(self):
  r=dict.fromkeys(m.COLUMNS);r.update(id='1001',type='61',created_at='2026-01-01 00:00:00',updated_at='2026-01-01 00:00:00',partner_id='0',name='SYNTHETIC_PRIVATE_NAME',url='192.168.56.74:88/hls',host_name='192.168.56.74',is_default='1',parent_id='0',status='0',streamer_type='applehttp',priority='0');return r
 def raw(self,*rows):return ('IDENTITY\thost\n'+''.join('ROW\t'+'\t'.join('N' if r[k] is None else 'H'+r[k].encode().hex().upper() for k in m.COLUMNS)+'\n' for r in rows)).encode()
 def identity(self,r):self.assertEqual(r,[['host']])
 def test_unchanged(self):
  b=self.before();r=m.compare(self.raw(b),b,self.identity);self.assertEqual(r['original_relation'],'EXACT_BACKUP');self.assertEqual(r['matching_https_clone_ids'],[])
 def test_autocommit_split(self):
  b=self.before();old=dict(b,media_protocols='http');new=dict(b,id='2001',media_protocols='https',url='192.168.56.74:8444/hls');r=m.compare(self.raw(old,new),b,self.identity);self.assertEqual(r['original_relation'],'EXPECTED_HTTP_DELTA');self.assertEqual(r['matching_https_clone_ids'],[2001]);self.assertNotIn('SYNTHETIC_PRIVATE_NAME',json.dumps(r));self.assertFalse(r['retry_authorized'])
 def test_partial_unexpected_and_duplicate(self):
  b=self.before();new=dict(b,id='2001',media_protocols='https',url='192.168.56.74:8444/hls');r=m.compare(self.raw(b,new),b,self.identity);self.assertEqual(r['original_relation'],'EXACT_BACKUP');self.assertEqual(r['candidate_rows'],1)
  wrong=dict(new,name='OTHER');r=m.compare(self.raw(b,wrong),b,self.identity);self.assertEqual(r['unexpected_candidate_rows'],1)
  with self.assertRaises(m.Rejected):m.compare(self.raw(b,new,new),b,self.identity)
 def test_caps_bad_encoding_and_missing(self):
  b=self.before()
  for raw in (self.raw(),self.raw(b,b,b,b),b'IDENTITY\thost\nROW\tHGG\n',b'x'*32769):
   with self.assertRaises(m.Rejected):m.compare(raw,b,self.identity)
 def test_backup_and_query_contract(self):
  b=self.before();self.assertEqual(m.validate_before({'schema':1,'row':b}),b)
  with self.assertRaises(m.Rejected):m.validate_before({'schema':True,'row':b})
  with self.assertRaises(m.Rejected):m.object_pairs([('a',1),('a',2)])
  self.assertEqual(m.SQL.count('HEX(CAST('),19);self.assertEqual(m.SQL.count(' AS BINARY)'),19);self.assertEqual(m.SQL.count('SELECT '),2);self.assertIn('START TRANSACTION READ ONLY',m.SQL);self.assertIn('LIMIT 4',m.SQL)
  for token in ('UPDATE ','INSERT ','DELETE ','ROLLBACK'):self.assertNotIn(token,m.SQL)
if __name__=='__main__':unittest.main()

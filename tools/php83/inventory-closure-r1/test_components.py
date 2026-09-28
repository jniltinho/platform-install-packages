import unittest
import components as c
import join_maxmind as m
class Tests(unittest.TestCase):
 def test_literal_markers_not_legal_decision(self):
  notice,generated,evidence=c.inspect('lib/LICENSE.txt',b'Copyright Example\nLicensed under stated terms\nAutomatically generated\n')
  self.assertTrue(notice);self.assertEqual(generated,[3]);self.assertEqual([r['line'] for r in evidence],[1,2])
 def test_lf_numbering_and_scope_cap(self):
  _,generated,evidence=c.inspect('file.php',b'x\rx\nVersion 1\n'+b'none\n'*100+b'Do not edit\n')
  self.assertEqual(generated,[]);self.assertEqual(evidence[0]['line'],2)
 def test_maxmind_hash_and_scope_reject(self):
  a={'source_archive_sha256':'a','source_members':[{'path':'vendor/MaxMind/x','sha256':'b'}]}
  row={'path':'vendor/MaxMind/x','equal':True,'local_sha256':'b','upstream_sha256':'b'}
  comp={'files':[row],'observed_tag':'v','commit':'c','declared_upstream_license':'literal','license_sha256':'d','bundled_license_text_present':False}
  b={'original_archive_sha256':'a','components':{'x':comp}}
  self.assertEqual(m.join(a,b)['files'],1)
  row['upstream_sha256']='wrong'
  with self.assertRaises(ValueError):m.join(a,b)
if __name__=='__main__':unittest.main()

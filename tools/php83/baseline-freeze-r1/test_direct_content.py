import unittest
import direct_content as d
class DirectTests(unittest.TestCase):
 def args(self):return dict(root='/opt/kaltura/web/',path='/content/entry/data//0/1/'+d.NAME,stored='/opt/kaltura/web/content/entry/data/0/1/'+d.NAME)
 def test_exact_source_doubled_path_without_rewrite(self):
  a=self.args();url='https://192.168.56.74'+a['path'];tokens=[];self.assertEqual(d.check(url,'s'*32,'k'*32,tokens,**a),url);self.assertEqual(tokens,[])
  self.assertEqual(d.check(url.replace('.74/','.74:443/'),'s'*32,'k'*32,[],**a),url.replace('.74/','.74:443/'))
 def test_wrong_stored_binding(self):
  a=self.args();a['stored']+='.wrong';self.assertRaises(d.Rejected,d.mapping,a['root'],a['path'],a['stored'])
 def test_unknown_signed_filename_and_route_fail(self):
  a=self.args();base='https://192.168.56.74'+a['path']
  for value in (base+'?signature=VERY_LONG_PRIVATE_SIGNATURE',base+'/kt/VERY_LONG_PRIVATE_TOKEN',base.replace(d.NAME,'arbitrary_long_filename.mp4'),base.replace('https:','http:'),base.replace('.74/','.74:8443/'),base.replace('.74/','.20/'),base.replace('//0/','/0/')):self.assertRaises(d.Rejected,d.check,value,'s'*32,'k'*32,[],**a)
 def test_real_credentials_never_exempt(self):
  a=self.args();base='https://192.168.56.74'+a['path'];self.assertRaises(d.Rejected,d.check,base,d.NAME,'k'*32,[],**a)
  self.assertRaises(d.Rejected,d.check,base,'s'*32,d.NAME,[],**a)
 def test_rejected_candidates_preserved(self):
  a=self.args();tokens=[];self.assertRaises(d.Rejected,d.check,'https://192.168.56.74/ks/INDEPENDENT_TOKEN_PRIVATE','s'*32,'k'*32,tokens,**a);self.assertIn('INDEPENDENT_TOKEN_PRIVATE',tokens)
 def test_path_grammar_rejects_traversal_extra_shards_and_encoding(self):
  a=self.args()
  for path in ('/content/entry/data/../1/'+d.NAME,'/content/entry/data/0/1000/'+d.NAME,'/content/entry/data/0/1/2/'+d.NAME,'/content/entry/data/00/1/'+d.NAME,a['path'].replace('0/1','0/%31')):self.assertRaises(d.Rejected,d.mapping,a['root'],path,a['stored'])
if __name__=='__main__':unittest.main()

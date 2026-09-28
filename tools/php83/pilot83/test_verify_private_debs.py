import copy,hashlib,importlib.util,io,pathlib,tarfile,tempfile,unittest
P=pathlib.Path(__file__).with_name('verify-private-debs.py');s=importlib.util.spec_from_file_location('independent_deb_verifier',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def tar(rows):
 b=io.BytesIO()
 with tarfile.open(fileobj=b,mode='w') as t:
  for name,data,kind,opts in rows:
   i=tarfile.TarInfo(name);i.type=kind;i.mode=opts.get('mode',0o644);i.uid=opts.get('uid',0);i.gid=opts.get('gid',0);i.mtime=opts.get('mtime',0);i.linkname=opts.get('link','');i.pax_headers=opts.get('pax',{})
   i.size=len(data) if kind==tarfile.REGTYPE else 0;t.addfile(i,io.BytesIO(data) if i.size else None)
 return b.getvalue()
def regular(name='a',body=b'A',**kw):return name,body,tarfile.REGTYPE,kw
class Tests(unittest.TestCase):
 def row(self,body=b'A'):return m.tar_inventory(tar([regular(body=body)]))['a']
 def test_unchanged(self):
  a={'a':self.row()};m.compare_members(a,copy.deepcopy(a),[])
 def test_unexpected_content(self):
  with self.assertRaises(ValueError):m.compare_members({'a':self.row()},{'a':self.row(b'B')},[])
 def test_unexpected_addition(self):
  with self.assertRaises(ValueError):m.compare_members({}, {'a':self.row()},[])
 def test_missing(self):
  with self.assertRaises(ValueError):m.compare_members({'a':self.row()}, {},[])
 def test_replace(self):
  m.compare_members({'a':self.row()},{'a':self.row(b'B')},[{'path':'a','before_sha256':m.sha(b'A'),'after_sha256':m.sha(b'B')}])
 def test_replace_wrong_before(self):
  with self.assertRaises(ValueError):m.compare_members({'a':self.row()},{'a':self.row(b'B')},[{'path':'a','before_sha256':'0'*64,'after_sha256':m.sha(b'B')}])
 def test_metadata_mode_uid_gid(self):
  for k in ['uid','gid','mode']:
   a=self.row();a[k]+=1
   with self.subTest(k=k),self.assertRaises(ValueError):m.compare_members({'a':self.row()},{'a':a},[{'path':'a','before_sha256':m.sha(b'A'),'after_sha256':m.sha(b'A')}])
 def test_add(self):m.compare_members({}, {'a':self.row()},[{'path':'a','before_sha256':None,'after_sha256':m.sha(b'A'),'mode':0o644,'uid':0,'gid':0}])
 def test_add_collision_any_type(self):
  for kind in ['0','1','2','5']:
   old=self.row();old['type']=kind
   with self.subTest(kind=kind),self.assertRaises(ValueError):m.compare_members({'a':old},{'a':self.row()},[{'path':'a','before_sha256':None,'after_sha256':m.sha(b'A')}])
 def test_bool_metadata(self):
  with self.assertRaises(ValueError):m.compare_members({}, {'a':self.row()},[{'path':'a','before_sha256':None,'after_sha256':m.sha(b'A'),'uid':False}])
 def test_symlink_preserved(self):
  a=m.tar_inventory(tar([('a',b'',tarfile.SYMTYPE,{'link':'b'})]));m.compare_members(a,copy.deepcopy(a),[])
  b=copy.deepcopy(a);b['a']['link']='other'
  with self.assertRaises(ValueError):m.compare_members(a,b,[])
 def test_nonregular_delta(self):
  a=self.row();a['type']='2'
  with self.assertRaises(ValueError):m.compare_members({}, {'a':a},[{'path':'a','before_sha256':None,'after_sha256':m.sha(b'A')}])
 def test_duplicate_tar(self):
  with self.assertRaises(ValueError):m.tar_inventory(tar([regular(),regular()]))
 def test_bad_paths(self):
  for p in ['../x','/x','a/../b','a//b','a/./b']:
   with self.subTest(p=p),self.assertRaises(ValueError):m.path_name(p)
 def test_special_member(self):
  with self.assertRaises(ValueError):m.tar_inventory(tar([('device',b'',tarfile.CHRTYPE,{})]))
 def test_mtime_permitted(self):self.assertEqual(m.tar_inventory(tar([regular(mtime=1)])),m.tar_inventory(tar([regular(mtime=2)])))
 def test_pax_security_retained(self):
  a=m.tar_inventory(tar([regular()]));b=m.tar_inventory(tar([regular(pax={'SCHILY.xattr.security.capability':'not-ignored'})]));
  with self.assertRaises(ValueError):m.compare_members(a,b,[])
 def test_md5(self):
  data={'a':self.row()};c=m.tar_inventory(tar([regular('md5sums',(hashlib.md5(b'A').hexdigest()+'  a\n').encode())]),True);m.verify_md5(data,c)
 def test_md5_missing_duplicate_wrong_extra(self):
  for body in [b'',b'0'*32+b'  a\n', (hashlib.md5(b'A').hexdigest()+'  a\n').encode()*2,(hashlib.md5(b'A').hexdigest()+'  other\n').encode()]:
   c=m.tar_inventory(tar([regular('md5sums',body)]),True)
   with self.subTest(body=body),self.assertRaises(ValueError):m.verify_md5({'a':self.row()},c)
 def test_duplicate_expected(self):
  with self.assertRaises(ValueError):m.delta_map([{'path':'a'},{'path':'a'}])
 def test_input_hash(self):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'input';p.write_bytes(b'{}')
   with self.assertRaises(ValueError):m.pinned_entry({'path':str(p),'sha256':'0'*64})
 def test_full_package(self):
  data=m.tar_inventory(tar([regular()]));md=(hashlib.md5(b'A').hexdigest()+'  a\n').encode();control=m.tar_inventory(tar([regular('control',b'Package: synthetic\n'),regular('md5sums',md)]),True);package={'data':data,'control':control};m.compare_package(package,copy.deepcopy(package),[],[])
if __name__=='__main__':unittest.main()

import copy,hashlib,io,json,pathlib,tempfile,unittest,zipfile
import build as b
class Tests(unittest.TestCase):
 def zip(self,entries):
  buf=io.BytesIO()
  with zipfile.ZipFile(buf,'w') as z:
   for name,raw in entries:z.writestr(b.PREFIX+name,raw)
  return buf.getvalue()
 def scan(self,raw,pin=None):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'input.zip';p.write_bytes(raw)
   return b.source_inventory(p,pin or b.sha(raw),b.scanner())
 def test_original_nonextension_php_and_no_excerpts(self):
  rows,calls=self.scan(self.zip([('bin/runner',b'#!/usr/bin/php\n<?php echo 1;'),('run.sh',b'php example.php --password=SYNTHETIC_ONLY'),('binary',b'\x00<?php')]))
  self.assertEqual(len(rows),3);self.assertIn('php_shebang',next(r['classes'] for r in rows if r['path']=='bin/runner'))
  self.assertEqual(len(calls),1);self.assertNotIn(b'SYNTHETIC_ONLY',b.canonical(calls));self.assertNotIn('line_excerpt',calls[0])
 def test_wrong_zip_pin(self):
  with self.assertRaisesRegex(ValueError,'ZIP_PIN'):self.scan(self.zip([('x',b'x')]),'0'*64)
 def test_traversal_and_duplicate(self):
  for entries in [[('../x',b'x')],[('x',b'x'),('x',b'x')]]:
   with self.assertRaises(ValueError):self.scan(self.zip(entries))
 def test_symlink_rejected(self):
  buf=io.BytesIO()
  with zipfile.ZipFile(buf,'w') as z:
   info=zipfile.ZipInfo(b.PREFIX+'link');info.external_attr=0o120777<<16;z.writestr(info,b'target')
  with self.assertRaisesRegex(ValueError,'NONREGULAR_SOURCE'):self.scan(buf.getvalue())
 def reports(self):
  owner={'package_file':'p.deb','package_sha256':'a'*64}
  pkg={'original_archive_sha256':b.ZIP_PIN,'bundle_sha256':'b'*64,'packages':[owner],
   'files':{'opt/kaltura/app/a.php':{'path':'opt/kaltura/app/a.php','sha256':'c'*64,'size':1,'type':'regular','owners':[owner]},
            'opt/kaltura/bin/x.php':{'path':'opt/kaltura/bin/x.php','sha256':'d'*64,'size':1,'type':'regular','owners':[owner]}},
   'source_differential':{'unchanged_upstream_php_files':1,'extra_packaged_php_files':1}}
  ent={'original_archive_sha256':b.ZIP_PIN,'bundle_sha256':'b'*64,'packages':[owner]}
  return pkg,ent
 def test_join_retains_overlay_and_original_only(self):
  pkg,ent=self.reports();rows=[{'path':'a.php','sha256':'c'*64},{'path':'only.xml','sha256':'d'*64}]
  result=b.join(rows,pkg,ent);self.assertEqual([r['relation'] for r in result],['same_original_bytes','package_only_php_overlay']);self.assertFalse(rows[1]['matched_in_packaged_php_index'])
 def test_owner_and_cohort_mutation(self):
  for field in ('bundle_sha256','packages'):
   pkg,ent=self.reports();ent[field]='wrong' if field=='bundle_sha256' else []
   with self.assertRaises(ValueError):b.join([{'path':'a.php','sha256':'c'*64}],pkg,ent)
 def test_duplicate_source_rejected(self):
  pkg,ent=self.reports()
  with self.assertRaisesRegex(ValueError,'SOURCE_DUPLICATE'):b.join([{'path':'x'},{'path':'x'}],pkg,ent)
 def test_missing_original_fails_historical_join(self):
  pkg,ent=self.reports()
  with self.assertRaisesRegex(ValueError,'UNCHANGED_JOIN'):b.join([],pkg,ent)
 def test_extraction_bytes_and_drift(self):
  raw=self.zip([('a.php',b'<?php'),('sub/file.txt',b'public')])
  with tempfile.TemporaryDirectory() as d:
   archive=pathlib.Path(d)/'a.zip';archive.write_bytes(raw);rows,_=b.source_inventory(archive,b.sha(raw),b.scanner());tree=pathlib.Path(d)/'tree'
   self.assertEqual(b.extract_new(archive,tree,rows)['files'],2)
   with self.assertRaisesRegex(ValueError,'EXTRACTION_EXISTS'):b.extract_new(archive,tree,rows)
   (tree/'a.php').write_bytes(b'drift')
   with self.assertRaisesRegex(ValueError,'EXTRACTED_BYTES'):b.extracted_identity(tree,rows)
 def test_extraction_missing_extra_link(self):
  with tempfile.TemporaryDirectory() as d:
   tree=pathlib.Path(d);row={'path':'x','sha256':b.sha(b'x'),'bytes':1}
   with self.assertRaisesRegex(ValueError,'EXTRACTED_MISSING'):b.extracted_identity(tree,[row])
   (tree/'x').symlink_to('/nonexistent')
   with self.assertRaisesRegex(ValueError,'EXTRACTED_LINK'):b.extracted_identity(tree,[row])
   (tree/'x').unlink();(tree/'x').write_bytes(b'x');(tree/'extra').write_bytes(b'')
   with self.assertRaisesRegex(ValueError,'EXTRACTED_INVENTORY'):b.extracted_identity(tree,[row])
 def test_deterministic_canonical(self):self.assertEqual(b.canonical({'b':2,'a':1}),b.canonical({'a':1,'b':2}))
if __name__=='__main__':unittest.main()

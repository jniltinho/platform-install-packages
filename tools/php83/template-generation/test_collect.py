import importlib.util,json,tempfile,unittest,base64
from pathlib import Path
s=importlib.util.spec_from_file_location('collect',Path(__file__).with_name('collect.py'));c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class CollectorTests(unittest.TestCase):
 def matrix(self):return [dict(runtime=r,variant=v,mode='method',case='string',exit=0) for r,v in c.VARIANTS]
 def test_exact_matrix(self):self.assertEqual(c.validate_matrix(self.matrix(),{'method':['string']}),5)
 def test_duplicate(self):
  a=self.matrix();a[2]=a[1]
  with self.assertRaises(ValueError):c.validate_matrix(a,{'method':['string']})
 def test_missing(self):
  with self.assertRaises(ValueError):c.validate_matrix(self.matrix()[:-1],{'method':['string']})
 def test_timeout(self):
  a=self.matrix();a[0]['exit']=124
  with self.assertRaises(ValueError):c.validate_matrix(a,{'method':['string']})
 def test_bool_exit(self):
  a=self.matrix();a[0]['exit']=False
  with self.assertRaises(ValueError):c.validate_matrix(a,{'method':['string']})
 def test_native_fatal_rejected(self):
  with self.assertRaises(ValueError):c.parse_record({'exit':255},{})
 def output(self,path='file.php',data=b'<?php echo 1;'):
  return {'outputs':{path:{'sha256':c.sha(data),'base64':base64.b64encode(data).decode()}}}
 def test_decode(self):self.assertEqual(c.decode_outputs(self.output()),{'file.php':b'<?php echo 1;'})
 def test_path_escape(self):
  with self.assertRaises(ValueError):c.decode_outputs(self.output('../bad.php'))
 def test_output_hash(self):
  a=self.output();a['outputs']['file.php']['sha256']='0'*64
  with self.assertRaises(ValueError):c.decode_outputs(a)
 def test_invalid_base64(self):
  a=self.output();a['outputs']['file.php']['base64']='!'
  with self.assertRaises(ValueError):c.decode_outputs(a)
 def test_atomic_progress(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'report.json';p.write_text('{}');c.persist(p,{'rows':[1]});self.assertEqual(json.loads(p.read_text()),{'rows':[1]});self.assertFalse(p.with_name('report.json.progress.tmp').exists())
 def test_stale_temp_does_not_block(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'report.json';stale=p.with_name(p.name+'.progress.tmp');stale.write_text('stale')
   c.persist(p,{'status':'INTERRUPTED_OR_FAILED'});self.assertEqual(json.loads(p.read_text())['status'],'INTERRUPTED_OR_FAILED');self.assertEqual(stale.read_text(),'stale')
 def test_failed_serialization_cleans_unique_temp(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'report.json';p.write_text('old')
   with self.assertRaises(TypeError):c.persist(p,{'bad':object()})
   self.assertEqual(p.read_text(),'old');self.assertEqual(list(Path(d).glob('*.tmp')),[])
 def test_failed_replace_cleans_unique_temp(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'report.json';p.write_text('old')
   with patch.object(Path,'replace',side_effect=OSError('fixture failure')):
    with self.assertRaises(OSError):c.persist(p,{'good':1})
   self.assertEqual(p.read_text(),'old');self.assertEqual(list(Path(d).glob('*.tmp')),[])
 def test_checksums_positive(self):self.assertEqual(c.parse_checksums('a'*64+'  /audit/file\n'),{'/audit/file':'a'*64})
 def test_checksums_duplicates(self):
  with self.assertRaises(ValueError):c.parse_checksums(('a'*64+'  /audit/file\n')*2)
 def test_checksums_malformed(self):
  for text in ['', '\n', 'short  /audit/file\n', 'a'*64+' /audit/file\n','a'*64+'  relative\n','a'*64+'  /audit/file','a'*64+'  /audit/file\n\n']:
   with self.subTest(text=text):
    with self.assertRaises(ValueError):c.parse_checksums(text)
 def test_empty_php_array_outputs(self):self.assertEqual(c.decode_outputs({'outputs':[]}),{})
 def test_invalid_output_containers(self):
  for value in [[{}],[1],None,False,0,'']:
   with self.subTest(value=value):
    with self.assertRaises(ValueError):c.decode_outputs({'outputs':value})
if __name__=='__main__':unittest.main()

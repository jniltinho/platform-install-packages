import importlib.util,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('trace_prepare',HERE/'prepare.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
SOURCE=Path('/home/nilton/Projetos/nilton/NOVOS/kaltura-rigel-18.20.0-source/server-Rigel-18.20.0')
class Tests(unittest.TestCase):
 def test_four_core_targets(self):
  self.assertEqual(len(p.TARGETS),4);self.assertFalse(any(x.startswith('vendor/') for x in p.TARGETS))
 def test_replay_all(self):
  for path in p.TARGETS:
   raw=(SOURCE/path).read_bytes();after=p.transform(path,raw)
   p.old.strict_replay(path,raw,p.old.patch_bytes(path,raw,after),after)
 def test_double_application(self):
  for path in p.TARGETS:
   with self.assertRaises(ValueError):p.transform(path,p.transform(path,(SOURCE/path).read_bytes()))
 def test_missing_anchor(self):
  for path in p.TARGETS:
   with self.assertRaises(ValueError):p.transform(path,b'no anchor')
 def test_unknown(self):
  with self.assertRaises(ValueError):p.transform('unknown',b'')
 def test_guard_only_three_changes(self):
  path=p.old.TARGETS[0];raw=(SOURCE/path).read_bytes();old=p.old.transform(path,raw)
  self.assertEqual(p.transform(path,raw).replace(b'if(!$message instanceof Throwable)',b'if(!$message instanceof Exception)'),old)
 def test_writer_existing_methods_unchanged(self):
  raw=(SOURCE/p.WRITER).read_bytes();after=p.transform(p.WRITER,raw)
  self.assertEqual(after.replace((HERE/'writer-methods.php.inc').read_bytes(),b''),raw)
 def test_no_generic_replacement_or_mutation(self):
  code=(HERE/'writer-methods.php.inc').read_text()
  for prohibited in ('preg_replace','getTraceAsString','__toString','setTrace','setMessage','serialize(', 'clone '):self.assertNotIn(prohibited,code)
  for expected in ('getPrevious()', 'getMessage()', 'getCode()', 'getFile()', 'getLine()', 'getTrace()', 'parent::_write($event)', 'gettype($argument)'):self.assertIn(expected,code)
 def test_known_copies_unchanged(self):
  for path in p.old.TARGETS[1:]:self.assertEqual(p.transform(path,(SOURCE/path).read_bytes()),p.old.transform(path,(SOURCE/path).read_bytes()))
 def test_existing_output_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(ValueError,'Fresh'):p.prepare(Path('bad'),Path('bad'),Path(tmp))
 def test_archive_pin_closed(self):
  with tempfile.TemporaryDirectory() as tmp:
   q=Path(tmp)/'x';q.write_bytes(b'not zip')
   with self.assertRaisesRegex(ValueError,'drift'):p.old.archive(q,p.PIN,p.TARGETS)
if __name__=='__main__':unittest.main()

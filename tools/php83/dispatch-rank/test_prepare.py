import pathlib,tempfile,unittest
import prepare
class PreparationTests(unittest.TestCase):
 def source(self):return b'<?php\nclass KalturaFrontController\n{\n\tprivate $disptacher = null;\n}\n'
 def test_alternatives(self):
  b=self.source();v=prepare.variants(b);self.assertEqual(v['original'],b);self.assertIn(b'public $dispatcher = null;',v['public-comparison']);self.assertNotIn(b'AllowDynamicProperties',v['public-comparison']);self.assertIn(b'AllowDynamicProperties',v['attribute-comparison']);self.assertNotIn(b'public $dispatcher',v['attribute-comparison'])
 def test_missing_class(self):
  with self.assertRaises(ValueError):prepare.variants(b'<?php\n')
 def test_duplicate_class(self):
  with self.assertRaises(ValueError):prepare.variants(self.source()*2)
 def test_missing_typo(self):
  with self.assertRaises(ValueError):prepare.variants(self.source().replace(b'disptacher',b'dispatcher'))
 def test_existing_output(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):prepare.prepare('missing',d)
 def test_external_stage_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):prepare.prepare('missing',pathlib.Path(d)/'new')

import contextlib,json,zipfile
from unittest.mock import patch
class ArchiveGuards(unittest.TestCase):
 @contextlib.contextmanager
 def fixture(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d); archive=root/'input.zip';out=root/'doc/php83/evidence/dispatch-rank/new'
   files={p:b'<?php /* harmless fixture */\n' for p in prepare.PATHS};files[prepare.PATHS[0]]=b'<?php\nclass KalturaFrontController\n{\n\tprivate $disptacher = null;\n}\n'
   with zipfile.ZipFile(archive,'w') as z:
    for p,b in files.items():z.writestr('server-Rigel-18.20.0/'+p,b)
   m=root/'doc/php83/evidence/exp12-candidate/selected-manifest.json';m.parent.mkdir(parents=True);m.write_text(json.dumps({'patches':[{'path':prepare.PATHS[0],'after_sha256':prepare.sha(files[prepare.PATHS[0]])}]}))
   with patch.object(prepare,'ROOT',root),patch.object(prepare,'PIN',prepare.sha(archive.read_bytes())),patch.object(prepare,'SELECTED_SHA',prepare.sha(m.read_bytes())),patch.object(prepare,'SOURCE_PINS',{p:prepare.sha(b) for p,b in files.items()}):yield archive,out,m
 def test_success_all_files_and_variant_exact(self):
  with self.fixture() as (a,o,m):
   r=prepare.prepare(a,o);self.assertEqual(len(r['files']),14)
   before=(o/'original.php').read_bytes();attr=(o/'attribute-comparison.php').read_bytes();public=(o/'public-comparison.php').read_bytes()
   self.assertEqual(attr.replace(b'#[\\AllowDynamicProperties]\n',b''),before)
   self.assertEqual(public.replace(b'\tpublic $dispatcher = null;\n',b''),before)
   self.assertIn(b'private $disptacher',public)
 def test_wrong_archive_hash(self):
  with self.fixture() as (a,o,m):
   a.write_bytes(a.read_bytes()+b'x')
   with self.assertRaises(ValueError):prepare.prepare(a,o)
   self.assertFalse(o.exists())
 def test_dependency_drift(self):
  with self.fixture() as (a,o,m):
   with patch.object(prepare,'SOURCE_PINS',{}):
    with self.assertRaises(ValueError):prepare.prepare(a,o)
   self.assertFalse(o.exists())
 def test_selected_manifest_drift(self):
  with self.fixture() as (a,o,m):
   m.write_bytes(m.read_bytes()+b' ')
   with self.assertRaises(ValueError):prepare.prepare(a,o)
   self.assertFalse(o.exists())
 def test_missing_archive(self):
  with self.fixture() as (a,o,m):
   a.unlink()
   with self.assertRaises(FileNotFoundError):prepare.prepare(a,o)
 def test_selected_target_mismatch(self):
  with self.fixture() as (a,o,m):
   raw=json.loads(m.read_text());raw['patches'][0]['after_sha256']='0'*64;m.write_text(json.dumps(raw))
   with patch.object(prepare,'SELECTED_SHA',prepare.sha(m.read_bytes())):
    with self.assertRaises(ValueError):prepare.prepare(a,o)
   self.assertFalse(o.exists())

if __name__=='__main__':unittest.main()

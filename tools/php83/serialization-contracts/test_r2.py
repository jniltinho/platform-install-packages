import importlib.util,json,unittest,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('prep',HERE/'prepare-r2.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
s=importlib.util.spec_from_file_location('collect',HERE/'collect-r2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class Guards(unittest.TestCase):
 def test_guard_before_envelope(self):
  result=p.bridge(b'<?php class X {\n    public function serialize() {return false;}\n}').decode()
  self.assertLess(result.index('if (!is_string($payload))'),result.index("return array('payload' => $payload)"));self.assertIn('throw new',result);self.assertIn('must return a string or NULL',result)
 def test_argument_order(self):
  source=b"prefix implode(str_split(hash('sha256', $id), 2), DIRECTORY_SEPARATOR) suffix"
  self.assertEqual(p.cachefix(source),b"prefix implode(DIRECTORY_SEPARATOR, str_split(hash('sha256', $id), 2)) suffix")
 def test_missing(self):
  with self.assertRaises(ValueError):p.cachefix(b'<?php')
 def test_duplicate(self):
  x=b"implode(str_split(hash('sha256', $id), 2), DIRECTORY_SEPARATOR)"
  with self.assertRaises(ValueError):p.cachefix(x+x)
 def test_stage_hashes(self):
  stage=HERE/'stage-r2';m=json.loads((stage/'identities.json').read_text())
  self.assertEqual({str(f.relative_to(stage)) for f in stage.rglob('*') if f.is_file()},set(m['files'])|{'identities.json'})
  for name,digest in m['files'].items():self.assertEqual(hashlib.sha256((stage/name).read_bytes()).hexdigest(),digest)
 def test_four_changes(self):
  m=json.loads((HERE/'stage-r2/identities.json').read_text());self.assertEqual(len(m['changes']),4);self.assertEqual(sum(x['family']=='filecache-implode-order' for x in m['changes']),1)
 def test_dual_runtime(self):
  m=json.loads((HERE/'stage-r2/identities.json').read_text());self.assertEqual(set(m['runtime_files']),{'native83','baseline74'});self.assertIn('/usr/bin/php7.4',m['runtime_files']['baseline74']);self.assertIn('/usr/lib/php/20190902/json.so',m['runtime_files']['baseline74'])
 def test_three_bridge_targets(self):
  stage=HERE/'stage-r2';changed=[name for name in p.PATHS if (stage/'cachefix'/name).read_bytes()!=(stage/'candidate'/name).read_bytes()];self.assertEqual(set(changed),set(p.r1.TARGETS))
 def test_one_cachefix(self):
  stage=HERE/'stage-r2';changed=[name for name in p.PATHS if (stage/'original'/name).read_bytes()!=(stage/'cachefix'/name).read_bytes()];self.assertEqual(changed,[p.FILECACHE])
 def test_wire_hash(self):
  with self.assertRaises(ValueError):c.wiredata({'base64':'Tjs=','sha256':'a'*64,'format':'N'})
 def test_wire_format(self):
  with self.assertRaises(ValueError):c.wiredata({'base64':'Tjs=','sha256':hashlib.sha256(b'N;').hexdigest(),'format':'C'})
 def test_bool_rejected(self):
  with self.assertRaises(ValueError):c.validate({'exit':False},'74',{})
 def test_float_rejected(self):
  with self.assertRaises(ValueError):c.validate({'exit':0.0},'83',{})
 def test_original_only74(self):
  s=(HERE/'run-r2.sh').read_text();self.assertIn('[[ $1 == original ]] || exit 64',s);self.assertIn('PrivateNetwork=yes',s);self.assertIn('SystemCallFilter=~socket socketpair',s);self.assertIn('PrivateTmp=yes',s)
 def test_private_cache(self):
  s=(HERE/'cache-probe.php').read_text();self.assertIn("$dir='/tmp/aws-serialization-cache'",s);self.assertIn('return false;',s);self.assertIn('E_ALL',s);self.assertNotIn('error_reporting(0)',s)
if __name__=='__main__':unittest.main()

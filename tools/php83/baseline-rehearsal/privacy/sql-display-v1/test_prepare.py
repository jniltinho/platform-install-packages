import importlib.util,unittest
from pathlib import Path
P=Path(__file__).with_name('prepare.py');s=importlib.util.spec_from_file_location('sql_display_prepare',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
SOURCE=Path('/home/nilton/Projetos/nilton/NOVOS/kaltura-rigel-18.20.0-source/server-Rigel-18.20.0')/m.TARGET
class Tests(unittest.TestCase):
 def setUp(self):self.raw=SOURCE.read_bytes();self.out=m.transform(self.raw)
 def test_real_execution_unchanged(self):
  for text in [b'parent::bindValue ($parameter, $value, $data_type)',b'parent::execute($input_parameters)',b'KalturaMonitorClient::monitorDatabaseAccess($sql, $sqlTook)',b'str_replace($search, $replace, $this->queryString)']:
   self.assertEqual(self.raw.count(text),self.out.count(text));self.assertEqual(self.out.count(text),1)
 def test_debug_only_template(self):self.assertNotIn(b'KalturaLog::debug($sql);',self.out);self.assertIn(b'KalturaLog::debug($this->queryString',self.out)
 def test_no_extra_value_storage(self):self.assertIn(b'gettype($value)',self.out);self.assertIn(b'gettype($logValue)',self.out);self.assertNotIn(b'serialize(',self.out)
 def test_twice_rejected(self):
  with self.assertRaises(ValueError):m.transform(self.out)
 def test_anchor_drift(self):
  with self.assertRaises(ValueError):m.transform(self.raw.replace(b'KalturaLog::debug($sql);',b'KalturaLog::debug("other");'))
 def test_bound_and_input_paths(self):self.assertIn(b'$logTypes = $this->logValueTypes;',self.out);self.assertIn(b'if (!is_null($input_parameters))',self.out)
 def test_old_value_array_unchanged(self):self.assertIn(b'$replace = array_reverse($this->values);',self.out)
 def test_probe_named_arrays(self):
  text=P.with_name('probe.php').read_text();self.assertIn("execute(array(':p1'=>$id,':p2'=>$value))",text);self.assertNotIn('execute(array($id,$value))',text)
 def test_source_authority_pin(self):self.assertEqual(m.old.sha(self.raw),'a80d6029db03e1880adf240b157489d6f25b47163c394d0b0969300416378d70')
if __name__=='__main__':unittest.main()

import copy,json,unittest
import prepare,validate
class Tests(unittest.TestCase):
 def test_exact_addition(self):
  raw=b'prefix\n'+prepare.ANCHOR+b'\nsuffix';out=prepare.transform(raw)
  self.assertEqual(out,raw.replace(prepare.ANCHOR,prepare.ANCHOR+prepare.ADDED))
  self.assertIn(b"=== 'KalturaSerializableStream'",out);self.assertIn(b"=== '_write'",out)
 def test_drift(self):
  for b in (b'',prepare.ANCHOR*2,prepare.ANCHOR+prepare.ADDED):
   with self.assertRaises(ValueError):prepare.transform(b)
 def body(self,variant):
  records=[]
  for c,f in validate.EMITTERS:
   for k in ('string','throwable'):
    records.append(dict(case=c+'::'+f+'/'+k,caller='KalturaSerializableStream->_write' if variant=='overlay' else c+'->'+f,extra='SYNTHETIC_EXTRA',priority='3',message_present=True,observer_same_message=True,observer_extra='SYNTHETIC_EXTRA',observer_logMethod_class='LogMethod',message_unchanged=True,writer_class='KalturaSerializableStream',formatter_class='Zend_Log_Formatter_Simple'))
  return {'records':records,'loaded':{'real.php':'a'*64},'diagnostics':[]}
 def test_positive_synthetic_contract(self):
  for v in ('original','overlay','repaired'):validate.validate(self.body(v),v,{'real.php':'a'*64})
 def test_empty_sources(self):
  b=self.body('original');b['loaded']={}
  with self.assertRaises(ValueError):validate.validate(b,'original',{})
 def test_missing_record(self):
  b=self.body('original');b['records'].pop()
  with self.assertRaises(ValueError):validate.validate(b,'original',b['loaded'])
 def test_boolean_not_integer(self):
  b=self.body('original');b['records'][0]['message_unchanged']=1
  with self.assertRaises(ValueError):validate.validate(b,'original',b['loaded'])
 def test_wrong_caller(self):
  b=self.body('repaired');b['records'][2]['caller']='global'
  with self.assertRaises(ValueError):validate.validate(b,'repaired',b['loaded'])
 def test_overlay_regression_required(self):
  b=self.body('original')
  with self.assertRaises(ValueError):validate.validate(b,'overlay',b['loaded'])
if __name__=='__main__':unittest.main()

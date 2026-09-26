"""Offline mutation checks, not independent native execution evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('reconcile',Path(__file__).with_name('reconcile-r3.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Contract(unittest.TestCase):
 def setUp(self):
  self.reports={v:json.loads((m.E/f'r3-primary{v}.json').read_text()) for v in ['74','83']}
  self.manifest=json.loads((m.E/'r3-stage-identities.json').read_text())
 def change(self,kind,op,mutate):
  import base64
  r=next(r for r in self.reports['83']['records'] if r['variant']=='candidate' and r['kind']==kind and r['operation']==op)
  b=json.loads(r['stdout']);mutate(b);r['stdout']=json.dumps(b);r['stdout_base64']=base64.b64encode(r['stdout'].encode()).decode()
 def reject(self):
  with self.assertRaises((ValueError,KeyError)):m.reconcile(self.reports,self.manifest)
 def test_actual_retained(self):self.assertEqual(len(m.reconcile(self.reports,self.manifest)),14)
 def test_bool_exit(self):self.reports['83']['records'][0]['exit']=False;self.reject()
 def test_missing_case(self):self.reports['83']['records'].pop();self.reject()
 def test_typed_getter(self):
  self.change('plain','roundtrip',lambda b:b['result']['restored']['getters']['isExpired'].update(value=0));self.reject()
 def test_delayed_utf8(self):
  self.change('plain','invalid-utf8',lambda b:b['result'].update(wire={'format':'O'}));self.reject()
 def test_wrong_save_phase(self):
  self.change('cache','invalid-utf8',lambda b:b['result']['exception'].update(phase='read'));self.reject()
 def test_warning_loss(self):
  self.change('cache','malformed',lambda b:b.update(diagnostics=[]));self.reject()
 def test_old_reader_now_accepts(self):
  r=next(r for r in self.reports['74']['records'] if r['operation']=='read' and r['writer']=='candidate83')
  import base64
  b=json.loads(r['stdout']);b['result']['restored']['value']=0;r['stdout']=json.dumps(b);r['stdout_base64']=base64.b64encode(r['stdout'].encode()).decode();self.reject()
if __name__=='__main__':unittest.main()

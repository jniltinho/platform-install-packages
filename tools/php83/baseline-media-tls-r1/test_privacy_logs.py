import unittest
from pathlib import Path
from unittest.mock import patch
import privacy_logs as m
class Tests(unittest.TestCase):
 def test_extend(self):
  with patch.object(m,'paths',return_value=[Path('/private/access.log'),Path('/private/error.log')]):
   self.assertEqual(len(m.extend(lambda:[Path('/legacy')])),3)
 def test_no_missing_adapter(self):
  with patch.object(m,'paths',side_effect=m.Rejected('MEDIA_TLS_LOG_METADATA')):
   with self.assertRaises(m.Rejected):m.extend(lambda:[])
 def test_duplicate(self):
  with patch.object(m,'paths',return_value=[Path('/same')]):
   for values in ([Path('/same')],[Path('/a'),Path('/a')]):
    with self.assertRaises(m.Rejected):m.extend(lambda:values)
 def test_inventory_each_call(self):
  with patch.object(m,'paths',return_value=[]) as p:
   m.extend(lambda:[]);m.extend(lambda:[]);self.assertEqual(p.call_count,2)
if __name__=='__main__':unittest.main()

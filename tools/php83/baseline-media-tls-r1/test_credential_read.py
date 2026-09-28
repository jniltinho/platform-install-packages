import unittest
from unittest.mock import patch
import credential_read as c
class Tests(unittest.TestCase):
 def test_unknown_path(self):
  with patch.object(c.os,'open') as o:
   with self.assertRaises(c.Rejected):c.read_fixed('/etc/shadow')
   o.assert_not_called()
 def test_wrong_account(self):
  with patch.object(c.pwd,'getpwuid',return_value=type('P',(),{'pw_name':'other'})()),patch.object(c.os,'open') as o:
   with self.assertRaises(c.Rejected):c.read_fixed('/opt/kaltura/app/configurations/db.ini')
   o.assert_not_called()
if __name__=='__main__':unittest.main()

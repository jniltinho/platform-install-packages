import unittest
from collect import host_projection,UUID,NAME
class Tests(unittest.TestCase):
 def fixture(self):return f'name="{NAME}"\nUUID="{UUID}"\nmemory=8192\ncpus=4\nVMState="running"\nsecret="excluded"\n'
 def test_allowlist(self):self.assertNotIn('secret',host_projection(self.fixture()))
 def test_target(self):
  with self.assertRaisesRegex(ValueError,'HOST_IDENTITY'):host_projection(self.fixture().replace(UUID,'wrong'))
 def test_resources(self):
  with self.assertRaisesRegex(ValueError,'HOST_RESOURCES'):host_projection(self.fixture().replace('8192','4096'))
 def test_duplicate(self):
  with self.assertRaisesRegex(ValueError,'DUPLICATE'):host_projection(self.fixture()+'cpus=4\n')
if __name__=='__main__':unittest.main()

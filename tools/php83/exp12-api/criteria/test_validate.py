import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('validation',Path(__file__).with_name('validate.py'))
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class ValidationTests(unittest.TestCase):
    def test_missing_modes(self):
        with self.assertRaisesRegex(ValueError,'Mode'):v.validate([], {})
    def test_duplicate_modes(self):
        with self.assertRaisesRegex(ValueError,'Mode'):v.validate([{'mode':'prior-filter'}]*4,{})
    def test_ordered_modes(self):
        with self.assertRaisesRegex(ValueError,'Mode'):v.validate([{'mode':m} for m in reversed(v.MODES)],{})
    def test_native_exact(self):
        e={'severity':2,'message':'fixture','file':'prior.php','line':40}
        self.assertEqual(v.native([e]),'Warning: fixture in /audit/probe/prior.php on line 40\n')
    def test_line_normalization(self):
        a={'severity':2,'message':'fixture','file':'prior.php','line':40};b=dict(a,file='candidate.php',line=41)
        self.assertEqual(v.normalized([a],'prior'),v.normalized([b],'candidate'))
    def test_unrelated_not_target(self):
        self.assertFalse(v.target({'severity':8192,'message':'Creation of dynamic property UnrelatedMarkerControl::$fixtureMarker is deprecated'}))
    def test_target_severity(self):
        self.assertFalse(v.target({'severity':2,'message':'Creation of dynamic property Criteria::$creteria_filter_attached is deprecated'}))
if __name__=='__main__':unittest.main()

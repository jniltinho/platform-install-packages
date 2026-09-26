import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location('composition', Path(__file__).with_name('prepare.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class PreparationTests(unittest.TestCase):
    def fixture(self):
        return b'\n' * 37 + m.ANCHOR + b'\n}\n'

    def test_exact_attribute_delta(self):
        data = self.fixture()
        with patch.object(m, 'PRIOR', m.sha(data)):
            out = m.transform(data)
        self.assertEqual(out.replace(m.ATTRIBUTE, b'', 1), data)
        self.assertEqual(out.count(m.ATTRIBUTE), 1)

    def test_source_drift(self):
        with self.assertRaisesRegex(ValueError, 'drift'):
            m.transform(self.fixture())

    def test_duplicate_anchor(self):
        data = self.fixture() + m.ANCHOR
        with patch.object(m, 'PRIOR', m.sha(data)), self.assertRaisesRegex(ValueError, 'declaration'):
            m.transform(data)

    def test_shifted_anchor(self):
        data = b'\n' + self.fixture()
        with patch.object(m, 'PRIOR', m.sha(data)), self.assertRaisesRegex(ValueError, 'declaration'):
            m.transform(data)

    def test_existing_attribute(self):
        data = self.fixture() + m.ATTRIBUTE
        with patch.object(m, 'PRIOR', m.sha(data)), self.assertRaisesRegex(ValueError, 'already'):
            m.transform(data)

    def test_existing_output_refused_before_reads(self):
        with tempfile.TemporaryDirectory() as td, self.assertRaisesRegex(ValueError, 'existing'):
            m.prepare(Path('/missing'), Path('/missing'), Path(td))

    def test_archive_and_member_pins(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'a.zip'
            with zipfile.ZipFile(p, 'w') as z:
                z.writestr(m.MEMBER, b'content')
            self.assertEqual(m.read_pinned(p, m.sha(p.read_bytes()), m.sha(b'content')), b'content')
            with self.assertRaisesRegex(ValueError, 'Archive'):
                m.read_pinned(p, 'bad', m.sha(b'content'))
            with self.assertRaisesRegex(ValueError, 'Member'):
                m.read_pinned(p, m.sha(p.read_bytes()), 'bad')

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'a.zip'
            with zipfile.ZipFile(p, 'w') as z:
                i = zipfile.ZipInfo(m.MEMBER)
                i.external_attr = 0o120777 << 16
                z.writestr(i, b'content')
            with self.assertRaisesRegex(ValueError, 'Symlink'):
                m.read_pinned(p, m.sha(p.read_bytes()), m.sha(b'content'))

class AdditionalGuardTests(unittest.TestCase):
    def test_duplicate_zip_member(self):
        import warnings
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'a.zip'
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                with zipfile.ZipFile(p,'w') as z:
                    z.writestr(m.MEMBER,b'x');z.writestr(m.MEMBER,b'x')
            with self.assertRaisesRegex(ValueError,'Duplicate'):
                m.read_pinned(p,m.sha(p.read_bytes()),m.sha(b'x'))

    def test_success_manifest_and_strict_replay(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);data=b'\n'*37+m.ANCHOR+b'\n}\n';a=root/'a.zip';b=root/'b.zip'
            for p in [a,b]:
                with zipfile.ZipFile(p,'w') as z:z.writestr(m.MEMBER,data)
            with patch.multiple(m,UPSTREAM=m.sha(a.read_bytes()),EXP11=m.sha(b.read_bytes()),BEFORE=m.sha(data),PRIOR=m.sha(data)):
                report=m.prepare(a,b,root/'out')
            self.assertFalse(report['next_zip_selected'])
            self.assertEqual(set(p.name for p in (root/'out').iterdir()),{'Criteria.php','Criteria-dynamic-hierarchy.patch','manifest.json'})
            target=root/'replay'/m.TARGET;target.parent.mkdir(parents=True);target.write_bytes(data)
            r=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(root/'out/Criteria-dynamic-hierarchy.patch')],cwd=root/'replay',capture_output=True)
            self.assertEqual(r.returncode,0);self.assertNotIn(b'offset',r.stdout+r.stderr)
            self.assertEqual(target.read_bytes(),(root/'out/Criteria.php').read_bytes())

if __name__ == '__main__':
    unittest.main()

"""Independent disposable write tests; never imports or executes guest guard."""
import importlib.util
from pathlib import Path
import os
import stat
import tempfile
import unittest
from unittest import mock

spec=importlib.util.spec_from_file_location('deploy_under_review',Path(__file__).with_name('deploy_helper.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class IndependentWriteTests(unittest.TestCase):
    def test_exclusive_private_file(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(m.os,'fchown'):
            p=Path(d)/'output';m.write(p,b'synthetic',0o600)
            self.assertEqual(p.read_bytes(),b'synthetic')
            self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
            with self.assertRaises(ValueError):m.write(p,b'replaced')
            self.assertEqual(p.read_bytes(),b'synthetic')
            self.assertEqual(sorted(x.name for x in Path(d).iterdir()),['output'])
    def test_exact_replacement(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(m.os,'fchown'):
            p=Path(d)/'output';p.write_bytes(b'before')
            m.write(p,b'after',previous=b'before')
            self.assertEqual(p.read_bytes(),b'after')
            with self.assertRaises(ValueError):m.write(p,b'wrong',previous=b'before')
            self.assertEqual(p.read_bytes(),b'after')
    def test_symlinks_reject_and_target_unchanged(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(m.os,'fchown'):
            target=Path(d)/'target';target.write_bytes(b'before')
            p=Path(d)/'link';p.symlink_to(target)
            for previous in (None,b'before'):
                with self.assertRaises(ValueError):m.write(p,b'wrong',previous=previous)
            self.assertEqual(target.read_bytes(),b'before')
            p.unlink();p.symlink_to(Path(d)/'absent')
            with self.assertRaises(ValueError):m.write(p,b'wrong')
    def test_failed_replace_cleans_owned_temporary(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(m.os,'fchown'):
            p=Path(d)/'output';p.write_bytes(b'before')
            with mock.patch.object(m.os,'replace',side_effect=OSError('synthetic')):
                with self.assertRaises(OSError):m.write(p,b'after',previous=b'before')
            self.assertEqual(p.read_bytes(),b'before')
            self.assertEqual(sorted(x.name for x in Path(d).iterdir()),['output'])
class IndependentBundleTests(unittest.TestCase):
    def bundle(self):
        import base64, sys
        root=Path(__file__).resolve().parents[1]
        sys.path.insert(0,str(root/'nginx-log-privacy-config'))
        import render_closure as r
        src=root.parents[1]/'doc/php83/evidence/nginx-r3-privacy/sources/opt/kaltura/nginx/conf'
        rendered=r.render({n:(src/n).read_bytes() for n in r.PINS})
        gs=importlib.util.spec_from_file_location('generator_review',root/'nginx-service-integration/generate.py')
        g=importlib.util.module_from_spec(gs);gs.loader.exec_module(g)
        enc=lambda b:base64.b64encode(b).decode()
        return {'old_helper':enc((root/'pilot83/nginx-first-start.py').read_bytes()),
                'rendered':{n:enc(b) for n,b in rendered.items()},
                'modules':{n:enc((root/d/n).read_bytes()) for n,d in [('service.py','nginx-service-integration'),('lab_adapter.py','nginx-log-privacy-supervisor'),('sanitizer.py','nginx-log-privacy')]},
                'init':enc(g.INIT.encode()),'unit':enc(g.UNIT.encode())}
    def test_pins_join_actual_reviewed_outputs(self):
        b=self.bundle()
        for key,pins in [('rendered',m.RENDER_PINS),('modules',m.MODULE_PINS)]:
            self.assertEqual(set(b[key]),set(pins))
            for n,pin in pins.items():m.decode(b[key][n],pin)
        m.decode(b['init'],m.INIT_PIN);m.decode(b['unit'],m.UNIT_PIN)
    def test_omissions_rejected_before_guest_guard(self):
        for key,name in [('rendered','main.conf'),('rendered','http.conf'),('modules','sanitizer.py')]:
            b=self.bundle();b[key].pop(name)
            with mock.patch.object(m.Path,'mkdir') as create,mock.patch.object(m,'write') as write:
                with self.assertRaises(ValueError):m.deploy(b)
                create.assert_not_called();write.assert_not_called()
    def test_drift_and_unknown_rejected_before_guest_guard(self):
        cases=[]
        b=self.bundle();b['extra']='x';cases.append(b)
        b=self.bundle();b['rendered']['main.conf']='eA==';cases.append(b)
        b=self.bundle();b['modules']['service.py']+='!';cases.append(b)
        for b in cases:
            with mock.patch.object(m.Path,'mkdir') as create,mock.patch.object(m,'write') as write:
                with self.assertRaises(ValueError):m.deploy(b)
                create.assert_not_called();write.assert_not_called()
if __name__=='__main__':unittest.main()

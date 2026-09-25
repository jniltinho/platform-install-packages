"""Offline classification and identity negative tests; no PHP execution."""
import importlib.util
import json
from unittest.mock import patch
from pathlib import Path
import tempfile
import unittest
import zipfile

spec=importlib.util.spec_from_file_location('compiler_triage',Path(__file__).with_name('build.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


def diagnostic(message, path='a.php', line=1, severity='Fatal error'):
    return f'{severity}: {message} in {path} on line {line}\n'


class CompilerTriageTests(unittest.TestCase):
    def test_curly_offset_and_object_property(self):
        message='Array and string offset access syntax with curly braces is no longer supported'
        for text in ['$x{0};', '$this->buffer{$this->bufferPos};', "$attr['size']{0};"]:
            self.assertEqual(b.classify('a.php',diagnostic(message),text)[0],'removed_curly_brace_offset')

    def test_curly_diagnostic_without_corresponding_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'source-unsubstantiated'):
            b.classify('a.php',diagnostic('Array and string offset access syntax with curly braces is no longer supported'),'$x[0];')

    def test_ternary(self):
        self.assertEqual(b.classify('a.php',diagnostic('Unparenthesized `a ? b : c ? d : e` is not supported.'),'$x = $a ? $b :\n$c ? $d : $e;')[0],'unparenthesized_nested_ternary')

    def test_autoload(self):
        self.assertEqual(b.classify('a.php',diagnostic('__autoload() is no longer supported'),'function __autoload($class) {}')[0],'removed_autoload_declaration')

    def test_reserved_object_alias(self):
        self.assertEqual(b.classify('a.php',diagnostic("Cannot use Riak\\Object as Object because 'Object' is a special class name"),'use Riak\\Object;')[0],'reserved_object_import_alias')

    def test_template_class_token(self):
        path='vendor/symfony-data/skeleton/module/module/actions/actions.class.php'
        category,_,_,placeholders=b.classify(path,diagnostic('syntax error',path,2,'Parse error'),'class ##MODULE_NAME##Actions extends sfActions\n{\n}')
        self.assertEqual(category,'unexpanded_generator_skeleton_placeholder')
        self.assertEqual(placeholders[0]['line'],1)

    def test_template_debug_token(self):
        path='vendor/symfony-data/skeleton/controller/controller.php'
        text="define('SF_DEBUG',       ##DEBUG##);\nrequire_once('config.php');"
        self.assertEqual(b.classify(path,diagnostic('syntax error',path,2,'Parse error'),text)[0],'unexpanded_generator_skeleton_placeholder')

    def test_template_path_alone_does_not_classify(self):
        path='vendor/symfony-data/skeleton/controller/controller.php'
        with self.assertRaisesRegex(ValueError,'source-unsubstantiated'):
            b.classify(path,diagnostic('syntax error',path,1,'Parse error'),"define('SF_DEBUG', false);")

    def test_diagnostic_path_and_line_mismatch(self):
        for d in [diagnostic('__autoload() is no longer supported','other.php'),diagnostic('__autoload() is no longer supported',line=2)]:
            with self.assertRaises(ValueError):b.classify('a.php',d,'function __autoload($x) {}')

    def test_unknown_compiler_cause_not_silently_waived(self):
        with self.assertRaisesRegex(ValueError,'source-unsubstantiated'):
            b.classify('a.php',diagnostic('unknown new error'),'<?php')

    def test_duplicate_evidence_paths_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate evidence'):
            b.indexed([{'path':'x'},{'path':'x'}])

    def test_source_path_escape_rejected(self):
        for path in ['../a.php','/a.php','a/../x.php','a\\b.php']:
            with self.assertRaises(ValueError):b.safe_path(path)

    def test_exact_baseline_join_distinguishes_new_and_retained(self):
        package={'sha256':'a'*64,'owners':[{'package_file':'example.deb'}]}
        historical={'sha256':'a'*64,'php83_returncode':255,'classification':'reported'}
        for code,expected in [(0,'new_php83_rejection'),(255,'baseline_rejection_retained')]:
            joined=b.historical_join('a.php','a'*64,package,{**historical,'php74_returncode':code})
            self.assertEqual(joined['baseline_classification'],expected)

    def test_different_candidate_bytes_never_inherit_baseline(self):
        joined=b.historical_join('a.php','b'*64,{'sha256':'a'*64},{'sha256':'a'*64})
        self.assertEqual(joined['status'],'not_comparable_different_candidate_bytes')
        self.assertIsNone(joined['baseline_classification'])

    def test_package_historical_conflict_rejected(self):
        with self.assertRaisesRegex(ValueError,'Conflicting historical/package bytes'):
            b.historical_join('a.php','a'*64,{'sha256':'a'*64},{'sha256':'b'*64})

    def test_missing_history_stays_unresolved(self):
        self.assertEqual(b.historical_join('a.php','a'*64,{},None)['status'],'unresolved_missing_evidence')

    def test_historical_invalid_exit_codes_and_types_rejected(self):
        package={'sha256':'a'*64,'owners':[]}
        base={'sha256':'a'*64,'php74_returncode':0,'php83_returncode':255,'classification':'reported'}
        for field in ('php74_returncode','php83_returncode'):
            for value in (124,-9,1,True,False,0.0,255.0,'255',None):
                with self.subTest(field=field,value=value), self.assertRaisesRegex(ValueError,'exit status invalid'):
                    b.historical_join('a.php','a'*64,package,{**base,field:value})
        with self.assertRaisesRegex(ValueError,'exit status invalid'):
            b.historical_join('a.php','a'*64,package,{**base,'php83_returncode':0})

    def test_paired_scan_invalid_exit_codes_and_types_rejected(self):
        # Reach build()'s real status guard with minimal local evidence. No archive
        # or subprocess operation should be reached when the scan is invalid.
        with tempfile.TemporaryDirectory() as directory:
            repo=Path(directory)
            documents={
                'doc/php83/evidence/source-audit/php74-vs-php83-compile.json':{},
                'doc/php83/evidence/package-identities/primary.json':{'original_archive_sha256':b.ORIGINAL},
                'doc/php83/evidence/compiler-triage/coverage.json':{},
                'doc/php83/evidence/exp9-candidate/manifest.json':{},
                'patches/php83/held/symfony-bootstrap.json':{},
            }
            for name,data in documents.items():
                target=repo/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(data))
            scan_path=repo/'doc/php83/evidence/candidate-syntax/primary-r2.json'
            scan_path.parent.mkdir(parents=True)
            for variant in ('original','exp9'):
                for value in (124,-9,1,True,False,0.0,255.0,'255',None):
                    scan={'collection_complete':True,'variants':{
                        'original':{'zip_sha256':b.ORIGINAL,'records':[{'path':'a.php','exit':0}]},
                        'exp9':{'zip_sha256':b.EXP9,'records':[{'path':'a.php','exit':255}]}}}
                    scan['variants'][variant]['records'][0]['exit']=value
                    scan_path.write_text(json.dumps(scan))
                    with self.subTest(variant=variant,value=value), patch.object(b,'archive') as opened:
                        with self.assertRaisesRegex(ValueError,'Paired compiler exit status invalid'):
                            b.build(repo,repo/'missing-source',repo/'missing-original.zip',repo/'missing-exp9.zip')
                        opened.assert_not_called()

    def test_archive_hash_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'source.zip'
            with zipfile.ZipFile(path,'w') as z:z.writestr('x','synthetic')
            with self.assertRaisesRegex(ValueError,'Archive hash mismatch'):b.archive(path,'0'*64)

if __name__=='__main__':unittest.main()

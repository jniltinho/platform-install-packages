import unittest
from build import inspect

class Tests(unittest.TestCase):
    def test_form_feed_keeps_lf_line_number(self):
        r=inspect('vendor/x/LICENSE',b'first\x0cpage\nCopyright Example\n')
        self.assertEqual(r['literal_notice_candidates'][0]['line'],2)
    def test_decode_loss_is_explicit(self):
        r=inspect('vendor/x/a.php',b'Copyright \xa9 Example')
        self.assertTrue(r['decode_replacement_present'])
    def test_variant_notice_full_scan(self):
        for name in ('DejaVu_LICENSE.txt','LICENSE_OFL.txt'):
            r=inspect('vendor/x/'+name,b'\n'*120+b'Permission is hereby granted\n')
            self.assertTrue(r['dedicated_notice_name'])
            self.assertEqual(r['literal_notice_candidates'][0]['line'],121)
    def test_explicit_spdx(self):
        r=inspect('vendor/x/a.php',b'<?php\n// SPDX-License-Identifier: MIT\n')
        self.assertEqual(r['literal_notice_candidates'][0]['line'],2)
        self.assertEqual(r['license_applicability'],'NOT_ADJUDICATED')
    def test_copyright_is_not_license(self):
        r=inspect('vendor/x/a.php',b'// Copyright Example\n')
        self.assertEqual(len(r['literal_notice_candidates']),1)
        self.assertEqual(r['license_applicability'],'NOT_ADJUDICATED')
    def test_header_bound_not_absence(self):
        r=inspect('vendor/x/a.php',b'\n'*100+b'// @license MIT\n')
        self.assertFalse(r['literal_notice_candidates']);self.assertFalse(r['absence_claim'])
    def test_named_notice_full_scan(self):
        r=inspect('vendor/x/LICENSE.txt',b'\n'*120+b'Permission is hereby granted\n')
        self.assertTrue(r['dedicated_notice_name']);self.assertEqual(r['literal_notice_candidates'][0]['line'],121)
    def test_no_neighbor_inheritance(self):
        r=inspect('vendor/x/b.php',b'<?php echo 1;')
        self.assertFalse(r['literal_notice_candidates']);self.assertEqual(r['license_applicability'],'NOT_ADJUDICATED')

if __name__=='__main__':unittest.main()

import unittest
import credential_patterns as c
RAW=b'[datasources]\ndefault=propel\npropel.connection.database=kaltura\npropel.connection.hostspec=localhost\npropel.connection.dsn="mysql:host=localhost;port=3306;dbname=kaltura;"\npropel.connection.password=synthetic1234567890\n'
class Tests(unittest.TestCase):
 def test_positive(self):self.assertEqual(c.native_password(RAW),b'synthetic1234567890');self.assertEqual(len(c.patterns(RAW,b'a'*48)),4)
 def test_printable_native_password(self):
  for secret in (b'Native-Password:123.%*+,?@_/',b'x'*15,b'x'*256):
   self.assertEqual(c.native_password(RAW.replace(b'synthetic1234567890',secret)),secret)
 def test_reject_ambiguous_or_out_of_bounds(self):
  for secret in (b'x'*14,b'x'*257,b'x'*16+b';comment',b'x'*16+b'#comment',b'x'*16+b'\\escape',b'x'*16+b'"',b'x'*16+b' ',b'x'*16+b'\t',b'x'*16+b'\x7f',b'@DB1_PASSWORD_PLACEHOLDER@'):
   with self.subTest(length=len(secret)):
    # Trailing INI whitespace is syntactic, so put whitespace inside the value.
    if secret.endswith((b' ',b'\t')):secret+=b'x'
    with self.assertRaises(c.Rejected):c.native_password(RAW.replace(b'synthetic1234567890',secret))
 def test_ini_interpretation_forms_rejected(self):
  for token in (b"'",b'${ENV}',b'|',b'&',b'~',b'!',b'(',b')',b'^',b'{',b'}',b'=',b'[',b']'):
   with self.assertRaises(c.Rejected):c.native_password(RAW.replace(b'synthetic1234567890',b'privateSynthetic'+token+b'123456'))
 def test_native_syntax_guards(self):
  self.assertEqual(c.native_password(RAW.replace(b'\n',b'\r\n')),b'synthetic1234567890')
  self.assertEqual(c.native_password(RAW.replace(b'=synthetic1234567890',b'="synthetic1234567890"')),b'synthetic1234567890')
  with self.assertRaises(c.Rejected):c.native_password(RAW.replace(b'"mysql:',b'mysql:').replace(b'kaltura;"',b'kaltura;'))
  for v in (b'\x0b',b'\x0c',b'\x1c',b'\r'):
   with self.assertRaises(c.Rejected):c.native_password(RAW+v)
 def test_root_newline_exact(self):
  for raw in (b'a'*48,b'a'*48+b'\n'):
   self.assertIn(b'a'*48,c.patterns(RAW,raw))
  for suffix in (b'\\',b'\\n',b'\n\n',b'\r\n',b' '):
   with self.assertRaises(c.Rejected):c.patterns(RAW,b'a'*48+suffix)
 def test_duplicate(self):
  for suffix in (b'propel.connection.password=otherpassword123456\n',b'[datasources]\n'):
   with self.assertRaises(c.Rejected):c.native_password(RAW+suffix)
 def test_target(self):
  for a,b in [(b'localhost',b'evilhost'),(b'default=propel',b'default=propel2'),(b'synthetic1234567890',b'@DB1_PASS@')]:
   with self.assertRaises(c.Rejected):c.native_password(RAW.replace(a,b))
 def test_root(self):
  for v in (b'bad',b'a'*49,b'A'*48):
   with self.assertRaises(c.Rejected):c.patterns(RAW,v)
 def test_unsupported_encoding(self):
  for v in (RAW+b'\xff',RAW+b'\0',b'x'*131073):
   with self.assertRaises(c.Rejected):c.native_password(v)
if __name__=='__main__':unittest.main()

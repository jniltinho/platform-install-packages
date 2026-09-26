import json,pathlib,unittest
P=pathlib.Path(__file__).with_name('cases.json')
class Cases(unittest.TestCase):
 def setUp(self):self.d=json.loads(P.read_text());self.rows=self.d['cases']
 def test_unique24(self):self.assertEqual(len(self.rows),24);self.assertEqual(len({r['id'] for r in self.rows}),24)
 def test_three_real_callers(self):self.assertEqual({r['caller'] for r in self.rows if 'caller' in r},{'BaseEntryService','MediaService','MixingService'})
 def test_success_count(self):self.assertEqual(sum(r['expected']=='null-return-and-one-kvote-row' for r in self.rows),9)
 def test_omission_count(self):self.assertEqual(sum(r['expected']=='ArgumentCountError-no-write' for r in self.rows),5)
 def test_no_selection(self):self.assertIs(self.d['source_mutation'],False);self.assertEqual(self.d['status'],'PREPARED_NOT_EXECUTED')
if __name__=='__main__':unittest.main()

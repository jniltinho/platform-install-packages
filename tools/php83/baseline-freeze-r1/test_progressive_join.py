import ast,copy,hashlib,json,pathlib,tempfile,unittest
import prepare_progressive_join as p
import run_progressive_join as r
import privacy_provenance as provenance
H=pathlib.Path(__file__).parent
class JoinTests(unittest.TestCase):
 def test_frozen_derivation_and_staged_pins(self):
  self.assertEqual((H/'guest_progressive_join.py').read_text(),p.build())
  for name,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/name).read_bytes()).hexdigest(),pin)
  self.assertTrue({'direct_content.py','privacy_provenance.py'}<=set(r.PINS))
 def test_original_row_kept_and_no_extra_sql(self):
  old=(H/'guest_progressive443.py').read_text();new=p.build()
  sql=lambda s:[ast.dump(n) for n in ast.walk(ast.parse(s)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='sql']
  self.assertEqual(sql(old),sql(new));self.assertIn("selected_rows=[row for row in rows if row[0]=='315']",new);self.assertIn('storage_path=selected_rows[0][5]',new)
 def test_source_alias_before_credentials_and_after(self):
  s=p.build();self.assertEqual(s.count('  direct_source_guard()'),2);self.assertLess(s.index('  direct_source_guard()'),s.index("report['phase']='invalid-nonce'"));self.assertIn('0cc12e21735c3f7e968ceb9fcf35426fab678ce8a68c9fdfc71fd03612ba8ba5',s)
 def test_unchanged_real_credential_scans_and_privacy_bounds(self):
  s=p.build();self.assertIn("audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)",s);self.assertIn('audit_all(rehearsal.patterns(secret,ks,tracked_tokens),start,jstart)',s);self.assertIn('settle.wait_quiet',s);self.assertIn('legacy.logs=lambda:tls_logs.extend(old_logs)',s)
 def test_record_precedes_both_acceptance_sites(self):
  s=p.build();self.assertIn("record_match('files_and_journal',patterns,f,j,number)\n   accepted(f,j)",s);self.assertIn("record_match('files_after_journal',patterns,f,j,number)\n   accepted(f,j)",s)
  self.assertLess(s.index("private_json(private_dir/('matches-'"),s.index("records=report.setdefault('match_provenance'"))
 def test_host_provenance_projection_no_arbitrary_fields(self):
  f={'counts':[1,0],'status':'COMPLETE_FINITE_FILE_WINDOW','uncovered_tail_bytes':0};j={'counts':[0,0],'status':'COMPLETE_FINITE_JOURNAL_WINDOW','cutoff_covered':True,'complete':True}
  value=provenance.receipt(4,'files_and_journal',[b'SYNTHETIC_SECRET_FULL',b'SYNTHETIC_SECRE'],f,j,secret=b'SYNTHETIC_SECRET_FULL')
  self.assertEqual(r.provenance_projection([value]),[value]);self.assertNotIn('SYNTHETIC',json.dumps(r.provenance_projection([value])))
  for mutate in (lambda v:v.update(raw='PRIVATE'),lambda v:v['patterns'][0].update(categories=['PRIVATE']),lambda v:v.update(any_match=False)):
   v=copy.deepcopy(value);mutate(v);self.assertRaises(Exception,r.provenance_projection,[v])
  row={'failure_code':'PRIVATE_MARKER_LOGGED','failure_stage':'BATCH_PRIVACY','match_provenance':[value]};self.assertTrue(r.failure_projection(row)['match_provenance'][0]['any_match'])
 def test_fresh_stage_no_old_resume(self):
  self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-short-progressive-join-r1');self.assertIn('assert not os.path.lexists(stage)',r.REMOTE_GUARD);self.assertIn('baseline-freeze-465479bb.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()

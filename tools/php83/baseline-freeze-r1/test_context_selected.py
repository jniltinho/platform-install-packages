import pathlib,hashlib,unittest
import context_selected as c
import playback_context_r4 as module
import prepare_context_observer_r2 as p
import run_context_observer_r2 as r
H=pathlib.Path(__file__).parent
class Tests(unittest.TestCase):
 def row(self):return dict(id='0_21p06l2j',entryId='0_wzmt2sfy',partnerId='102',status='2',version='2',flavorParamsId='2',size='128',fileExt='mp4',isOriginal=False,tags='ipad')
 def test_canonical_existing_no_api(self):
  for original in [False,0,'0']:
   row=self.row();row['isOriginal']=original;self.assertEqual(module.selected(c.select([row])),'0_21p06l2j')
 def test_noncanonical_or_original_reject(self):
  for k,v in [('isOriginal',True),('isOriginal','1'),('version','02'),('status',True),('size',2.5),('partnerId',' 102'),('tags',{})]:
   row=self.row();row[k]=v
   with self.assertRaises(c.Rejected):c.select([row])
 def test_identity_and_ready_still_required(self):
  for k,v in [('entryId','other'),('partnerId',103),('status',4),('version',0),('flavorParamsId',3),('fileExt','flv')]:
   row=self.row();row[k]=v
   with self.assertRaises(module.Rejected):module.selected(c.select([row]))
 def test_duplicate(self):self.assertRaises(c.Rejected,c.select,[self.row(),self.row()])
 def test_regen_pins(self):
  self.assertEqual(p.build(),(H/'guest_context_observer_r2.py').read_text())
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),pin)
  self.assertIn('baseline-freeze-51a2b804.service',r.REMOTE_GUARD)
 def test_one_context_no_delivery(self):
  s=p.build();self.assertEqual(s.count('context.observe('),1);self.assertNotIn('delivery.progressive(',s);self.assertNotIn("action='getUrl'",s);self.assertIn('selection.select(assets)',s)
 def test_closed_projection(self):
  response=dict(objectType='KalturaPlaybackContext',sources=[],actions=[],messages=[],flavorAssets=[])
  v=module.observe(lambda **kw:response,lambda url:None,c.select([self.row()]));self.assertEqual(r.context_projection(v),v)
  for bad in ['secret',0,{}]:
   x=dict(v);x['selected_hls_tag_match']=bad;self.assertRaises(Exception,r.context_projection,x)
if __name__=='__main__':unittest.main()

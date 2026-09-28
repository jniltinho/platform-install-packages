"""Versioned native serveFlavor GET derivative; historical observers unchanged."""
import hashlib
from pathlib import Path
H=Path(__file__).parent
ROOT=H.parents[2]/'doc/php83/evidence/inventory-closure-r1/.extracted'
SOURCES=['vendor/symfony/controller/sfRouting.class.php','alpha/apps/kaltura/modules/extwidget/actions/serveFlavorAction.class.php','alpha/apps/kaltura/config/routing.yml','api_v3/services/FlavorAssetService.php']
def build():
 raw=(H/'guest_route_observer.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='5268b5544bb601f37d19b3a2a5d9a5f0708a32e20b8a1d3b383fa808340dba3d'
 s=raw.decode();pins={str(Path('/opt/kaltura/app')/p):hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}
 s=s.replace('  route_source_guard()\n',"  route_source_guard()\n  def serve_source_guard():\n   for name,pin in "+repr(pins)+".items():\n    f=Path(name);m=f.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==0 and m.st_nlink==1 and m.st_size<=512*1024 and hashlib.sha256(f.read_bytes()).hexdigest()==pin,'ROUTE_SOURCE_PIN')\n  serve_source_guard()\n",1)
 a=s.index("  try:report['route_observation']");b=s.index("  failure_stage='QUIET_SETTLE'",a)
 mods={n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in ('serve_flavor_guard.py','short_delivery443.py','media_get443.py')}
 block="  for name,pin in "+repr(mods)+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'DELIVERY_PIN')\n"
 block+='''  serve=load('serve_flavor_guard',NEW_HERE/'serve_flavor_guard.py')
  delivery=load('short_delivery443',NEW_HERE/'short_delivery443.py')
  import media_get443
  try:
   native=serve.check(raw_url,expected_filename=expected_filename,secret=secret,ks=ks)
  except serve.Rejected as error:
   # Rejected routes retain ALL candidate patterns for failure scanning.
   try:report['route_observation']=descriptor.describe(raw_url,stored_path=storage_path,expected_filename=expected_filename,secret=secret,ks=ks,candidates=tracked_tokens)
   except descriptor.Rejected:pass
   raise Rejected(str(error) if str(error) in serve.CODES else 'SOURCE_ROUTE_SHAPE') from None
  report['serve_route_join']={'closed_unique_pairs':True,'source_filename_equal':True,'owned_identity_equal':True,'native_url_unchanged':True,'historical_failure_reclassified':False}
  began=time.monotonic()
  def get(url,headers,limit):
   need(time.monotonic()-began<180,'DELIVERY_DEADLINE')
   serve.check(url,expected_filename=expected_filename,secret=secret,ks=ks)
   response=media_get443.request(tls_ca,url,headers,limit)
   need(time.monotonic()-began<180,'DELIVERY_DEADLINE')
   return response
  try:report['progressive'],private_media=delivery.progressive(get,native)
  except delivery.Rejected as error:
   code=str(error);raise Rejected('DELIVERY_'+code if code in ('URL','ORIGIN','TRANSPORT','RESPONSE','STATUS','BODY_LIMIT','HEADERS','HEADER_NAME','DUPLICATE_HEADER','ENCODING_REDIRECT','LENGTH','SOURCE_HASH','CONTENT_RANGE','RANGE_BYTES') else 'DELIVERY_REJECTED') from None
  del private_media,raw_url,native,expected_filename,rows
'''
 s=s[:a]+block+s[b:]
 import importlib.util
 spec=importlib.util.spec_from_file_location('sg',H/'serve_flavor_guard.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES=['+repr(list(m.CODES))[1:-1]+',')
 s=s.replace("  route_source_guard()\n  need(","  route_source_guard()\n  serve_source_guard()\n  need(")
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())

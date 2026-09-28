"""One getUrl descriptor, no GET, no URL persistence, no candidate exemptions."""
import argparse,hashlib
from pathlib import Path
H=Path(__file__).parent
SOURCE_REL=['alpha/lib/model/flavorAsset.php','alpha/lib/model/om/BaseassetPeer.php','alpha/lib/model/om/BaseassetParamsPeer.php','alpha/apps/kaltura/lib/kAssetUtils.class.php','infra/general/kString.class.php']
ROOT=H.parents[2]/'doc/php83/evidence/inventory-closure-r1/.extracted'
CODES=['ROUTE_DESCRIPTOR_PIN','ROUTE_SOURCE_PIN','ROUTE_NAME_ROW','ROUTE_FILENAME_INPUT','ROUTE_URL_SHAPE','ROUTE_PATTERN_LIMIT','ROUTE_RESPONSE_TYPE']
QUERY="SELECT a.id,a.partner_id,a.entry_id,a.flavor_params_id,a.version,a.file_ext,IF(p.id IS NULL,'ABSENT','PRESENT'),HEX(COALESCE(p.name,'')) FROM flavor_asset a LEFT JOIN flavor_params p ON p.id=a.flavor_params_id WHERE a.id='0_ewuu0o46' AND a.partner_id=102 AND a.entry_id='0_wzmt2sfy' LIMIT 2"
def build():
 raw=(H/'guest_progressive_join_r2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='052e9b4ce6f5f5fb6575641a63c7d04d1c30157d58dcecdac4022e3431cfd362'
 s=raw.decode();descriptor_pin=hashlib.sha256((H/'route_descriptor.py').read_bytes()).hexdigest();pins={str(Path('/opt/kaltura/app')/n):hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in SOURCE_REL}
 anchor='  direct_source_guard()\n'
 addition="  need(hashlib.sha256((NEW_HERE/'route_descriptor.py').read_bytes()).hexdigest()=="+repr(descriptor_pin)+",'ROUTE_DESCRIPTOR_PIN')\n  descriptor=load('route_descriptor',NEW_HERE/'route_descriptor.py')\n  def route_source_guard():\n   for name,pin in "+repr(pins)+".items():\n    file=Path(name);meta=file.lstat();need(stat.S_ISREG(meta.st_mode) and meta.st_uid==0 and meta.st_nlink==1 and meta.st_size<=512*1024 and hashlib.sha256(file.read_bytes()).hexdigest()==pin,'ROUTE_SOURCE_PIN')\n  route_source_guard()\n"
 s=s.replace(anchor,anchor+addition,1)
 a=s.index("  report['phase']='short-progressive'");b=s.index("  failure_stage='QUIET_SETTLE'",a)
 block="  report['phase']='native-route-observation';failure_stage='API_ROUND'\n"
 block+="  rows=legacy.sql("+repr(QUERY)+")\n"
 block+="""  need(len(rows)==1 and len(rows[0])==8 and rows[0][0:6]==['0_ewuu0o46','102','0_wzmt2sfy','0','2','mp4'] and rows[0][6] in ('ABSENT','PRESENT') and re.fullmatch('[0-9A-F]{0,2048}',rows[0][7]) is not None,'ROUTE_NAME_ROW')
  need(str(asset.get('flavorParamsId'))=='0' and asset.get('fileExt')=='mp4','ROUTE_NAME_ROW')
  expected_filename=None
  try:
   params_name=bytes.fromhex(rows[0][7]).decode('utf-8')
   expected_filename=descriptor.filename(entry.get('name'),params_name,'mp4')
  except (ValueError,UnicodeError):pass
  raw_url=call(service='flavorasset',action='getUrl',ks=ks,id='0_ewuu0o46')
  need(type(raw_url) is str,'ROUTE_RESPONSE_TYPE')
  guard=load('url_privacy',NEW_HERE/'url_privacy.py')
  report['native_url_shape']=guard.shape(raw_url)
  try:report['route_observation']=descriptor.describe(raw_url,stored_path=storage_path,expected_filename=expected_filename,secret=secret,ks=ks,candidates=tracked_tokens)
  except descriptor.Rejected as error:raise Rejected(str(error) if str(error) in ('ROUTE_URL_SHAPE','ROUTE_PATTERN_LIMIT') else 'ROUTE_URL_SHAPE') from None
  private_json(private_dir/'route-descriptor.json',report['route_observation'])
  del raw_url,expected_filename,rows
"""
 s=s[:a]+block+s[b:]
 s=s.replace("  report['direct_content_join']={'file_sync_id':315,'source_grammar_verified':True,'stored_source_bytes_verified':True,'native_url_unchanged':True,'historical_failure_reclassified':False}","  route_source_guard()")
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES=['+repr(CODES)[1:-1]+',')
 return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();s=build()
 with Path(a.output).open('x') as f:f.write(s)
 print(hashlib.sha256(s.encode()).hexdigest())

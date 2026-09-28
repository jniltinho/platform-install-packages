"""One native getUrl plus three progressive GETs inside existing TLS privacy lifecycle."""
import argparse,hashlib
from pathlib import Path
H=Path(__file__).parent
def build():
 raw=(H/'guest_metadata.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='34045ad35098b834866ab0dbc29108858d327c61807915ef182ac52dcdc87462'
 s=raw.decode();a=s.index("  report['phase']='short-flavor-metadata'");b=s.index("  failure_stage='QUIET_SETTLE'",a)
 pins={n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in ['short_delivery.py','media_get.py','url_privacy.py']}
 assert pins['short_delivery.py']=='ee144fa2a27e9b86e6cfb6257965cbec47970b3217df255376198fdc661ab72e'
 block="  report['phase']='short-progressive';failure_stage='API_ROUND'\n"
 block+="  for name,pin in "+repr(pins)+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'DELIVERY_PIN')\n"
 block+="""  delivery=load('short_delivery',NEW_HERE/'short_delivery.py')
  guard=load('url_privacy',NEW_HERE/'url_privacy.py')
  # Import by stable module name so the private spawn worker remains importable.
  import media_get
  began=time.monotonic()
  def native_call(**form):
   result=call(ks=ks,**form)
   report['native_url_shape']=guard.shape(result)
   try:return guard.inspect(result,secret,ks,tracked_tokens)
   except guard.Rejected as error:
    code=str(error)
    raise Rejected(code if code in ('URL_SHAPE','URL_PATTERN_LIMIT','URL_CREDENTIAL','URL_AUTH_SHAPE') else 'URL_SHAPE') from None
  def get(url,headers,limit):
   need(time.monotonic()-began<180,'DELIVERY_DEADLINE')
   guard.inspect(url,secret,ks,tracked_tokens)
   result=media_get.request(tls_ca,url,headers,limit)
   need(time.monotonic()-began<180,'DELIVERY_DEADLINE')
   return result
  try:
   # Keep API shape failures separate; no exception/message or URL enters receipt.
   native=native_call(service='flavorasset',action='getUrl',id=delivery.ASSET)
   url=delivery.target(native)
   report['progressive'],private_media=delivery.progressive(get,url)
   del private_media,url,native
  except delivery.Rejected as error:
   code=str(error)
   raise Rejected('DELIVERY_'+code if code in ('URL','ORIGIN','TRANSPORT','RESPONSE','STATUS','BODY_LIMIT','HEADERS','HEADER_NAME','DUPLICATE_HEADER','ENCODING_REDIRECT','LENGTH','SOURCE_HASH','CONTENT_RANGE','RANGE_BYTES') else 'DELIVERY_REJECTED') from None
"""
 s=s[:a]+block+s[b:]
 codes=['DELIVERY_PIN','DELIVERY_DEADLINE','DELIVERY_REJECTED','URL_SHAPE','URL_PATTERN_LIMIT','URL_CREDENTIAL','URL_AUTH_SHAPE']+['DELIVERY_'+v for v in ['URL','ORIGIN','TRANSPORT','RESPONSE','STATUS','BODY_LIMIT','HEADERS','HEADER_NAME','DUPLICATE_HEADER','ENCODING_REDIRECT','LENGTH','SOURCE_HASH','CONTENT_RANGE','RANGE_BYTES']]
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES=['+repr(codes)[1:-1]+',')
 return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();s=build()
 with Path(a.output).open('x') as f:f.write(s)
 print(hashlib.sha256(s.encode()).hexdigest())

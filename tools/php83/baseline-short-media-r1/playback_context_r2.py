"""No-GET native playback-context observation. Caller owns TLS/auth/privacy.
URL callback only enrolls private response values for privacy checking; it MUST
NOT request those URLs. This module never approves transmission or prints URLs.
"""
ENTRY='0_wzmt2sfy'
ASSET='0_ewuu0o46'
class Rejected(ValueError):pass

def need(ok,code):
 if not ok:raise Rejected(code)

def observe(call,private_url):
 try:
  value=call(service='baseentry',action='getPlaybackContext',entryId=ENTRY,
   **{'contextDataParams:objectType':'KalturaPlaybackContextOptions',
      'contextDataParams:flavorAssetId':ASSET,'contextDataParams:streamerType':'applehttp',
      'contextDataParams:mediaProtocol':'https'})
 except Exception:raise Rejected('CONTEXT_CALL') from None
 need(type(value) is dict and value.get('objectType')=='KalturaPlaybackContext','CONTEXT_TYPE')
 sources=value.get('sources')
 need(type(sources) is list and len(sources)<=16,'URL_ENROLLMENT_INCOMPLETE')
 # Enroll the complete bounded URL list BEFORE metadata rejection, including
 # rows with malformed non-URL metadata. Any uncovered URL prevents privacy PASS.
 complete=True
 for row in sources:
  url=row.get('url') if type(row) is dict else None
  if type(url) is not str or not 0<len(url)<=8192:
   complete=False;continue
  try:private_url(url)
  except Exception:complete=False
 need(complete,'URL_ENROLLMENT_INCOMPLETE')
 eligible=0
 for row in sources:
  need(row.get('objectType')=='KalturaPlaybackSource','SOURCE_TYPE')
  formats=row.get('format');protocols=row.get('protocols');flavors=row.get('flavorIds')
  need(type(formats) is str and len(formats)<=64 and type(protocols) is str and len(protocols)<=64 and type(flavors) is str and len(flavors)<=2048,'SOURCE_FIELDS')
  # This is a descriptor count, NOT URL origin/auth/profile authorization.
  if formats=='applehttp' and 'https' in protocols.split(',') and flavors.split(',')==[ASSET]:eligible+=1
 for key in ('actions','messages','flavorAssets'):
  need(type(value.get(key)) is list and len(value[key])<=100,'CONTEXT_ARRAY')
 return {'case':'NATIVE_HLS_CONTEXT_NO_GET','api_calls':1,'sources':len(sources),
  'original_https_hls_descriptors':eligible,'actions':len(value['actions']),
  'messages':len(value['messages']),'flavor_assets':len(value['flavorAssets']),
  'delivery_authorized':False,'hls_fetched':False,'decoded':False,'full_acceptance':False}

"""No-GET native playback-context observation. Caller owns TLS/auth/privacy.
URL callback only enrolls private response values for privacy checking; it MUST
NOT request those URLs. This module never approves transmission or prints URLs.
"""
ENTRY='0_wzmt2sfy'
KNOWN={'0_21p06l2j':2,'0_afjr7pyj':3,'0_lcy0x0op':4}
class Rejected(ValueError):pass

def need(ok,code):
 if not ok:raise Rejected(code)

def selected(row):
 need(type(row) is dict,'SELECTED_ASSET')
 ident=row.get('id')
 need(type(ident) is str and ident in KNOWN,'SELECTED_ASSET')
 expected={'entryId':ENTRY,'partnerId':102,'status':2,'isOriginal':False,'version':2,'flavorParamsId':KNOWN[ident],'fileExt':'mp4'}
 need(all(type(row.get(k)) is type(v) and row[k]==v for k,v in expected.items()),'SELECTED_ASSET')
 need(type(row.get('size')) is int and 0<row['size']<=2048,'SELECTED_SIZE')
 return ident

def tag_match(row):
 # Tags may be absent from the already-projected metadata. Do not infer them.
 if 'tags' not in row:return None
 value=row['tags'];need(type(value) is str and len(value)<=1024,'SELECTED_TAGS')
 tags=value.split(',');need(len(tags)<=128,'SELECTED_TAGS')
 return bool(set(tags)&{'applembr','ipadnew','iphonenew','h265','dash','ipad','iphone'})

def observe(call,private_url,asset_row):
 asset=selected(asset_row);tags_match=tag_match(asset_row)
 try:
  value=call(service='baseentry',action='getPlaybackContext',entryId=ENTRY,
   **{'contextDataParams:objectType':'KalturaPlaybackContextOptions',
      'contextDataParams:flavorAssetId':asset,'contextDataParams:streamerType':'applehttp',
      'contextDataParams:mediaProtocol':'https'})
 except Exception:raise Rejected('CONTEXT_CALL') from None
 need(type(value) is dict and value.get('objectType')=='KalturaPlaybackContext','CONTEXT_TYPE')
 sources=value.get('sources')
 need(type(sources) is list and len(sources)<=16,'URL_ENROLLMENT_INCOMPLETE')
 # Enroll the complete bounded URL list BEFORE metadata rejection, including
 # rows with malformed non-URL metadata. Uncovered source URL prevents successful source enrollment; this is not a complete response privacy claim.
 complete=True
 for row in sources:
  url=row.get('url') if type(row) is dict else None
  if type(url) is not str or not 0<len(url)<=8192:
   complete=False;continue
  try:private_url(url)
  except Exception:complete=False
 need(complete,'URL_ENROLLMENT_INCOMPLETE')
 need(set(value)<= {'objectType','sources','actions','messages','flavorAssets','playbackCaptions','bumperData'},'RESPONSE_COVERAGE_INCOMPLETE')
 for field in ('playbackCaptions','bumperData'):
  need(value.get(field) is None or value[field]==[],'RESPONSE_COVERAGE_INCOMPLETE')
 for row in sources:
  need(set(row)<= {'objectType','deliveryProfileId','format','protocols','flavorIds','url','drm'},'RESPONSE_COVERAGE_INCOMPLETE')
  need(row.get('drm') is None or row['drm']==[],'RESPONSE_COVERAGE_INCOMPLETE')
 eligible=0
 for row in sources:
  need(row.get('objectType')=='KalturaPlaybackSource','SOURCE_TYPE')
  formats=row.get('format');protocols=row.get('protocols');flavors=row.get('flavorIds')
  need(type(formats) is str and len(formats)<=64 and type(protocols) is str and len(protocols)<=64 and type(flavors) is str and len(flavors)<=2048,'SOURCE_FIELDS')
  # This is a descriptor count, NOT URL origin/auth/profile authorization.
  if formats=='applehttp' and 'https' in protocols.split(',') and flavors.split(',')==[asset]:eligible+=1
 for key in ('actions','messages','flavorAssets'):
  need(type(value.get(key)) is list and len(value[key])<=100,'CONTEXT_ARRAY')
 return {'case':'NATIVE_HLS_CONTEXT_NO_GET','api_calls':1,'sources':len(sources),
  'selected_hls_tag_match':tags_match,'selected_https_hls_descriptors':eligible,'actions':len(value['actions']),
  'messages':len(value['messages']),'flavor_assets':len(value['flavorAssets']),
  'response_secret_coverage_complete':False,'delivery_authorized':False,'hls_fetched':False,'decoded':False,'full_acceptance':False}

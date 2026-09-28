"""Owned two manifests plus five source-guarded TS segments and private local decode."""
import hls_media8444 as manifests
import hls_segments as segments
import hls_decode_r3 as decoder
class Rejected(ValueError):pass
CODES=(*manifests.CODES,*segments.CODES,*decoder.CODES,'HLS_DELIVERY_SCHEMA')
def need(ok):
 if not ok:raise Rejected('HLS_DELIVERY_SCHEMA')
def observe(call,enroll,get443,get8444,secret,ks,asset,expected_id,describe,segment_describe):
 captured=[]
 def capture(url,headers,limit):
  response=get8444(url,headers,limit);captured.append((url,response));return response
 try:
  ctx,media=manifests.observe(call,enroll,get443,capture,secret,ks,asset,expected_id,describe)
  need(len(captured)==1)
  url,response=captured[0]
  targets=segments.parse(response[2],url,secret,ks,lambda value:segment_describe('ROUTES',value))
  fetched,payload=segments.fetch(get8444,targets,media['master_bytes']+media['media_bytes'],lambda value:segment_describe('TRANSFER',value))
  decoded=decoder.decode(payload,lambda value:segment_describe('DECODE',value))
 except (manifests.Rejected,segments.Rejected,decoder.Rejected) as error:
  raise Rejected(str(error) if str(error) in CODES else 'HLS_DELIVERY_SCHEMA') from None
 return ctx,{'case':'OWNED_HLS_TS_FETCH_AND_LOCAL_DECODE','profile_id':expected_id,'requests':7,'manifests':media,'segments':fetched,'decode':decoded,'response_secret_coverage_complete':False,'full_acceptance':False}

def diagnostics(v):
 need(type(v) is dict and set(v)<= {'ROUTES','TRANSFER','DECODE'} and bool(v));out={}
 if 'DECODE' in v:
  import decode_diagnostic_r3 as decode_diagnostic
  out['DECODE']=decode_diagnostic.validate(v['DECODE'])
 if 'ROUTES' in v:
  row=v['ROUTES'];need(type(row) is dict and set(row)=={'references','values_exported'} and row['values_exported'] is False and type(row['references']) is list and 1<=len(row['references'])<=5)
  for i,r in enumerate(row['references'],1):
   need(type(r) is dict and set(r)=={'ordinal','absolute_reference','expected_parent','expected_sequence_tracks','encoding_or_delimiter_present'} and type(r['ordinal']) is int and r['ordinal']==i and all(type(r[k]) is bool for k in ('absolute_reference','expected_parent','expected_sequence_tracks','encoding_or_delimiter_present')))
  out['ROUTES']=row
 if 'TRANSFER' in v:
  row=v['TRANSFER'];need(type(row) is dict and set(row)=={'segments_received','segment_bytes_received'} and type(row['segments_received']) is int and 1<=row['segments_received']<=5 and type(row['segment_bytes_received']) is int and 0<row['segment_bytes_received']<=2*1024*1024);out['TRANSFER']=row
 return out

def validate(v):
 need(type(v) is dict and set(v)=={'case','profile_id','requests','manifests','segments','decode','response_secret_coverage_complete','full_acceptance'} and v['case']=='OWNED_HLS_TS_FETCH_AND_LOCAL_DECODE' and type(v['requests']) is int and v['requests']==7 and v['response_secret_coverage_complete'] is False and v['full_acceptance'] is False)
 media=manifests.validate(v['manifests']);need(type(v['profile_id']) is int and v['profile_id']==media['profile_id'])
 f=v['segments'];need(type(f) is dict and set(f)=={'segments','requests','segment_bytes','total_bytes','transport_stream_framing_verified','full_acceptance'})
 need(type(f['segments']) is int and f['segments']==5 and type(f['requests']) is int and f['requests']==5 and type(f['segment_bytes']) is int and 0<f['segment_bytes']<=2*1024*1024 and type(f['total_bytes']) is int and f['total_bytes']==f['segment_bytes']+media['master_bytes']+media['media_bytes'] and f['total_bytes']<=2*1024*1024 and f['transport_stream_framing_verified'] is True and f['full_acceptance'] is False)
 d=v['decode'];need(type(d) is dict and set(d)=={'case','metadata','full_decode_verified','decoded_stream_scope','auxiliary_metadata_payload_verified','dynamic_library_cohort_attested','profile_golden_equivalence','full_acceptance'} and d['case']=='FETCHED_TS_FULL_LOCAL_DECODE' and d['full_decode_verified'] is True and d['decoded_stream_scope']=='ONE_VIDEO_ONE_AUDIO' and d['auxiliary_metadata_payload_verified'] is False and all(d[k] is False for k in ('dynamic_library_cohort_attested','profile_golden_equivalence','full_acceptance')))
 m=d['metadata'];limits={'auxiliary_timed_id3_streams':(0,1),'width':(1,4096),'height':(1,2160),'video_frames':(1,6000),'fps_numerator':(1,120000000),'fps_denominator':(1,100000000),'duration_milliseconds':(1,120000),'audio_sample_rate':(8000,192000),'audio_channels':(1,8)}
 need(type(m) is dict and set(m)==set(limits)|{'video_codec','audio_codec'} and m['video_codec']=='h264' and m['audio_codec']=='aac')
 need(all(type(m[k]) is int and lo<=m[k]<=hi for k,(lo,hi) in limits.items()))
 return v

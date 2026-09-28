"""One context, one master443, one source-bound media playlist8444; no segments."""
import playback_context_r4 as context
import hls_source_r2 as source
import hls_nested8444 as nested
import hls_playlist_bridge as playlist
import hls_response as response_check
import manifest_diagnostic as diagnostic
import nested_descriptor
class Rejected(ValueError):pass
CODES=('HLS_CONTEXT_REJECTED','HLS_PROFILE_JOIN','HLS_ACCESS_ACTIONS','HLS_MASTER_REJECTED','HLS_MEDIA_REJECTED','HLS_REFERENCE_ENROLLMENT','HLS_MASTER_CARDINALITY',*nested.CODES)
def need(ok,code):
 if not ok:raise Rejected(code)
def observe(call,enroll,request443,request8444,secret,ks,asset,expected_id,describe):
 captured=[];urls=[]
 def capture(**form):v=call(**form);captured.append(v);return v
 try:
  ctx=context.observe(capture,urls.append,asset)
  need(ctx['sources']==1 and len(captured)==1,'HLS_PROFILE_JOIN')
  need(ctx['actions']==ctx['messages']==0,'HLS_ACCESS_ACTIONS')
  row=captured[0]['sources'][0];need(type(row.get('deliveryProfileId')) in (str,int) and str(row['deliveryProfileId'])==str(expected_id),'HLS_PROFILE_JOIN')
  master=source.guard(row,secret,ks)
 except Exception as e:
  for url in urls:
   try:enroll(url)
   except Exception:pass
  if type(e) is Rejected:raise
  raise Rejected('HLS_CONTEXT_REJECTED') from None
 response=None
 try:
  response=request443(master,{'Accept-Encoding':'identity'},65536);describe('MASTER',diagnostic.project(response))
  _,body=response_check.validate(response)
  refs=nested_descriptor.observe(body,master,enroll);need(refs['candidate_enrollment_complete'],'HLS_REFERENCE_ENROLLMENT')
  kind,targets=playlist.playlist(body,master);need(kind=='master' and len(targets)==1,'HLS_MASTER_CARDINALITY')
  target=nested.guard(targets[0],secret,ks)
 except (response_check.Rejected,playlist.Rejected) as e:
  describe('MASTER',diagnostic.project(response,str(e) if str(e) in diagnostic.REASONS else 'UNKNOWN'));raise Rejected('HLS_MASTER_REJECTED') from None
 except nested.Rejected as e:raise Rejected(str(e) if str(e) in nested.CODES else 'NESTED_ROUTE_KEY') from None
 except nested_descriptor.Incomplete:raise Rejected('HLS_REFERENCE_ENROLLMENT') from None
 except Rejected:raise
 except Exception:
  describe('MASTER',diagnostic.project(response,'TRANSPORT'));raise Rejected('HLS_MASTER_REJECTED') from None
 # The second response is observed, not segment-route/complete-HLS acceptance.
 media=None
 try:
  media=request8444(target,{'Accept-Encoding':'identity'},65536);facts=diagnostic.project(media);describe('MEDIA',facts)
  _,body=response_check.validate(media)
  refs=nested_descriptor.observe(body,target,enroll);need(refs['candidate_enrollment_complete'],'HLS_REFERENCE_ENROLLMENT')
  need(facts['extm3u_first_line'] and not facts['line_limit_exceeded'] and 0<facts['uri_lines']<=32 and facts['tag_counts']['EXTINF']>0,'HLS_MEDIA_REJECTED')
 except Rejected:raise
 except Exception as e:
  reason=str(e) if type(e) is response_check.Rejected and str(e) in diagnostic.REASONS else 'TRANSPORT'
  describe('MEDIA',diagnostic.project(media,reason));raise Rejected('HLS_MEDIA_REJECTED') from None
 return ctx,{'case':'NATIVE_HLS_MASTER_AND_MEDIA_OBSERVED','profile_id':expected_id,'requests':2,'master_bytes':len(response[2]),'media_bytes':len(body),'media_references_declared':facts['uri_lines'],'segments_requested':0,'media_playlist_semantics_verified':False,'segment_routes_authorized':False,'decoded':False,'response_secret_coverage_complete':False,'full_acceptance':False}

def validate(v):
 keys={'case','profile_id','requests','master_bytes','media_bytes','media_references_declared','segments_requested','media_playlist_semantics_verified','segment_routes_authorized','decoded','response_secret_coverage_complete','full_acceptance'}
 need(type(v) is dict and set(v)==keys,'HLS_RESULT')
 need(v['case']=='NATIVE_HLS_MASTER_AND_MEDIA_OBSERVED','HLS_RESULT')
 for k,lo,hi in [('profile_id',1,2147483647),('requests',2,2),('master_bytes',1,65536),('media_bytes',1,65536),('media_references_declared',1,32),('segments_requested',0,0)]:need(type(v[k]) is int and lo<=v[k]<=hi,'HLS_RESULT')
 for k in ('media_playlist_semantics_verified','segment_routes_authorized','decoded','response_secret_coverage_complete','full_acceptance'):need(v[k] is False,'HLS_RESULT')
 return dict(v)
def diagnostics(v):
 need(type(v) is dict and set(v)<= {'MASTER','MEDIA'} and bool(v),'HLS_RESULT')
 return {k:diagnostic.validate(x) for k,x in v.items()}

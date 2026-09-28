"""One source-bound manifest GET; references remain private and unfetched."""
import playback_context_r4 as context
import hls_source_r2 as hls_source
import short_delivery443 as delivery
import manifest_diagnostic as diag
class Rejected(ValueError):pass
CODES=('HLS_CONTEXT','HLS_CONTEXT_COVERAGE','HLS_SOURCE_COUNT','HLS_ACCESS_ACTIONS','HLS_SOURCE_GUARD','HLS_REFERENCE_ENROLLMENT','HLS_MANIFEST_REJECTED')
def observe(call,enroll,request,secret,ks,asset,describe,diagnose):
 captured=[];urls=[]
 def capture(**form):
  value=call(**form);captured.append(value);return value
 def save_url(url):urls.append(url)
 try:ctx=context.observe(capture,save_url,asset)
 except context.Rejected:
  for url in urls:
   try:enroll(url)
   except Exception:pass
  raise Rejected('HLS_CONTEXT_COVERAGE') from None
 try:
  if len(captured)!=1 or len(captured[0]['sources'])!=1:raise Rejected('HLS_SOURCE_COUNT')
  if ctx['actions']!=0 or ctx['messages']!=0:raise Rejected('HLS_ACCESS_ACTIONS')
  target=hls_source.guard(captured[0]['sources'][0],secret,ks)
 except Exception as error:
  for url in urls:
   try:enroll(url)
   except Exception:pass
  if type(error) is Rejected:raise
  raise Rejected('HLS_SOURCE_GUARD') from None
 describe({'route':'NATIVE_PLAYMANIFEST','source_bound':True,'credential_free_fixed_grammar':True,'nested_get_authorized':False})
 # Only the exact source-proven route is excluded from heuristic long-key enrollment.
 # Known current secret/KS patterns remain owned by the caller's complete scans.
 response=None
 diagnose(diag.project())
 try:
  try:response=request(target,{'Accept-Encoding':'identity'},65536)
  except Exception:raise delivery.Rejected('TRANSPORT') from None
  diagnose(diag.project(response))
  _,body=delivery.fetch(lambda *args:response,target,{'Accept-Encoding':'identity'},65536,200)
  kind,refs=delivery.playlist(body,target)
 except delivery.Rejected as error:
  reason=str(error) if str(error) in diag.REASONS else 'UNKNOWN'
  diagnose(diag.project(response,reason));raise Rejected('HLS_MANIFEST_REJECTED') from None
 complete=True
 for ref in refs:
  try:enroll(ref)
  except Exception:complete=False
 if not complete:raise Rejected('HLS_REFERENCE_ENROLLMENT')
 return ctx,{'case':'FIRST_HLS_MANIFEST_ONLY','requests':1,'bytes':len(body),'playlist_kind':kind,'references':len(refs),'nested_requests':0,'decoded':False,'response_secret_coverage_complete':False,'full_acceptance':False}

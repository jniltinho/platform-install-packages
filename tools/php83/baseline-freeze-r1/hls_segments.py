"""Closed five-segment short VOD grammar derived from primary nginx-vod tag1.33."""
import re
from fractions import Fraction
from urllib.parse import urljoin,unquote
import hls_nested8444 as nested
class Rejected(ValueError):pass
CODES=('SEGMENT_MANIFEST_SHAPE','SEGMENT_MANIFEST_TAG','SEGMENT_MANIFEST_ORDER','SEGMENT_CARDINALITY','SEGMENT_DURATION','SEGMENT_CREDENTIAL','SEGMENT_ROUTE','SEGMENT_LIMIT','SEGMENT_FRAMING','SEGMENT_RESPONSE')
def need(ok,code):
 if not ok:raise Rejected(code)
def parse(data,parent,secret,ks,describe):
 nested.guard(parent,secret,ks)
 need(type(data) is bytes and 0<len(data)<=65536,'SEGMENT_MANIFEST_SHAPE')
 try:text=data.decode('ascii')
 except UnicodeError:raise Rejected('SEGMENT_MANIFEST_SHAPE') from None
 need(not any(ord(c)<32 and c not in '\r\n' or ord(c)==127 for c in text),'SEGMENT_MANIFEST_SHAPE')
 lines=text.split('\n');lines=[x[:-1] if x.endswith('\r') else x for x in lines];need(len(lines)<=512 and lines[0]=='#EXTM3U' and all('\r' not in x and len(x)<=8192 for x in lines),'SEGMENT_MANIFEST_SHAPE')
 tags={};refs=[];pending=False;ended=False;duration=Fraction(0);maximum=Fraction(0)
 for line in lines[1:]:
  if not line:continue
  need(not ended,'SEGMENT_MANIFEST_ORDER')
  if line.startswith('#EXTINF:'):
   need(not pending,'SEGMENT_MANIFEST_ORDER');token=line[8:];need(re.fullmatch(r'[0-9]{1,2}(?:\.[0-9]{1,6})?,',token) is not None,'SEGMENT_DURATION');value=Fraction(token[:-1]);need(0<value<=30,'SEGMENT_DURATION');duration+=value;maximum=max(maximum,value);pending=True
  elif line=='#EXT-X-ENDLIST':need(not pending,'SEGMENT_MANIFEST_ORDER');ended=True
  elif line.startswith('#'):
   need(not pending and not refs,'SEGMENT_MANIFEST_ORDER');key,sep,value=line.partition(':');need(sep and key in ('#EXT-X-VERSION','#EXT-X-ALLOW-CACHE','#EXT-X-PLAYLIST-TYPE','#EXT-X-TARGETDURATION','#EXT-X-MEDIA-SEQUENCE') and key not in tags,'SEGMENT_MANIFEST_TAG');tags[key]=value
  else:
   need(pending and len(refs)<5,'SEGMENT_CARDINALITY');refs.append(line);pending=False
 need(ended and not pending and len(refs)==5,'SEGMENT_CARDINALITY')
 need(tags.get('#EXT-X-VERSION')=='3' and tags.get('#EXT-X-ALLOW-CACHE')=='YES' and tags.get('#EXT-X-PLAYLIST-TYPE')=='VOD' and tags.get('#EXT-X-MEDIA-SEQUENCE')=='1','SEGMENT_MANIFEST_TAG')
 need(re.fullmatch('[1-9][0-9]?',tags.get('#EXT-X-TARGETDURATION','')) is not None and int(tags['#EXT-X-TARGETDURATION'])<=30,'SEGMENT_MANIFEST_TAG')
 need(maximum<=int(tags['#EXT-X-TARGETDURATION']),'SEGMENT_DURATION')
 need(Fraction(19,2)<=duration<=Fraction(21,2),'SEGMENT_DURATION')
 base=parent.rsplit('/',1)[0]+'/';targets=[];proofs=[]
 for i,raw in enumerate(refs,1):
  decoded=unquote(unquote(raw))
  need(all(type(v) is str and len(v)>=16 for v in (secret,ks)),'SEGMENT_CREDENTIAL')
  need(not any(t in decoded for v in (secret,ks) for t in (v,v[:15])),'SEGMENT_CREDENTIAL')
  target=urljoin(parent,raw);expected=base+'seg-'+str(i)+'-v1-a1.ts'
  safe=not any(ord(c)<=32 or ord(c)==127 for c in raw) and not any(c in raw for c in ('%','?','#','\\'))
  proof={'ordinal':i,'absolute_reference':raw.startswith('https://'),'expected_parent':target.rsplit('/',1)[0]+'/'==base,'expected_sequence_tracks':target==expected,'encoding_or_delimiter_present':not safe}
  proofs.append(proof);describe({'references':proofs,'values_exported':False})
  need(safe and target==expected and (raw==expected or raw==expected[len(base):]),'SEGMENT_ROUTE');targets.append(target)
 return targets

def fetch(request,targets,initial_bytes,describe):
 import hls_response
 need(type(initial_bytes) is int and 0<initial_bytes<2*1024*1024 and type(targets) is list and len(targets)==5,'SEGMENT_LIMIT')
 total=initial_bytes;payload=[]
 for index,url in enumerate(targets,1):
  remaining=2*1024*1024-total;need(remaining>0,'SEGMENT_LIMIT')
  try:
   response=request(url,{'Accept-Encoding':'identity'},remaining)
   _,data=hls_response.validate(response,remaining)
  except Exception:raise Rejected('SEGMENT_RESPONSE') from None
  need(data and len(data)%188==0 and all(data[i]==0x47 for i in range(0,len(data),188)),'SEGMENT_FRAMING')
  total+=len(data);payload.append(data);describe({'segments_received':index,'segment_bytes_received':sum(map(len,payload))})
 return {'segments':5,'requests':5,'segment_bytes':sum(map(len,payload)),'total_bytes':total,'transport_stream_framing_verified':True,'full_acceptance':False},b''.join(payload)

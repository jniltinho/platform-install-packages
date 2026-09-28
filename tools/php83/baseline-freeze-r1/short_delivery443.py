"""Finite short-media checks with injected privacy-covered TLS transport.
request(url, headers, limit) returns (status, header_pairs, bytes), MUST disable
redirects, verify the pinned CA and enforce an overall deadline <=30 seconds.
No authentication or subprocess execution here; all URLs remain private memory.
"""
import hashlib
import json
import math
import re
from urllib.parse import urlsplit, urljoin

ORIGIN = 'https://192.168.56.74'
ASSET = '0_ewuu0o46'
SIZE = 1511134
SHA = '612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473'
MAX_BODY = 2 * 1024 * 1024

class Rejected(ValueError): pass

def require(ok, code):
    if not ok: raise Rejected(code)

def target(url):
    require(type(url) is str and 0 < len(url) <= 8192 and not any(ord(c)<=32 or ord(c)==127 for c in url) and '\\' not in url,'URL')
    try:
        p=urlsplit(url)
        require(p.scheme=='https' and p.hostname=='192.168.56.74' and (p.port is None or p.port==443) and p.username is None and p.password is None and not p.fragment,'ORIGIN')
    except ValueError: raise Rejected('ORIGIN') from None
    return url

def native_url(call):
    try: value=call(service='flavorasset',action='getUrl',id=ASSET)
    except Exception: raise Rejected('API_CALL') from None
    return target(value)  # Never silently rewrite an HTTP API response to HTTPS.

def fetch(request,url,headers,limit,status):
    target(url)
    try: response=request(url, headers, limit)
    except Exception: raise Rejected('TRANSPORT') from None
    require(type(response) is tuple and len(response)==3,'RESPONSE')
    code,pairs,body=response
    require(type(code) is int and code==status,'STATUS')
    require(type(body) is bytes and len(body)<=limit,'BODY_LIMIT')
    require(type(pairs) in (list,tuple) and len(pairs)<=100,'HEADERS')
    selected={}
    for pair in pairs:
        require(type(pair) in (list,tuple) and len(pair)==2 and all(type(v) is str for v in pair),'HEADERS')
        k,v=pair
        require(re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+",k),'HEADER_NAME')
        k=k.lower()
        require(not any(c in v for c in '\r\n\0'),'HEADERS')
        if k in {'content-length','content-range','content-encoding','location'}:
            require(k not in selected,'DUPLICATE_HEADER');selected[k]=v
    require('location' not in selected and selected.get('content-encoding','identity')=='identity','ENCODING_REDIRECT')
    if 'content-length' in selected:
        require(re.fullmatch(r'0|[1-9][0-9]*',selected['content-length']) and int(selected['content-length'])==len(body),'LENGTH')
    return selected,body

def progressive(request,url):
    """Three finite requests, original source identity then first/last ranges."""
    _,full=fetch(request,url,{'Accept-Encoding':'identity'},MAX_BODY,200)
    require(len(full)==SIZE and hashlib.sha256(full).hexdigest()==SHA,'SOURCE_HASH')
    for start,end in [(0,1023),(SIZE-1024,SIZE-1)]:
        h,b=fetch(request,url,{'Accept-Encoding':'identity','Range':f'bytes={start}-{end}'},1024,206)
        require(h.get('content-range')==f'bytes {start}-{end}/{SIZE}','CONTENT_RANGE')
        require(b==full[start:end+1],'RANGE_BYTES')
    return {'case':'ORIGINAL_PROGRESSIVE','requests':3,'bytes':SIZE,'sha256':SHA,'range_checks':2,'decoded':False,'full_acceptance':False},full

def playlist(data,parent):
    """Closed VOD MPEG-TS subset. Unsupported HLS features fail, never omitted."""
    target(parent);require(type(data) is bytes and len(data)<=65536,'PLAYLIST_SIZE')
    try:
        text=data.decode('utf-8')
        require(not any((ord(c)<32 and c not in '\r\n') or ord(c)==127 or c in '\x85\u2028\u2029' for c in text),'PLAYLIST_CONTROL')
        lines=text.split('\n')
        lines=[line[:-1] if line.endswith('\r') else line for line in lines]
        require(all('\r' not in line for line in lines),'PLAYLIST_CONTROL')
    except UnicodeError: raise Rejected('PLAYLIST_ENCODING') from None
    require(lines and lines[0]=='#EXTM3U' and len(lines)<=512,'PLAYLIST_HEADER')
    refs=[];kind=None;pending=None;ended=False;duration=0
    for line in lines[1:]:
        require(len(line)<=8192 and '\0' not in line,'PLAYLIST_LINE')
        if not line: continue
        if line.startswith('#EXT-X-STREAM-INF:'):
            require(kind in (None,'master') and pending is None and not ended,'PLAYLIST_ORDER')
            kind='master';pending='variant'
        elif line.startswith('#EXTINF:'):
            require(kind in (None,'media') and pending is None and not ended,'PLAYLIST_ORDER')
            token=line[8:].split(',',1)[0]
            require(re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',token),'DURATION')
            value=float(token);require(math.isfinite(value) and 0<value<=120,'DURATION')
            duration+=value;require(duration<=120,'DURATION');kind='media';pending='segment'
        elif line=='#EXT-X-ENDLIST':
            require(kind=='media' and pending is None and not ended,'PLAYLIST_ORDER');ended=True
        elif re.fullmatch(r'#EXT-X-(?:VERSION|TARGETDURATION|MEDIA-SEQUENCE):[0-9]+',line) or line=='#EXT-X-PLAYLIST-TYPE:VOD' or line=='#EXT-X-INDEPENDENT-SEGMENTS':
            pass
        elif line.startswith('#'):
            raise Rejected('HLS_UNSUPPORTED')
        else:
            require(pending is not None and not ended,'PLAYLIST_URI')
            require(not any(ord(c)<=32 or ord(c)==127 for c in line) and '\\' not in line,'PLAYLIST_URI')
            refs.append(target(urljoin(parent,line)));pending=None
            require(len(refs)<=32,'REFERENCE_LIMIT')
    require(refs and pending is None and (kind=='master' or ended),'PLAYLIST_INCOMPLETE')
    return kind,refs

def hls(request,url):
    """At most one master, one media playlist,32segments,total2MiB; no decode claim.
    First listed variant only. Other variants remain explicitly untested.
    """
    _,data=fetch(request,url,{'Accept-Encoding':'identity'},65536,200)
    total=len(data);kind,refs=playlist(data,url);calls=1;variants=0
    if kind=='master':
        variants=len(refs);url=refs[0]
        _,data=fetch(request,url,{'Accept-Encoding':'identity'},65536,200)
        total+=len(data);calls+=1;kind,refs=playlist(data,url)
        require(kind=='media','NESTING')
    payload=[]
    for ref in refs:
        remaining=MAX_BODY-total;require(remaining>0,'TOTAL_LIMIT')
        _,segment=fetch(request,ref,{'Accept-Encoding':'identity'},remaining,200)
        require(segment and len(segment)%188==0 and all(segment[i]==0x47 for i in range(0,len(segment),188)),'TS_FRAMING')
        payload.append(segment);total+=len(segment);calls+=1
    return {'case':'HLS_TS_FETCH','requests':calls,'segments':len(refs),'bytes':total,'variants_declared':variants,'variants_tested':1,'decoded':False,'full_acceptance':False},b''.join(payload)

def probe_projection(data):
    """Validate bounded ffprobe JSON from caller's pinned offline decoder.
    ffprobe metadata is NOT proof of complete ffmpeg decode.
    """
    require(type(data) is bytes and len(data)<=32768,'PROBE_SIZE')
    def pairs(rows):
        result={}
        for k,v in rows:
            require(k not in result,'PROBE_DUPLICATE');result[k]=v
        return result
    try: value=json.loads(data,object_pairs_hook=pairs,parse_constant=lambda _: (_ for _ in ()).throw(Rejected('PROBE_NUMBER')))
    except (ValueError,UnicodeError): raise Rejected('PROBE_JSON') from None
    require(type(value) is dict and type(value.get('streams')) is list and 1<=len(value['streams'])<=4,'PROBE_SCHEMA')
    video=audio=0
    for stream in value['streams']:
        require(type(stream) is dict,'PROBE_SCHEMA')
        typ=stream.get('codec_type');codec=stream.get('codec_name')
        require((typ,codec) in {('video','h264'),('audio','aac')},'PROBE_CODEC')
        if typ=='video':
            video+=1
            require(all(type(stream.get(k)) is int and 0<stream[k]<=4096 for k in ('width','height')),'PROBE_DIMENSIONS')
        else: audio+=1
    require(video==1 and audio<=1,'PROBE_STREAMS')
    return {'video_streams':video,'audio_streams':audio,'probe_metadata_valid':True,'full_decode_verified':False}

"""Closed bounded response facts only; never raw header/body/URL/hash output."""
REASONS={'TRANSPORT','RESPONSE','STATUS','BODY_LIMIT','HEADERS','HEADER_NAME','DUPLICATE_HEADER','ENCODING_REDIRECT','LENGTH','URL','ORIGIN','PLAYLIST_SIZE','PLAYLIST_CONTROL','PLAYLIST_ENCODING','PLAYLIST_HEADER','PLAYLIST_LINE','PLAYLIST_ORDER','DURATION','HLS_UNSUPPORTED','PLAYLIST_URI','REFERENCE_LIMIT','PLAYLIST_INCOMPLETE','UNKNOWN'}
TAGS=('EXTM3U','EXT-X-STREAM-INF','EXTINF','EXT-X-ENDLIST','EXT-X-VERSION','EXT-X-TARGETDURATION','EXT-X-MEDIA-SEQUENCE','EXT-X-PLAYLIST-TYPE','EXT-X-INDEPENDENT-SEGMENTS','EXT-X-ALLOW-CACHE','EXT-X-KEY','EXT-X-MAP','EXT-X-MEDIA','EXT-X-DISCONTINUITY','EXT-X-PROGRAM-DATE-TIME')
MIME={'application/vnd.apple.mpegurl':'HLS','application/x-mpegurl':'HLS','audio/mpegurl':'HLS','audio/x-mpegurl':'HLS','text/html':'HTML','application/json':'JSON','text/plain':'TEXT','application/octet-stream':'BINARY'}
def project(response=None,reason=None):
 out={'status':None,'content_type':'UNOBSERVED','body_bytes':None,'extm3u_first_line':False,'tag_counts':dict.fromkeys(TAGS,0),'other_tags':0,'uri_lines':0,'line_limit_exceeded':False,'reason':reason,'raw_values_exported':False}
 if reason is not None and reason not in REASONS:raise ValueError('DIAGNOSTIC_SCHEMA')
 if type(response) is not tuple or len(response)!=3:return out
 status,headers,body=response
 if type(status) is int and 100<=status<=599:out['status']=status
 if type(headers) in (list,tuple) and len(headers)<=100:
  found=[v for row in headers if type(row) in (tuple,list) and len(row)==2 for k,v in [row] if type(k) is str and type(v) is str and k.lower()=='content-type']
  out['content_type']='ABSENT' if not found else 'DUPLICATE' if len(found)>1 else MIME.get(found[0].split(';',1)[0].strip().lower(),'OTHER')
 if type(body) is not bytes or len(body)>65536:return out
 out['body_bytes']=len(body);lines=body.split(b'\n');out['line_limit_exceeded']=len(lines)>512;out['extm3u_first_line']=lines[0].rstrip(b'\r')==b'#EXTM3U'
 for line in lines[:512]:
  if line.startswith(b'#'):
   key=line.split(b':',1)[0].strip(b'#\r').decode('ascii','replace')
   if key in TAGS:out['tag_counts'][key]+=1
   else:out['other_tags']+=1
  elif line.strip(b'\r'):out['uri_lines']+=1
 return out

def validate(v):
 expected=project()
 if type(v) is not dict or set(v)!=set(expected):raise ValueError('DIAGNOSTIC_SCHEMA')
 if v['status'] is not None and (type(v['status']) is not int or not 100<=v['status']<=599):raise ValueError('DIAGNOSTIC_SCHEMA')
 if v['content_type'] not in set(MIME.values())|{'UNOBSERVED','ABSENT','DUPLICATE','OTHER'}:raise ValueError('DIAGNOSTIC_SCHEMA')
 if v['body_bytes'] is not None and (type(v['body_bytes']) is not int or not 0<=v['body_bytes']<=65536):raise ValueError('DIAGNOSTIC_SCHEMA')
 if v['reason'] is not None and v['reason'] not in REASONS:raise ValueError('DIAGNOSTIC_SCHEMA')
 if type(v['tag_counts']) is not dict or set(v['tag_counts'])!=set(TAGS):raise ValueError('DIAGNOSTIC_SCHEMA')
 if any(type(n) is not int or not 0<=n<=512 for n in [v['other_tags'],v['uri_lines']]+list(v['tag_counts'].values())):raise ValueError('DIAGNOSTIC_SCHEMA')
 if any(type(v[k]) is not bool for k in ('extm3u_first_line','line_limit_exceeded','raw_values_exported')) or v['raw_values_exported'] is not False:raise ValueError('DIAGNOSTIC_SCHEMA')
 return v

"""Pure bounded master parser bridge443->8444. No GET authorization."""
import re,math
from urllib.parse import urlsplit,urljoin
class Rejected(ValueError):pass
def require(ok,code):
 if not ok:raise Rejected(code)
def target(url):
 require(type(url) is str and 0<len(url)<=8192 and not any(ord(c)<=32 or ord(c)==127 for c in url) and '\\' not in url,'URL')
 try:p=urlsplit(url);port=p.port if p.port is not None else 443
 except ValueError:raise Rejected('ORIGIN') from None
 require(p.scheme=='https' and p.hostname=='192.168.56.74' and port in (443,8444) and p.username is None and p.password is None and '?' not in url and '#' not in url,'ORIGIN')
 return url
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


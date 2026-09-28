import hashlib
import json
import unittest
from unittest.mock import patch
import delivery as d

U=d.ORIGIN+'/media'
class Tests(unittest.TestCase):
 def test_origin(self):
  for u in ['http://192.168.56.74:8443/x','https://evil/x',U+'#x',U+'\n',d.ORIGIN+'/a\\b']:
   with self.assertRaises(d.Rejected):d.target(u)
 def test_invalid_header_names(self):
  for name in ['Content-Length ', 'Location\r\nX', '', 'Content Encoding']:
   with self.assertRaisesRegex(d.Rejected,'HEADER_NAME'):
    d.fetch(lambda *a:(200,[(name,'1')],b'x'),U,{},10,200)
 def test_non_hls_line_breaks(self):
  for char in ['\u2028','\u2029','\x85','\v','\f','\x1c','\r']:
   body=('#EXTM3U\n#EXTINF:1,x'+char+'seg.ts\n#EXT-X-ENDLIST\n').encode()
   with self.assertRaisesRegex(d.Rejected,'PLAYLIST_CONTROL'):d.playlist(body,U)
  self.assertEqual(d.playlist(b'#EXTM3U\r\n#EXTINF:1,\r\nseg.ts\r\n#EXT-X-ENDLIST\r\n',U)[0],'media')
 def test_api_private(self):
  seen=[]
  self.assertEqual(d.native_url(lambda **k:seen.append(k) or U),U)
  self.assertEqual(seen,[dict(service='flavorasset',action='getUrl',id=d.ASSET)])
 def test_progressive(self):
  raw=b'a'*2048+b'b'*2048
  def req(u,h,limit):
   if 'Range' not in h:return 200,[],raw
   a,b=map(int,h['Range'][6:].split('-'));return 206,[('Content-Range',f'bytes {a}-{b}/{len(raw)}')],raw[a:b+1]
  with patch.object(d,'SIZE',len(raw)),patch.object(d,'SHA',hashlib.sha256(raw).hexdigest()):
   r,b=d.progressive(req,U);self.assertEqual(r['range_checks'],2);self.assertEqual(b,raw)
 def test_source_hash(self):
  with self.assertRaisesRegex(d.Rejected,'SOURCE_HASH'):d.progressive(lambda *a:(200,[],b'x'),U)
 def test_bad_range(self):
  raw=b'x'*4096
  with patch.object(d,'SIZE',4096),patch.object(d,'SHA',hashlib.sha256(raw).hexdigest()):
   with self.assertRaisesRegex(d.Rejected,'CONTENT_RANGE'):
    d.progressive(lambda u,h,l:(200,[],raw) if 'Range' not in h else (206,[],raw[:1024]),U)
 def test_header_guards(self):
  for status,headers,body in [(302,[],b''),(200,[('Content-Length','2')],b'x'),(200,[('Content-Encoding','gzip')],b'x'),(200,[('Content-Length','1'),('content-length','1')],b'x')]:
   with self.assertRaises(d.Rejected):d.fetch(lambda *a:(status,headers,body),U,{},10,200)
 def test_hls(self):
  master=b'#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=100\nlist.m3u8\n'
  media=b'#EXTM3U\n#EXT-X-TARGETDURATION:1\n#EXTINF:1,\nseg.ts\n#EXT-X-ENDLIST\n'
  ts=b'G'+b'\0'*187
  def req(u,h,l):return 200,[],master if u==U else media if u.endswith('m3u8') else ts
  r,b=d.hls(req,U);self.assertEqual(r['requests'],3);self.assertEqual(b,ts);self.assertFalse(r['decoded'])
 def test_hls_negative(self):
  for body in [b'#EXTM3U\n#EXT-X-KEY:METHOD=AES-128\n',b'#EXTM3U\n#EXTINF:1,\nhttp://evil/a\n#EXT-X-ENDLIST\n',b'#EXTM3U\n#EXTINF:1,\na.ts\n',b'#EXTM3U\n#EXTINF:NaN,\na.ts\n#EXT-X-ENDLIST\n']:
   with self.assertRaises(d.Rejected):d.playlist(body,U)
 def test_probe(self):
  b=json.dumps({'streams':[{'codec_type':'video','codec_name':'h264','width':640,'height':360}]}).encode()
  self.assertFalse(d.probe_projection(b)['full_decode_verified'])
  for v in [b'{}',b'{"streams":[],"streams":[]}',b'{"streams":NaN}']:
   with self.assertRaises(d.Rejected):d.probe_projection(v)
 def test_error_redacted(self):
  def req(*a):raise ValueError('SECRET')
  with self.assertRaisesRegex(d.Rejected,'^TRANSPORT$'):d.fetch(req,U,{},10,200)
if __name__=='__main__':unittest.main()

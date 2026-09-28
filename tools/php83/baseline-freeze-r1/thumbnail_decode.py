"""Finite pinned MJPEG-only memfd decode; no file/network references in image input."""
import json,os,stat
from pathlib import Path
import offline_decode as runtime
class Rejected(ValueError):pass
CODES=('THUMB_DECODE_INPUT','THUMB_DECODE_BINARY','THUMB_DECODE_METADATA','THUMB_DECODE_FAILED')
def need(v,code):
 if not v:raise Rejected(code)
def decode(data,width,height):
 need(type(data) is bytes and 0<len(data)<=1024*1024 and data.startswith(b'\xff\xd8') and data.endswith(b'\xff\xd9') and type(width) is int and type(height) is int and 0<width<=4096 and 0<height<=4096 and width*height<=4*1024*1024,'THUMB_DECODE_INPUT')
 fds=[]
 try:
  media=runtime.sealed(data,'private-thumbnail');fds.append(media);bins={}
  for name,(path,pin) in runtime.BINARIES.items():
   m=Path(path).lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==m.st_gid==0 and m.st_nlink==1 and stat.S_IMODE(m.st_mode)==0o755 and not os.listxattr(path),'THUMB_DECODE_BINARY');bins[name]=runtime.sealed(runtime.pinned(path,pin,1024*1024),name);fds.append(bins[name])
  path=f'/proc/self/fd/{media}'
  probe=['-v','error','-protocol_whitelist','file','-err_detect','explode','-f','mjpeg','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,nb_read_frames','-of','json',path]
  raw=runtime.run(bins['ffprobe'],probe,media)
  def pairs(items):
   out={}
   for k,v in items:need(k not in out,'THUMB_DECODE_METADATA');out[k]=v
   return out
  value=json.loads(raw,object_pairs_hook=pairs);rows=value.get('streams') if type(value) is dict else None
  need(type(rows) is list and len(rows)==1 and type(rows[0]) is dict,'THUMB_DECODE_METADATA');row=rows[0]
  need(row.get('codec_type')=='video' and row.get('codec_name')=='mjpeg' and type(row.get('width')) is int and row['width']==width and type(row.get('height')) is int and row['height']==height and row.get('nb_read_frames')=='1','THUMB_DECODE_METADATA')
  args=['-nostdin','-hide_banner','-v','error','-xerror','-protocol_whitelist','file','-threads','1','-err_detect','explode','-f','mjpeg','-i',path,'-map','0:v:0','-f','null','-']
  need(runtime.run(bins['ffmpeg'],args,media)==b'','THUMB_DECODE_FAILED')
  return {'codec':'mjpeg','width':width,'height':height,'frames':1,'full_image_decode':True,'api_dimensions_match':True,'dynamic_library_cohort_attested':False,'full_acceptance':False}
 except Rejected:raise
 except Exception:raise Rejected('THUMB_DECODE_FAILED') from None
 finally:
  for fd in reversed(fds):os.close(fd)

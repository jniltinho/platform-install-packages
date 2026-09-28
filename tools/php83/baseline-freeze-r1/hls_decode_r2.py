"""Pinned local full decode of privately fetched TS; observed metadata, no golden claim."""
import json,os,stat
from fractions import Fraction
from pathlib import Path
import offline_decode as runtime
import decode_diagnostic
class Rejected(ValueError):pass
CODES=('HLS_DECODE_SHAPE','HLS_DECODE_BINARY','HLS_DECODE_METADATA','HLS_DECODE_FAILED')
def need(ok,code):
 if not ok:raise Rejected(code)
def projection(value):
 need(type(value) is dict and type(value.get('streams')) is list and len(value['streams'])==2,'HLS_DECODE_METADATA')
 v=[x for x in value['streams'] if type(x) is dict and x.get('codec_type')=='video'];a=[x for x in value['streams'] if type(x) is dict and x.get('codec_type')=='audio']
 need(len(v)==len(a)==1,'HLS_DECODE_METADATA');v,a=v[0],a[0]
 need(v.get('codec_name')=='h264' and a.get('codec_name')=='aac','HLS_DECODE_METADATA')
 def integer(x,low,high):
  need(type(x) in (str,int) and str(x).isascii() and str(x).isdigit() and str(int(x))==str(x) and low<=int(x)<=high,'HLS_DECODE_METADATA');return int(x)
 width=integer(v.get('width'),1,4096);height=integer(v.get('height'),1,2160);frames=integer(v.get('nb_read_frames'),1,6000)
 rate=v.get('avg_frame_rate');duration=value.get('format',{}).get('duration')
 need(type(rate) is str and len(rate)<=24 and type(duration) is str and len(duration)<=24,'HLS_DECODE_METADATA')
 try:fps=Fraction(rate);seconds=Fraction(duration)
 except (ValueError,ZeroDivisionError):raise Rejected('HLS_DECODE_METADATA') from None
 need(0<fps<=120 and 0<seconds<=120 and fps.numerator<=120000000 and fps.denominator<=100000000,'HLS_DECODE_METADATA')
 return {'video_codec':'h264','audio_codec':'aac','width':width,'height':height,'video_frames':frames,'fps_numerator':fps.numerator,'fps_denominator':fps.denominator,'duration_milliseconds':int(seconds*1000),'audio_sample_rate':integer(a.get('sample_rate'),8000,192000),'audio_channels':integer(a.get('channels'),1,8)}
def decode(data,describe):
 need(type(data) is bytes and 0<len(data)<=2*1024*1024 and len(data)%188==0 and all(data[x]==0x47 for x in range(0,len(data),188)),'HLS_DECODE_SHAPE')
 fds=[]
 try:
  media=runtime.sealed(data,'hls-private-ts');fds.append(media);binaries={}
  for name,(path,pin) in runtime.BINARIES.items():
   meta=Path(path).lstat();need(stat.S_ISREG(meta.st_mode) and meta.st_uid==meta.st_gid==0 and stat.S_IMODE(meta.st_mode)==0o755 and meta.st_nlink==1 and not os.listxattr(path),'HLS_DECODE_BINARY')
   binaries[name]=runtime.sealed(runtime.pinned(path,pin,1024*1024),name);fds.append(binaries[name])
  path=f'/proc/self/fd/{media}'
  probe=['-v','error','-protocol_whitelist','file','-f','mpegts','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,avg_frame_rate,sample_rate,channels,nb_read_frames:format=duration','-of','json',path]
  args=['-nostdin','-hide_banner','-v','error','-xerror','-protocol_whitelist','file','-threads','1','-f','mpegts','-i',path,'-map','0:v:0','-map','0:a:0','-f','null','-']
  raw=runtime.run(binaries['ffprobe'],probe,media)
  def pairs(items):
   out={}
   for k,v in items:
    need(k not in out,'HLS_DECODE_METADATA');out[k]=v
   return out
  parsed=json.loads(raw,object_pairs_hook=pairs)
  facts=decode_diagnostic.project(parsed);describe(facts)
  need(facts['duration']['state']=='NUMBER' and all(row['avg_frame_rate']['state']=='NUMBER' for row in facts['streams'] if row['kind']=='VIDEO'),'HLS_DECODE_METADATA')
  observed=projection(parsed)
  need(runtime.run(binaries['ffmpeg'],args,media)==b'','HLS_DECODE_FAILED')
  return {'case':'FETCHED_TS_FULL_LOCAL_DECODE','metadata':observed,'full_decode_verified':True,'dynamic_library_cohort_attested':False,'profile_golden_equivalence':False,'full_acceptance':False}
 except Rejected:raise
 except Exception:raise Rejected('HLS_DECODE_FAILED') from None
 finally:
  for fd in fds:os.close(fd)

"""Pinned full local decode of the stored Decision 7 1080p60 flavor (params 118) of the profile-15 FullHD60 entry.
Reuses offline_decode.sealed/pinned and the pinned ffprobe/ffmpeg executables (sealed memfds, file protocol only,
-xerror, single thread), with bounds sized for 60 s of 1920x1080@60 H.264: CPU 150 s, wall 180 s, 2 GiB address
space per child. Accept: h264 1920x1080 exactly 60/1 fps, 3600 +/- 1 decoded frames (protocol tolerance: one
video frame), duration 60 s +/- (1/60 s + one AAC frame at 48 kHz), one AAC audio stream; zero exit and empty stderr.
Exports observed metadata only; delivered-stream equivalence is a separate step (hash match of fetched bytes)."""
import json,os,resource,selectors,signal,stat,subprocess,time
from fractions import Fraction
from pathlib import Path
import offline_decode as runtime
CODES=('FLAVOR_DECODE_INPUT','FLAVOR_DECODE_BINARY','FLAVOR_DECODE_METADATA','FLAVOR_DECODE_FAILED','FLAVOR_DECODE_LIMIT')
MAX_BYTES=64*1024*1024;CPU=150;WALL=180;AS=2*1024**3;CAP=65536
FRAMES=3600;FPS=Fraction(60);SECONDS=Fraction(60);TOLERANCE=Fraction(1,60)+Fraction(1024,48000)
def meets(width,height,fps,frames,duration_ms):
 """Single acceptance rule used by projection() and validate(): duration compared on integer milliseconds
 (truncated from ffprobe) with 1 ms slack for that truncation."""
 return (width,height)==(1920,1080) and fps==FPS and abs(frames-FRAMES)<=1 and abs(Fraction(duration_ms,1000)-SECONDS)<=TOLERANCE+Fraction(1,1000)
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def _limits():
 resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1));resource.setrlimit(resource.RLIMIT_AS,(AS,AS));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 resource.setrlimit(resource.RLIMIT_FSIZE,(0,0));resource.setrlimit(resource.RLIMIT_NOFILE,(64,64))
def run(executable_fd,args,media_fd):
 """Same fixed-argv, bounded-output, group-kill discipline as offline_decode.run, with larger bounds."""
 os.lseek(media_fd,0,os.SEEK_SET)
 p=subprocess.Popen([f'/proc/self/fd/{executable_fd}',*args],pass_fds=(executable_fd,media_fd),stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
  env={'PATH':'/usr/bin:/bin','LC_ALL':'C','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'},cwd='/',start_new_session=True,preexec_fn=_limits)
 sel=selectors.DefaultSelector();outputs=[bytearray(),bytearray()];deadline=time.monotonic()+WALL
 try:
  for i,stream in enumerate((p.stdout,p.stderr)):os.set_blocking(stream.fileno(),False);sel.register(stream,selectors.EVENT_READ,i)
  while sel.get_map():
   need(time.monotonic()<deadline,'FLAVOR_DECODE_LIMIT')
   for key,_ in sel.select(min(.1,max(0,deadline-time.monotonic()))):
    b=os.read(key.fileobj.fileno(),8192)
    if not b:sel.unregister(key.fileobj)
    else:outputs[key.data].extend(b);need(len(outputs[key.data])<=CAP,'FLAVOR_DECODE_LIMIT')
  while True:
   result=os.waitid(os.P_PID,p.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)
   if result is not None:break
   need(time.monotonic()<deadline,'FLAVOR_DECODE_LIMIT');time.sleep(.01)
  need(result.si_code==os.CLD_EXITED and result.si_status==0,'FLAVOR_DECODE_FAILED');need(not outputs[1],'FLAVOR_DECODE_FAILED')
  return bytes(outputs[0])
 finally:
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  p.wait(timeout=5);sel.close();p.stdout.close();p.stderr.close()
def integer(x,low,high):
 need(type(x) in (str,int) and str(x).isascii() and str(x).isdigit() and str(int(x))==str(x) and low<=int(x)<=high,'FLAVOR_DECODE_METADATA');return int(x)
def projection(value):
 need(type(value) is dict and type(value.get('streams')) is list and len(value['streams'])==2,'FLAVOR_DECODE_METADATA')
 v=[x for x in value['streams'] if type(x) is dict and x.get('codec_type')=='video'];a=[x for x in value['streams'] if type(x) is dict and x.get('codec_type')=='audio']
 need(len(v)==len(a)==1 and v[0].get('codec_name')=='h264' and a[0].get('codec_name')=='aac','FLAVOR_DECODE_METADATA');v,a=v[0],a[0]
 rate=v.get('avg_frame_rate');duration=value.get('format',{}).get('duration')
 need(type(rate) is str and len(rate)<=24 and type(duration) is str and len(duration)<=24,'FLAVOR_DECODE_METADATA')
 try:fps=Fraction(rate);seconds=Fraction(duration)
 except (ValueError,ZeroDivisionError):raise Rejected('FLAVOR_DECODE_METADATA') from None
 out={'video_codec':'h264','audio_codec':'aac','width':integer(v.get('width'),1,4096),'height':integer(v.get('height'),1,2160),'video_frames':integer(v.get('nb_read_frames'),1,100000),
  'fps_numerator':fps.numerator,'fps_denominator':fps.denominator,'duration_milliseconds':int(seconds*1000),'audio_sample_rate':integer(a.get('sample_rate'),8000,192000),'audio_channels':integer(a.get('channels'),1,8)}
 need(fps.numerator<=120000000 and fps.denominator<=100000000,'FLAVOR_DECODE_METADATA')
 need(0<fps<=120 and 0<seconds<=86400,'FLAVOR_DECODE_METADATA') # same bounds validate() enforces
 out['meets_1080p60']=meets(out['width'],out['height'],fps,out['video_frames'],out['duration_milliseconds'])
 return out
def decode(data):
 need(type(data) is bytes and 0<len(data)<=MAX_BYTES,'FLAVOR_DECODE_INPUT')
 fds=[]
 try:
  media=runtime.sealed(data,'stored-flavor-118');fds.append(media);binaries={}
  for name,(path,pin) in runtime.BINARIES.items():
   meta=Path(path).lstat();need(stat.S_ISREG(meta.st_mode) and meta.st_uid==meta.st_gid==0 and stat.S_IMODE(meta.st_mode)==0o755 and meta.st_nlink==1 and not os.listxattr(path),'FLAVOR_DECODE_BINARY')
   binaries[name]=runtime.sealed(runtime.pinned(path,pin,1024*1024),name);fds.append(binaries[name])
  path=f'/proc/self/fd/{media}'
  probe=['-v','error','-protocol_whitelist','file','-f','mp4','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,avg_frame_rate,sample_rate,channels,nb_read_frames:format=duration','-of','json',path]
  args=['-nostdin','-hide_banner','-v','error','-xerror','-protocol_whitelist','file','-threads','1','-f','mp4','-i',path,'-map','0:v:0','-map','0:a:0','-f','null','-']
  def pairs(items):
   out={}
   for k,v in items:need(k not in out,'FLAVOR_DECODE_METADATA');out[k]=v
   return out
  observed=projection(json.loads(run(binaries['ffprobe'],probe,media),object_pairs_hook=pairs))
  need(run(binaries['ffmpeg'],args,media)==b'','FLAVOR_DECODE_FAILED')
  return {'case':'STORED_FLAVOR_FULL_LOCAL_DECODE','metadata':observed,'full_decode_verified':True,'decoded_stream_scope':'ONE_VIDEO_ONE_AUDIO','delivery_verified':False,'dynamic_library_cohort_attested':False,'full_acceptance':False}
 except Rejected:raise
 except Exception:raise Rejected('FLAVOR_DECODE_FAILED') from None
 finally:
  for fd in reversed(fds):os.close(fd)
META_KEYS={'video_codec','audio_codec','width','height','video_frames','fps_numerator','fps_denominator','duration_milliseconds','audio_sample_rate','audio_channels','meets_1080p60'}
def validate(v):
 need(type(v) is dict and set(v)=={'case','metadata','full_decode_verified','decoded_stream_scope','delivery_verified','dynamic_library_cohort_attested','full_acceptance'},'FLAVOR_DECODE_METADATA')
 need(v['case']=='STORED_FLAVOR_FULL_LOCAL_DECODE' and v['full_decode_verified'] is True and v['decoded_stream_scope']=='ONE_VIDEO_ONE_AUDIO' and v['delivery_verified'] is False and v['dynamic_library_cohort_attested'] is False and v['full_acceptance'] is False,'FLAVOR_DECODE_METADATA')
 m=v['metadata'];need(type(m) is dict and set(m)==META_KEYS and type(m['meets_1080p60']) is bool and all(type(m[k]) is int for k in META_KEYS-{'video_codec','audio_codec','meets_1080p60'}),'FLAVOR_DECODE_METADATA')
 need(m['video_codec']=='h264' and m['audio_codec']=='aac','FLAVOR_DECODE_METADATA')
 for k,lo,hi in (('width',1,4096),('height',1,2160),('video_frames',1,100000),('fps_numerator',1,120000000),('fps_denominator',1,100000000),('duration_milliseconds',1,86400000),('audio_sample_rate',8000,192000),('audio_channels',1,8)):
  need(lo<=m[k]<=hi,'FLAVOR_DECODE_METADATA')
 fps=Fraction(m['fps_numerator'],m['fps_denominator'])
 need(m['meets_1080p60']==meets(m['width'],m['height'],fps,m['video_frames'],m['duration_milliseconds']),'FLAVOR_DECODE_METADATA')
 return dict(v)

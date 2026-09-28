"""Fixed offline decoder argv and exact short-media expectation projection.
Caller must pin executable/runtime, supply owned seekable memfd, bound20s CPU/
30s wall/64KiB outputs, reap group, and verify exit0+stderr0 for full decode.
No process execution and no URLs accepted here.
"""
from fractions import Fraction
class Rejected(ValueError):pass

def need(ok,code):
 if not ok:raise Rejected(code)

def commands(fd,kind):
 need(type(fd) is int and 3<=fd<=1048576,'FD')
 need(kind in ('original_mp4','selected_hls_ts'),'KIND')
 path=f'/proc/self/fd/{fd}';fmt='mov' if kind=='original_mp4' else 'mpegts'
 probe=['-v','error','-protocol_whitelist','file','-f',fmt,'-count_frames','-show_entries','stream=codec_type,codec_name,width,height,avg_frame_rate,sample_rate,channels,nb_read_frames,duration:format=duration','-of','json',path]
 decode=['-nostdin','-hide_banner','-v','error','-xerror','-protocol_whitelist','file','-threads','1','-f',fmt,'-i',path,'-map','0:v:0','-map','0:a:0','-f','null','-']
 return probe,decode

def validate(probe,kind):
 need(kind in ('original_mp4','selected_hls_ts') and type(probe) is dict,'SCHEMA')
 streams=probe.get('streams');need(type(streams) is list and len(streams)==2 and all(type(s) is dict for s in streams),'STREAMS')
 video=[s for s in streams if s.get('codec_type')=='video'];audio=[s for s in streams if s.get('codec_type')=='audio'];need(len(video)==len(audio)==1,'STREAMS')
 v,a=video[0],audio[0]
 need(v.get('codec_name')=='h264' and a.get('codec_name')=='aac','CODEC')
 need(type(v.get('width')) is int and v['width']==640 and type(v.get('height')) is int and v['height']==360,'DIMENSIONS')
 need(v.get('avg_frame_rate')=='25/1' and v.get('nb_read_frames')=='250','VIDEO_FRAMES')
 need(a.get('sample_rate')==('48000' if kind=='original_mp4' else '44100') and type(a.get('channels')) is int and a['channels']==2,'AUDIO')
 fmt=probe.get('format');need(type(fmt) is dict and type(fmt.get('duration')) is str and len(fmt['duration'])<=20,'DURATION')
 try:duration=Fraction(fmt['duration'])
 except (ValueError,ZeroDivisionError):raise Rejected('DURATION') from None
 need(Fraction(19,2)<=duration<=Fraction(21,2),'DURATION')
 return {'codec_dimensions_fps_frames_audio_matched':True,'video_frames':250,'full_decode_verified':False,'full_acceptance':False}

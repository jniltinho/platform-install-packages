"""Derivative for exact five source-guarded segments and private memfd decode."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
MODULES=['hls_segments.py','hls_decode.py','hls_delivery8444.py','offline_decode.py']
def build():
 raw=(H/'guest_hls_media8444_r3.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='26fcdfcf317f5d0dfc5a1540635c7d02a38517cfe797faa7258de6820e76c4b0';s=raw.decode()
 anchor="  hls=load('hls_media8444',NEW_HERE/'hls_media8444.py')"
 new='  for name,pin in '+repr({n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in MODULES})+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'HLS_PIN')\n  hls=load('hls_delivery8444',NEW_HERE/'hls_delivery8444.py')"
 assert s.count(anchor)==1;s=s.replace(anchor,new)
 anchor='  def hls_source_guard():\n'
 addition="   for name,pin,size in [('/usr/bin/ffmpeg','ed16af623947494a72e284b6eb8ff225f2da22b38b5d5069c2fd4b4ba3384e41',342488),('/usr/bin/ffprobe','272f6ebc634a63d9c8b4ca68e964119d980f25154e5aa2c35e5487da48e9a58f',191888)]:\n    f=Path(name);m=f.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==m.st_gid==0 and m.st_nlink==1 and m.st_size==size and stat.S_IMODE(m.st_mode)==0o755 and not os.listxattr(f) and hashlib.sha256(f.read_bytes()).hexdigest()==pin,'HLS_DECODE_BINARY')\n"
 assert s.count(anchor)==1;s=s.replace(anchor,anchor+addition)
 s=s.replace("  def described(stage,value):report.setdefault('hls_diagnostics',{})[stage]=value","  def described(stage,value):report.setdefault('hls_diagnostics',{})[stage]=value\n  def segment_described(stage,value):report.setdefault('hls_segment_diagnostics',{})[stage]=value")
 s=s.replace("report['playback_context'],report['hls_media']=hls.observe", "report['playback_context'],report['hls_delivery']=hls.observe").replace('expected_https_id,described)','expected_https_id,described,segment_described)')
 import sys
 sys.path.insert(0,str(H));import hls_delivery8444
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES='+repr(list(hls_delivery8444.CODES))+'+[')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())

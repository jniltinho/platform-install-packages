"""Bounded read-only quiet observation; never advances scanner start boundaries."""
import time
class Unsettled(RuntimeError):pass
def wait_quiet(snapshot,*,clock=time.monotonic,sleep=time.sleep):
 deadline=clock()+30;stable_since=None;previous=None;samples=0
 while samples<121:
  if clock()>=deadline:raise Unsettled('QUIET_WINDOW_NOT_ESTABLISHED')
  current=snapshot();now=clock();samples+=1
  if now>=deadline:raise Unsettled('QUIET_WINDOW_NOT_ESTABLISHED')
  if current!=previous:previous=current;stable_since=now
  elif now-stable_since>=2:return {'status':'QUIET_WINDOW_OBSERVED','samples':samples,'quiet_seconds':2,'maximum_seconds':30}
  sleep(min(.25,deadline-now))
 raise Unsettled('QUIET_WINDOW_NOT_ESTABLISHED')

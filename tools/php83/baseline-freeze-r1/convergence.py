"""Retry only a complete-zero file/journal append conflict, never API operations."""
import time
class Exhausted(ValueError):pass
def run(operation,rejected,*,clock=time.monotonic):
 deadline=clock()+210
 for attempt in range(3):
  # One attempt has unchanged 30s settle +10s files +15s journal +10s files caps.
  if clock()+65>deadline:raise Exhausted('AUDIT_CONVERGENCE_DEADLINE')
  try:result=operation()
  except rejected as error:
   if str(error)!='FILE_TAIL_DURING_JOURNAL':raise
   if attempt==2:raise Exhausted('AUDIT_CONVERGENCE_EXHAUSTED') from None
   continue
  if clock()>deadline:raise Exhausted('AUDIT_CONVERGENCE_DEADLINE')
  return result

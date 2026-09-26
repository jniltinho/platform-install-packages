#!/usr/bin/env python3
"""Retain current CLI tool/result evidence, excluding reasoning/history/hooks."""
import collections
import hashlib
import json
from pathlib import Path
import sys

phase=sys.argv[1]
if phase not in ['prep','final','repeat74','repeat83','contract']:raise SystemExit('unknown phase')
source=Path('/tmp/serialization-claude-r3-'+phase+'-private.jsonl')
raw=source.read_bytes();out=[];counts=collections.Counter();ids=set()
for line in raw.splitlines():
 event=json.loads(line);counts[event.get('type','unknown')]+=1
 if event.get('type') in ['assistant','user']:
  blocks=[]
  for block in event.get('message',{}).get('content',[]):
   if not isinstance(block,dict):continue
   if block.get('type')=='tool_use':
    ids.add(block['id']);blocks.append({k:block[k] for k in ['type','id','name','input'] if k in block})
   elif block.get('type')=='tool_result' and block.get('tool_use_id') in ids:
    blocks.append({k:block[k] for k in ['type','tool_use_id','content','is_error'] if k in block})
  if blocks:out.append({'type':event['type'],'content':blocks})
 elif event.get('type')=='result':
  out.append({k:event[k] for k in ['type','subtype','is_error','result','duration_ms','num_turns'] if k in event})
data=('\n'.join(json.dumps(e,ensure_ascii=False) for e in out)+'\n').encode()
prefix=Path('doc/php83/evidence/serialization-contracts/claude-r3-'+phase)
with Path(str(prefix)+'.sanitized.jsonl').open('xb') as f:f.write(data)
metadata={'raw_sha256':hashlib.sha256(raw).hexdigest(),'sanitized_sha256':hashlib.sha256(data).hexdigest(),'raw_event_counts':dict(counts),'retained_events':len(out),'retained_tool_ids':len(ids),'policy':'Only current tool_use and matching tool_result blocks plus public final result; omit thinking, system/init, hook responses, historical context and unrelated narration. Raw outside repository; hash provenance is not approval.'}
with Path(str(prefix)+'.sanitization.json').open('x') as f:json.dump(metadata,f,indent=2);f.write('\n')

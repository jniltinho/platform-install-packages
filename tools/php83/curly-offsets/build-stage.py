#!/usr/bin/env python3
"""Prepare bounded original43+tools tar, never execute source or overwrite a stage."""
import argparse,hashlib,io,json,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[3]
j=json.loads((repo/'doc/php83/evidence/compiler-triage/primary-r2.json').read_text())
rows={r['path']:r['source_sha256'] for r in j['rows'] if r['category']=='removed_curly_brace_offset'}
if len(rows)!=43:raise ValueError('Expected exact43 cohort')
with a.output.open('xb') as output,tarfile.open(fileobj=output,mode='w') as t:
 for name,want in sorted(rows.items()):
  data=(a.source_root/name).read_bytes()
  if hashlib.sha256(data).hexdigest()!=want:raise ValueError('Original source mismatch')
  m=tarfile.TarInfo('original/'+name);m.size=len(data);m.mode=0o444;t.addfile(m,io.BytesIO(data))
 data=json.dumps(rows,sort_keys=True).encode();m=tarfile.TarInfo('selection.json');m.size=len(data);t.addfile(m,io.BytesIO(data))
 for filename in ['build-lab.py','build-run.sh','verify-tokens.php']:
  file=Path(__file__).parent/filename;t.add(file,arcname='tools/'+filename)

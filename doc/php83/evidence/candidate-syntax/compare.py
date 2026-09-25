"""Independent paired compiler evidence, ignoring only per-file durations."""
import hashlib, json
from pathlib import Path
base = Path(__file__).resolve().parent
read = lambda n: json.loads((base/n).read_text())
a, b = read('primary-r2.json'), read('claude.json')
def require(value, message):
    if not value: raise RuntimeError(message)
for report in (a,b):
    for variant in report['variants'].values():
        for row in variant['records']:
            row.pop('duration_ns')
require(a == b, 'Independent syntax reports differ beyond duration')
require(a['collection_complete'], 'Incomplete collection')
require(not a['candidate_all_files_compile'], 'Candidate compile failures wrongly accepted')
repo = base.parents[3]
for filename, expected in a['harness'].items():
    p = repo/'tools/php83/candidate-syntax'/filename
    require(hashlib.sha256(p.read_bytes()).hexdigest() == expected, 'Harness drift: '+filename)
original = {r['path']:r for r in a['variants']['original']['records']}
candidate = {r['path']:r for r in a['variants']['exp9']['records']}
require(original.keys() == candidate.keys() and len(candidate) == 11784, 'Path denominator mismatch')
new_rejections = [p for p,r in candidate.items() if r['exit'] == 255 and original[p]['exit'] != 255]
resolved = [p for p,r in candidate.items() if r['exit'] == 0 and original[p]['exit'] == 255]
require(not new_rejections and len(resolved) == 4, 'Unexpected compiler delta')
for p,r in candidate.items():
    old = original[p]
    if old['sha256'] == r['sha256']:
        require((old['exit'],old['diagnostics']) == (r['exit'],r['diagnostics']), 'Unchanged-source outcome drift')
result = {'independent_logical_rows': 23568, 'reports_equal_except_duration_ns': True,
          'collection_complete': True, 'candidate_all_files_compile': False,
          'original': a['variants']['original']['summary'], 'exp9': a['variants']['exp9']['summary'],
          'fixed_compiler_rejections': resolved, 'new_compiler_rejections': new_rejections,
          'unchanged_source_outcomes_equal': True, 'remaining_rejected_paths': [p for p,r in candidate.items() if r['exit']==255],
          'application_acceptance': False, 't0_04_complete':False,
          'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(base/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print('23568 independently equal syntax rows;54candidate rejections remain')

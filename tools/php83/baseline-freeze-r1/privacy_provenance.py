"""Closed match-index provenance. Private needles are compared, never returned/hashed.
Instrumentation only: does not change patterns, scanners, acceptance or windows.
"""
PHASES={'files_and_journal','files_after_journal'}
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('PROVENANCE_SCHEMA')
def _bytes(value):
 need(value is None or type(value) is bytes and 16<=len(value)<=8192)
 return value

def receipt(number,phase,patterns,files,journal,*,secret=None,ks=None,canary=None,candidates=()):
 need(type(number) is int and 1<=number<=128 and phase in PHASES)
 need(type(patterns) is list and 2<=len(patterns)<=32 and all(type(v) is bytes and 1<=len(v)<=8192 for v in patterns))
 secret=_bytes(secret);ks=_bytes(ks);canary=_bytes(canary)
 need(type(candidates) in (list,tuple) and len(candidates)<=34)
 candidates=[_bytes(v) for v in candidates];need(all(v is not None for v in candidates))
 for result in (files,journal):
  need(type(result) is dict and type(result.get('counts')) is list and len(result['counts'])==len(patterns) and all(type(n) is int and 0<=n<2**63 for n in result['counts']))
 rows=[]
 for index,pattern in enumerate(patterns):
  categories=[]
  for value,kind in ((secret,'CURRENT_SECRET'),(ks,'CURRENT_KS'),(canary,'INVALID_CANARY')):
   if value is not None:
    if pattern==value:categories.append(kind+'_FULL')
    if pattern==value[:15]:categories.append(kind+'_PREFIX')
  if any(pattern==v for v in candidates):categories.append('URL_CANDIDATE_FULL')
  if any(pattern==v[:15] for v in candidates):categories.append('URL_CANDIDATE_PREFIX')
  rows.append({'index':index+1,'categories':categories or ['UNATTRIBUTED_PATTERN'],'file_count':files['counts'][index],'journal_count':journal['counts'][index]})
 file_complete=files.get('status')=='COMPLETE_FINITE_FILE_WINDOW' and type(files.get('uncovered_tail_bytes')) is int and files['uncovered_tail_bytes']==0
 journal_complete=journal.get('status')=='COMPLETE_FINITE_JOURNAL_WINDOW' and journal.get('cutoff_covered') is True and journal.get('complete') is True
 return {'schema':1,'audit':number,'phase':phase,'patterns':rows,'file_window_complete':file_complete,'journal_window_complete':journal_complete,'any_match':any(r['file_count'] or r['journal_count'] for r in rows),'final_privacy_acceptance':False}

def validate_public(value):
 need(type(value) is dict and set(value)=={'schema','audit','phase','patterns','file_window_complete','journal_window_complete','any_match','final_privacy_acceptance'})
 need(type(value['schema']) is int and value['schema']==1 and type(value['audit']) is int and 1<=value['audit']<=128 and value['phase'] in PHASES)
 need(all(type(value[k]) is bool for k in ('file_window_complete','journal_window_complete','any_match','final_privacy_acceptance')) and value['final_privacy_acceptance'] is False)
 rows=value['patterns'];need(type(rows) is list and 2<=len(rows)<=32)
 allowed={'CURRENT_SECRET_FULL','CURRENT_SECRET_PREFIX','CURRENT_KS_FULL','CURRENT_KS_PREFIX','INVALID_CANARY_FULL','INVALID_CANARY_PREFIX','URL_CANDIDATE_FULL','URL_CANDIDATE_PREFIX','UNATTRIBUTED_PATTERN'}
 for index,row in enumerate(rows):
  need(type(row) is dict and set(row)=={'index','categories','file_count','journal_count'} and type(row['index']) is int and row['index']==index+1)
  need(type(row['categories']) is list and 1<=len(row['categories'])<=8 and all(type(k) is str and k in allowed for k in row['categories']) and len(set(row['categories']))==len(row['categories']))
  need(all(type(row[k]) is int and 0<=row[k]<2**63 for k in ('file_count','journal_count')))
 need(value['any_match']==any(row['file_count'] or row['journal_count'] for row in rows))
 return value

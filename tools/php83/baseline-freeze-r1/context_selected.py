"""Normalize one already-fetched asset; no network or new API call."""
import short_metadata
class Rejected(ValueError):pass
def select(rows):
 if type(rows) is not list or not 1<=len(rows)<=64:raise Rejected('SELECTED_ASSET')
 found=[r for r in rows if type(r) is dict and r.get('id')=='0_21p06l2j']
 if len(found)!=1:raise Rejected('SELECTED_ASSET')
 raw=found[0];out={k:raw.get(k) for k in ('id','entryId','fileExt')}
 for k in ('partnerId','status','version','flavorParamsId','size'):
  try:out[k]=short_metadata.integer(raw.get(k),'SELECTED_ASSET')
  except short_metadata.Rejected:raise Rejected('SELECTED_ASSET') from None
 original=raw.get('isOriginal')
 if not (original is False or type(original) is int and original==0 or type(original) is str and original=='0'):raise Rejected('SELECTED_ASSET')
 out['isOriginal']=False
 if 'tags' in raw:
  if type(raw['tags']) is not str or len(raw['tags'])>1024:raise Rejected('SELECTED_TAGS')
  out['tags']=raw['tags']
 return out

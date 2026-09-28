"""V2 pure typed current-selection observation projection. No transport, credentials or source execution."""
import re
FIELDS={'objectType','id','partnerId','status','mediaType'}
ENTRY='0_wzmt2sfy';PARTNER=102
SOURCE='612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473'
class Invalid(ValueError):pass
def need(value,code):
 if not value:raise Invalid(code)
def projection(row):
 need(type(row) is dict and FIELDS<=set(row),'MEDIA_SHAPE')
 out={k:row[k] for k in sorted(FIELDS)}
 need(out['objectType']=='KalturaMediaEntry' and out['id']==ENTRY,'ENTRY_IDENTITY')
 for key,want in [('partnerId',PARTNER),('status',2),('mediaType',1)]:need(type(out[key]) in (int,str) and str(out[key])==str(want),'MEDIA_DOMAIN')
 return out
def typed_equal(a,b):return type(a) is type(b) and a.keys()==b.keys() and all(type(a[k]) is type(b[k]) and a[k]==b[k] for k in a)
def entry_version(data):
 # entry::getVersion: first ^ (if present) else & segment, PATHINFO_FILENAME.
 # Accept only explicit simple numeric representation; unknown is not guessed.
 need(type(data) is str and len(data)<=256,'DATA_SHAPE')
 first=data.split('^' if '^' in data else '&',1)[0]
 if first=='':return 0
 if not re.fullmatch(r'[0-9]{1,9}(?:\.[A-Za-z0-9]{1,12})?',first):return None
 return int(first.split('.',1)[0])
def fixture(entry,listing,version):
 view=projection(entry);need(type(listing) is dict and listing.get('objectType')=='KalturaMediaListResponse' and type(listing.get('objects')) is list and len(listing['objects'])==1,'LIST_SHAPE')
 need(typed_equal(view,projection(listing['objects'][0])),'TYPED_LIST')
 count=listing.get('totalCount');need(type(count) in (int,str) and str(count)=='1','COUNT')
 need(version is None or type(version) is int and version>=0,'ENTRY_VERSION_SHAPE')
 return {'version':2,'entry':view,'page_size':1,'page_index':1,'order_by':'+createdAt','list_total_count':count,'media_get_version':-1,'observed_entry_data_version':version,'source_asset':{'id':'0_ewuu0o46','version':'2','file_sync_id':315},'source_media_sha256':SOURCE}
def profile(row,selected):
 if type(selected) not in (str,int) or not re.fullmatch('[1-9][0-9]*',str(selected)):
  return {'status':'UNRESOLVED_SELECTED_PROFILE','selected_profile_id':None}
 selected=int(selected)
 if type(row) is not dict or row.get('objectType')!='KalturaConversionProfile':return {'status':'UNRESOLVED_API_PROFILE','selected_profile_id':selected}
 values={}
 for k in ('id','partnerId','status'):
  v=row.get(k)
  need(type(v) in (str,int) and re.fullmatch('-?[0-9]{1,10}',str(v)) is not None,'PROFILE_SCALAR');values[k]=int(v)
 need(values['id']==selected and values['partnerId'] in (0,PARTNER),'PROFILE_RELATION')
 raw=row.get('flavorParamsIds');need(type(raw) is str and (raw=='' or re.fullmatch(r'-?[0-9]{1,10}(?:,-?[0-9]{1,10})*',raw) is not None),'PROFILE_FLAVORS')
 return {'status':'OBSERVED_CONFIGURED_PROFILE','selected_profile_id':selected,'partner_id':values['partnerId'],'profile_status':values['status'],'configured_flavor_ids':[int(v) for v in raw.split(',')] if raw else []}

def assets_projection(assets):
 need(type(assets) is list and 1<=len(assets)<=64,'ASSET_BOUND')
 result=[]
 for a in assets:
  need(type(a) is dict and type(a.get('id')) is str and re.fullmatch(r'[0-9]_[a-z0-9]{8}',a['id']) is not None,'ASSET_ID')
  need(type(a.get('partnerId')) in (int,str) and str(a['partnerId'])==str(PARTNER) and a.get('entryId')==ENTRY,'ASSET_OWNER')
  need(type(a.get('version')) in (int,str) and re.fullmatch('[0-9]{1,9}',str(a['version'])) is not None,'ASSET_VERSION')
  need(type(a.get('status')) in (int,str) and re.fullmatch('-?[0-9]{1,4}',str(a['status'])) is not None,'ASSET_STATUS')
  original=a.get('isOriginal');need(type(original) in (bool,int,str) and original in (True,False,0,1,'0','1'),'ASSET_ORIGINAL')
  result.append({'id':a['id'],'version':str(a['version']),'status':a['status'],'is_original':original in (True,1,'1')})
 return result

"""One-time creation of the Decision 7 lab conversion profile on partner 102 (operator decision 2026-09-29, option 1).
Clones system flavor params 7 (HD/1080 h264h 4000) into a partner-102 params with maxFrameRate=60 (KDLFlavor.php
evaluateTargetVideoFramerate caps source fps at KDLConstants::MaxFramerate unless _maxFrameRate>0), then creates
profile lab_decision7 = profile 14's params with 7 replaced by the clone. Profile 14 and the partner default are
never modified (isDefault=0). Consumed once: any existing object with the lab system names aborts before writing.
Requires an admin KS. No retry; every response is checked; exports ids/numbers/enums only."""
import re
SOURCE_PARAMS=7;SOURCE_PROFILE=14;PARTNER=102
PARAMS_SYSTEM='lab_decision7_1080p60';PROFILE_SYSTEM='lab_decision7'
# Writable KalturaAssetParams/KalturaFlavorParams scalars (pinned Rigel-18.20.0); id/createdAt/isSystemDefault are
# readonly, partnerId requiresPermission; requiredPermissions (array) and remote storage profile ids are not copied.
WRITABLE=('tags','mediaParserType','sourceAssetParamsIds','videoCodec','videoBitrate','audioCodec','audioBitrate','audioChannels',
 'audioSampleRate','width','height','frameRate','gopSize','conversionEngines','conversionEnginesExtraParams','twoPass','deinterlice',
 'rotate','operators','engineVersion','format','aspectRatioProcessingMode','forceFrameToMultiplication16','isGopInSec',
 'isAvoidVideoShrinkFramesizeToSource','isAvoidVideoShrinkBitrateToSource','isVideoFrameRateForLowBrAppleHls','multiStream',
 'anamorphicPixels','isAvoidForcedKeyFrames','forcedKeyFramesMode','isCropIMX','optimizationPolicy','videoConstantBitrate',
 'videoBitrateTolerance','watermarkData','subtitlesData','isEncrypted','contentAwareness','chunkedEncodeMode','clipOffset','clipDuration')
CODES=('LAB_PROFILE_API','LAB_PROFILE_EXISTS','LAB_PROFILE_SOURCE','LAB_PROFILE_PARAMS','LAB_PROFILE_PROFILE','LAB_PROFILE_SCHEMA')
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def whole(v):
 return v if type(v) is int else int(v) if type(v) is float and v.is_integer() else int(v) if type(v) is str and re.fullmatch('-?[0-9]{1,10}',v) else None
def api(call,service,action,code,**form):
 try:v=call(service,action,**form)
 except Exception:raise Rejected('LAB_PROFILE_API') from None
 need(type(v) in (dict,list) and not (type(v) is dict and v.get('objectType')=='KalturaAPIException'),code);return v
def ids(csv):
 need(type(csv) is str and re.fullmatch(r'[0-9]+(,[0-9]+){0,31}',csv) is not None,'LAB_PROFILE_PROFILE');return [int(x) for x in csv.split(',')]
def scalar(v):
 return type(v) in (int,float,str) or type(v) is bool
def setup(call,ks,progress=lambda value:None):
 """call(service,action,**form)->decoded API value, bound to an ADMIN KS by the caller. progress() receives the ids
 actually created so a partial mutation (params created, profile failed) stays visible for manual reconciliation;
 a second run then aborts at LAB_PROFILE_EXISTS (consumed once, never auto-reconciled).
 flavorParamsIds membership is compared as a set: Kaltura returns relation rows in DB order, and order is not an
 acceptance criterion."""
 for service,filt,system in (('flavorparams','KalturaFlavorParamsFilter',PARAMS_SYSTEM),('conversionprofile','KalturaConversionProfileFilter',PROFILE_SYSTEM)):
  v=api(call,service,'list','LAB_PROFILE_EXISTS',ks=ks,**{'filter:objectType':filt,'filter:systemNameEqual':system})
  need(type(v) is dict and whole(v.get('totalCount'))==0,'LAB_PROFILE_EXISTS')
 src=api(call,'flavorparams','get','LAB_PROFILE_SOURCE',ks=ks,id=SOURCE_PARAMS)
 need(type(src) is dict and src.get('objectType')=='KalturaFlavorParams' and whole(src.get('id'))==SOURCE_PARAMS and whole(src.get('partnerId'))==0,'LAB_PROFILE_SOURCE')
 need(whole(src.get('height'))==1080 and whole(src.get('frameRate')) in (0,None) and whole(src.get('maxFrameRate')) in (0,None) and src.get('videoCodec')=='h264h' and whole(src.get('videoBitrate'))==4000,'LAB_PROFILE_SOURCE')
 form={'flavorParams:objectType':'KalturaFlavorParams'}
 for k in WRITABLE:
  if k in src and src[k] is not None and scalar(src[k]):form['flavorParams:'+k]=int(src[k]) if type(src[k]) is bool else src[k]
 form.update({'flavorParams:name':'Lab Decision7 HD/1080p60 (clone of 7)','flavorParams:systemName':PARAMS_SYSTEM,
  'flavorParams:description':'Decision 7 lab: params 7 with maxFrameRate=60','flavorParams:maxFrameRate':60})
 new=api(call,'flavorparams','add','LAB_PROFILE_PARAMS',ks=ks,**form)
 need(type(new) is dict and new.get('objectType')=='KalturaFlavorParams' and whole(new.get('partnerId'))==PARTNER and new.get('systemName')==PARAMS_SYSTEM,'LAB_PROFILE_PARAMS')
 new_id=whole(new.get('id'));need(new_id is not None and new_id>SOURCE_PARAMS,'LAB_PROFILE_PARAMS')
 progress({'lab_params_id':new_id,'lab_profile_id':None})
 need(whole(new.get('maxFrameRate'))==60,'LAB_PROFILE_PARAMS')
 for k in ('height','width','videoCodec','videoBitrate','frameRate','audioCodec','audioBitrate','conversionEngines','tags','format'):
  need(new.get(k)==src.get(k) or whole(new.get(k))==whole(src.get(k)) and whole(src.get(k)) is not None,'LAB_PROFILE_PARAMS')
 base=api(call,'conversionprofile','get','LAB_PROFILE_PROFILE',ks=ks,id=SOURCE_PROFILE)
 need(type(base) is dict and whole(base.get('id'))==SOURCE_PROFILE and whole(base.get('partnerId'))==PARTNER,'LAB_PROFILE_PROFILE')
 old=ids(base.get('flavorParamsIds'));need(SOURCE_PARAMS in old and new_id not in old,'LAB_PROFILE_PROFILE')
 default_before=base.get('isPartnerDefault')
 wanted=[new_id if x==SOURCE_PARAMS else x for x in old]
 prof=api(call,'conversionprofile','add','LAB_PROFILE_PROFILE',ks=ks,**{'conversionProfile:objectType':'KalturaConversionProfile','conversionProfile:name':'Lab Decision7 (profile 14 with 1080p60)',
  'conversionProfile:systemName':PROFILE_SYSTEM,'conversionProfile:type':1,'conversionProfile:isDefault':0,'conversionProfile:flavorParamsIds':','.join(map(str,wanted))})
 need(type(prof) is dict and prof.get('objectType')=='KalturaConversionProfile' and whole(prof.get('partnerId'))==PARTNER and prof.get('systemName')==PROFILE_SYSTEM,'LAB_PROFILE_PROFILE')
 prof_id=whole(prof.get('id'));need(prof_id is not None and prof_id!=SOURCE_PROFILE,'LAB_PROFILE_PROFILE')
 progress({'lab_params_id':new_id,'lab_profile_id':prof_id})
 need(sorted(ids(prof.get('flavorParamsIds')))==sorted(wanted),'LAB_PROFILE_PROFILE')
 need(prof.get('isPartnerDefault') in (False,0,'0',None) and whole(prof.get('isDefault')) in (0,None),'LAB_PROFILE_PROFILE')
 after=api(call,'conversionprofile','get','LAB_PROFILE_PROFILE',ks=ks,id=SOURCE_PROFILE)
 need(type(after) is dict and whole(after.get('id'))==SOURCE_PROFILE and sorted(ids(after.get('flavorParamsIds')))==sorted(old),'LAB_PROFILE_PROFILE') # profile 14 untouched
 need(after.get('isPartnerDefault')==default_before,'LAB_PROFILE_PROFILE') # partner default observed unchanged
 return {'case':'DECISION7_LAB_PROFILE_CREATED','partner_id':PARTNER,'source_params_id':SOURCE_PARAMS,'lab_params_id':new_id,'lab_params_system_name':PARAMS_SYSTEM,
  'lab_params_max_frame_rate':60,'source_profile_id':SOURCE_PROFILE,'lab_profile_id':prof_id,'lab_profile_system_name':PROFILE_SYSTEM,
  'lab_profile_flavor_params':sorted(wanted),'source_profile_flavor_params':sorted(old),'partner_default_changed':False,'copied_param_fields':sorted(k[len('flavorParams:'):] for k in form if k[len('flavorParams:'):] in WRITABLE),'full_acceptance':False}
def validate(v):
 need(type(v) is dict and set(v)=={'case','partner_id','source_params_id','lab_params_id','lab_params_system_name','lab_params_max_frame_rate','source_profile_id','lab_profile_id','lab_profile_system_name','lab_profile_flavor_params','source_profile_flavor_params','partner_default_changed','copied_param_fields','full_acceptance'},'LAB_PROFILE_SCHEMA')
 need(v['case']=='DECISION7_LAB_PROFILE_CREATED' and v['partner_id']==PARTNER and v['source_params_id']==SOURCE_PARAMS and v['source_profile_id']==SOURCE_PROFILE and v['lab_params_max_frame_rate']==60,'LAB_PROFILE_SCHEMA')
 need(v['lab_params_system_name']==PARAMS_SYSTEM and v['lab_profile_system_name']==PROFILE_SYSTEM and v['partner_default_changed'] is False and v['full_acceptance'] is False,'LAB_PROFILE_SCHEMA')
 need(all(type(v[k]) is int and v[k]>0 for k in ('lab_params_id','lab_profile_id')) and v['lab_profile_id']!=SOURCE_PROFILE,'LAB_PROFILE_SCHEMA')
 a,b=v['lab_profile_flavor_params'],v['source_profile_flavor_params']
 need(all(type(x) is list and all(type(i) is int for i in x) for x in (a,b)) and sorted(a)==sorted([v['lab_params_id'] if i==SOURCE_PARAMS else i for i in b]),'LAB_PROFILE_SCHEMA')
 need(type(v['copied_param_fields']) is list and set(v['copied_param_fields'])<=set(WRITABLE),'LAB_PROFILE_SCHEMA')
 return dict(v)
def validate_progress(v):
 need(type(v) is dict and set(v)=={'lab_params_id','lab_profile_id'} and type(v['lab_params_id']) is int and v['lab_params_id']>SOURCE_PARAMS,'LAB_PROFILE_SCHEMA')
 need(v['lab_profile_id'] is None or type(v['lab_profile_id']) is int and v['lab_profile_id']>0 and v['lab_profile_id']!=SOURCE_PROFILE,'LAB_PROFILE_SCHEMA')
 return dict(v)

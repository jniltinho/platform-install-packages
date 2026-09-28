"""Pure observation/envelope assembler; never promotes unknown runtime to acceptance."""
import argparse,hashlib,json,re
from pathlib import Path
from observation_v2 import FIELDS,PARTNER,SOURCE,ENTRY,need,projection,typed_equal
LABEL='PUBLISHED_PHP74_WITH_APPROVED_PRIVACY_OVERLAY'
OVERLAY='cf16bc5c49acbe5863934ba737c72e2b65878c84048389354e79163afeca0cb8'
FIXTURE_KEYS={'version','entry','page_size','page_index','order_by','list_total_count','media_get_version','observed_entry_data_version','source_asset','source_media_sha256'}
ENV_KEYS={'vm_uuid','snapshot_id','box_name','box_version','box_sha256','cpus','memory_mib','disk_controller','disk_capacity_bytes','observed_readonly'}
def forbidden(v):
 if type(v) is dict:
  need(not set(v)&{'secret','password','ks','token','raw_body','raw_error','credentials'},'PRIVATE_PUBLIC_FIELD')
  for value in v.values():forbidden(value)
 elif type(v) is list:
  for value in v:forbidden(value)
def fixture(value):
 need(type(value) is dict and set(value)==FIXTURE_KEYS,'FIXTURE_SCHEMA')
 need(type(value['version']) is int and value['version']==2 and type(value['page_size']) is int and value['page_size']==1 and type(value['page_index']) is int and value['page_index']==1 and value['order_by']=='+createdAt','PROTOCOL')
 need(type(value['list_total_count']) in (int,str) and str(value['list_total_count'])=='1','COUNT_TYPE')
 need(type(value['media_get_version']) is int and value['media_get_version']==-1 and (value['observed_entry_data_version'] is None or type(value['observed_entry_data_version']) is int and 0<=value['observed_entry_data_version']<=999999999) and value['source_media_sha256']==SOURCE,'SOURCE_VERSION')
 need(value['source_asset']=={'id':'0_ewuu0o46','version':'2','file_sync_id':315} and type(value['source_asset']['file_sync_id']) is int,'ASSET_IDENTITY')
 need(type(value['entry']) is dict and set(value['entry'])==FIELDS,'ENTRY_FIELDS');projection(value['entry']);return value

def privacy(value):
 need(type(value) is dict and set(value)=={'files','journal','scope'},'PRIVACY_SCHEMA')
 for key in ('files','journal'):
  r=value[key];need(type(r) is dict and type(r.get('counts')) is list and len(r['counts'])>=2 and all(type(n) is int and n==0 for n in r['counts']),'PRIVACY_COUNTS')
 f=value['files'];j=value['journal']
 need(f.get('status')=='COMPLETE_FINITE_FILE_WINDOW' and type(f.get('uncovered_tail_bytes')) is int and f['uncovered_tail_bytes']==0,'FILE_WINDOW')
 need(j.get('status')=='COMPLETE_FINITE_JOURNAL_WINDOW' and j.get('cutoff_covered') is True and j.get('complete') is True,'JOURNAL_WINDOW')

def assemble(report,environment):
 forbidden(report);forbidden(environment)
 need(report.get('status')=='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE' and report.get('baseline_label')==LABEL and report.get('upload_attempted') is False and report.get('wrong_secret_rejected') is True and report.get('admin_escalation_rejected') is True,'OBSERVATION')
 for key in ('invalid_nonce','user_privacy','media_privacy'):privacy(report.get(key))
 need(report.get('overlay_manifest_sha256')==OVERLAY and report.get('runtime_pins_verified') is True and report.get('sources_before')==report.get('sources_after') and type(report.get('sources_before')) is dict and len(report['sources_before'])==5,'SOURCE_RUNTIME_JOIN')
 f=fixture(report.get('fixture'));need(report.get('source_sha256')==report.get('stored_source_sha256')==SOURCE and report.get('original_asset_id')=='0_ewuu0o46' and report.get('file_sync_id')==315 and type(report.get('asset_version')) is str and report['asset_version']=='2','SOURCE_JOIN')
 versions=report.get('version_observations');need(type(versions) is list and all(type(x) is dict and set(x)=={'requested','outcome'} and type(x['requested']) is int and x['outcome'] in ('API_REJECTED','TYPED_PROJECTION_MATCH') for x in versions),'VERSION_SCHEMA')
 observed=f['observed_entry_data_version'];expected={-1,0}|({observed} if observed is not None else set())
 need(len(versions)==len(expected) and {x['requested'] for x in versions}==expected,'VERSION_OBSERVATIONS')
 need(any(x['requested']==-1 and x['outcome']=='TYPED_PROJECTION_MATCH' for x in versions),'CURRENT_SELECTION')
 need(report.get('entry_version_status')==('OBSERVED_FROM_ENTRY_DATA' if observed is not None else 'UNRESOLVED'),'ENTRY_VERSION_OBSERVATION')
 need(type(environment) is dict and set(environment)==ENV_KEYS and environment['observed_readonly'] is True,'ENV_SCHEMA')
 need(type(environment['vm_uuid']) is str and re.fullmatch('[a-f0-9-]{36}',environment['vm_uuid']) is not None,'ENV_ID')
 need(environment['snapshot_id'] is None or type(environment['snapshot_id']) is str and re.fullmatch('[a-f0-9-]{36}',environment['snapshot_id']) is not None,'SNAPSHOT_ID')
 for key in ('box_name','box_version','disk_controller'):
  value=environment[key];need(value is None or type(value) is str and re.fullmatch('[A-Za-z0-9_.:/+-]{1,128}',value) is not None,'ENV_VALUE')
 for key in ('cpus','memory_mib','disk_capacity_bytes'):need(environment[key] is None or type(environment[key]) is int and 0<environment[key]<2**50,'ENV_NUMBER')
 need(environment['box_sha256'] is None or type(environment['box_sha256']) is str and re.fullmatch('[a-f0-9]{64}',environment['box_sha256']) is not None,'BOX_PIN')
 prof=report.get('profile');need(type(prof) is dict,'PROFILE')
 if prof.get('status')=='OBSERVED_CONFIGURED_PROFILE':
  need(set(prof)=={'status','selected_profile_id','partner_id','profile_status','configured_flavor_ids'},'PROFILE_SCHEMA')
  need(type(prof['selected_profile_id']) is int and prof['selected_profile_id']==14 and type(prof['partner_id']) is int and prof['partner_id'] in (0,PARTNER) and type(prof['profile_status']) is int,'PROFILE_BINDING')
  need(type(prof['configured_flavor_ids']) is list and len(prof['configured_flavor_ids'])<=128 and all(type(v) is int for v in prof['configured_flavor_ids']),'FLAVORS')
 else:need(set(prof)=={'status','selected_profile_id'} and prof['status'] in ('UNRESOLVED_SELECTED_PROFILE','UNRESOLVED_API_PROFILE') and (prof['selected_profile_id'] is None or type(prof['selected_profile_id']) is int),'PROFILE_UNRESOLVED')
 return {'schema':2,'status':'OBSERVATION_ENVELOPE_PENDING_APPROVAL','baseline_label':LABEL,'protocol_fixture':f,'selection_semantics':'CURRENT_DEFAULT_MINUS_ONE_NOT_HISTORICAL_VERSION_PROOF','environment':environment,'profile':prof,'overlay_manifest_sha256':OVERLAY,'source_media_sha256':SOURCE,'apache_runtime_current':'UNVERIFIED_NO_WEB_FILE_PROBE','full_acceptance':False,'approved_freeze':False,'recovery_snapshot_attested':False,'remaining':['Current native Apache runtime observation','Independent environment/protocol approval','Full task1.2 runtime/repetition acceptance']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--observation',required=True);p.add_argument('--environment',required=True);p.add_argument('--output',required=True);p.add_argument('--observation-sha256',required=True);p.add_argument('--environment-sha256',required=True);a=p.parse_args()
 r=Path(a.observation).read_bytes();e=Path(a.environment).read_bytes();need(hashlib.sha256(r).hexdigest()==a.observation_sha256 and hashlib.sha256(e).hexdigest()==a.environment_sha256,'EXTERNAL_INPUT_PINS')
 out=assemble(json.loads(r),json.loads(e))
 with Path(a.output).open('x') as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
if __name__=='__main__':main()

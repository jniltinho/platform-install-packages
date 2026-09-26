"""Offline completeness/equality guards, not collectors or native attestation."""
import hashlib
import json
import re
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'baseline-protocol'))
from guarded_http import Origin

PUBLISHED_REPO='91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b'
PUBLISHED_INSTALLER='3888f90a295f03421ea54c5055aad978cefb7121428941880ee0e787b38f30a5'
UPSTREAM='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
IDENTITY_KEYS={'php_version','sapi','runtime_binary_sha256','provider_binary_sha256','module_manifest_sha256','source_manifest_sha256','public_config_manifest_sha256','package_manifest_sha256','box_identity_sha256','collector_sha256'}
class RehearsalError(ValueError):pass
def need(ok,code):
    if not ok:raise RehearsalError(code)
def keys(value,expected,code):
    need(type(value) is dict and set(value)==set(expected),code)
def sha(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None
def integer(value,minimum=0):
    return type(value) is int and value>=minimum
def identity(value):
    keys(value,IDENTITY_KEYS,'identity_schema')
    need(type(value['php_version']) is str and re.fullmatch(r'7\.4\.\d+',value['php_version']) is not None,'native74_required')
    need(value['sapi'] in {'apache2handler','fpm-fcgi'},'web_provider_required')
    need(all(sha(value[k]) for k in IDENTITY_KEYS-{'php_version','sapi'}),'identity_hashes')
def validate(plan,observation):
    keys(plan,{'schema','nonce','target','published','expected_identity','owner_namespace','partner_id','source_media_sha256','profile_id','selected_requested_version'},'plan_schema')
    need(type(plan['schema']) is int and plan['schema']==1,'plan_version')
    need(type(plan['nonce']) is str and re.fullmatch('[0-9a-f]{32}',plan['nonce']) is not None,'nonce')
    need(plan['owner_namespace']=='baseline-'+plan['nonce'],'owner_namespace')
    keys(plan['target'],{'hostname','ip','scheme','port'},'target_schema')
    target=plan['target']
    need(target['hostname']=='kaltura-php74-baseline' and target['ip']=='192.168.56.74','baseline_target')
    try:Origin(target['ip'],target['scheme'],target['port'])
    except Exception:raise RehearsalError('target_transport') from None
    keys(plan['published'],{'repository_sha256','installer_sha256','upstream_sha256'},'published_schema')
    need(plan['published']=={'repository_sha256':PUBLISHED_REPO,'installer_sha256':PUBLISHED_INSTALLER,'upstream_sha256':UPSTREAM},'published_drift')
    identity(plan['expected_identity'])
    need(integer(plan['partner_id'],1) and integer(plan['profile_id'],1) and sha(plan['source_media_sha256']),'owned_fixture_identity')
    need(integer(plan['selected_requested_version']),'selected_explicit_version')
    keys(observation,{'schema','nonce','target','published','identity_before','identity_after','network','privacy','provisioning','media','version_observations','api'},'observation_schema')
    need(type(observation['schema']) is int and observation['schema']==1 and observation['nonce']==plan['nonce'],'observation_binding')
    need(observation['target']==target and observation['published']==plan['published'],'target_published_binding')
    for phase in ['identity_before','identity_after']:
        identity(observation[phase]);need(observation[phase]==plan['expected_identity'],'identity_drift')
    network=observation['network']
    keys(network,{'ipv4_self_loopback_only','ipv6_self_loopback_only','dns_disabled','proxies_disabled','redirects_disabled','firewall_persistent_for_run'},'network_schema')
    need(all(v is True for v in network.values()),'network_guard')
    privacy=observation['privacy']
    keys(privacy,{'configuration_reviewed','invalid_canary_hits','valid_secret_hits','valid_ks_hits','raw_values_exported','log_inventory_sha256','guest_private_config_unchanged'},'privacy_schema')
    need(privacy['configuration_reviewed'] is True and privacy['raw_values_exported'] is False and privacy['guest_private_config_unchanged'] is True,'privacy_gate')
    need(all(type(privacy[k]) is int and privacy[k]==0 for k in ['invalid_canary_hits','valid_secret_hits','valid_ks_hits']) and sha(privacy['log_inventory_sha256']),'log_privacy_hits')
    provision=observation['provisioning']
    keys(provision,{'owner_namespace','partner_id','session_type','wrong_secret_rejected','admin_escalation_rejected','credential_parent_mode','credential_file_mode','credential_link_count','credential_owner_matches','private_guest_only'},'provisioning_schema')
    need(provision['owner_namespace']==plan['owner_namespace'] and type(provision['partner_id']) is int and provision['partner_id']==plan['partner_id'],'owned_partner')
    need(type(provision['session_type']) is int and provision['session_type']==0,'user_only')
    need(all(provision[k] is True for k in ['wrong_secret_rejected','admin_escalation_rejected','credential_owner_matches','private_guest_only']),'auth_privacy_controls')
    need(provision['credential_parent_mode']=='0700' and provision['credential_file_mode']=='0600' and type(provision['credential_link_count']) is int and provision['credential_link_count']==1,'credential_permissions')
    media=observation['media']
    keys(media,{'owner_namespace','partner_id','entry_id','profile_id','ready','source_before_sha256','uploaded_stream_sha256','stored_source_sha256','source_after_sha256','stored_source_after_sha256','file_sync_id','asset_id','resolved_version','binding_receipt_sha256'},'media_schema')
    need(media['owner_namespace']==plan['owner_namespace'] and type(media['partner_id']) is int and media['partner_id']==plan['partner_id'] and type(media['profile_id']) is int and media['profile_id']==plan['profile_id'],'media_ownership')
    need(type(media['entry_id']) is str and re.fullmatch(r'[0-9]_[a-z0-9]{8}',media['entry_id']) is not None,'entry_identity')
    need(media['ready'] is True and integer(media['file_sync_id'],1) and integer(media['resolved_version']) and type(media['asset_id']) is str and bool(media['asset_id']) and sha(media['binding_receipt_sha256']),'asset_binding')
    need(all(media[k]==plan['source_media_sha256'] for k in ['source_before_sha256','uploaded_stream_sha256','stored_source_sha256','source_after_sha256','stored_source_after_sha256']),'source_byte_binding')
    versions=observation['version_observations']
    need(type(versions) is list and len(versions)==len(set([-1,0,plan['selected_requested_version']])),'version_inventory')
    need(all(type(x) is dict and set(x)=={'requested_version','accepted','resolved_version','stored_source_sha256','entry_id'} for x in versions),'version_schema')
    need(all(type(x['requested_version']) is int for x in versions),'version_type')
    need(sorted(x['requested_version'] for x in versions)==sorted(set([-1,0,plan['selected_requested_version']])),'version_unique')
    selected=next(x for x in versions if x['requested_version']==plan['selected_requested_version'])
    need(selected['accepted'] is True and type(selected['resolved_version']) is int and selected['resolved_version']==media['resolved_version'] and selected['stored_source_sha256']==plan['source_media_sha256'] and selected['entry_id']==media['entry_id'],'selected_version_binding')
    for row in versions:
        need(type(row['accepted']) is bool,'version_outcome')
        if row['accepted']:
            need(integer(row['resolved_version']) and sha(row['stored_source_sha256']) and row['entry_id']==media['entry_id'],'accepted_version_evidence')
        else:
            need(row['resolved_version'] is None and row['stored_source_sha256'] is None and row['entry_id'] is None,'rejected_version_evidence')
    api=observation['api']
    keys(api,{'session_start','media_list','media_get','content_type','typed_fixture_sha256','source_media_attested','request_paths'},'api_schema')
    need(all(api[k] is True for k in ['session_start','media_list','media_get','source_media_attested']) and api['content_type']=='application/json' and sha(api['typed_fixture_sha256']),'untimed_api_contract')
    need(api['request_paths']==['/api_v3/index.php']*3,'queryless_post_targets')
    return {'status':'OFFLINE_REHEARSAL_RECEIPT_CONSISTENT','native_execution_proven_by_this_validator':False,'baseline_acceptance':False,'timing_acceptance':False,'selected_version_zero':plan['selected_requested_version']==0,'baseline_api_v1_compatible':plan['selected_requested_version']>0,'protocol_revision_required':plan['selected_requested_version']==0,'remaining_gates':['authentic native receipts and coordinator review','complete HTTP/TLS 2+5 round workload','both media upload/READY/HLS/browser','recovery and cutover']}

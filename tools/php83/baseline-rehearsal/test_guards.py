import copy
import unittest
import guards as g
def fixtures(selected=1):
    nonce='1'*32;owner='baseline-'+nonce;h='a'*64
    identity={k:h for k in g.IDENTITY_KEYS};identity.update(php_version='7.4.33',sapi='apache2handler')
    plan={'schema':1,'nonce':nonce,'target':{'hostname':'kaltura-php74-baseline','ip':'192.168.56.74','scheme':'http','port':80},'published':{'repository_sha256':g.PUBLISHED_REPO,'installer_sha256':g.PUBLISHED_INSTALLER,'upstream_sha256':g.UPSTREAM},'expected_identity':identity,'owner_namespace':owner,'partner_id':101,'source_media_sha256':h,'profile_id':1,'selected_requested_version':selected}
    observation={'schema':1,'nonce':nonce,'target':copy.deepcopy(plan['target']),'published':copy.deepcopy(plan['published']),'identity_before':copy.deepcopy(identity),'identity_after':copy.deepcopy(identity),
    'network':dict.fromkeys(['ipv4_self_loopback_only','ipv6_self_loopback_only','dns_disabled','proxies_disabled','redirects_disabled','firewall_persistent_for_run'],True),
    'privacy':{'configuration_reviewed':True,'invalid_canary_hits':0,'valid_secret_hits':0,'valid_ks_hits':0,'raw_values_exported':False,'log_inventory_sha256':h,'guest_private_config_unchanged':True},
    'provisioning':{'owner_namespace':owner,'partner_id':101,'session_type':0,'wrong_secret_rejected':True,'admin_escalation_rejected':True,'credential_parent_mode':'0700','credential_file_mode':'0600','credential_link_count':1,'credential_owner_matches':True,'private_guest_only':True},
    'media':{'owner_namespace':owner,'partner_id':101,'entry_id':'0_abcdefgh','profile_id':1,'ready':True,'source_before_sha256':h,'uploaded_stream_sha256':h,'stored_source_sha256':h,'source_after_sha256':h,'stored_source_after_sha256':h,'file_sync_id':22,'asset_id':'0_sourcexx','resolved_version':selected,'binding_receipt_sha256':h},
    'version_observations':[{'requested_version':n,'accepted':True,'resolved_version':selected,'stored_source_sha256':h,'entry_id':'0_abcdefgh'} for n in sorted(set([-1,0,selected]))],
    'api':{'session_start':True,'media_list':True,'media_get':True,'content_type':'application/json','typed_fixture_sha256':h,'source_media_attested':True,'request_paths':['/api_v3/index.php']*3}}
    return plan,observation
class GuardTests(unittest.TestCase):
    def test_consistent_synthetic_receipt_not_native_proof(self):
        result=g.validate(*fixtures())
        self.assertFalse(result['native_execution_proven_by_this_validator'])
        self.assertFalse(result['baseline_acceptance']);self.assertFalse(result['timing_acceptance'])
    def test_zero_explicitly_supported_with_binding_requires_protocol_revision(self):
        result=g.validate(*fixtures(0))
        self.assertTrue(result['protocol_revision_required']);self.assertFalse(result['baseline_api_v1_compatible'])
    def test_latest_minus_one_cannot_be_frozen(self):
        plan,obs=fixtures();plan['selected_requested_version']=-1
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_target20_rejected_even_matching_observation(self):
        plan,obs=fixtures();plan['target']['ip']='192.168.56.20';obs['target']=plan['target']
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_dns_target_rejected(self):
        plan,obs=fixtures();plan['target']['ip']='localhost'
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_publishedpin_drift(self):
        plan,obs=fixtures();plan['published']['repository_sha256']='b'*64
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_runtime83_rejected(self):
        plan,obs=fixtures();plan['expected_identity']['php_version']='8.3.6'
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_cli_only_not_web_attestation(self):
        plan,obs=fixtures();plan['expected_identity']['sapi']='cli'
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_config_postrun_drift(self):
        plan,obs=fixtures();obs['identity_after']['public_config_manifest_sha256']='b'*64
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_every_network_guard_required(self):
        for key in fixtures()[1]['network']:
            plan,obs=fixtures();obs['network'][key]=False
            with self.subTest(key=key),self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_loghits_and_false_zero_rejected(self):
        for value in [1,False,'0']:
            plan,obs=fixtures();obs['privacy']['valid_ks_hits']=value
            with self.subTest(value=value),self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_admin_session_rejected(self):
        plan,obs=fixtures();obs['provisioning']['session_type']=2
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_other_partner_or_namespace_rejected(self):
        for key,value in [('partner_id',102),('owner_namespace','other')]:
            plan,obs=fixtures();obs['media'][key]=value
            with self.subTest(key=key),self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_each_source_byte_join_required(self):
        for key in ['source_before_sha256','uploaded_stream_sha256','stored_source_sha256','source_after_sha256','stored_source_after_sha256']:
            plan,obs=fixtures();obs['media'][key]='b'*64
            with self.subTest(key=key),self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_missing_ready_rejected(self):
        plan,obs=fixtures();obs['media']['ready']=False
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_duplicate_version_rejected(self):
        plan,obs=fixtures();obs['version_observations'][1]=copy.deepcopy(obs['version_observations'][0])
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_unbound_selected_version_rejected(self):
        plan,obs=fixtures();obs['version_observations'][-1]['stored_source_sha256']='b'*64
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_querysecret_path_rejected(self):
        plan,obs=fixtures();obs['api']['request_paths'][0]+='?ks=synthetic-marker'
        with self.assertRaises(g.RehearsalError):g.validate(plan,obs)
    def test_unknown_secret_field_rejected_without_echo(self):
        plan,obs=fixtures();obs['privacy']['secret']='synthetic-private-marker'
        with self.assertRaises(g.RehearsalError) as caught:g.validate(plan,obs)
        self.assertNotIn('synthetic-private-marker',str(caught.exception))
    def test_nonselected_version_may_be_rejected_but_not_waived(self):
        plan,obs=fixtures();obs['version_observations'][0].update(accepted=False,resolved_version=None,stored_source_sha256=None,entry_id=None)
        self.assertEqual(g.validate(plan,obs)['status'],'OFFLINE_REHEARSAL_RECEIPT_CONSISTENT')
if __name__=='__main__':unittest.main()

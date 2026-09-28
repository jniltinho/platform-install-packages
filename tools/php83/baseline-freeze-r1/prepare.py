"""Produce exact derivative of pinned V4 media guest without upload/provider writes."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
old=ROOT/'tools/php83/baseline-rehearsal/privacy/media-overlay-v3/guest.py'
raw=old.read_bytes();assert hashlib.sha256(raw).hexdigest()=='716786236935d53bbe513275b4cac71b4f9b42b67cf1615d50031d76789b6810'
s=raw.decode().replace('Approved lab74 synthetic upload/READY/source delivery after finite privacy gates.','Read-only existing lab74 media observation after finite privacy gates; no upload.')
s=s.replace('HERE=Path(__file__).resolve().parent',"NEW_HERE=Path(__file__).resolve().parent\nHERE=Path('/home/vagrant/privacy-media-overlay-v3/tools/php83/baseline-rehearsal/privacy/media-overlay-v3')")
s=s.replace("'privacy-media-[0-9a-f]{8}'","'baseline-freeze-[0-9a-f]{8}'")
anchor="  sys.path.insert(0,str(HERE.parents[1]))"
freeze=json.loads((ROOT/'doc/php83/evidence/baseline-rehearsal/privacy/media-overlay-v3/freeze.json').read_text())
checks="  stage=Path('/home/vagrant/privacy-media-overlay-v3')\n  frozen="+repr({k:v for k,v in freeze.items() if k.endswith('.py') and not k.endswith(('/run.py','/test_guest.py','/test_runner.py'))})+"\n  for name,pin in frozen.items():\n   p=stage/name;st=p.lstat();need(stat.S_ISREG(st.st_mode) and st.st_uid==0 and not st.st_mode&0o222 and hashlib.sha256(p.read_bytes()).hexdigest()==pin,'DEPENDENCY_PIN')\n"
obspin=hashlib.sha256((HERE/'observation.py').read_bytes()).hexdigest()
checks+="  obsraw=(NEW_HERE/'observation.py').read_bytes();need(hashlib.sha256(obsraw).hexdigest()=="+repr(obspin)+",'OBSERVATION_PIN')\n  obs=load('baseline_observation',NEW_HERE/'observation.py')\n"
s=s.replace(anchor,checks+anchor)
a=s.index("  report['phase']='web-provider'");b=s.index("  state=Path",a)
s=s[:a]+"  report['apache_runtime_current']='UNVERIFIED_NO_WEB_FILE_PROBE'\n  report['cli_version']=subprocess.check_output(['/usr/bin/php','-n','-r','echo PHP_VERSION;'],timeout=10).decode()\n  need(re.fullmatch(r'7\\.4\\.[0-9]+',report['cli_version']) is not None,'CLI_VERSION')\n"+s[b:]
s=s.replace("  secret=rows[0][2];", "  need(partner==102,'EXACT_PRIOR_PARTNER')\n  secret=rows[0][2];")
s=s.replace("  ks=call(service='session'", "  media_window=(start,jstart);ks=''\n  ks=call(service='session'",1)
a=s.index("  report['phase']='upload'");b=s.index("  assets=value",a)
s=s[:a]+"  report['phase']='existing-entry-observation';entry_id=obs.ENTRY\n  entry=value('media','get',ks=ks,entryId=entry_id,version=-1);bind_entry(entry,partner,entry_id)\n  report['media_projection']=obs.projection(entry)\n"+s[b:]
a=s.index("  report['owned_list_passed']=True;");b=s.index("  report['media_privacy']=audit",a)
s=s[:a]+'''  report['list_total_count']=listing['totalCount']
  rows=legacy.sql("SELECT id,partner_id,data,conversion_profile_id FROM entry WHERE id='0_wzmt2sfy' AND partner_id=102 LIMIT 2")
  need(len(rows)==1 and len(rows[0])==4 and rows[0][:2]==['0_wzmt2sfy','102'],'ENTRY_DB_BINDING')
  concrete=obs.entry_version(rows[0][2]);selected=rows[0][3]
  report['version_observations']=[]
  for version in [-1,0]+([concrete] if concrete is not None and concrete not in (-1,0) else []):
   reply=call(service='media',action='get',ks=ks,entryId=entry_id,version=version)
   if type(reply) is dict and reply.get('objectType')=='KalturaAPIException':
    report['version_observations'].append({'requested':version,'outcome':'API_REJECTED'})
   else:
    need(obs.typed_equal(obs.projection(reply),report['media_projection']),'VERSION_PROJECTION')
    report['version_observations'].append({'requested':version,'outcome':'TYPED_PROJECTION_MATCH'})
  positive=concrete is not None and any(r['requested']==concrete and r['outcome']=='TYPED_PROJECTION_MATCH' for r in report['version_observations'])
  report['fixture']=obs.fixture(entry,listing,concrete) if positive else None
  report['entry_version_status']='OBSERVED_FROM_ENTRY_DATA' if positive else 'UNRESOLVED'
  profile_reply=call(service='conversionprofile',action='get',ks=ks,id=int(selected)) if re.fullmatch('[1-9][0-9]*',selected) else None
  report['profile']=obs.profile(profile_reply,selected)
  report['actual_assets']=[{'id':a['id'],'version':str(a.get('version')),'status':a.get('status'),'is_original':a.get('isOriginal') is True or a.get('isOriginal') in (1,'1')} for a in assets]
''' + s[b:]
s=s.replace("'SYNTHETIC_MEDIA_READY_AND_SOURCE_DELIVERY_OBSERVED'","'EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE'")
s=s.replace("[secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],*media_window","[v for v in [secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()] if v],*media_window")
s=s.replace("code=str(error);report['failure_code']=code if (isinstance(error,Rejected) or type(error).__name__=='Failed') and re.fullmatch('[A-Z0-9_]{1,100}',code) else type(error).__name__", "report['failure_code']='OBSERVATION_REJECTED'")
s=s.replace("need(type(assets) is list and all(type(a) is dict for a in assets),'ASSET_LIST')","report['actual_assets']=obs.assets_projection(assets)")
s=s.replace("need(type(asset_id) is str and legacy.ID.fullmatch(asset_id) is not None and version.isdigit(),'ASSET_VERSION')","need(asset_id=='0_ewuu0o46' and version=='2','PRIOR_ASSET_IDENTITY')")
s=s.replace("need(legacy.checksum(stored)==legacy.SOURCE_PIN,'STORED_SOURCE_BYTES')","need(sync_id==315 and legacy.checksum(stored)==legacy.SOURCE_PIN,'STORED_SOURCE_BYTES')")
s=s.replace("AND version='\"+version+\"'\")","AND version='\"+version+\"' LIMIT 2\")")
s=s.replace("  report['actual_assets']=[{'id':a['id'],'version':str(a.get('version')),'status':a.get('status'),'is_original':a.get('isOriginal') is True or a.get('isOriginal') in (1,'1')} for a in assets]\n",'')
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
s=s.replace("report['sources_after']=overlay.source_state(manifest['after']);","report['sources_after']=overlay.source_state(manifest['after']);report['overlay_manifest_sha256']=EXPECTED_OVERLAY_MANIFEST;report['runtime_pins_verified']=True;")
s=s.replace("report['media_privacy_failure_class']=type(scan_error).__name__","report['media_privacy_failure_class']='FINITE_SCAN_INCOMPLETE'")
with Path(args.output).open('x') as f:f.write(s)
print(hashlib.sha256(s.encode()).hexdigest())

"""Independent, read-only private-DEB verifier. Never extracts payloads or runs hooks."""
import argparse, hashlib, io, json, pathlib, re, subprocess, tarfile, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,code):
 if not ok:raise ValueError(code)
def digest_file(p):return sha(pathlib.Path(p).read_bytes())
def path_name(raw):
 if raw in ('.','./'):return '.'
 n=raw[2:] if raw.startswith('./') else raw
 n=n.rstrip('/');p=pathlib.PurePosixPath(n)
 require(bool(n) and not p.is_absolute() and '..' not in p.parts and str(p)==n and '\x00' not in n,'UNSAFE_MEMBER_PATH')
 return n

def tar_inventory(raw,control=False):
 rows={}
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:*') as t:
  for m in t.getmembers():
   n=path_name(m.name);require(n not in rows,'DUPLICATE_MEMBER');require(not m.name.endswith('/') or m.isdir(),'REGULAR_TRAILING_SLASH')
   require(m.isfile() or m.isdir() or m.issym() or m.islnk(),'UNEXPECTED_MEMBER_TYPE')
   row={'type':m.type.decode('ascii'),'mode':m.mode,'uid':m.uid,'gid':m.gid,'link':m.linkname,'pax':{k:v for k,v in m.pax_headers.items() if k!='mtime'}}
   if m.isfile():
    b=t.extractfile(m).read();row.update(sha256=sha(b),md5=hashlib.md5(b).hexdigest())
    if control and n=='md5sums':row['content']=b
   rows[n]=row
 return rows

def read_deb(path):
 answer={}
 for label,flag in [('data','--fsys-tarfile'),('control','--ctrl-tarfile')]:
  r=subprocess.run(['dpkg-deb',flag,str(path)],capture_output=True,timeout=120)
  require(r.returncode==0,'DEB_TAR_READ_FAILED');answer[label]=tar_inventory(r.stdout,label=='control')
 return answer

def metadata(row):return {k:row[k] for k in ('type','mode','uid','gid','link','pax')}
def delta_map(rows):
 out={}
 for r in rows:
  require(r['path'] not in out,'DUPLICATE_EXPECTED_DELTA');path_name(r['path']);out[r['path']]=r
 return out

def compare_members(before,after,deltas):
 """Only explicitly expected regular-file changes; all other members exactly preserved."""
 expected=delta_map(deltas)
 additions={n for n,r in expected.items() if r['before_sha256'] is None}
 require(set(after)==set(before)|additions,'MEMBER_INVENTORY_DRIFT')
 for n in additions:
  require(n not in before,'ADDITION_COLLISION');require(after[n].get('pax')=={},'ADDITION_PAX_METADATA')
 for n,b in before.items():
  if n not in expected:require(b==after[n],'UNCHANGED_MEMBER_DRIFT:'+n)
 for n,r in expected.items():
  a=after.get(n);require(a is not None,'EXPECTED_MEMBER_MISSING')
  require(a['type'] in ('0','\x00') and a['link']=='','DELTA_NOT_REGULAR')
  require(a.get('sha256')==r['after_sha256'],'DELTA_OUTPUT_HASH')
  if r['before_sha256'] is not None:
   b=before.get(n);require(b is not None and b['type'] in ('0','\x00') and b.get('sha256')==r['before_sha256'],'DELTA_INPUT_HASH')
   require(metadata(b)==metadata(a),'REPLACEMENT_METADATA_DRIFT')
  for k in ('mode','uid','gid'):
   if k in r:require(type(r[k]) is int and a[k]==r[k],'EXPECTED_METADATA_DRIFT')
 return len(expected)

def verify_md5(data,control):
 require('md5sums' in control and 'content' in control['md5sums'],'MD5SUMS_MISSING')
 expected={n:r['md5'] for n,r in data.items() if 'md5' in r};actual={}
 for line in control['md5sums']['content'].splitlines():
  match=re.fullmatch(rb'([0-9a-f]{32})  (.+)',line);require(match is not None,'MD5SUMS_LINE')
  n=match[2].decode('utf-8');require(path_name(n)==n and n not in actual,'MD5SUMS_PATH_OR_DUPLICATE');actual[n]=match[1].decode()
 require(actual==expected,'MD5SUMS_CONTENT_OR_INVENTORY')

def compare_package(before,after,data_deltas,control_deltas):
 compare_members(before['data'],after['data'],data_deltas)
 # md5sums is derived, not blindly trusted as an allowlisted arbitrary file.
 verify_md5(after['data'],after['control'])
 b=dict(before['control']);a=dict(after['control']);old=b.pop('md5sums',None);new=a.pop('md5sums')
 if old is not None:require(metadata(old)==metadata(new),'MD5SUMS_METADATA')
 else:require(metadata(new)=={'type':'0','mode':0o644,'uid':0,'gid':0,'link':'','pax':{}},'MD5SUMS_ADDITION_METADATA')
 compare_members(b,a,control_deltas)


def pinned_entry(entry):
 require(set(entry)=={'path','sha256'},'INPUT_ENTRY_SCHEMA')
 p=pathlib.Path(entry['path']);p=p if p.is_absolute() else ROOT/p
 require(p.is_file() and not p.is_symlink(),'INPUT_REGULAR_REQUIRED')
 raw=p.read_bytes();require(sha(raw)==entry['sha256'],'INPUT_HASH_DRIFT');return raw

def load_inputs(path,pin):
 raw=pathlib.Path(path).read_bytes();require(sha(raw)==pin,'VERIFIER_CONTRACT_HASH')
 c=json.loads(raw);require(type(c.get('schema')) is int and c['schema']==1,'VERIFIER_SCHEMA')
 names={'bundle','published','payload','controls','hooks','privacy_contract'}
 require(set(c['inputs'])==names,'INPUT_NAMES')
 loaded={n:pinned_entry(e) for n,e in c['inputs'].items()}
 for n in names-{'bundle'}:loaded[n]=json.loads(loaded[n])
 privacy=loaded['privacy_contract']
 for name,p in {**privacy['helpers'],**privacy['evidence']}.items():pinned_entry({'path':name,'sha256':p})
 require(loaded['payload']['privacy_contract_sha256']==c['inputs']['privacy_contract']['sha256'],'PRIVACY_PROOF_JOIN')
 require(loaded['payload']['bundle_sha256']==c['inputs']['bundle']['sha256'] and loaded['controls']['bundle_sha256']==c['inputs']['bundle']['sha256'],'BUNDLE_PROOF_JOIN')
 for h in c['new_helpers']:pinned_entry({'path':h['source_path'],'sha256':h['after_sha256']})
 return c,loaded


def expected_deltas(c,inputs):
 packages=inputs['published']['packages'];names=[p['control']['Package'] for p in packages]
 require(len(names)==17 and len(set(names))==17,'PACKAGE_INVENTORY')
 result={n:{'data':[],'control':[]} for n in names}
 payload=inputs['payload']['source_changes'];require(len(payload)==78,'PAYLOAD_COUNT')
 require(len({r['path'] for r in payload})==78 and sum(r['operation']=='add' for r in payload)==1,'PAYLOAD_INVENTORY')
 for r in payload:
  require(r['package'] in result and r['operation'] in ('add','replace'),'PAYLOAD_PACKAGE_OPERATION')
  require((r['published_sha256'] is None)==(r['operation']=='add'),'PAYLOAD_BEFORE_OPERATION')
  result[r['package']]['data'].append({'path':'opt/kaltura/app/'+r['path'],'before_sha256':r['published_sha256'],'after_sha256':r['after_sha256'],'mode':r['mode'],'uid':r['uid'],'gid':r['gid']})
 privacy={r['path']:r['after_sha256'] for r in payload if r['privacy']}
 require(privacy==inputs['privacy_contract']['expected_privacy_after'],'PRIVACY_OUTPUT_JOIN')
 controls=inputs['controls']['packages'];require(len(controls)==17 and {r['package'] for r in controls}==set(names),'CONTROL_INVENTORY')
 for r in controls:result[r['package']]['control'].append({'path':'control','before_sha256':r['before_sha256'],'after_sha256':r['after_sha256']})
 for r in inputs['hooks']['rows']:
  if 'hook' in r:
   require(r['package'] in result and r['hook'] in ('preinst','postinst','prerm','postrm','config'),'HOOK_IDENTITY')
   result[r['package']]['control'].append({'path':r['hook'],'before_sha256':r['before_sha256'],'after_sha256':r['after_sha256']})
  else:
   require(r['path']=='opt/kaltura/bin/kaltura-functions.rc','HOOK_PAYLOAD_IDENTITY')
   result['kaltura-postinst']['data'].append({'path':r['path'],'before_sha256':r['before_sha256'],'after_sha256':r['after_sha256']})
 helpers=c['new_helpers'];require(len(helpers)==2 and {r['path'] for r in helpers}=={'opt/kaltura/bin/pilot83-private-hook-functions.sh','opt/kaltura/bin/pilot83-private-argv.php'},'HELPER_INVENTORY')
 for r in helpers:
  require(r['package']=='kaltura-postinst' and r['before_sha256'] is None,'HELPER_IDENTITY')
  result[r['package']]['data'].append({k:r[k] for k in ('path','before_sha256','after_sha256','mode','uid','gid')})
 for p in result.values():
  for section in p.values():delta_map(section)
 return result


def verify(first,second,contract,pin,output):
 output=pathlib.Path(output);require(not output.exists(),'FRESH_REPORT_REQUIRED')
 require(first.resolve()!=second.resolve(),'INDEPENDENT_DIRECTORIES_REQUIRED')
 c,inputs=load_inputs(contract,pin);deltas=expected_deltas(c,inputs);rows=[]
 versions={r['package']:r['after_version'] for r in inputs['controls']['packages']}
 expected_names={p['control']['Package']+'_'+versions[p['control']['Package']]+'_'+p['control']['Architecture']+'.deb' for p in inputs['published']['packages']}
 for root in (first,second):require({p.name for p in (root/'packages').glob('*.deb')}==expected_names,'BUILT_PACKAGE_INVENTORY')
 with tarfile.open(fileobj=io.BytesIO(inputs['bundle']),mode='r:gz') as bundle,tempfile.TemporaryDirectory(prefix='private-deb-verifier-') as temp:
  members=bundle.getmembers();require(len({m.name for m in members})==len(members),'BUNDLE_DUPLICATE_MEMBER')
  for p in inputs['published']['packages']:
   name=p['control']['Package'];member=bundle.getmember(p['member']);require(member.isfile() and member.size==p['bytes'],'INPUT_DEB_MEMBER');raw=bundle.extractfile(member).read();require(sha(raw)==p['sha256'],'INPUT_DEB_HASH')
   old=pathlib.Path(temp)/(name+'.deb');old.write_bytes(raw);before=read_deb(old)
   filename=name+'_'+versions[name]+'_'+p['control']['Architecture']+'.deb';files=[root/'packages'/filename for root in (first,second)]
   require(all(f.is_file() and not f.is_symlink() for f in files),'BUILT_DEB_REGULAR')
   hashes=[digest_file(f) for f in files];require(hashes[0]==hashes[1],'REPRODUCIBLE_DEB_BYTES')
   # Equal complete DEB bytes implies equal parsed trees; parse both anyway for explicit per-build validation.
   for f in files:compare_package(before,read_deb(f),deltas[name]['data'],deltas[name]['control'])
   rows.append({'package':name,'input_sha256':p['sha256'],'sha256':hashes[0],'bytes':files[0].stat().st_size,'builds_verified':2,'data_expected_deltas':len(deltas[name]['data']),'control_expected_deltas':len(deltas[name]['control'])})
 # Inputs must not change during the scan.
 load_inputs(contract,pin)
 report={'status':'PRIVATE_DEB_BYTES_VERIFIED_NOT_INSTALLED','verifier_sha256':digest_file(__file__),'inputs_contract_sha256':pin,'packages':rows,'package_count':17,'builds':2,'normalization':'tar mtime/order and textual owner names ignored; other PAX fields, numeric uid/gid, mode, type, link, regular bytes strict','build_report_trusted':False,'md5sums_recomputed':True,'hooks_executed':False,'apt_resolution_verified':False,'application_acceptance':False}
 output.write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('first',type=pathlib.Path);a.add_argument('second',type=pathlib.Path);a.add_argument('--inputs',type=pathlib.Path,required=True);a.add_argument('--inputs-sha256',required=True);a.add_argument('--output',type=pathlib.Path,required=True);x=a.parse_args();print(json.dumps(verify(x.first,x.second,x.inputs,x.inputs_sha256,x.output),indent=2))

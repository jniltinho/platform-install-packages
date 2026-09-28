"""Versioned exact FileSync URL join plus pre-throw private provenance receipts."""
import argparse,hashlib
from pathlib import Path
H=Path(__file__).parent
SOURCE_PINS={'/opt/kaltura/app/alpha/lib/model/asset.php':'34f9e81972369706ea01f5e8a3ba19cd6999d2f6804f25ccdf89cac0bf74933d','/opt/kaltura/app/alpha/lib/model/DeliveryProfileVod.php':'e9058bbd6cc16aa79a928ddf91ef80e819481f43404ed7d3fddb35ec4b310494','/opt/kaltura/app/alpha/apps/kaltura/lib/myContentStorage.class.php':'090d3232baca0482cf7cf52f7011eb896270f3e18e778fdee7e2171421c3f2a9','/opt/kaltura/app/configurations/apache/conf.d/enabled.kaltura.conf':'0cc12e21735c3f7e968ceb9fcf35426fab678ce8a68c9fdfc71fd03612ba8ba5'}
CODES=['DIRECT_STORAGE_ROOT','DIRECT_STORAGE_PATH','DIRECT_STORAGE_JOIN','DIRECT_URL_SHAPE','DIRECT_CREDENTIAL_SHAPE','DIRECT_PATTERN_LIMIT','DIRECT_URL_CREDENTIAL','DIRECT_URL_AUTH','DIRECT_URL_MISMATCH','DIRECT_SOURCE_PIN','PROVENANCE_PIN','PROVENANCE_LIMIT','DIRECT_ROW']
def build():
 raw=(H/'guest_progressive443.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='2b6cc743bb9dfa59dc0256294c924f39de05e4bff9c6649b24ac2799fb6bd889'
 s=raw.decode().replace("media_window=None;tracked_tokens=[];failure_stage='PREFLIGHT'","media_window=None;tracked_tokens=[];failure_stage='PREFLIGHT';secret=None;ks=None;canary=None")
 helpers={n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in ('direct_content.py','privacy_provenance.py')}
 anchor="  private_before=legacy.logging_preflight();config_before=overlay.audits()[1]"
 added="  for name,pin in "+repr(helpers)+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'PROVENANCE_PIN')\n"
 added+="  content=load('direct_content',NEW_HERE/'direct_content.py');provenance=load('privacy_provenance',NEW_HERE/'privacy_provenance.py')\n"
 added+="  def direct_source_guard():\n   for name,pin in "+repr(SOURCE_PINS)+".items():\n    p=Path(name);info=p.lstat();need(stat.S_ISREG(info.st_mode) and info.st_uid==0 and info.st_nlink==1 and info.st_size<=512*1024 and not info.st_mode&0o002 and hashlib.sha256(p.read_bytes()).hexdigest()==pin,'DIRECT_SOURCE_PIN')\n  direct_source_guard()\n"
 s=s.replace(anchor,added+anchor)
 anchor="   accepted(f,j)\n"
 # Both accepted() sites receive provenance BEFORE the possible positive-match throw.
 idx=s.index(anchor);s=s[:idx]+"   record_match('files_and_journal',patterns,f,j,number)\n"+s[idx:]
 idx=s.index(anchor,s.index(anchor)+len(anchor));s=s[:idx]+"   record_match('files_after_journal',patterns,f,j,number)\n"+s[idx:]
 anchor="  def audit(patterns,start,jstart):"
 added="""  def record_match(phase,patterns,f,j,number):
   item=provenance.receipt(number,phase,patterns,f,j,secret=secret.encode() if secret else None,ks=ks.encode() if ks else None,canary=canary.encode() if canary else None,candidates=[v.encode() for v in tracked_tokens])
   private_json(private_dir/('matches-'+str(number)+'-'+phase+'.json'),item)
   records=report.setdefault('match_provenance',[]);need(len(records)<128,'PROVENANCE_LIMIT');records.append(item)
"""
 s=s.replace(anchor,added+anchor)
 anchor="  need(sync_id==315 and legacy.checksum(stored)==legacy.SOURCE_PIN,'STORED_SOURCE_BYTES')"
 s=s.replace(anchor,anchor+"\n  selected_rows=[row for row in rows if row[0]=='315'];need(len(selected_rows)==1,'DIRECT_ROW');storage_root=selected_rows[0][4];storage_path=selected_rows[0][5]\n  try:content.mapping(storage_root,storage_path,str(stored))\n  except content.Rejected as error:raise Rejected(str(error)) from None")
 s=s.replace("guard.inspect(result,secret,ks,tracked_tokens)","content.check(result,secret,ks,tracked_tokens,root=storage_root,path=storage_path,stored=str(stored))")
 s=s.replace("except guard.Rejected as error:","except content.Rejected as error:").replace("code if code in ('URL_SHAPE','URL_PATTERN_LIMIT','URL_CREDENTIAL','URL_AUTH_SHAPE') else 'URL_SHAPE'","code if code in "+repr(CODES)+" else 'DIRECT_URL_SHAPE'")
 s=s.replace("   guard.inspect(url,secret,ks,tracked_tokens)","   content.check(url,secret,ks,tracked_tokens,root=storage_root,path=storage_path,stored=str(stored))")
 s=s.replace("  failure_stage='POSTCHECK'","  failure_stage='POSTCHECK'\n  direct_source_guard()\n  report['direct_content_join']={'file_sync_id':315,'source_grammar_verified':True,'stored_source_bytes_verified':True,'native_url_unchanged':True,'historical_failure_reclassified':False}")
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES=['+repr(CODES)[1:-1]+',')
 return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();s=build()
 with Path(a.output).open('x') as f:f.write(s)
 print(hashlib.sha256(s.encode()).hexdigest())

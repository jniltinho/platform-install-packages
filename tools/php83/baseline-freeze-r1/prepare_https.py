"""HTTPS-only derivative with mandatory exact TLS sink extension on every inventory."""
import argparse,hashlib
from pathlib import Path
H=Path(__file__).parent
raw=(H/'guest_untimed_r2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='b6d8c3e0145690c070ff78c2cb09de8ff74ede5641c662873fedc62406395b4c'
s=raw.decode();pin='d67eb65900c3134c91efaf94b18ba482b59261c81b0084de0cea3bcd37d5246c'
assert hashlib.sha256((H/'privacy_logs_r2.py').read_bytes()).hexdigest()==pin
anchor="  legacy=__import__('untimed_driver') # Importable by multiprocessing spawn children."
s=s.replace(anchor,anchor+"""
  need(hashlib.sha256((NEW_HERE/'privacy_logs_r2.py').read_bytes()).hexdigest()=='d67eb65900c3134c91efaf94b18ba482b59261c81b0084de0cea3bcd37d5246c','TLS_LOG_ADAPTER_PIN')
  tls_logs=load('baseline_tls_logs_r2',NEW_HERE/'privacy_logs_r2.py')
  old_logs=legacy.logs
  legacy.logs=lambda:tls_logs.extend(old_logs)
  legacy.logs() # Mandatory metadata inventory before any credential request/read.
  tls_ca=legacy.read_file(Path('/var/lib/kaltura-baseline-tls-r2/ca.crt'),16384,private=True)
  need(hashlib.sha256(tls_ca).hexdigest()=='5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef','TLS_CA_PIN')
""")
old="legacy.PostTransport(legacy.Origin('192.168.56.74','http',80))"
new="legacy.PostTransport(legacy.Origin('192.168.56.74','https',8443),tls_ca,'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef')"
assert s.count(old)==2;s=s.replace(old,new)
s=s.replace("report['status']='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE'", "report['tls_transport']={'scheme':'https','port':8443,'ca_sha256':'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef','tls_logs_in_every_inventory':True};report['status']='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE'")
s=s.replace('FIXED_FAILURE_CODES=[',"FIXED_FAILURE_CODES=['TLS_LOG_ADAPTER_PIN','TLS_CA_PIN',")
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
with Path(a.output).open('x') as f:f.write(s)
print(hashlib.sha256(s.encode()).hexdigest())

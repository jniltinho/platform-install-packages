"""Exact derivative; no PHP/application/source mutation on host or guest."""
import argparse,hashlib
from pathlib import Path
HERE=Path(__file__).parent
raw=(HERE/'guest.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='6826f1b731dd9edcfefd0cf4c39f5fe5a85797f4443d0bc7fc37d67f661931cb'
s=raw.decode().replace("NEW_HERE/'observation.py'", "NEW_HERE/'observation_v2.py'")
s=s.replace('e945b7f0ff5a9896f942281a123ee8c76ea398e45bffce9fb3d95ff8f3796364',hashlib.sha256((HERE/'observation_v2.py').read_bytes()).hexdigest())
s=s.replace("SELECT id,partner_id,data,conversion_profile_id FROM entry", "SELECT id,partner_id,COALESCE(data,''),conversion_profile_id FROM entry")
s=s.replace("concrete=obs.entry_version(rows[0][2]);selected=rows[0][3]", "concrete=obs.entry_version(rows[0][2]);selected=rows[0][3]\n  need(selected=='14','OBSERVED_PROFILE_SELECTION')")
s=s.replace("report['fixture']=obs.fixture(entry,listing,concrete) if positive else None", "report['fixture']=obs.fixture(entry,listing,concrete)")
s=s.replace("'OBSERVED_FROM_ENTRY_DATA' if positive else 'UNRESOLVED'", "'OBSERVED_FROM_ENTRY_DATA' if concrete is not None else 'UNRESOLVED'")
a=argparse.ArgumentParser();a.add_argument('--output',required=True);args=a.parse_args()
with Path(args.output).open('x') as f:f.write(s)
print(hashlib.sha256(s.encode()).hexdigest())

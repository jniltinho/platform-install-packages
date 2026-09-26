#!/usr/bin/env python3
"""Guest-only baseline74 one-round collector; no baseline acceptance claim."""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import datetime
import sys
from protocol import private_credentials,run_round,strict_json,validate_fixture,read_file
from transport import Origin,PostTransport

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--credentials',type=Path,required=True)
    ap.add_argument('--fixture',type=Path,required=True)
    ap.add_argument('--fixture-sha256',required=True)
    ap.add_argument('--scheme',choices=['http','https'],required=True)
    ap.add_argument('--port',type=int,required=True)
    ap.add_argument('--ca',type=Path)
    ap.add_argument('--ca-sha256')
    ap.add_argument('--phase',choices=['warmup','measured'],required=True)
    ap.add_argument('--round-index',type=int,required=True)
    args=ap.parse_args()
    if socket.gethostname()!='kaltura-php74-baseline':raise ValueError('Guest identity')
    if not 1<=args.round_index<=({'warmup':2,'measured':5}[args.phase]):raise ValueError('Round identity')
    before=read_file(args.fixture,65536)
    if hashlib.sha256(before).hexdigest()!=args.fixture_sha256:raise ValueError('Fixture identity')
    fixture=strict_json(before)
    credentials=private_credentials(args.credentials)
    validate_fixture(fixture,credentials.partner_id)
    ca=read_file(args.ca,1024*1024) if args.ca else None
    transport=PostTransport(Origin('192.168.56.74',args.scheme,args.port),ca,args.ca_sha256)
    here=Path(__file__).resolve().parent
    dependencies=[here/n for n in ['run.py','protocol.py','transport.py']]+[here.parent/'baseline-protocol'/n for n in ['guarded_http.py','deadline_transport.py']]
    hashes={str(p.relative_to(here.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}
    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=run_round(transport,credentials,fixture)
    try:
        harness_ok=hashes=={str(p.relative_to(here.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}
        fixture_ok=read_file(args.fixture,65536)==before
    except Exception:
        harness_ok=False;fixture_ok=False
    result.update(harness_unchanged=harness_ok,fixture_unchanged=fixture_ok)
    if not (harness_ok and fixture_ok):result['functional_round_pass']=False
    result.update(phase=args.phase,round_index=args.round_index,fixture_sha256=args.fixture_sha256,scheme=args.scheme,port=args.port,ca_sha256=args.ca_sha256,hostname=socket.gethostname(),harness_sha256=hashes,started_at_utc=timestamp)
    print(json.dumps(result))
    return 0 if result['functional_round_pass'] else 1
if __name__=='__main__':
    try:code=main()
    except Exception:
        # Even unexpected parser/file/JSON/API exceptions cannot echo credentials.
        print('Baseline API preparation rejected',file=sys.stderr);code=1
    raise SystemExit(code)

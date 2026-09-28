"""Exact native port443 GET derivative; API8443 and all privacy controls unchanged."""
import argparse,hashlib
from pathlib import Path
H=Path(__file__).parent
def pinned(name,pin):
 raw=(H/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==pin;return raw.decode()
def sources():
 delivery=pinned('short_delivery.py','ee144fa2a27e9b86e6cfb6257965cbec47970b3217df255376198fdc661ab72e')
 assert delivery.count("ORIGIN = 'https://192.168.56.74:8443'")==1
 assert delivery.count('p.port==8443')==1
 delivery=delivery.replace("ORIGIN = 'https://192.168.56.74:8443'","ORIGIN = 'https://192.168.56.74'").replace('p.port==8443','(p.port is None or p.port==443)')
 transport=pinned('media_get.py','fb67ac1f7bdb39c75cc875389f2f9734d4a0012df550f1d62e2ee120a6240476')
 assert transport.count("Origin('192.168.56.74','https',8443)")==1
 transport=transport.replace("Origin('192.168.56.74','https',8443)","Origin('192.168.56.74','https',443)")
 guest=pinned('guest_progressive.py','70de8974818252d0f5a26a81efe7f861aa8d8387b6ef700bb3c7bf9e060d9cd1')
 guest=guest.replace('short_delivery.py','short_delivery443.py').replace("load('short_delivery'","load('short_delivery443'").replace('media_get.py','media_get443.py').replace('import media_get','import media_get443').replace('media_get.request','media_get443.request')
 guest=guest.replace('ee144fa2a27e9b86e6cfb6257965cbec47970b3217df255376198fdc661ab72e',hashlib.sha256(delivery.encode()).hexdigest()).replace('fb67ac1f7bdb39c75cc875389f2f9734d4a0012df550f1d62e2ee120a6240476',hashlib.sha256(transport.encode()).hexdigest())
 return {'short_delivery443.py':delivery,'media_get443.py':transport,'guest_progressive443.py':guest}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',required=True);a=p.parse_args();out=Path(a.output_dir);out.mkdir(mode=0o700)
 for name,value in sources().items():
  with (out/name).open('x') as f:f.write(value)
  print(name,hashlib.sha256(value.encode()).hexdigest())

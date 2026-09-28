"""Fix only new dependency pin iteration; preserve failed R1 source/receipt."""
from pathlib import Path
import hashlib,ast
H=Path(__file__).parent
def build():
 raw=(H/'guest_hls_media8444.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='3b91f946c0145067d292c125b1fb6f96ad5eaefe0e931e03f2129eebb2daedad'
 text=raw.decode();tree=ast.parse(text)
 matches=[n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.iter,ast.Dict) and any(isinstance(k,ast.Constant) and k.value=='hls_context_proof.py' for k in n.iter.keys)]
 assert len(matches)==1
 node=matches[0];lines=text.splitlines(keepends=True);line=lines[node.lineno-1];assert line.count('}:need(')==1
 lines[node.lineno-1]=line.replace('}:need(','}.items():need(')
 return ''.join(lines)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())

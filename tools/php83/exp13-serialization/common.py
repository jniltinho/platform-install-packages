"""Pinned existing sources and oracle; no application code executes locally."""
import hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
E=ROOT/'doc/php83/evidence/exp13-serialization'
OLD=ROOT/'doc/php83/evidence/serialization-contracts'
PHASE='exp13-serialization-r1';REMOTE='/home/vagrant/php-exp13-serialization-r1'
ZIP_PINS={'exp12':'de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b','exp13':'6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944'}
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def inputs():
 raw=(HERE/'input-pins.json').read_bytes();need(sha(raw)=='dbd49511b260ecdd7fa431ef395c45c72717a5a01d0a846dc8177e9d244383da','Input pin identity');pins=json.loads(raw)
 for p,h in pins.items():need(sha((ROOT/p).read_bytes())==h,'Frozen input drift '+p)
 need(pins['doc/php83/evidence/serialization-contracts/r3-stage-identities.json']=='5f628293182feed0066274ed89dff3d362cd6ad781d2ba4b9198df9aef6df7d5','Wrong R3 closure')
 return pins
def load_oracle():
 inputs();directory=ROOT/'tools/php83/serialization-contracts';sys.path.insert(0,str(directory))
 spec=importlib.util.spec_from_file_location('frozen_r3',directory/'reconcile-r3.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def references():
 inputs();return {v:json.loads((OLD/f'r3-primary{v}.json').read_bytes()) for v in ['74','83']}
def key(r):return tuple(r[k] for k in ['variant','kind','operation','writer'])
def expected():return [r for r in references()['83']['records'] if r['variant']!='cachefix']
def compare(records):
 oracle=load_oracle();refs=references();expected_rows=expected()
 need(len(records)==88 and [key(r) for r in records]==[key(r) for r in expected_rows],'Exact88 inventory')
 for row,old in zip(records,expected_rows):
  need(type(row['exit']) is int and row['exit']==0,'Native integer exit0')
  need(row['stdout']==old['stdout'] and row['stderr']==old['stderr'],'Historical full channels changed')
 # An analysis-only join supplies 38 historical74 and 8 historical cachefix rows
 # to the unchanged typed oracle. Never export this join as a native report.
 live={key(r):r for r in records}
 refs['83']['records']=[r if r['variant']=='cachefix' else live[key(r)] for r in refs['83']['records']]
 checks=oracle.reconcile(refs,json.loads((OLD/'r3-stage-identities.json').read_bytes()))
 return {'status':'MATCHED_BOUNDED_ARTIFACT_CONTRACT_WITH_KNOWN_WIRE_BREAK','new_native83_processes':88,'historical74_rows_NOT_RERUN':38,'historical_cachefix83_rows_NOT_RERUN':8,'typed_oracle_checks':checks,'rollback_compatible':False,'application_acceptance':False}

def preparation():
 raw=(E/'preparation.json').read_bytes();need(sha(raw)=='849ce67704d6598a28ff7b04ba157aea8d249587e5076bdd40e90d209ddfb5e2','Preparation identity');return json.loads(raw)

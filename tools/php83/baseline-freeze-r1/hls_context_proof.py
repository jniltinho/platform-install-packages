"""Exact observed context selection, not a forged commit-success receipt."""
import hashlib,json
from delivery_context_pair_r2 import validate
class Rejected(ValueError):pass
def receipt_id(v):
 # Canonical object digest accepts insignificant serialization whitespace only.
 expected='306ef7ef587ec8e29ceb172a38fa2b299f8a3ffe6b5592bc5532f14044be88ac'
 if hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=expected:raise Rejected('CONTEXT_PROOF')
 if v['guest_exit']!=0 or v['unit_inactive'] is not True or v['status']!='OBSERVATION_CAPTURED_NOT_APPROVED':raise Rejected('CONTEXT_PROOF')
 row=v['phase_receipts'][-1];pair=validate(row['delivery_context_pair'])
 if row['media_tls_logs_in_every_inventory'] is not True:raise Rejected('CONTEXT_PROOF')
 return pair['selections'][1]['profile_id']

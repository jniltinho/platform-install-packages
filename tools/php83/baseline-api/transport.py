"""Private POST adapter over the separately reviewed total-deadline executor."""
import base64
from dataclasses import dataclass, field
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request
PROTOCOL=Path(__file__).resolve().parent.parent/'baseline-protocol'
sys.path.insert(0,str(PROTOCOL))
import deadline_transport as deadline
from guarded_http import BoundaryError, Client, Origin, read_bounded

RESPONSE_LIMIT=1024*1024
IPC_LIMIT=2*1024*1024
API_PATH='/api_v3/index.php'

class WorkerCleanupError(RuntimeError):
    pass

@dataclass(frozen=True)
class Reply:
    value: object = field(repr=False)
    child_http_ns: int
    parent_ns: int

def strict_json(raw):
    def pairs(items):
        out={}
        for key,value in items:
            if key in out:raise ValueError('Duplicate JSON key')
            out[key]=value
        return out
    def bad_constant(_):raise ValueError('Non-finite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad_constant)

def _post(client,url,params,timeout):
    # Authentication is POST-body-only; the endpoint is fixed, without query.
    payload=urlencode(params).encode('ascii')
    if len(payload)>64*1024:raise BoundaryError('Request body limit')
    req=Request(url,data=payload,method='POST',
                headers={'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json'})
    started=time.monotonic_ns()
    with client.opener.open(req,timeout=timeout) as response:
        if response.status!=200:raise BoundaryError('HTTP status')
        client.origin.validate(response.geturl())
        if response.headers.get_content_type()!='application/json':raise BoundaryError('Response type')
        raw=read_bounded(response,RESPONSE_LIMIT)
    elapsed=time.monotonic_ns()-started
    return raw,elapsed

def _pack_post(client,url,params,buffer,state):
    raw,elapsed=_post(client,url,params,30)
    packed=json.dumps({'response':base64.b64encode(raw).decode('ascii'),'http_ns':elapsed},separators=(',',':')).encode()
    if len(packed)>IPC_LIMIT:raise BoundaryError('IPC body limit')
    memoryview(buffer).cast('B')[:len(packed)]=packed
    state.value=len(packed)

def _post_worker(fields,ca,pin,params,buffer,state):
    try:
        origin=Origin(*fields)
        if origin.ip!='192.168.56.74':raise BoundaryError('Baseline74 only')
        client=Client(origin,ca,pin)
        _pack_post(client,f'{origin.scheme}://{origin.ip}:{origin.port}{API_PATH}',params,buffer,state)
    except Exception:
        state.value=-2  # Never marshal exception text or request/response bodies.

class PostTransport:
    def __init__(self,origin,ca=None,pin=None):
        if type(origin) is not Origin or origin.ip!='192.168.56.74':
            raise BoundaryError('Explicit baseline74 origin required')
        Client(origin,ca,pin)
        self.origin=origin;self.ca=ca;self.pin=pin
    def request(self,params):
        start=time.monotonic_ns()
        try:
            packed=deadline._bounded(_post_worker,((self.origin.ip,self.origin.scheme,self.origin.port),self.ca,self.pin,params),limit=IPC_LIMIT,deadline=30)
        except BoundaryError as exc:
            if str(exc)=='Transport worker cleanup failed':
                raise WorkerCleanupError('Request worker cleanup failed') from None
            raise BoundaryError('Transport request failed') from None
        try:
            envelope=strict_json(packed)
            if set(envelope)!={'response','http_ns'} or type(envelope['http_ns']) is not int or envelope['http_ns']<=0:
                raise ValueError('Invalid timing envelope')
            raw=base64.b64decode(envelope['response'],validate=True)
            if len(raw)>RESPONSE_LIMIT:raise ValueError('Excessive response')
            value=strict_json(raw)
            elapsed=time.monotonic_ns()-start
            if elapsed<envelope['http_ns']:raise ValueError('Timing mismatch')
            return Reply(value,envelope['http_ns'],elapsed)
        except Exception:
            raise BoundaryError('Invalid API response') from None

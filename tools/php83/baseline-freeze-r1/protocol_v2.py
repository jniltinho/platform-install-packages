"""V2 explicit current-selection 34/33/33 protocol: never drop failed or dependency-blocked calls."""
from dataclasses import dataclass,field
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time
from transport import strict_json,WorkerCleanupError

ENTRY=re.compile(r'[0-9]_[a-z0-9]{8}\Z')
TOKEN=re.compile(r'[A-Za-z0-9_+/=-]{20,8192}\Z')
FIELDS={'objectType','id','partnerId','status','mediaType'}
OPERATIONS=['session.start']*34+['media.list']*33+['media.get']*33

class ContractError(ValueError): pass

@dataclass(frozen=True)
class Credentials:
    partner_id:int
    user_id:str
    secret:str=field(repr=False)

def read_file(path,limit,private=False):
    """Walk directories with dir_fd+NOFOLLOW; no FIFO/device or symlink reads."""
    path=Path(path)
    if not path.is_absolute():raise ContractError('Absolute input path required')
    fd=None
    try:
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
        for part in path.parts[1:-1]:
            nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=nxt
        parent=os.fstat(fd)
        if private and (parent.st_uid!=os.geteuid() or stat.S_IMODE(parent.st_mode)!=0o700):
            raise ValueError()
        child=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
        try:
            info=os.fstat(child)
            if not stat.S_ISREG(info.st_mode) or info.st_size>limit:raise ValueError()
            if private and (info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1):raise ValueError()
            raw=os.read(child,limit+1)
            if len(raw)>limit:raise ValueError()
            return raw
        finally:os.close(child)
    except Exception:
        raise ContractError('Invalid input file') from None
    finally:
        if fd is not None:os.close(fd)

def private_credentials(path):
    try:
        data=strict_json(read_file(path,16384,private=True))
        if set(data)!={'partner_id','user_id','secret'}:raise ValueError()
        if type(data['partner_id']) is not int or data['partner_id']<=0:raise ValueError()
        if type(data['user_id']) is not str or not re.fullmatch(r'[A-Za-z0-9_.-]{1,128}',data['user_id']):raise ValueError()
        if type(data['secret']) is not str or not 1<=len(data['secret'])<=4096 or any(ord(c)<32 for c in data['secret']):raise ValueError()
        return Credentials(**data)
    except Exception:
        raise ContractError('Invalid private credential file') from None

def validate_fixture(fixture,partner_id):
    if type(fixture) is not dict or set(fixture)!={'version','entry','page_size','page_index','order_by','list_total_count','media_get_version','observed_entry_data_version','source_asset','source_media_sha256'}:raise ContractError('Fixture schema')
    if type(fixture['version']) is not int or fixture['version']!=2 or type(fixture['page_size']) is not int or fixture['page_size']!=1 or type(fixture['page_index']) is not int or fixture['page_index']!=1 or fixture['order_by']!='+createdAt':raise ContractError('Frozen paging contract')
    if type(fixture['list_total_count']) not in {int,str} or str(fixture['list_total_count'])!='1':raise ContractError('Frozen count domain')
    if type(fixture['media_get_version']) is not int or fixture['media_get_version']!=-1:raise ContractError('Frozen current selection')
    observed=fixture['observed_entry_data_version']
    if observed is not None and (type(observed) is not int or not 0<=observed<=999999999):raise ContractError('Observed entry data version')
    asset=fixture['source_asset']
    if type(asset) is not dict or set(asset)!={'id','version','file_sync_id'} or type(asset['id']) is not str or not ENTRY.fullmatch(asset['id']) or type(asset['version']) is not str or not re.fullmatch('[0-9]{1,9}',asset['version']) or type(asset['file_sync_id']) is not int or asset['file_sync_id']<=0:raise ContractError('Frozen source asset identity')
    if type(fixture['source_media_sha256']) is not str or not re.fullmatch(r'[0-9a-f]{64}',fixture['source_media_sha256']):raise ContractError('Frozen source media identity')
    entry=fixture['entry']
    if type(entry) is not dict or set(entry)!=FIELDS or entry['objectType']!='KalturaMediaEntry' or type(entry['id']) is not str or not ENTRY.fullmatch(entry['id']):raise ContractError('Frozen media identity')
    for key,value in [('partnerId',partner_id),('status',2),('mediaType',1)]:
        if type(entry[key]) not in {int,str} or str(entry[key])!=str(value):raise ContractError('Frozen media domain')
    return fixture

def media(value,expected):
    if type(value) is not dict:raise ContractError('Media object')
    for key,want in expected.items():
        if key not in value or type(value[key]) is not type(want) or value[key]!=want:raise ContractError('Media typed projection')

def validate_response(operation,value,fixture):
    if operation=='session.start':
        if type(value) is not str or not TOKEN.fullmatch(value):raise ContractError('Session token contract')
        return value
    if operation=='media.get':
        media(value,fixture['entry'])
    elif operation=='media.list':
        if type(value) is not dict or value.get('objectType')!='KalturaMediaListResponse' or type(value.get('objects')) is not list or len(value['objects'])!=1:
            raise ContractError('Media list contract')
        # Count's wire type is frozen explicitly by the fixture (not guessed).
        if type(value.get('totalCount')) is not type(fixture['list_total_count']) or value['totalCount']!=fixture['list_total_count']:raise ContractError('Media list count contract')
        media(value['objects'][0],fixture['entry'])
    else:raise ContractError('Unknown operation')

def run_round(transport,credentials,fixture):
    validate_fixture(fixture,credentials.partner_id)
    records=[];token=None;aborted=False
    for index,operation in enumerate(OPERATIONS):
        row={'index':index+1,'operation':operation,'status':'NOT_EXECUTED_DEPENDENCY','child_http_ns':None,'parent_ns':None,'parent_overhead_ns':None,'attempt_wall_ns':None}
        if aborted:
            row['status']='NOT_EXECUTED_ABORT';records.append(row);continue
        if operation!='session.start' and token is None:
            records.append(row);continue
        if operation=='session.start':
            params={'service':'session','action':'start','format':1,'partnerId':credentials.partner_id,'userId':credentials.user_id,'secret':credentials.secret,'type':0,'expiry':3600}
        elif operation=='media.list':
            params={'service':'media','action':'list','format':1,'ks':token,'filter:objectType':'KalturaMediaEntryFilter','filter:idEqual':fixture['entry']['id'],'filter:orderBy':fixture['order_by'],'pager:objectType':'KalturaFilterPager','pager:pageSize':1,'pager:pageIndex':1}
        else:
            params={'service':'media','action':'get','format':1,'ks':token,'entryId':fixture['entry']['id'],'version':fixture['media_get_version']}
        started=time.monotonic_ns()
        try:
            reply=transport.request(params)
            if type(reply.child_http_ns) is not int or type(reply.parent_ns) is not int or not 0<reply.child_http_ns<=reply.parent_ns:raise ContractError('Transport timing contract')
            row.update(child_http_ns=reply.child_http_ns,parent_ns=reply.parent_ns,parent_overhead_ns=reply.parent_ns-reply.child_http_ns)
            validated=validate_response(operation,reply.value,fixture)
            if operation=='session.start':token=validated
            row['status']='PASS'
        except WorkerCleanupError:
            aborted=True;row.update(status='FAIL',failure_kind='WORKER_CLEANUP')
        except Exception:
            row.update(status='FAIL')
            if operation=='session.start':token=None
        row['attempt_wall_ns']=time.monotonic_ns()-started
        records.append(row)
    passed=sum(r['status']=='PASS' for r in records)
    return {'protocol_version':2,'planned':100,'attempted':sum(not r['status'].startswith('NOT_EXECUTED') for r in records),'passed':passed,'failed':sum(r['status']=='FAIL' for r in records),'not_executed':sum(r['status'].startswith('NOT_EXECUTED') for r in records),'aborted':aborted,'functional_round_pass':passed==100,'records':records,'baseline_acceptance':False,'runtime_provider_attestation':'PENDING','timing_boundary':'child opener.open through complete bounded body/close; parent spawn/copy/parse separately'}

"""Frozen r3 ledger guards, reused without weakening; no runtime execution."""
import hashlib,re
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]
RUN=REPO/"doc/php83/evidence/exp14-runtime"

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def strict_exit(value, expected):
    require(type(value) is int and value==expected,'Unexpected or noninteger process status')

def ledger_validate(entries,runtime,phase):
    prefix=phase+runtime
    require(entries[0]['orchestrator_sha256']==digest((RUN/f'{prefix}-orchestrator.py').read_bytes()),'Orchestrator identity')
    expected=[prefix+'-runtime-before',prefix+'-original-before']
    if phase=='primary':expected+=['stage'+runtime]
    if runtime=='74':expected+=['api-primary' if phase=='primary' else 'claude-api']
    expected+=[f'cli{runtime}-primary' if phase=='primary' else f'claude-cli{runtime}',prefix+'-original-after',prefix+'-runtime-after']
    commands=[e for e in entries if 'command' in e]
    require([e['phase'] for e in commands]==expected,'Missing/duplicate/reordered phase ledger')
    require(entries[-1]['stopped_at_unexpected_exit'] is None and entries[-1]['after_snapshot_exit_as_expected'] is True,'Incomplete execution ledger')
    for entry in commands:
        strict_exit(entry['process_exit'],0)
        for channel in ('stdout','stderr','exit'):
            path=REPO/entry[channel+'_path']
            require(path.resolve().is_relative_to(RUN.resolve()) and not path.is_symlink(),'Unconfined ledger path')
            require(digest(path.read_bytes())==entry[channel+'_sha256'],'Ledger output drift')
        require((REPO/entry['exit_path']).read_text().strip()=='0','Recorded exit contents')
        if entry['phase'] not in ('stage74','stage83'):
            require(isinstance(entry['output_sha256'],str) and re.fullmatch('[0-9a-f]{64}',entry['output_sha256']) is not None,'Missing productive phase output hash')
        else:
            require(entry['output_sha256'] is None,'Unexpected stage report')
        if entry['phase'] not in ('stage74','stage83'):
            path=REPO/entry['output']
            require(path.resolve()==(RUN/(entry['phase']+'.json')).resolve() and not path.is_symlink(),'Unexpected phase report path')
            require(digest(path.read_bytes())==entry['output_sha256'],'Ledger JSON drift')

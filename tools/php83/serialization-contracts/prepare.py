#!/usr/bin/env python3
"""Read only pinned existing archives; produce owned metadata, no extraction or PHP execution."""
import hashlib,json,zipfile
from pathlib import Path
ORIGINAL=Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip')
EXP12=Path('/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip')
PINS={str(ORIGINAL):'58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28',str(EXP12):'de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'}
BASE='vendor/aws/Aws/Common/Credentials/'
PATHS=[BASE+n+'.php' for n in ['CredentialsInterface','Credentials','NullCredentials','AbstractCredentialsDecorator','AbstractRefreshableCredentials','CacheableCredentials','RefreshableInstanceProfileCredentials']]+['infra/storage/RefreshableRole.class.php','vendor/aws/aws-autoloader.php']+['vendor/aws/Doctrine/Common/Cache/'+n+'.php' for n in ['FilesystemCache','FileCache','CacheProvider']]+['vendor/aws/Guzzle/Cache/'+n+'.php' for n in ['DoctrineCacheAdapter','CacheAdapterInterface']]
PATHS += ['vendor/aws/Aws/Common/Enum.php','vendor/aws/Aws/Common/Enum/ClientOptions.php','vendor/aws/Guzzle/Common/FromConfigInterface.php']
TARGETS=[BASE+n+'.php' for n in ['Credentials','NullCredentials','AbstractCredentialsDecorator']]
BRIDGE='''
    /** Native O-format bridge; legacy Serializable payload readers remain intact. */
    public function __serialize(): array
    {
        return array('payload' => $this->serialize());
    }

    public function __unserialize(array $data): void
    {
        if (array_keys($data) !== array('payload') || !is_string($data['payload'])) {
            throw new \\UnexpectedValueException('Invalid credential serialization envelope');
        }
        $this->unserialize($data['payload']);
    }
'''
def candidate(source):
    if b'function __serialize' in source or source.count(b'    public function serialize()')!=1:
        raise ValueError('unexpected source signature')
    return source.replace(b'    public function serialize()',BRIDGE.encode()+b'\n    public function serialize()',1)
def read_sources(path):
    if hashlib.sha256(path.read_bytes()).hexdigest()!=PINS[str(path)]: raise ValueError('archive pin mismatch')
    with zipfile.ZipFile(path) as z:
        result={}
        for p in PATHS:
            names=[n for n in z.namelist() if n.endswith('/'+p)]
            if len(names)!=1:raise ValueError('ambiguous/missing source '+p)
            result[p]=z.read(names[0])
    return result
if __name__=='__main__':
    original=read_sources(ORIGINAL); current=read_sources(EXP12);rows=[]
    for p in PATHS:
        a,b=original[p],current[p]
        rows.append({'path':p,'original_sha256':hashlib.sha256(a).hexdigest(),'exp12_sha256':hashlib.sha256(b).hexdigest(),'unchanged':a==b,'candidate_sha256':hashlib.sha256(candidate(b)).hexdigest() if p in TARGETS else None,'numbered_source': ''.join('%d %s\n'%(i,l) for i,l in enumerate(b.decode().splitlines(),1)) if p!='vendor/aws/aws-autoloader.php' else 'Large classmap omitted; exact hash pinned, fixture loads actual file.'})
    out={'status':'LOCAL_PREPARATION_NOT_EXECUTED','archives':PINS,'targets':TARGETS,'files':rows,'candidate':'Provisional 3-file magic bridges only; not selected, not runtime validated.'}
    Path('doc/php83/evidence/serialization-contracts/source-pins.json').write_text(json.dumps(out,indent=2)+'\n')

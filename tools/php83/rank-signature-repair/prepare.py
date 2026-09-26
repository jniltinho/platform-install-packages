#!/usr/bin/env python3
"""Prepare a held single-declaration edit; no PHP, network, SQL or VM actions."""
import argparse
import difflib
import hashlib
import io
import json
from pathlib import Path
import zipfile

TARGET = 'api_v3/lib/KalturaEntryService.php'
ORIGINAL_PIN = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
EXP13_PIN = '6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944'
SOURCE_PIN = '9495b584f73df1f4a11812efa964f57f42562159a405693b71e1731d53fe4dd5'
BEFORE = b'protected function anonymousRankEntry($entryId, $entryType = null, $rank)'
AFTER = b'protected function anonymousRankEntry($entryId, $entryType, $rank)'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def repair(source):
    if sha(source) != SOURCE_PIN or source.count(BEFORE) != 1:
        raise ValueError('Source identity/declaration mismatch')
    candidate = source.replace(BEFORE, AFTER, 1)
    validate(source, candidate)
    return candidate

def validate(source, candidate):
    if sha(source) != SOURCE_PIN or source.count(BEFORE) != 1:
        raise ValueError('Unapproved original')
    if candidate != source.replace(BEFORE, AFTER, 1):
        raise ValueError('Unexpected candidate byte delta')
    if source.count(b'\n') != candidate.count(b'\n'):
        raise ValueError('Line drift')
    return True

def member(path, pin):
    raw = Path(path).read_bytes()
    if sha(raw) != pin:
        raise ValueError('Wrong archive pin')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive members')
        return archive.read('server-Rigel-18.20.0/' + TARGET)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--original', required=True)
    parser.add_argument('--exp13', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    original = member(args.original, ORIGINAL_PIN)
    current = member(args.exp13, EXP13_PIN)
    if original != current:
        raise ValueError('Original/exp13 source disagreement')
    candidate = repair(current)
    patch = ''.join(difflib.unified_diff(current.decode().splitlines(True), candidate.decode().splitlines(True), fromfile='a/'+TARGET, tofile='b/'+TARGET)).encode()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    for name, data in [('original.php',current),('candidate.php',candidate),('rank-signature.patch',patch)]:
        (output/name).write_bytes(data)
    manifest = {'status':'HELD_SOURCE_ONLY_NOT_RUNTIME_VALIDATED','target':TARGET,
        'original_zip_sha256':ORIGINAL_PIN,'exp13_zip_sha256':EXP13_PIN,
        'before_sha256':sha(current),'after_sha256':sha(candidate),'patch_sha256':sha(patch),
        'deleted_bytes':' = null','deleted_byte_count':7,'source_line':1836,
        'body_and_all_other_bytes_unchanged':True,'artifact_selected':False,
        'rank_body_or_persistence_executed':False,'preparer_sha256':sha(Path(__file__).read_bytes())}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest))

if __name__ == '__main__':
    main()

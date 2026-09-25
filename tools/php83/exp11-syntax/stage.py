#!/usr/bin/env python3
"""Validate public ZIP paths/hashes before fresh extraction; never execute PHP."""
import hashlib
import os
import socket
import sys
from pathlib import Path
import stat
import zipfile
from scan import load_contract, require

require(len(sys.argv) == 1 and os.geteuid() == 1000 and
        socket.gethostname() == 'kaltura-php83-lab', 'Requires isolated php83 lab as vagrant')
root = Path('/home/vagrant/php-candidate-syntax-exp11')
require(root.is_dir() and not root.is_symlink(), 'Invalid fresh stage root')
contract = load_contract()
for variant, pin in contract['pins'].items():
    archive = root/(variant+'.zip')
    require(hashlib.sha256(archive.read_bytes()).hexdigest() == pin, 'ZIP mismatch')
    target = root/variant
    require(not target.exists(), 'Refusing existing extraction')
    with zipfile.ZipFile(archive) as z:
        seen = set()
        for item in z.infolist():
            p = Path(item.filename)
            require(not p.is_absolute() and '..' not in p.parts and p.parts[0] == 'server-Rigel-18.20.0', 'Unsafe ZIP path')
            require(item.filename not in seen, 'Duplicate ZIP entry')
            seen.add(item.filename)
            require(not stat.S_ISLNK(item.external_attr >> 16), 'ZIP symlink')
        target.mkdir()
        z.extractall(target)
print('Fresh extraction completed; runtime scanner revalidates every file.')

"""Fail closed until the independently verified exp10 ZIP has a concrete pin."""
from pathlib import Path
import re

def read_pin(path=None):
    path = Path(path) if path is not None else Path(__file__).with_name('artifact-sha256.txt')
    value = path.read_text().strip()
    if not re.fullmatch(r'[0-9a-f]{64}', value):
        raise RuntimeError('Missing or invalid verified exp10 artifact pin')
    return value

if __name__ == '__main__':
    print(read_pin())

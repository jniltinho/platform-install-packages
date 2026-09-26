#!/usr/bin/env bash
# Explicit bootstrap of public artifacts in the two authorized disposable labs.
set -euo pipefail
case "${1:-}" in
 74) conf=/tmp/kaltura-php74-ssh.conf; alias=baseline74; expected=kaltura-php74-baseline ;;
 83) conf=/tmp/kaltura-php83-ssh.conf; alias=php83; expected=kaltura-php83-lab ;;
 *) exit 64 ;;
esac
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
zip=/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp13/Rigel-18.20.0-php83-experimental.exp13.zip
pin=$(python3 "$root/tools/php83/exp13-api/artifact.py")
echo "$pin  $zip" | sha256sum --check --strict
ssh -T -F "$conf" "$alias" "test \"\$(hostname)\" = $expected && mkdir /home/vagrant/php-exp13-regression"
cat "$zip" | ssh -T -F "$conf" "$alias" 'cat > /home/vagrant/php-exp13-regression/exp13.zip'
tar -C "$root/tools/php83" --exclude='__pycache__' -cf - patch-tests exp13-api exp13-regression | ssh -T -F "$conf" "$alias" 'tar -xf - -C /home/vagrant/php-exp13-regression; mv /home/vagrant/php-exp13-regression/patch-tests /home/vagrant/php-exp13-regression/tests; mv /home/vagrant/php-exp13-regression/exp13-api /home/vagrant/php-exp13-regression/api'
ssh -T -F "$conf" "$alias" 'python3 -' <<'PY'
from pathlib import Path
import hashlib,zipfile,re
if not __debug__:raise RuntimeError('Optimized Python not supported')
root=Path('/home/vagrant/php-exp13-regression'); archive=root/'exp13.zip'; source=root/'source'
pin=(root/'api/artifact-sha256.txt').read_text().strip()
assert re.fullmatch('[0-9a-f]{64}',pin)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==pin
source.mkdir()
with zipfile.ZipFile(archive) as z:
 names=z.namelist()
 assert len(names)==len(set(names))
 for i in z.infolist():
  assert not Path(i.filename).is_absolute() and ".." not in Path(i.filename).parts
  assert (i.external_attr >> 16) & 0o170000 != 0o120000
  assert (source/i.filename).resolve().is_relative_to(source.resolve())
 z.extractall(source)
print('EXTRACTED_VERIFIED_EXP13')
PY

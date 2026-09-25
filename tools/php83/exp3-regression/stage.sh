#!/usr/bin/env bash
# Explicit bootstrap of public artifacts in the two authorized disposable labs.
set -euo pipefail
case "${1:-}" in
 74) conf=/tmp/kaltura-php74-ssh.conf; alias=baseline74; expected=kaltura-php74-baseline ;;
 83) conf=/tmp/kaltura-php83-ssh.conf; alias=php83; expected=kaltura-php83-lab ;;
 *) exit 64 ;;
esac
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
zip=/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp3/Rigel-18.20.0-php83-experimental.exp3.zip
echo "1c64edb5ff34308cedfcea3c7879187c21417b6bd1a8e083d70d580bedc985e3  $zip" | sha256sum --check --strict
ssh -T -F "$conf" "$alias" "test \"\$(hostname)\" = $expected && mkdir /home/vagrant/php-exp3-regression"
cat "$zip" | ssh -T -F "$conf" "$alias" 'cat > /home/vagrant/php-exp3-regression/exp3.zip'
tar -C "$root/tools/php83" --exclude='__pycache__' -cf - patch-tests exp3-regression/run-one.sh exp3-regression/batch.py | ssh -T -F "$conf" "$alias" 'tar -xf - -C /home/vagrant/php-exp3-regression; mv /home/vagrant/php-exp3-regression/patch-tests /home/vagrant/php-exp3-regression/tests'
ssh -T -F "$conf" "$alias" 'python3 -' <<'PY'
from pathlib import Path
import hashlib,zipfile
root=Path('/home/vagrant/php-exp3-regression'); archive=root/'exp3.zip'; source=root/'source'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='1c64edb5ff34308cedfcea3c7879187c21417b6bd1a8e083d70d580bedc985e3'
source.mkdir()
with zipfile.ZipFile(archive) as z:
 for i in z.infolist():
  assert (source/i.filename).resolve().is_relative_to(source.resolve())
 z.extractall(source)
print('EXTRACTED_VERIFIED_EXP3')
PY

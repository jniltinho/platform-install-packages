#!/usr/bin/env bash
# Explicit bootstrap of public artifacts in the two authorized disposable labs.
set -euo pipefail
case "${1:-}" in
 74) conf=/tmp/kaltura-php74-ssh.conf; alias=baseline74; expected=kaltura-php74-baseline ;;
 83) conf=/tmp/kaltura-php83-ssh.conf; alias=php83; expected=kaltura-php83-lab ;;
 *) exit 64 ;;
esac
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
zip=/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp4/Rigel-18.20.0-php83-experimental.exp4.zip
echo "a1ce4c46792667b07a733e622a3ee71dd01c87a94f7841edfc72d58746ab9d08  $zip" | sha256sum --check --strict
ssh -T -F "$conf" "$alias" "test \"\$(hostname)\" = $expected && mkdir /home/vagrant/php-exp4-regression"
cat "$zip" | ssh -T -F "$conf" "$alias" 'cat > /home/vagrant/php-exp4-regression/exp4.zip'
tar -C "$root/tools/php83" --exclude='__pycache__' -cf - patch-tests exp4-api exp4-regression | ssh -T -F "$conf" "$alias" 'tar -xf - -C /home/vagrant/php-exp4-regression; mv /home/vagrant/php-exp4-regression/patch-tests /home/vagrant/php-exp4-regression/tests; mv /home/vagrant/php-exp4-regression/exp4-api /home/vagrant/php-exp4-regression/api'
ssh -T -F "$conf" "$alias" 'python3 -' <<'PY'
from pathlib import Path
import hashlib,zipfile
root=Path('/home/vagrant/php-exp4-regression'); archive=root/'exp4.zip'; source=root/'source'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='a1ce4c46792667b07a733e622a3ee71dd01c87a94f7841edfc72d58746ab9d08'
source.mkdir()
with zipfile.ZipFile(archive) as z:
 for i in z.infolist():
  assert (source/i.filename).resolve().is_relative_to(source.resolve())
 z.extractall(source)
print('EXTRACTED_VERIFIED_EXP4')
PY

#!/usr/bin/env bash
# Explicit bootstrap of public artifacts in the two authorized disposable labs.
set -euo pipefail
case "${1:-}" in
 74) conf=/tmp/kaltura-php74-ssh.conf; alias=baseline74; expected=kaltura-php74-baseline ;;
 83) conf=/tmp/kaltura-php83-ssh.conf; alias=php83; expected=kaltura-php83-lab ;;
 *) exit 64 ;;
esac
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
zip=/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp8/Rigel-18.20.0-php83-experimental.exp8.zip
echo "67acaa1ad78332273901fceac9d75824b8f21437eb93607cb20a78db9cd77adc  $zip" | sha256sum --check --strict
ssh -T -F "$conf" "$alias" "test \"\$(hostname)\" = $expected && mkdir /home/vagrant/php-exp8-regression"
cat "$zip" | ssh -T -F "$conf" "$alias" 'cat > /home/vagrant/php-exp8-regression/exp8.zip'
tar -C "$root/tools/php83" --exclude='__pycache__' -cf - patch-tests exp8-api exp8-regression | ssh -T -F "$conf" "$alias" 'tar -xf - -C /home/vagrant/php-exp8-regression; mv /home/vagrant/php-exp8-regression/patch-tests /home/vagrant/php-exp8-regression/tests; mv /home/vagrant/php-exp8-regression/exp8-api /home/vagrant/php-exp8-regression/api'
ssh -T -F "$conf" "$alias" 'python3 -' <<'PY'
from pathlib import Path
import hashlib,zipfile
root=Path('/home/vagrant/php-exp8-regression'); archive=root/'exp8.zip'; source=root/'source'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='67acaa1ad78332273901fceac9d75824b8f21437eb93607cb20a78db9cd77adc'
source.mkdir()
with zipfile.ZipFile(archive) as z:
 for i in z.infolist():
  assert (source/i.filename).resolve().is_relative_to(source.resolve())
 z.extractall(source)
print('EXTRACTED_VERIFIED_EXP8')
PY

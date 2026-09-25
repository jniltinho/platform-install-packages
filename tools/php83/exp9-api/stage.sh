#!/usr/bin/env bash
# Explicit bootstrap of public artifacts in the two authorized disposable labs.
set -euo pipefail
case "${1:-}" in
 74) conf=/tmp/kaltura-php74-ssh.conf; alias=baseline74; expected=kaltura-php74-baseline ;;
 83) conf=/tmp/kaltura-php83-ssh.conf; alias=php83; expected=kaltura-php83-lab ;;
 *) exit 64 ;;
esac
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
zip=/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp9/Rigel-18.20.0-php83-experimental.exp9.zip
echo "cb61e4cd11009bbf9e6e362dfafa5ef2f4af22da817c75fedbd7741a08e44cbc  $zip" | sha256sum --check --strict
ssh -T -F "$conf" "$alias" "test \"\$(hostname)\" = $expected && mkdir /home/vagrant/php-exp9-regression"
cat "$zip" | ssh -T -F "$conf" "$alias" 'cat > /home/vagrant/php-exp9-regression/exp9.zip'
tar -C "$root/tools/php83" --exclude='__pycache__' -cf - patch-tests exp9-api exp9-regression | ssh -T -F "$conf" "$alias" 'tar -xf - -C /home/vagrant/php-exp9-regression; mv /home/vagrant/php-exp9-regression/patch-tests /home/vagrant/php-exp9-regression/tests; mv /home/vagrant/php-exp9-regression/exp9-api /home/vagrant/php-exp9-regression/api'
ssh -T -F "$conf" "$alias" 'python3 -' <<'PY'
from pathlib import Path
import hashlib,zipfile
root=Path('/home/vagrant/php-exp9-regression'); archive=root/'exp9.zip'; source=root/'source'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='cb61e4cd11009bbf9e6e362dfafa5ef2f4af22da817c75fedbd7741a08e44cbc'
source.mkdir()
with zipfile.ZipFile(archive) as z:
 for i in z.infolist():
  assert (source/i.filename).resolve().is_relative_to(source.resolve())
 z.extractall(source)
print('EXTRACTED_VERIFIED_EXP9')
PY

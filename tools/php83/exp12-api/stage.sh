#!/usr/bin/env bash
# Explicit bootstrap of public artifacts in the two authorized disposable labs.
set -euo pipefail
case "${1:-}" in
 74) conf=/tmp/kaltura-php74-ssh.conf; alias=baseline74; expected=kaltura-php74-baseline ;;
 83) conf=/tmp/kaltura-php83-ssh.conf; alias=php83; expected=kaltura-php83-lab ;;
 *) exit 64 ;;
esac
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
zip=/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip
pin=$(python3 "$root/tools/php83/exp12-api/artifact.py")
echo "$pin  $zip" | sha256sum --check --strict
ssh -T -F "$conf" "$alias" "test \"\$(hostname)\" = $expected && mkdir /home/vagrant/php-exp12-regression"
cat "$zip" | ssh -T -F "$conf" "$alias" 'cat > /home/vagrant/php-exp12-regression/exp12.zip'
tar -C "$root/tools/php83" --exclude='__pycache__' -cf - patch-tests exp12-api exp12-regression base-object-ternary autoload83 autoload83-composition | ssh -T -F "$conf" "$alias" 'tar -xf - -C /home/vagrant/php-exp12-regression; mv /home/vagrant/php-exp12-regression/patch-tests /home/vagrant/php-exp12-regression/tests; mv /home/vagrant/php-exp12-regression/exp12-api /home/vagrant/php-exp12-regression/api'
cat "$root/tools/php83/curly-offsets/probe.php" | ssh -T -F "$conf" "$alias" 'cat > /home/vagrant/php-exp12-regression/tests/curly-offsets-probe.php'
ssh -T -F "$conf" "$alias" 'python3 -' <<'PY'
from pathlib import Path
import hashlib,zipfile,re
if not __debug__:raise RuntimeError('Optimized Python not supported')
root=Path('/home/vagrant/php-exp12-regression'); archive=root/'exp12.zip'; source=root/'source'
pin=(root/'api/artifact-sha256.txt').read_text().strip()
assert re.fullmatch('[0-9a-f]{64}',pin)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==pin
source.mkdir()
with zipfile.ZipFile(archive) as z:
 for i in z.infolist():
  assert (source/i.filename).resolve().is_relative_to(source.resolve())
 z.extractall(source)
print('EXTRACTED_VERIFIED_EXP12')
PY

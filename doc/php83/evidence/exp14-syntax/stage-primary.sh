#!/usr/bin/env bash
# Only execute after explicit native83 handoff; all checks precede first SSH.
set -euo pipefail
prior=../platform-install-packages-php83-artifacts/exp13/Rigel-18.20.0-php83-experimental.exp13.zip
candidate=../platform-install-packages-php83-artifacts/exp14/Rigel-18.20.0-php83-experimental.exp14.zip
PYTHONDONTWRITEBYTECODE=1 python3 tools/php83/exp14-syntax/preflight.py "$prior" "$candidate"
base=/home/vagrant/php-candidate-syntax-exp14
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 "test \"\$(hostname)\" = kaltura-php83-lab && test \"\$(id -u)\" = 1000 && mkdir '$base' && mkdir '$base/tools'"
scp -q -F /tmp/kaltura-php83-ssh.conf "$prior" "php83:$base/exp13.zip"
scp -q -F /tmp/kaltura-php83-ssh.conf "$candidate" "php83:$base/exp14.zip"
for name in scan.py frozen-exp13-scan.py frozen-core.py input-contract.json stage.py run.sh; do
 scp -q -F /tmp/kaltura-php83-ssh.conf "tools/php83/exp14-syntax/$name" "php83:$base/tools/$name"
done
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 "python3 -B '$base/tools/stage.py' && sudo -n chown -R root:root '$base' && sudo -n chmod -R a-w '$base'"

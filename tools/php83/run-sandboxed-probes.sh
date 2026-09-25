#!/usr/bin/env bash
# Run inside one of the disposable Noble audit VMs, never on production.
set -euo pipefail
case "$(hostname)" in
  kaltura-php83-lab) runtime=/usr/bin/php8.3; tree=/home/vagrant/php83-audit/packaged/opt/kaltura/app ;;
  kaltura-php74-baseline) runtime=/usr/bin/php7.4; tree=/home/vagrant/php74-audit/packaged/opt/kaltura/app ;;
  *) echo 'Refusing unexpected host' >&2; exit 64 ;;
esac
scripts=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# No write access to payload, home, application configuration, or root secrets.
# Output goes through stdout; the service owns only its private temporary space.
exec sudo systemd-run --quiet --wait --pipe --collect \
  -p User=nobody -p Group=nogroup -p PrivateNetwork=yes \
  -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM -p PrivateDevices=yes -p ProtectSystem=strict \
  -p ProtectHome=yes -p PrivateTmp=yes -p NoNewPrivileges=yes \
  -p 'InaccessiblePaths=-/opt/kaltura /root' \
  -p "BindReadOnlyPaths=$tree:/audit/app $scripts:/audit/tools" \
  -p MemoryMax=512M -p RuntimeMaxSec=600 \
  /usr/bin/python3 /audit/tools/run-runtime-probes.py --require-sandbox /audit/app "$runtime" -

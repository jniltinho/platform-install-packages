#!/usr/bin/env bash
set -euo pipefail
case "$(hostname)" in
 kaltura-php83-lab) runtime=/usr/bin/php8.3; number=83 ;;
 kaltura-php74-baseline) runtime=/usr/bin/php7.4; number=74 ;;
 *) echo 'Refusing unexpected host' >&2; exit 64 ;;
esac
[[ "$number" != 74 || "${1:-}" == original ]] || exit 64
case "${1:-}" in
 original) tree=/home/vagrant/php${number}-audit/packaged/opt/kaltura/app ;;
 exp10) tree=/home/vagrant/php-exp10-regression/source/server-Rigel-18.20.0 ;;
 exp11) tree=/home/vagrant/php-exp11-regression/source/server-Rigel-18.20.0 ;;
 *) exit 64 ;;
esac
case "${2:-}" in doc-comment-export|doc-comment-consumer|doc-comment|legacy-json|zend-json|environment) ;; *) exit 64 ;; esac
ini=()
case "${3:-standard}" in
 standard) ;;
 minimal) ini=(-n); if [[ "$number" == 74 ]]; then ini+=(-d extension=json); fi ;;
 *) exit 64 ;;
esac
# The real consumer bootstrap enforces euid through POSIX and uses text helpers.
# Keep that guard intact even with -n; do not mistake absent guard support for
# an application regression. Other minimal fixtures remain extension-minimal.
if [[ "$2" == doc-comment-consumer && "${3:-standard}" == minimal ]]; then
 ini+=(-d extension=posix -d extension=ctype -d extension=iconv)
fi
scripts=/home/vagrant/php-exp11-regression/tests
if [[ "$2" == debug-pdo* ]]; then
 [[ "${3:-standard}" == standard ]] || exit 64
 abi=20230831; [[ "$number" == 74 ]] && abi=20190902
 ini+=(-d "extension=/audit/tests/sqlite/extracted/usr/lib/php/$abi/pdo_sqlite.so")
fi
cache=()
if [[ "$2" == symfony-bootstrap || "$2" == doc-comment-consumer || "$2" == api-bootstrap || "$2" == api-dispatch ]]; then
 # Private ephemeral cache overlay, never the host payload or application cache.
 cache=(-p 'TemporaryFileSystem=/audit/app/cache:rw,nosuid,nodev,mode=1777')
fi
if [[ "$2" == doc-comment-consumer || "$2" == api-bootstrap || "$2" == api-dispatch ]]; then
 cache+=(-p 'TemporaryFileSystem=/audit/app/configurations:rw,nosuid,nodev,mode=1777')
fi
exec sudo systemd-run --quiet --wait --pipe --collect \
 -p User=nobody -p Group=nogroup -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes \
 -p PrivateTmp=yes -p NoNewPrivileges=yes -p 'InaccessiblePaths=-/opt/kaltura /root' \
 -p "BindReadOnlyPaths=$tree:/audit/app $scripts:/audit/tests" \
 "${cache[@]}" \
 -p MemoryMax=512M -p RuntimeMaxSec=60 \
 "$runtime" "${ini[@]}" -d log_errors=0 -d opcache.enable_cli=0 -d allow_url_fopen=0 \
 -d allow_url_include=0 -d date.timezone=UTC /audit/tests/behavior.php /audit/app "$2"

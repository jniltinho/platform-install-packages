#!/usr/bin/env bash
# Offline tests only: no root requirement, package installation or host changes.
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=../quick-install-ubuntu-26.04.sh
source "$SCRIPT_DIR/../quick-install-ubuntu-26.04.sh"

for ip in 192.168.56.40 10.0.0.1 172.16.1.254; do
    valid_ipv4 "$ip" || { echo "Rejected valid address: $ip"; exit 1; }
done
for ip in '' localhost 127.0.0.1 0.0.0.0 224.1.1.1 255.255.255.255 \
    192.168.1.256 192.168.1 192.168.01.1 '10.0.0.1;id' $'10.0.0.1\n'; do
    if valid_ipv4 "$ip"; then echo "Accepted invalid address: $ip"; exit 1; fi
done
valid_email 'admin@example.com'
for email in '' 'admin' 'x@y' $'admin@example.com\ninjected'; do
    if valid_email "$email"; then echo 'Accepted invalid email'; exit 1; fi
done
# Synthetic test strings, not real credentials.
valid_password 'Test123!'
for password in short lowercase123 ALLCAPS123! 'MissingDigit!' 'NoSymbol123' 'Test 123!' 'FarTooLongPassword123!'; do
    if valid_password "$password"; then echo 'Accepted invalid password'; exit 1; fi
done

# Argument/help paths cannot call the installer.
preflight() { printf 'mock preflight\n'; }
apt-get() { echo 'Unexpected apt invocation' >&2; exit 99; }
main --help >/dev/null
main --host 192.168.56.40 --admin-email admin@example.com --with-console --check >/dev/null
for option in --unknown --host --admin-email; do
    if (main "$option") >/dev/null 2>&1; then echo "Accepted invalid option: $option"; exit 1; fi
done

TMP=$(mktemp -d)
trap 'rm -rf -- "$TMP"' EXIT
printf 'test artifact\n' > "$TMP/package.deb"
(cd "$TMP" && sha256sum package.deb > SHA256SUMS)
verify_asset "$TMP" package.deb >/dev/null
if (verify_asset "$TMP" missing.deb) >/dev/null 2>&1; then echo 'Accepted missing checksum'; exit 1; fi
cp "$TMP/SHA256SUMS" "$TMP/duplicate"
cat "$TMP/duplicate" >> "$TMP/SHA256SUMS"
if (verify_asset "$TMP" package.deb) >/dev/null 2>&1; then echo 'Accepted duplicate checksum'; exit 1; fi
mv "$TMP/duplicate" "$TMP/SHA256SUMS"
printf 'corrupt\n' >> "$TMP/package.deb"
if (verify_asset "$TMP" package.deb) >/dev/null 2>&1; then echo 'Accepted corrupt asset'; exit 1; fi
printf 'All quick installer offline tests passed.\n'

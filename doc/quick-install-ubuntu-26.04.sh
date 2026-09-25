#!/usr/bin/env bash
# Fresh-machine installer. See quick-install-ubuntu-26.04.md before running.
set +x # Never trace passwords, even if invoked with bash -x.
set -Eeuo pipefail

readonly REPOSITORY='https://github.com/jniltinho/platform-install-packages'
readonly SERVER_TAG='kaltura-server/v18.20.0-1'
readonly CONSOLE_TAG='kaltura-console/v0.1.0'
readonly INSTALLER_COMMIT='c9b93424aa57b88164084ba78b336664c299a8d0'
readonly INSTALLER_SHA256='de4847ded7be605e7502368a78302f2f3a296b46a8a26ccb10ecf2f78ce23b05'
readonly WORK_DIR='/opt/kaltura-quick-install'

usage() {
    cat <<'HELP'
Usage: sudo bash quick-install-ubuntu-26.04.sh --host IPV4 --admin-email EMAIL [--with-console] [--check]

Fresh Ubuntu 26.04 amd64 only. Requires a trusted private network and systemd.
  --host IPV4       Stable IPv4 address assigned to this server (required).
  --admin-email    Kaltura administrator email (required).
  --with-console   Also install the Go Console DEB; configure it manually afterward.
  --check          Read-only preflight. No download, install or password prompt.
  -h, --help       Show this help without requiring root.

Installation requires a terminal, explicit confirmation and a hidden password
prompt. Existing Kaltura, MariaDB/MySQL, Apache or console state is refused.
This is NOT an upgrade/resume tool. PHP 7.4 is still required. It does not
configure the firewall, enable Kaltura HTTPS or create a publisher partner.
HELP
}

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

valid_ipv4() {
    local ip=$1 octet
    local -a octets
    [[ $ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || return 1
    IFS=. read -r -a octets <<< "$ip"
    for octet in "${octets[@]}"; do
        [[ ${#octet} -le 3 ]] && ((10#$octet <= 255)) || return 1
        [[ $octet == 0 || $octet != 0* ]] || return 1
    done
    [[ ${octets[0]} != 0 && ${octets[0]} != 127 ]] && ((10#${octets[0]} < 224))
}

valid_email() {
    [[ $1 =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]
}

valid_password() {
    local password=$1
    [[ ${#password} -ge 8 && ${#password} -le 14 &&
       $password =~ [a-z] && $password =~ [0-9] &&
       $password =~ [^a-zA-Z0-9[:space:]] && ! $password =~ [[:space:]] ]]
}

preflight() {
    [[ $EUID -eq 0 ]] || fail 'Run as root (sudo).'
    # shellcheck source=/dev/null
    . /etc/os-release
    [[ ${ID:-} == ubuntu && ${VERSION_ID:-} == 26.04 ]] || fail 'Ubuntu 26.04 is required.'
    [[ $(dpkg --print-architecture) == amd64 ]] || fail 'amd64 is required.'
    [[ -d /run/systemd/system ]] || fail 'A running systemd host is required.'
    command -v ip >/dev/null || fail 'iproute2 is required.'
    ip -4 -o addr show | awk '{split($4, a, "/"); print a[1]}' | grep -Fxq "$HOST_IP" ||
        fail '--host must be an IPv4 address assigned to this machine.'
    local path package status
    for path in /opt/kaltura /var/lib/mysql /etc/mysql /etc/kaltura-console \
        /var/lib/kaltura-console /root/kaltura-mariadb-root-password "$WORK_DIR" \
        /etc/apt/sources.list.d/kaltura-local.list; do
        [[ ! -e $path && ! -L $path ]] || fail "Existing state: $path. Refusing to overwrite; inspect manually."
    done
    while IFS=$'\t' read -r package status; do
        [[ $status == installed ]] || continue
        case "$package" in
            kaltura-*|mariadb-server*|mysql-server*|apache2*)
                fail "Existing package: $package. Use a fresh dedicated machine." ;;
        esac
    done < <(dpkg-query -W -f='${binary:Package}\t${db:Status-Status}\n')
    printf 'Preflight OK: Ubuntu 26.04 amd64, host %s.\n' "$HOST_IP"
}

download() {
    curl --fail --location --retry 3 --connect-timeout 30 --max-time 1800 \
        --proto '=https' --proto-redir '=https' "$1" -o "$2"
}

verify_asset() {
    local directory=$1 asset=$2 line
    line=$(awk -v name="$asset" '$2 == name {print}' "$directory/SHA256SUMS")
    [[ -n $line && $line != *$'\n'* ]] || fail "Missing or duplicate checksum: $asset"
    (cd "$directory" && printf '%s\n' "$line" | sha256sum --check --strict -)
}

main() {
    local with_console=false check_only=false confirmation password_again
    HOST_IP='' ADMIN_EMAIL=''
    while (($#)); do
        case "$1" in
            --host|--admin-email)
                [[ $# -ge 2 && $2 != --* ]] || fail "Missing value for $1"
                if [[ $1 == --host ]]; then HOST_IP=$2; else ADMIN_EMAIL=$2; fi
                shift 2 ;;
            --with-console) with_console=true; shift ;;
            --check) check_only=true; shift ;;
            -h|--help) usage; return ;;
            *) fail "Unknown option: $1 (see --help)" ;;
        esac
    done
    valid_ipv4 "$HOST_IP" || fail 'Supply a valid unicast IPv4 address with --host.'
    valid_email "$ADMIN_EMAIL" || fail 'Supply a valid --admin-email.'
    preflight
    $check_only && return 0
    [[ -t 0 && -t 1 ]] || fail 'An interactive terminal is required; do not pipe this script to Bash.'
    printf '\nThis installs legacy PHP 7.4, changes MariaDB/Apache and uses third-party repositories.\n'
    printf 'Use a fresh machine on a trusted private network. No firewall/TLS hardening is performed.\n'
    read -r -p 'Type INSTALL to continue: ' confirmation
    [[ $confirmation == INSTALL ]] || fail 'Cancelled; no changes made.'
    printf 'Password: 8–14 chars, lowercase, digit, symbol; no name/email fragments or whitespace.\n'
    read -r -s -p 'Kaltura administrator password: ' ADMIN_PASSWD; printf '\n'
    valid_password "$ADMIN_PASSWD" || fail 'Password does not meet the local format checks.'
    read -r -s -p 'Confirm password: ' password_again; printf '\n'
    [[ $ADMIN_PASSWD == "$password_again" ]] || fail 'Passwords do not match.'
    unset password_again
    trap 'unset ADMIN_PASSWD MYSQL_ROOT_PASSWD' EXIT
    trap 'printf "Installation stopped at line %s. Preserve state and inspect the error; do not purge or rerun blindly.\n" "$LINENO" >&2' ERR

    umask 077
    mkdir -m 0700 "$WORK_DIR"
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y ca-certificates curl openssl
    mkdir "$WORK_DIR/server"
    local asset='kaltura-server-ubuntu-26.04-repo.tar.gz'
    local base="$REPOSITORY/releases/download/$SERVER_TAG"
    download "$base/$asset" "$WORK_DIR/server/$asset"
    download "$base/SHA256SUMS" "$WORK_DIR/server/SHA256SUMS"
    verify_asset "$WORK_DIR/server" "$asset"
    download "https://raw.githubusercontent.com/jniltinho/platform-install-packages/$INSTALLER_COMMIT/deb/ubuntu-26.04/install-aio.sh" "$WORK_DIR/install-aio.sh"
    printf '%s  %s\n' "$INSTALLER_SHA256" "$WORK_DIR/install-aio.sh" | sha256sum --check --strict -
    bash -n "$WORK_DIR/install-aio.sh"
    mkdir "$WORK_DIR/repo"
    tar --extract --gzip --file "$WORK_DIR/server/$asset" --directory "$WORK_DIR/repo" \
        --no-same-owner --no-same-permissions
    [[ -f $WORK_DIR/repo/Packages.gz ]] || fail 'The archive is missing its apt index.'
    # _apt must be able to traverse/read the local repository, but not secret files.
    chmod 0755 "$WORK_DIR" "$WORK_DIR/repo"
    find "$WORK_DIR/repo" -type d -exec chmod 0755 {} +
    find "$WORK_DIR/repo" -type f -exec chmod 0644 {} +

    MYSQL_ROOT_PASSWD=$(openssl rand -hex 24)
    (set -o noclobber; printf '%s\n' "$MYSQL_ROOT_PASSWD" > /root/kaltura-mariadb-root-password)
    export HOST_IP ADMIN_EMAIL ADMIN_PASSWD MYSQL_ROOT_PASSWD
    export KALTURA_APT="file:$WORK_DIR/repo"
    # The pinned AIO script supplies distro-specific dependency repositories.
    # Any apt failure aborts; there is no suite/PHP-version substitution.
    bash "$WORK_DIR/install-aio.sh"
    unset ADMIN_PASSWD MYSQL_ROOT_PASSWD
    systemctl is-active mariadb apache2 memcached elasticsearch kaltura-nginx \
        kaltura-sphinx kaltura-batch kaltura-populate kaltura-elastic-populate
    curl -fsS --max-time 30 "http://$HOST_IP/api_v3/index.php?service=system&action=ping" |
        grep -Eq '<result>(1|true)</result>'

    if $with_console; then
        mkdir "$WORK_DIR/console"
        asset='kaltura-console_0.1.0_amd64.deb'
        base="$REPOSITORY/releases/download/$CONSOLE_TAG"
        download "$base/$asset" "$WORK_DIR/console/$asset"
        download "$base/SHA256SUMS" "$WORK_DIR/console/SHA256SUMS"
        verify_asset "$WORK_DIR/console" "$asset"
        apt-get install -y "$WORK_DIR/console/$asset"
        printf '\nConsole installed but NOT configured or started.\n'
        printf 'Follow step 5 in doc/quick-install-ubuntu-26.04.md: publisher, TLS and local account.\n'
    fi
    printf '\nServer ready: http://%s/admin_console/ (email: %s)\n' "$HOST_IP" "$ADMIN_EMAIL"
    printf 'Database password saved root-only in /root/kaltura-mariadb-root-password.\n'
    printf 'Back up credentials securely. This installer does not create test media.\n'
}

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
    main "$@"
fi

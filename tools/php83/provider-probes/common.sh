#!/usr/bin/env bash
# Source only inside the disposable container, never on a host.
set -euo pipefail
[[ ${PHP83_DISPOSABLE_CONTAINER:-} == yes && -f /.dockerenv ]] || { echo 'Disposable Docker container required' >&2; exit 2; }
[[ $(id -u) == 0 ]] || exit 2
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
webroot=/var/www/php83-provider-probe
mkdir -p "$webroot"
cp "$here/probe.php" "$webroot/probe.php"
# Fresh, public anti-stale marker fixed before server start, not a secret.
nonce="php83-$(cat /proc/sys/kernel/random/uuid)"
printf '%s\n' "$nonce" > "$webroot/nonce"
http_pid= fpm_pid=
cleanup() {
    [[ -z $http_pid ]] || kill "$http_pid" 2>/dev/null || true
    [[ -z $fpm_pid ]] || kill "$fpm_pid" 2>/dev/null || true
    wait 2>/dev/null || true
    # Retain server diagnostics outside JSON response framing.
    for log in /tmp/provider-httpd.log /tmp/provider-fpm.log; do
        if [[ -f $log ]]; then printf "SERVER_LOG %s\n" "$log"; cat "$log"; fi
    done
}
trap cleanup EXIT
validate_json() {
    php -r '$r=json_decode(file_get_contents($argv[1]),true,512,JSON_THROW_ON_ERROR); if (($r["ok"]??false)!==true || $r["nonce"]!==$argv[2] || $r["sapi"]!==$argv[3] || $r["method"]!==$argv[4] || !str_starts_with($r["php"],"8.3.")) {fwrite(STDERR,"Invalid probe JSON\n");exit(1);}' "$1" "$nonce" "$2" "$3"
}
run_requests() {
    local sapi=$1 method
    printf '%s\n' "$sapi" > "$webroot/expected-sapi"
    echo 'PHP83_PROVIDER_CLI_BEGIN'
    php "$webroot/probe.php" > /tmp/provider-cli.json
    validate_json /tmp/provider-cli.json cli CLI
    cat /tmp/provider-cli.json
    echo 'PHP83_PROVIDER_CLI_END'
    for attempt in $(seq 1 40); do
        kill -0 "$http_pid"
        [[ -z $fpm_pid ]] || kill -0 "$fpm_pid"
        if curl --noproxy '*' --silent --fail --max-time 2 "http://127.0.0.1:18083/probe.php?nonce=$nonce" -o /tmp/provider-ready.json; then break; fi
        sleep 0.25
    done
    for method in GET POST; do
        args=(); [[ $method != POST ]] || args=(--data 'marker=php83-provider-synthetic')
        curl --noproxy '*' --silent --show-error --fail --max-time 10 "${args[@]}" "http://127.0.0.1:18083/probe.php?nonce=$nonce" -o /tmp/provider-web.json
        validate_json /tmp/provider-web.json "$sapi" "$method"
        echo "PHP83_PROVIDER_${method}_BEGIN"
        cat /tmp/provider-web.json
        echo "PHP83_PROVIDER_${method}_END"
    done
    # Endpoint must reject an invalid marker, not just accept happy paths.
    code=$(curl --noproxy '*' --silent --show-error --max-time 10 --data 'marker=invalid' "http://127.0.0.1:18083/probe.php?nonce=$nonce" -o /tmp/provider-negative.json -w '%{http_code}')
    [[ $code == 500 ]] || { echo 'Invalid POST accepted' >&2; return 1; }
    php -r '$r=json_decode(file_get_contents($argv[1]),true,512,JSON_THROW_ON_ERROR); if ($r["ok"]!==false || !in_array("post",$r["failures"],true)) exit(1);' /tmp/provider-negative.json
    echo 'PHP83_PROVIDER_NEGATIVE_POST_OK'
}

# Sourced only by reviewed private laboratory maintainer hooks, not user profiles.
# Shell function arguments are not exec argv. Do not export these functions.
# All temporary material stays root-only; no global log-level changes.
[[ $- != *x* ]] || return 92
pilot83_private_mysql() (
    umask 077
    local dir status arg password='' have_password=0
    local -a args=()
    for arg in "$@"; do
        case "$arg" in
            --defaults*|--login-path*) return 92 ;;
            -p) return 92 ;;
            -p*) (( have_password == 0 )) || return 92; password=${arg#-p}; have_password=1 ;;
            --password=*) (( have_password == 0 )) || return 92; password=${arg#--password=}; have_password=1 ;;
            --password) return 92 ;;
            *) args+=("$arg") ;;
        esac
    done
    # Fresh pilot passwords use this alphabet. Reject unsupported option-file syntax.
    if [[ "$password" == *[!A-Za-z0-9_=@%+./:-]* ]]; then return 92; fi
    dir=$(mktemp -d /run/kaltura-pilot83-mysql.XXXXXXXX) || return 93
    trap 'exit 129' HUP
    trap 'exit 130' INT
    trap 'exit 143' TERM
    trap 'rm -f -- "$dir/client.cnf"; rmdir -- "$dir"' EXIT
    printf '[client]\n' > "$dir/client.cnf"
    if (( have_password )); then printf 'password="%s"\n' "$password" >> "$dir/client.cnf"; fi
    if /usr/bin/mysql --defaults-extra-file="$dir/client.cnf" "${args[@]}"; then status=0; else status=$?; fi
    exit "$status"
)
pilot83_private_sed() (
    umask 077
    local dir status script_seen=0
    local -a args=()
    dir=$(mktemp -d /run/kaltura-pilot83-sed.XXXXXXXX) || return 93
    trap 'exit 129' HUP
    trap 'exit 130' INT
    trap 'exit 143' TERM
    trap 'rm -f -- "$dir/program.sed"; rmdir -- "$dir"' EXIT
    : > "$dir/program.sed"
    while (( $# )); do
        case "$1" in
            -e) (( $# >= 2 )) || return 92; printf '%s\n' "$2" >> "$dir/program.sed"; script_seen=1; shift 2 ;;
            -i|-n|-E|-r) args+=("$1"); shift ;;
            -*) return 92 ;;
            *) if (( script_seen )); then args+=("$1"); else printf '%s\n' "$1" >> "$dir/program.sed"; script_seen=1; fi; shift ;;
        esac
    done
    (( script_seen )) || return 92
    if /usr/bin/sed -f "$dir/program.sed" "${args[@]}"; then status=0; else status=$?; fi
    exit "$status"
)
pilot83_private_php() (
    umask 077
    local dir status
    (( $# )) || return 92
    dir=$(mktemp -d /run/kaltura-pilot83-php.XXXXXXXX) || return 93
    trap 'exit 129' HUP
    trap 'exit 130' INT
    trap 'exit 143' TERM
    trap 'rm -f -- "$dir/arguments"; rmdir -- "$dir"' EXIT
    printf '%s\0' "$@" > "$dir/arguments"
    if /usr/bin/php8.3 /opt/kaltura/bin/pilot83-private-argv.php "$dir/arguments"; then status=0; else status=$?; fi
    exit "$status"
)

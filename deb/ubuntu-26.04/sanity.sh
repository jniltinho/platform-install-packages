#!/bin/bash
# Kaltura AIO sanity: services, API, UIs, upload -> transcoding -> HLS through nginx VOD.
# Exits non-zero if any check fails.
set -uo pipefail

HOST_IP=${HOST_IP:-192.168.56.40}
URL=http://$HOST_IP
MYSQL_ROOT_PASSWD=${MYSQL_ROOT_PASSWD:-kaltura-root}
BIN=/opt/kaltura/bin
STATE=/root/kaltura-sanity.rc
FAILS=0

ok()   { echo "[ OK ] $*"; }
fail() { echo "[FAIL] $*"; FAILS=$((FAILS+1)); }
check() { local d=$1; shift; if "$@" >/dev/null 2>&1; then ok "$d"; else fail "$d"; fi; }
http_code() { curl -s -o /dev/null -L -w '%{http_code}' "$1"; }
sql() { mysql -N -uroot -p"$MYSQL_ROOT_PASSWD" kaltura -e "$1"; }

for s in mariadb apache2 memcached elasticsearch kaltura-nginx kaltura-sphinx kaltura-batch kaltura-populate kaltura-elastic-populate; do
	check "service $s active" systemctl is-active $s
done
check "searchd running" pgrep -x searchd

check "API system.ping" bash -c "curl -sf '$URL/api_v3/index.php?service=system&action=ping' | grep -Eq '<result>(1|true)</result>'"
[ "$(http_code $URL/admin_console/)" = 200 ] && ok "admin_console HTTP 200" || fail "admin_console HTTP 200"
[ "$(http_code $URL/index.php/kmcng/)" = 200 ] && ok "kmcng HTTP 200" || fail "kmcng HTTP 200"

ADMIN_SECRET=$(sql "select admin_secret from partner where id=-2")
check "session.start partner -2" bash -c "curl -sf '$URL/api_v3/index.php?service=session&action=start&partnerId=-2&type=2&secret=$ADMIN_SECRET' | grep -q '<result>[^<]\{20,\}</result>'"

# test partner, created once
if [ ! -r $STATE ]; then
	PID=$(cd $BIN && php create_partner.php "$ADMIN_SECRET" sanity@kaltura.local 'Vid30#Test' "$URL" 2>/dev/null | tail -1)
	[[ "$PID" =~ ^[0-9]+$ ]] && echo "PARTNER_ID=$PID" > $STATE
fi
if [ ! -r $STATE ]; then
	fail "test partner creation"; echo "Failures: $FAILS"; exit 1
fi
. $STATE
SECRET=$(sql "select secret from partner where id=$PARTNER_ID")
ok "test partner $PARTNER_ID"

MP4=/tmp/sanity.mp4
[ -s $MP4 ] || ffmpeg -nostdin -loglevel error -y -f lavfi -i testsrc=duration=10:size=640x360:rate=25 \
	-f lavfi -i sine=duration=10 -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest $MP4
ENTRY=$(cd $BIN && php upload_test.php "$URL" "$PARTNER_ID" "$SECRET" $MP4 2>/dev/null | tail -1)
if [[ ! "$ENTRY" =~ ^[0-9]_[a-z0-9]{8}$ ]]; then
	fail "MP4 upload ($ENTRY)"; echo "Failures: $FAILS"; exit 1
fi
ok "upload -> entry $ENTRY"

STATUS=-1
for _ in $(seq 60); do
	(cd $BIN && php check_entry_status.php "$URL" "$PARTNER_ID" "$SECRET" "$ENTRY" >/dev/null 2>&1); STATUS=$?
	[ $STATUS = 2 ] && break
	[ $STATUS = 255 ] || [ $STATUS = -1 ] && break  # 255 = ERROR_CONVERTING
	sleep 10
done
[ "$STATUS" = 2 ] && ok "entry READY (transcoding ok)" || fail "entry READY (status $STATUS)"

M3U8=$(curl -sfL "$URL/p/$PARTNER_ID/sp/${PARTNER_ID}00/playManifest/entryId/$ENTRY/format/applehttp/protocol/${URL%%:*}/a.m3u8")
VARIANT=$(echo "$M3U8" | grep -m1 -v '^#')
if echo "$M3U8" | grep -q '^#EXTM3U' && [ -n "$VARIANT" ]; then
	ok "HLS manifest"
	SEG=$(curl -sfL "$VARIANT" | grep -m1 -v '^#')
	[[ "$SEG" != http* ]] && SEG="${VARIANT%/*}/$SEG"
	SIZE=$(curl -sfL "$SEG" | wc -c)
	[ "$SIZE" -gt 1000 ] && ok "HLS segment ($SIZE bytes)" || fail "HLS segment ($SEG)"
else
	fail "HLS manifest"
fi

echo "Failures: $FAILS"
[ $FAILS = 0 ]

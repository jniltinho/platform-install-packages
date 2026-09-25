#!/bin/sh
set -eu
getent group kaltura-console >/dev/null || groupadd --system kaltura-console
getent passwd kaltura-console >/dev/null || useradd --system --gid kaltura-console --home-dir /var/lib/kaltura-console --no-create-home --shell /usr/sbin/nologin kaltura-console

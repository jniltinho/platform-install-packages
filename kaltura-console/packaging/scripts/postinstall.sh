#!/bin/sh
set -eu
install -d -o kaltura-console -g kaltura-console -m 0750 /var/lib/kaltura-console /var/lib/kaltura-console/tmp
chown root:kaltura-console /etc/kaltura-console/config.toml
chmod 0640 /etc/kaltura-console/config.toml
runuser -u kaltura-console -- /usr/bin/kaltura-console --config /etc/kaltura-console/config.toml migrate
if [ -d /run/systemd/system ]; then
    systemctl daemon-reload
    systemctl enable kaltura-console.service
    # Fresh installation requires a partner and secret. Restart only an existing service.
    if systemctl is-active --quiet kaltura-console.service; then
        systemctl restart kaltura-console.service
    fi
fi
printf '%s\n' 'Configure /etc/kaltura-console/config.toml, then run:' \
    '  sudo -u kaltura-console kaltura-console --config /etc/kaltura-console/config.toml user add --email EMAIL --role admin' \
    '  sudo systemctl start kaltura-console'

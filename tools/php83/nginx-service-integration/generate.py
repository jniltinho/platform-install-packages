"""Generate reviewed fixed lab unit/init text locally; never installs or starts."""
UNIT='''[Unit]
Description=Bounded Kaltura nginx privacy lab
After=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/bin/python3 -I -B /usr/local/lib/kaltura-nginx-lab/service.py
KillMode=control-group
KillSignal=SIGTERM
SendSIGKILL=yes
TimeoutStopSec=6
RuntimeMaxSec=126
Restart=no
UMask=0077
RuntimeDirectory=kaltura-php83-nginx-log
RuntimeDirectoryMode=0750
RuntimeDirectoryPreserve=no
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
'''
# No raw nginx -t, PID-file execution or inherited native stderr branch.
INIT='''#!/bin/sh
### BEGIN INIT INFO
# Provides: kaltura-nginx
# Required-Start: $local_fs $network
# Required-Stop: $local_fs $network
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: supervised bounded nginx lab
### END INIT INFO
case "$1" in
 start|stop|restart|status) exec /usr/bin/systemctl --no-ask-password "$1" kaltura-nginx.service ;;
 reload|force-reload|configtest|testconfig) echo 'LAB_ACTION_REQUIRES_REVIEW' >&2; exit 2 ;;
 *) echo 'LAB_ACTION_REJECTED' >&2; exit 2 ;;
esac
'''

def artifacts():return {'kaltura-nginx.service':UNIT,'kaltura-nginx.init':INIT}


def manifest(config_pins,socket_gid):
    import service
    files={str(service.BINARY):service.BINARY_PIN,
           str(service.BASE/'lab_adapter.py'):service.ADAPTER_PIN,
           str(service.BASE/'sanitizer.py'):service.SANITIZER_PIN}
    if type(config_pins) is not dict or any(path in files for path in config_pins):raise ValueError('CONFIG_PINS')
    files.update(config_pins)
    result={'schema':1,'seconds':120,'socket_gid':socket_gid,'files':files}
    service.validate_contract(result)
    if str(service.CONFIG.parent/'kaltura.conf') not in files:raise ValueError('SERVER_CONFIG')
    return result

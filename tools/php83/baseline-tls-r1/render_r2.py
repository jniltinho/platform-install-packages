"""Fixed isolated-lab TLS configuration bytes; not an installer."""
IP='192.168.56.74'
PRIVATE='/var/lib/kaltura-baseline-tls-r2'
LOGDIR='/var/lib/kaltura-baseline-tls-logs-r2'
def config():
 return f'''# Owned isolated baseline listener; included after ports.conf.
<IfModule !ssl_module>
 LoadModule ssl_module /usr/lib/apache2/modules/mod_ssl.so
</IfModule>
Listen {IP}:8443 https
<VirtualHost {IP}:8443>
 SSLEngine on
 SSLProtocol -all +TLSv1.2 +TLSv1.3
 SSLCipherSuite HIGH:!aNULL:!MD5:!3DES
 SSLCertificateFile {PRIVATE}/server.crt
 SSLCertificateKeyFile {PRIVATE}/server.key
 ErrorLog {LOGDIR}/error.log
 CustomLog {LOGDIR}/access.log "%>s %B %D"
 Include "/opt/kaltura/app/configurations/apache/conf.d/enabled.*.conf"
</VirtualHost>
'''
def ca_extensions():
 return 'basicConstraints=critical,CA:TRUE,pathlen:0\nkeyUsage=critical,keyCertSign,cRLSign\nsubjectKeyIdentifier=hash\n'
def leaf_extensions():
 return f'basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\nsubjectAltName=IP:{IP}\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n'

PORTS_SHA='ca3f42f4f226ca53efba66a162f224375b78ff4be50ed146d303753b53fee76f'
def ports_after(raw):
 import hashlib,re
 if hashlib.sha256(raw).hexdigest()!=PORTS_SHA:raise ValueError('PORTS_PIN')
 out,n=re.subn(rb'(?m)^([ \t]*)Listen 443[ \t]*$',rb'\1# baseline-tls-r2: dedicated .74:8443 listener only',raw)
 if n!=2 or b'Listen 80' not in out:raise ValueError('PORTS_SHAPE')
 return out

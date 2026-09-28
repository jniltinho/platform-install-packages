import json,os,subprocess,socket
from pathlib import Path
assert socket.gethostname()=="kaltura-php83-lab"
a=json.loads(subprocess.check_output(["ip","-j","-4","addr"]));ips=sorted({v["local"] for x in a for v in x.get("addr_info",[])})
assert "192.168.56.83" in ips and not set(ips)&{"192.168.56.20","192.168.56.74"}
r={"hostname":socket.gethostname(),"ips":ips,"os":Path("/etc/os-release").read_text(),"paths":{p:Path(p).exists() for p in ["/opt/kaltura/app","/opt/kaltura/bin","/opt/kaltura/web","/var/lib/mysql","/etc/apache2/mods-enabled/php8.3.load","/etc/php/8.3/mods-available/soap.ini"]}}
cmds={"packages":["dpkg-query","-W","-f=${Package} ${Version} ${db:Status-Status}\n","php8.3*","libapache2-mod-php8.3","mariadb*","kaltura*","elasticsearch*","memcached*","sphinx*","ffmpeg*","monit*"],"php":["php8.3","-r","echo json_encode([PHP_VERSION,PHP_SAPI,php_ini_loaded_file(),get_loaded_extensions()]);"],"services":["systemctl","show","apache2","mariadb","memcached","elasticsearch","monit","-p","Id","-p","ActiveState","-p","SubState"]}
for name,cmd in cmds.items():
 p=subprocess.run(cmd,capture_output=True,timeout=25);r[name]={"exit":p.returncode,"stdout":p.stdout.decode(),"stderr_bytes":len(p.stderr)}
print(json.dumps(r))

"""Exact published-hook-only private derivation. Never executes hooks or builds DEBs."""
import argparse,difflib,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
INVENTORY=ROOT/'doc/php83/evidence/pilot83/published-hook-inputs.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def transform(package,hook,before):
 inventory=json.loads(INVENTORY.read_text())
 matches=[r for r in inventory['hooks'] if r['package']==package and r['hook']==hook]
 if len(matches)!=1 or sha(before)!=matches[0]['sha256']:raise ValueError('Unreviewed published hook identity')
 text=before.decode();changes=[];lines=[]
 for number,line in enumerate(text.splitlines(keepends=True),1):
  old=line
  if package=='kaltura-db' and hook=='postinst' and line.strip()=='rm -f $APP_DIR/log/kaltura-*.log':
   line=line.replace('rm -f $APP_DIR/log/kaltura-*.log',': # private pilot: retain installation logs; no deletion')
  elif line.startswith('# mysql -h$MYSQL_HOST -u$MYSQL_SUPER_USER -p$MYSQL_SUPER_USER_PASSWD'):
   line='# MySQL connectivity failed; credential-bearing command intentionally not rendered.\n'
  elif not line.lstrip().startswith('#'):
   # Inputs are pinned entire published hook bytes; these are NOT general shell parsing rules.
   line=re.sub(r'(?<![\w/-])mysql(?=\s)', 'pilot83_private_mysql',line)
   if re.search(r'\b(?:[A-Z0-9_]*SECRETS?|[A-Z_]*PASS(?:WORD|WD)?|NEW_SECRETS|ENCRYPTION_IV|APP_REMOTE_ADDR_HEADER_SALT)\b',line) and re.search(r'(?<![\w/-])sed\s',line):
    line=re.sub(r'(?<![\w/-])sed(?=\s)','pilot83_private_sed',line)
   if 'php $HTML5LIB3_BASEDIR/create_playkit_uiconf.php 0 $PARTNER_ZERO_SECRET' in line:
    line=line.replace('php $HTML5LIB3_BASEDIR/create_playkit_uiconf.php 0 $PARTNER_ZERO_SECRET','pilot83_private_php "$HTML5LIB3_BASEDIR/create_playkit_uiconf.php" 0 "$PARTNER_ZERO_SECRET"')
   # Pin executable token, not .php paths or textual/log labels.
   line=re.sub(r'(^\s*|[;|]\s*|while ! )php(?=\s)',r'\1/usr/bin/php8.3',line)
   line=re.sub(r'(^\s*)phpenmod(?=\s)',r'\1phpenmod -v 8.3',line)
   line=line.replace('s#@PHP_BIN@#/usr/bin/php#g','s#@PHP_BIN@#/usr/bin/php8.3#g')
   line=line.replace('/etc/php5/cli/php.ini /etc/php5/apache2/php.ini','/etc/php/8.3/cli/php.ini /etc/php/8.3/apache2/php.ini')
   line=line.replace('/etc/php5/mods-available /etc/php/7.0/mods-available /etc/php/7.4/mods-available','/etc/php/8.3/mods-available')
  if line!=old:changes.append({'original_line':number,'before_sha256':sha(old.encode()),'after_sha256':sha(line.encode())})
  lines.append(line)
 after=''.join(lines)
 if after!=text:
  first,rest=after.split('\n',1)
  if first.strip() not in ('#!/bin/bash','#!/bin/bash -'):raise ValueError('Expected bash hook')
  after=first+'\n# Private lab only. Reject tracing before loading any credential values.\n[[ $- != *x* ]] || exit 92\n. /opt/kaltura/bin/pilot83-private-hook-functions.sh || exit 92\n'+rest
 raw=after.encode()
 return raw,{'package':package,'hook':hook,'before_sha256':sha(before),'after_sha256':sha(raw),'changed_lines':changes,'status':'PRIVATE_DERIVATION_NOT_EXECUTED','limits':['Only direct commands in exact pinned maintainer hooks; reached payload helper scripts need separate review.','Pre-existing optional-command redirects/guards remain; no new failure masking introduced.','Intrinsic child diagnostics and intended credential storage require installation privacy gate.']}
PAYLOAD_PIN='7dfb684d83787f1c84ccba08b51ee7f4b578feba3ce111717e3fc09cc68f0ab4'
PAYLOAD_PATH='opt/kaltura/bin/kaltura-functions.rc'
def transform_payload(path,before):
 if path!=PAYLOAD_PATH or sha(before)!=PAYLOAD_PIN:raise ValueError('Payload source identity')
 text=before.decode();lines=[];changed=[]
 for n,line in enumerate(text.splitlines(True),1):
  old=line
  if 'MSG="${BRIGHT_RED}ERROR: Couldn\'t connect with mysql -u$DB_USER -p$DB_PASSWD' in line:
   line='\t\tMSG="${BRIGHT_RED}ERROR: MySQL connectivity failed (credential command omitted).${NORMAL}"\n'
  elif not line.lstrip().startswith('#') and '| mysql ' in line:
   line=line.replace('| mysql ','| pilot83_private_mysql ')
  if old!=line:changed.append({'original_line':n,'before_sha256':sha(old.encode()),'after_sha256':sha(line.encode())})
  lines.append(line)
 if len(changed)!=7:raise ValueError('Payload exact anchors')
 after=('# Private pilot transport before loading credential configuration.\n[[ $- != *x* ]] || return 92\n. /opt/kaltura/bin/pilot83-private-hook-functions.sh || return 92\n'+''.join(lines)).encode()
 return after,{'path':path,'before_sha256':sha(before),'after_sha256':sha(after),'changed_lines':changed,'status':'PRIVATE_PAYLOAD_HELPER_NOT_EXECUTED'}
def main():
 p=argparse.ArgumentParser();p.add_argument('package');p.add_argument('hook');p.add_argument('before',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 raw,m=transform(a.package,a.hook,a.before.read_bytes());a.output.mkdir(parents=True,exist_ok=False)
 (a.output/a.hook).write_bytes(raw);(a.output/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 diff=''.join(difflib.unified_diff(a.before.read_text().splitlines(True),raw.decode().splitlines(True),fromfile=a.package+'/'+a.hook,tofile=a.package+'/'+a.hook))
 (a.output/'change.patch').write_text(diff)
if __name__=='__main__':main()

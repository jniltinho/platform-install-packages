"""Pure Debian-control transformation for private Noble PHP83 lab derivatives."""
import re
PHP_REVISION='8.3.6-0ubuntu0.24.04.11'
SUFFIX='+php83lab1'
RUNTIME_PACKAGES={'kaltura-base','kaltura-front','kaltura-batch','kaltura-html5lib','kaltura-html5lib3'}
def transform(raw,package):
 text=raw.decode('utf-8')
 for key in ('Package','Version'):
  if len(re.findall(r'^'+key+r': ',text,re.M))!=1:raise ValueError('CONTROL_FIELD')
 actual=re.search(r'^Package: (.+)$',text,re.M).group(1)
 if actual!=package or not re.fullmatch(r'kaltura-[a-z0-9-]+',package):raise ValueError('PACKAGE_ID')
 version=re.search(r'^Version: (.+)$',text,re.M).group(1)
 if '+' in version or not re.fullmatch(r'[0-9][a-zA-Z0-9.~-]*-[0-9]+',version):raise ValueError('VERSION')
 text=text.replace('Version: '+version+'\n','Version: '+version+SUFFIX+'\n',1)
 # Only dependency fields are changed; descriptions and unrelated values remain exact.
 lines=text.splitlines(keepends=True); field=None; php_changes=0
 for i,line in enumerate(lines):
  if not line.startswith((' ','\t')):field=line.partition(':')[0]
  if field in ('Depends','Pre-Depends','Recommends'):
   new,count=re.subn(r'(?<![a-z0-9])php7\.4(?=$|[- ,(\n])','php8.3',line)
   php_changes+=count;lines[i]=new
 text=''.join(lines)
 if bool(php_changes)!=(package in RUNTIME_PACKAGES):raise ValueError('RUNTIME_EDGE_DRIFT')
 if 'php7.4' in text:raise ValueError('PHP74_REMAINS')
 if package=='kaltura-base':
  needle='Depends: '
  if text.count(needle)!=1:raise ValueError('BASE_DEPENDS')
  text=text.replace(needle,needle+f'php8.3-common (= {PHP_REVISION}), php8.3-soap (= {PHP_REVISION}), ',1)
 return text.encode(),{'package':package,'before_version':version,'after_version':version+SUFFIX,'php_dependency_substitutions':php_changes,'soap_exact_revision':PHP_REVISION if package=='kaltura-base' else None}

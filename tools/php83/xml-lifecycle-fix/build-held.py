"""Pinned local patch construction only; not artifact selection or VM execution."""
import difflib,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PINS=json.loads((HERE.parent/'xml-lifecycle/source-pins.json').read_text())
SOURCE=Path('/tmp/php-xml-lifecycle-prep-r2/exp11')
OUT=REPO/'patches/php83/held/xml-lifecycle'
def sha(b):return hashlib.sha256(b).hexdigest()
def build():
 OUT.mkdir(parents=True,exist_ok=True);changes=[]
 for path in ['alpha/config/kConf.php','infra/general/kSoapClient.php','infra/general/kXmlEntityLoaderPolicy.php']:
  if path.endswith('kXmlEntityLoaderPolicy.php'):
   before=b'';after=(HERE/'candidate/kXmlEntityLoaderPolicy.php').read_bytes()
  else:
   before=(SOURCE/path).read_bytes()
   if sha(before)!=PINS['exp11']['files'][path]:raise ValueError('Before source pin mismatch')
   if path.endswith('kConf.php'):
    after=before.replace(b'libxml_disable_entity_loader(true);',b"require_once __DIR__ . '/../../infra/general/kXmlEntityLoaderPolicy.php';\nkXmlEntityLoaderPolicy::installDefaultDeny();",1)
   else:
    text=before.decode().replace('\r\n','\n')
    text=text.replace('<?php\n',"<?php\nrequire_once __DIR__ . '/kXmlEntityLoaderPolicy.php';\n",1)
    start=text.index('\tpublic function __construct');end=text.index('\tprivate function beforeCall')
    text=text[:start]+'''\tpublic function __construct($wsdl, $options = array())
\t{
\t\t$scope = kXmlEntityLoaderPolicy::beginSoapScope();
\t\t$error = null;
\t\ttry {
\t\t\tparent::__construct($wsdl, $options);
\t\t} catch (Throwable $failure) {
\t\t\t$error = $failure;
\t\t\tthrow $failure;
\t\t} finally {
\t\t\tkXmlEntityLoaderPolicy::endSoapScope($scope, $error);
\t\t}
\t}

\tpublic function __call($function_name, $arguments): mixed
\t{
\t\t$scope = kXmlEntityLoaderPolicy::beginSoapScope();
\t\t$error = null;
\t\ttry {
\t\t\treturn parent::__call($function_name, $arguments);
\t\t} catch (Throwable $failure) {
\t\t\t$error = $failure;
\t\t\tthrow $failure;
\t\t} finally {
\t\t\tkXmlEntityLoaderPolicy::endSoapScope($scope, $error);
\t\t}
\t}

\tpublic function __soapCall($function_name, $arguments, $options = NULL, $input_headers = NULL, &$output_headers = NULL): mixed
\t{
\t\t$scope = kXmlEntityLoaderPolicy::beginSoapScope();
\t\t$error = null;
\t\ttry {
\t\t\t// Preserve existing argument forwarding; headers/options are a separate repair.
\t\t\treturn parent::__soapCall($function_name, $arguments);
\t\t} catch (Throwable $failure) {
\t\t\t$error = $failure;
\t\t\tthrow $failure;
\t\t} finally {
\t\t\tkXmlEntityLoaderPolicy::endSoapScope($scope, $error);
\t\t}
\t}
}
'''
    after=text.replace('\n','\r\n').encode()
  dest=HERE/'candidate-tree'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(after)
  patch=''.join(difflib.unified_diff(before.decode().splitlines(keepends=True),after.decode().splitlines(keepends=True),fromfile='a/'+path if before else '/dev/null',tofile='b/'+path))
  patchpath=OUT/(Path(path).name+'.patch');patchpath.write_bytes(patch.encode())
  changes.append({'path':path,'operation':'modify' if before else 'add','before_sha256':sha(before) if before else None,'after_sha256':sha(after),'patch':str(patchpath.relative_to(REPO)),'patch_sha256':sha(patch.encode())})
 metadata={'status':'HELD_LOCAL_UNTESTED_PROTOTYPE','target':'PHP8.3 synchronous only','base_archive_sha256':PINS['exp11']['archive_sha256'],'selected_in_artifact':False,'requires_new_file_builder_support':True,'changes':changes}
 (OUT/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n');return metadata
if __name__=='__main__':print(json.dumps(build(),indent=2))

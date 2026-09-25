<?php
// Real bootstrap/classes; only the logger sink is replaced with an in-memory sink.
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
$root = '/audit/app';
$case = 'null-probe';
$out = array();
set_include_path($root.'/vendor/ZendFramework/library'.PATH_SEPARATOR.$root.'/vendor');
require '/audit/tests/api-bootstrap.php';
$diagnostics = array();
set_error_handler(function ($severity, $message, $file, $line) use (&$diagnostics) {
    // Synthetic inputs only. Preserve warnings separately from contract output.
    $diagnostics[] = array($severity, $message, $file, $line);
    return true;
});
class NullProbeLogger {
    public $messages = array();
    public function log($message, $priority) { $this->messages[] = $message; }
    public function setEventItem($name, $value) {}
}
$logger = new NullProbeLogger();
KalturaLog::setLogger($logger);
$values = array('null'=>null, 'empty'=>'', 'false'=>false, 'zero'=>0,
    'zero-string'=>'0', 'space'=>'  ', 'dummy'=>'DUMMY', 'commas'=>',DUMMY,',
    'array'=>array('x'), 'object'=>new stdClass());
$rows = array();
foreach ($values as $label => $value) {
    foreach (array('partner', 'custom-data', 'analytics', 'front-user') as $operation) {
        $logger->messages = array();
        try {
            if ($operation === 'partner') {
                $partner = new Partner();
                $partner->putInCustomData('always_allowed_permission_names', $value);
                $result = $partner->getAlwaysAllowedPermissionNames();
                if ($label === 'dummy' && $result !== 'DUMMY') throw new RuntimeException('Dummy permission changed');
                if ($label === 'null' && $result !== PermissionName::ALWAYS_ALLOWED_ACTIONS) throw new RuntimeException('Default permission changed');
            } elseif ($operation === 'custom-data') {
                $result = myCustomData::fromString($value)->toString(false);
            } elseif ($operation === 'analytics') {
                KalturaLog::analytics(array($value));
                $result = $logger->messages;
            } else {
                // Avoid singleton constructor/dispatch; invoke the actual end-logging method.
                $ref = new ReflectionClass('KalturaFrontController');
                $controller = $ref->newInstanceWithoutConstructor();
                $start = $ref->getProperty('requestStart');$start->setAccessible(true);$start->setValue($controller, microtime(true));
                kCurrentContext::$uid = null; kCurrentContext::$ks_uid = $value;
                kCurrentContext::$ks = ''; // never generate/use a real token in this fixture
                $controller->onRequestEnd();
                $message = $logger->messages[0];
                $result = explode(',', $message)[5]; // only deterministic user-id field, not timing
            }
            $rows[] = array($operation, $label, 'return', $result);
        } catch (Throwable $e) {
            if ($e instanceof RuntimeException) throw $e; // fixture assertions never normalized as application errors
            $rows[] = array($operation, $label, 'error', get_class($e));
        }
    }
}
$legacy = array('ns:key'=>'v', 'plain'=>array('nested'=>123));
$custom = myCustomData::fromString(serialize($legacy));
if ($custom->toArray() !== array('plain'=>array('nested'=>123),'ns'=>array('key'=>'v'))) throw new RuntimeException('Legacy namespace conversion changed');
$rows[] = array('custom-data', 'legacy-namespace', $custom->toArray(), $custom->toString(false));
echo json_encode(array('php'=>PHP_VERSION,'rows'=>$rows,'diagnostics'=>$diagnostics)), "\n";

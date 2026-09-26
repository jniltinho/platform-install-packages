<?php
// Native API/identity prerequisite only. No application, parser input or transport.
error_reporting(E_ALL);
if (PHP_VERSION_ID < 80300 || PHP_VERSION_ID >= 80400 ||
    !function_exists('libxml_get_external_entity_loader')) {
    fwrite(STDERR, "Requires native PHP 8.3 loader getter\n");
    exit(65);
}
$diagnostics = array();
set_error_handler(function ($severity, $message, $file, $line) use (&$diagnostics) {
    $diagnostics[] = array('severity' => $severity, 'message' => $message, 'line' => $line);
    return false;
});
function xmlLifecycleIdentityNamed($public, $system, $context) { return null; }
class XmlLifecycleIdentityCallable {
    public static function named($public, $system, $context) { return null; }
    public function __invoke($public, $system, $context) { return null; }
}
$original = libxml_get_external_entity_loader();
$cases = array(
    'closure' => static function ($public, $system, $context) { return null; },
    'named' => 'xmlLifecycleIdentityNamed',
    'static-array' => array('XmlLifecycleIdentityCallable', 'named'),
    'invokable' => new XmlLifecycleIdentityCallable(),
    'null' => null,
);
$rows = array();
try {
    foreach ($cases as $name => $callback) {
        $set = libxml_set_external_entity_loader($callback);
        $got = libxml_get_external_entity_loader();
        $rows[] = array(
            'case' => $name, 'setter_return' => $set, 'setter_type' => gettype($set),
            'input_type' => gettype($callback), 'getter_type' => gettype($got),
            'strict_identity' => $got === $callback,
            'callable_or_null' => $got === null || is_callable($got),
        );
    }
} finally {
    libxml_set_external_entity_loader($original);
}
echo json_encode(array(
    'scope' => 'native callable identity only; not application or parser behavior',
    'php' => PHP_VERSION, 'php_id' => PHP_VERSION_ID, 'libxml' => LIBXML_DOTTED_VERSION,
    'error_reporting' => error_reporting(), 'rows' => $rows,
    'original_restored_identity' => libxml_get_external_entity_loader() === $original,
    'diagnostics' => $diagnostics, 'probe_sha256' => hash_file('sha256', __FILE__),
), JSON_UNESCAPED_SLASHES) . "\n";

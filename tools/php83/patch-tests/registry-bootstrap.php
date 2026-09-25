<?php
require_once 'Zend/Registry.php';
require_once 'Zend/Application/Bootstrap/Bootstrapper.php';
require_once 'Zend/Application/Bootstrap/ResourceBootstrapper.php';
require_once 'Zend/Application/Bootstrap/BootstrapAbstract.php';
class Php83BootstrapContainerProbe extends Zend_Application_Bootstrap_BootstrapAbstract
{
    // Isolate inherited container methods; no application initialization/run.
    public function __construct($application = null) {}
    public function run() { throw new RuntimeException('Application run forbidden'); }
}
$bootstrap = new Php83BootstrapContainerProbe();
$container = $bootstrap->getContainer();
if (!($container instanceof Zend_Registry)) { throw new RuntimeException('Wrong container'); }
foreach (array('text' => 'value', 'zero' => 0, 'false' => false, 'nullable' => null,
    'nested' => array('a' => 1)) as $name => $value) {
    // Matches the property-write form used by _executeResource, without running
    // resource plugins or the real application bootstrap.
    $container->$name = $value;
    $actual = $bootstrap->getResource(strtoupper($name));
    $exists = $bootstrap->hasResource($name);
    if ($actual !== $value) {
        throw new RuntimeException('Bootstrap resource API differs');
    }
    $out[] = array($name, $exists, $actual);
}
unset($container->text);
$out[] = array('unset', $bootstrap->hasResource('text'), $bootstrap->getResource('text'));
$out[] = array('absent', $bootstrap->hasResource('missing'), $bootstrap->getResource('missing'));

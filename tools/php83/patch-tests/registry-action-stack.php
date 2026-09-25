<?php
// Actual Zend classes, synthetic requests; no front controller or HTTP dispatch.
require_once 'Zend/Controller/Plugin/ActionStack.php';
require_once 'Zend/Controller/Request/Simple.php';
Zend_Registry::_unsetInstance();
$plugin = new Zend_Controller_Plugin_ActionStack();
if (!Zend_Registry::isRegistered($plugin->getRegistryKey()) || $plugin->getStack() !== array()
    || $plugin->popStack() !== false) {
    throw new RuntimeException('Initial singleton stack mismatch');
}
$current = new Zend_Controller_Request_Simple('current', 'controller', 'module', array('keep' => 'old'));
$plugin->setRequest($current);
$first = new Zend_Controller_Request_Simple('first');
$second = new Zend_Controller_Request_Simple('second', 'other-controller', 'other-module');
$empty = new Zend_Controller_Request_Simple();
$plugin->pushStack($first)->pushStack($second)->pushStack($empty);
if (count($plugin->getStack()) !== 3 || $plugin->popStack() !== $second || $plugin->popStack() !== $first
    || $first->getControllerName() !== 'controller' || $first->getModuleName() !== 'module'
    || $plugin->popStack() !== false) {
    throw new RuntimeException('LIFO/skip/inheritance mismatch');
}
$out[] = array('lifo', $second->getActionName(), $first->getActionName(),
    $first->getControllerName(), $first->getModuleName());
foreach (array(false, true) as $clear) {
    $current = new Zend_Controller_Request_Simple('current', 'controller', 'module', array('keep' => 'old'));
    $current->setDispatched(true);
    $plugin->setRequest($current)->setClearRequestParams($clear);
    $next = new Zend_Controller_Request_Simple('next', 'new-controller', 'new-module', array('new' => 'value'));
    $plugin->pushStack($next);
    $plugin->postDispatch($current);
    $params = $current->getParams();
    if ($current->isDispatched() || $current->getActionName() !== 'next'
        || $current->getControllerName() !== 'new-controller' || $current->getModuleName() !== 'new-module'
        || $params['new'] !== 'value' || array_key_exists('keep', $params) === $clear
        || $plugin->getStack() !== array()) {
        throw new RuntimeException('Forwarding state mismatch');
    }
    $out[] = array('forward', $clear, $current->getActionName(), $params);
}
$separate = new Zend_Registry();
$custom = new Zend_Controller_Plugin_ActionStack($separate, 'custom-stack');
$custom->pushStack(new Zend_Controller_Request_Simple('custom', 'controller', 'module'));
if (count($custom->getStack()) !== 1 || $plugin->getStack() !== array()) {
    throw new RuntimeException('Custom registry is not isolated');
}
$out[] = array('custom', $custom->getRegistryKey(), $custom->popStack()->getActionName());
$plugin->pushStack(new Zend_Controller_Request_Simple('pending', 'controller', 'module'));
$current->setDispatched(false);
$plugin->postDispatch($current);
if (count($plugin->getStack()) !== 1) { throw new RuntimeException('Undispatched request consumed stack'); }
$out[] = array('undispatched-keeps-stack', count($plugin->getStack()));

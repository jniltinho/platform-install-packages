<?php
// Reflection only: no connection, source loading, filesystem write or network.
$targets = array(
    'PDOStatement' => array('bindValue', 'execute'),
    'PDO' => array('exec', 'query', 'beginTransaction', 'commit', 'rollBack', 'setAttribute', 'getAttribute', 'prepare'),
    'IteratorAggregate' => array('getIterator'),
    'Iterator' => array('rewind', 'valid', 'key', 'current', 'next'),
    'Countable' => array('count'),
    'ArrayAccess' => array('offsetExists', 'offsetSet', 'offsetGet', 'offsetUnset'),
    'Exception' => array('__wakeup')
);
$rows = array();
foreach ($targets as $class => $methods) {
    foreach ($methods as $method) {
        $r = new ReflectionMethod($class, $method);
        $rows[] = array(
            'class' => $class, 'method' => $method,
            'declared_return' => $r->hasReturnType() ? (string)$r->getReturnType() : null,
            'tentative_return' => method_exists($r, 'getTentativeReturnType') && $r->hasTentativeReturnType() ? (string)$r->getTentativeReturnType() : null
        );
    }
}
echo json_encode(array('php'=>PHP_VERSION, 'sapi'=>PHP_SAPI, 'rows'=>$rows), JSON_PRETTY_PRINT), "\n";

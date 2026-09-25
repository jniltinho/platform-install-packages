<?php
function __autoload($class) {
    $GLOBALS['hits'][] = array('legacy', $class);
    if ($class === 'FixtureLegacyHit') require '/audit/fixtures/extra/FixtureLegacyHit.php';
}

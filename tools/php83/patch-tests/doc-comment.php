<?php
require_once $root . '/api_v3/lib/reflection/KalturaDocCommentParser.php';
$cacheExports = array();
foreach (array(
    array('/** Empty */', array()),
    array('/** @disableRelativeTime $createdAt */', array('createdAt')),
    array("/**\n * @disableRelativeTime \$createdAt\n * @disableRelativeTime \$updatedAt\n */", array('createdAt', 'updatedAt')),
    array("/**\n * @disableRelativeTime \$createdAt\n * @disableRelativeTime \$createdAt\n */", array('createdAt', 'createdAt')),
    array('/** @disableRelativeTime $ */', array('')),
    array('/** @disablerelativetime $ignored */', array()),
) as $fixture) {
    $parsed = new KalturaDocCommentParser($fixture[0]);
    if ($parsed->disableRelativeTimeParams !== $fixture[1]) {
        throw new RuntimeException('Doc comment parse contract changed');
    }
    $serialized = serialize($parsed);
    $cacheExports[] = array('comment' => $fixture[0], 'payload_base64' => base64_encode($serialized), 'sha256' => hash('sha256', $serialized));
    $restored = unserialize($serialized);
    if (get_object_vars($restored) !== get_object_vars($parsed)) {
        throw new RuntimeException('Doc comment cache roundtrip changed');
    }
    $out[] = array('parsed', $parsed->disableRelativeTimeParams, 'serialized_sha256', hash('sha256', $serialized));
}
// A legacy serialized public-property entry must remain loadable.
$legacy = 'O:23:"KalturaDocCommentParser":1:{s:25:"disableRelativeTimeParams";a:1:{i:0;s:9:"createdAt";}}';
$restored = unserialize($legacy);
if (!$restored instanceof KalturaDocCommentParser || $restored->disableRelativeTimeParams !== array('createdAt')) {
    throw new RuntimeException('Legacy property cache cannot be read');
}
$out[] = array('legacy-public-property-cache', true);

if ($case === 'doc-comment-export') {
    $out = array('producer_php' => PHP_VERSION, 'source_sha256' => hash_file('sha256', $root . '/api_v3/lib/reflection/KalturaDocCommentParser.php'), 'entries' => $cacheExports);
}

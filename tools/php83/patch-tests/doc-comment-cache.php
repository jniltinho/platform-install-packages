<?php
require_once $root . '/api_v3/lib/reflection/KalturaDocCommentParser.php';
$fixture = json_decode(file_get_contents(__DIR__ . '/doc-comment-legacy-cache.json'), true);
if (strpos($fixture['producer_php'], '7.4.') !== 0 || count($fixture['entries']) !== 6) {
    throw new RuntimeException('Unexpected cache producer fixture');
}
foreach ($fixture['entries'] as $entry) {
    $payload = base64_decode($entry['payload_base64'], true);
    if ($payload === false || hash('sha256', $payload) !== $entry['sha256']) {
        throw new RuntimeException('Legacy payload identity mismatch');
    }
    $cached = unserialize($payload, array('allowed_classes' => array('KalturaDocCommentParser')));
    $fresh = new KalturaDocCommentParser($entry['comment']);
    if (!$cached instanceof KalturaDocCommentParser || get_object_vars($cached) !== get_object_vars($fresh) ||
        serialize($cached) !== $payload || serialize($fresh) !== $payload) {
        throw new RuntimeException('Legacy full parser cache changed');
    }
    $out[] = array('full-original-cache', $entry['sha256'], count(get_object_vars($cached)), $cached->disableRelativeTimeParams);
}

<?php
// Real application bootstrap, reflection and deserializer; no DB or service invocation.
require __DIR__ . '/api-bootstrap.php';
$reflector = new KalturaActionReflector('playlist', 'update', array('PlaylistService', 'updateAction', 'playlist', 'update'));
$params = $reflector->getActionParams();
foreach (array('id' => false, 'playlist' => true, 'updateStats' => false) as $name => $expected) {
    if ($params[$name]->getDisableRelativeTime() !== $expected) {
        throw new RuntimeException('Real playlist annotation not propagated: ' . $name);
    }
    $out[] = array('playlist-reflection', $name, $expected);
}
$out[] = array('real-mixed-docblock-hash', hash('sha256', serialize($reflector->getActionInfo())));
// Synthetic object signature isolates nested time conversion through real reflection.
class SyntheticTimeObject extends KalturaObject {
    /** @var time */
    public $createdAt;
}
class SyntheticRelativeTimeService {
    /**
     * Preserve one relative expression and resolve the other.
     * @action times
     * @param SyntheticTimeObject $marked
     * @param SyntheticTimeObject $normal
     * @disableRelativeTime $marked
     * @return string
     */
    public function timesAction(SyntheticTimeObject $marked, SyntheticTimeObject $normal) { throw new RuntimeException('Must not invoke synthetic action'); }
}
$reflector = new KalturaActionReflector('synthetic', 'times', array('SyntheticRelativeTimeService', 'timesAction', 'synthetic', 'times'));
$params = $reflector->getActionParams();
$deserializer = new KalturaRequestDeserializer(array('marked:createdAt' => '-3600', 'normal:createdAt' => '-3600'));
$start = time();
$args = $deserializer->buildActionArguments($params);
$end = time();
if (!$args[0] instanceof SyntheticTimeObject || !$args[1] instanceof SyntheticTimeObject ||
    $args[0]->createdAt !== '-3600' || !is_int($args[1]->createdAt) ||
    $args[1]->createdAt < $start - 3600 || $args[1]->createdAt > $end - 3600) {
    throw new RuntimeException('Relative-time conversion or opt-out changed');
}
$out[] = array('relative-time-opt-out', 'literal-preserved', 'unmarked-converted');

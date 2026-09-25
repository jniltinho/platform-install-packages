<?php
// Unit isolation only: exact source functions, explicit query/criteria doubles.
// Never include the endpoint bootstrap. Default unit mode performs no DB I/O;
// the separate integration harness may provide an isolated PDO statement.
$source = file_get_contents($root . '/api_v3/web/analyticsSyncServe.php');
$sourceHash = 'b2fe37440f542a49020547bfc6babc76049ab713e65495247b0c6a6eb1f010dc';
if (hash('sha256', $source) !== $sourceHash) {
    throw new RuntimeException('Analytics source drift');
}
$lines = explode("\n", $source);
foreach (array(array(59, 73), array(75, 83), array(116, 165)) as $range) {
    $function = implode("\n", array_slice($lines, $range[0] - 1, $range[1] - $range[0] + 1));
    eval($function); // Hash-pinned, exact function-only ranges; no bootstrap.
}
define('MAX_ITEMS', 2000);
foreach (array('PARTNER_SECRET' => 's', 'PARTNER_CRM_ID' => 'ci', 'PARTNER_VERTICAL' => 'v',
    'PARTNER_PARENT_ID' => 'pp', 'PARTNER_SERVICE_EDITION' => 'se', 'PARTNER_ACCOUNT_TYPE' => 'at') as $key => $value) {
    define($key, $value);
}
class Criteria
{
    const GREATER_EQUAL = '>=';
    public function addSelectColumn($column) {}
    public function add($column, $value, $comparison) {}
    public function addAscendingOrderByColumn($column) {}
    public function setLimit($limit) { if ($limit !== 2000) { throw new RuntimeException('Unexpected limit'); } }
}
class Partner { const PARTNER_STATUS_ACTIVE = 1; }
class AnalyticsStatementDouble
{
    public function fetchAll($mode) {
        if ($mode !== PDO::FETCH_ASSOC) { throw new RuntimeException('Unexpected fetch mode'); }
        return PartnerPeer::$rows;
    }
}
class PartnerPeer
{
    const ID = 'ID', STATUS = 'STATUS', ADMIN_SECRET = 'ADMIN_SECRET', CUSTOM_DATA = 'CUSTOM_DATA',
        PARTNER_PARENT_ID = 'PARTNER_PARENT_ID', PARTNER_PACKAGE = 'PARTNER_PACKAGE', UPDATED_AT = 'UPDATED_AT';
    public static $rows;
    public static $statementFactory;
    public static $filter = true;
    public static function setUseCriteriaFilter($enabled) { self::$filter = $enabled; }
    public static function doSelectStmt($criteria) {
        if (self::$statementFactory !== null) { return call_user_func(self::$statementFactory); }
        return new AnalyticsStatementDouble();
    }
}
if (isset($analyticsFunctionsOnly) && $analyticsFunctionsOnly) { return; }
$results = array();
foreach (array('text' => array('42', '7'), 'native' => array(42, 7), 'null' => array(null, null)) as $shape => $values) {
    $row = array('ID' => '101', 'STATUS' => Partner::PARTNER_STATUS_ACTIVE,
        'ADMIN_SECRET' => 'SYNTHETIC_NOT_A_SECRET', 'CUSTOM_DATA' => serialize(array('crmId' => 'synthetic')),
        'PARTNER_PARENT_ID' => $values[0], 'PARTNER_PACKAGE' => $values[1], 'UPDATED_AT' => '2020-01-01 00:00:00');
    $inactive = $row;
    $inactive['ID'] = '102';
    $inactive['STATUS'] = 99;
    PartnerPeer::$rows = array($row, $inactive);
    $result = getPartnerUpdates(0);
    $info = json_decode($result['items'][101], true);
    if ($info['pp'] !== $values[0] || $info['se'] !== $values[1] || $result['items'][102] !== ''
        || $result['totalCount'] !== 2 || $result['updatedAt'] !== 1577836800 || !PartnerPeer::$filter) {
        throw new RuntimeException('Analytics characterization mismatch');
    }
    $results[$shape] = $result;
}
if ($results['text']['items'][101] === $results['native']['items'][101]) {
    throw new RuntimeException('Expected raw numeric JSON distinction was not reproduced');
}
$out[] = array('source_sha256' => $sourceHash, 'fixture_kind' => 'function-only with query doubles', 'results' => $results);

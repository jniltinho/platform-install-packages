<?php
// Real SessionService action and KS implementation, with synthetic DB only.
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
$root = '/audit/app';
$case = 'api-mysql';
$out = array();
set_include_path($root . '/vendor/ZendFramework/library' . PATH_SEPARATOR . $root . '/vendor');
require __DIR__ . '/api-bootstrap.php';
file_put_contents($root . "/configurations/cache.ini", "[mapping]\npartnerSecrets = disabledProbe\nqueryCacheKeys = \"\"\n");
// Public test-only constants, never deployment credentials.
$connection->exec("INSERT INTO partner (id,partner_name,status,secret,admin_secret) VALUES (83001,'Synthetic session partner',1,'synthetic-user-only','synthetic-admin-only')");
$connection->exec(file_get_contents(__DIR__ . '/api-session-schema.sql'));
$service = new SessionService();
foreach (array(SessionType::USER => 'synthetic-user-only', SessionType::ADMIN => 'synthetic-admin-only') as $type => $secret) {
    $token = $service->startAction($secret, 'synthetic-user', $type, 83001, 60, '');
    if (!is_string($token) || $token === '') { throw new RuntimeException('Session token missing'); }
    $decoded = ks::fromSecureString($token);
    if ((int)$decoded->partner_id !== 83001 || $decoded->user !== 'synthetic-user' || (int)$decoded->type !== $type) {
        throw new RuntimeException('Session fields changed');
    }
    $out[] = array('session-roundtrip', $type, 'matched');
    if ($decoded->isValid(83001, 'synthetic-user', $type) !== ks::OK) {
        throw new RuntimeException('Valid session rejected');
    }
    $out[] = array('session-valid', $type, true);
    if ($decoded->isValid(83002, 'synthetic-user', $type) !== ks::INVALID_PARTNER) {
        throw new RuntimeException('Cross-partner session accepted');
    }
    $out[] = array('cross-partner-rejected', $type, true);
    if ($decoded->isValid(83001, 'different-user', $type) !== ks::INVALID_USER) {
        throw new RuntimeException('Wrong user accepted');
    }
    $out[] = array('wrong-user-rejected', $type, true);
    $tampered = $token;
    $position = (int)(strlen($tampered) / 2);
    $tampered[$position] = $tampered[$position] === 'A' ? 'B' : 'A';
    $rejected = false;
    try {
        $invalid = ks::fromSecureString($tampered);
        $rejected = $invalid->isValid(83001, 'synthetic-user', $type) === ks::INVALID_STR;
    } catch (Exception $error) {
        $rejected = $error->getMessage() === ks::getErrorStr(ks::INVALID_STR);
    }
    if (!$rejected) { throw new RuntimeException('Tampered session not rejected as invalid'); }
    $out[] = array('tampered-rejected', $type, true);
    $expired = ks::fromSecureString($service->startAction($secret, 'synthetic-user', $type, 83001, -60, ''));
    if ($expired->isValid(83001, 'synthetic-user', $type) !== ks::EXPIRED) {
        throw new RuntimeException('Expired session accepted');
    }
    $out[] = array('expired-rejected', $type, true);
}
try {
    $service->startAction('synthetic-wrong-secret', 'synthetic-user', 0, 83001, 60, '');
    throw new RuntimeException('Wrong secret accepted');
} catch (KalturaAPIException $error) {
    if ($error->getCode() !== 'START_SESSION_ERROR') { throw $error; }
    $out[] = array('wrong-secret', $error->getCode());
}
try {
    $service->startAction('synthetic-user-only', 'synthetic-user', SessionType::ADMIN, 83001, 60, '');
    throw new RuntimeException('User secret escalated to admin');
} catch (KalturaAPIException $error) {
    if ($error->getCode() !== 'START_SESSION_ERROR') { throw $error; }
    $out[] = array('user-secret-admin-rejected', $error->getCode());
}
// Preserve PHP 7.4's left-associative formatting, including legacy quirks.
foreach (array(0, 999, 10000, 600000, 3600000, 36000000, 39600000, 86400000, -1000) as $duration) {
    $out[] = array('duration', $duration, dateUtils::formatDuration($duration));
}
echo json_encode($out), "\n";

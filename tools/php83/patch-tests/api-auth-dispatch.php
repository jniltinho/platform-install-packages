<?php
// Reuse the isolated setup and its prerequisite assertions without emitting KS.
ob_start();
require __DIR__ . '/api-session.php';
ob_end_clean();
$connection->exec("INSERT INTO permission (id,type,name,partner_id,status) VALUES (2,1,'SYNTHETIC_SESSION_READ',0,1)");
$connection->exec("INSERT INTO permission_item (id,type,partner_id,param_1,param_2,param_3,param_4,param_5) VALUES (2,'kApiActionPermissionItem',0,'session','get','','','')");
$connection->exec("INSERT INTO permission_to_permission_item (id,permission_id,permission_item_id) VALUES (2,2,2)");
$connection->exec("INSERT INTO user_role (id,str_id,name,partner_id,status,permission_names) VALUES (2,'BASE_USER_SESSION_ROLE','Synthetic user',0,1,'SYNTHETIC_SESSION_READ'),(3,'PARTNER_ADMIN_ROLE','Synthetic admin',0,1,'SYNTHETIC_SESSION_READ')");
$connection->exec("INSERT INTO partner (id,partner_name,status,secret,admin_secret) VALUES (83002,'Other synthetic partner',1,'synthetic-other-user','synthetic-other-admin')");
$connection->exec("INSERT INTO permission (id,type,name,partner_id,status) VALUES (3,1,'SYNTHETIC_ADMIN_PING',0,1),(4,1,'SYNTHETIC_UNGRANTED',0,1)");
$connection->exec("INSERT INTO permission_item (id,type,partner_id,param_1,param_2,param_3,param_4,param_5) VALUES (3,'kApiActionPermissionItem',0,'system','ping','','',''),(4,'kApiActionPermissionItem',0,'system','getversion','','','')");
$connection->exec("INSERT INTO permission_to_permission_item (id,permission_id,permission_item_id) VALUES (3,3,3),(4,4,4)");
$connection->exec("UPDATE user_role SET permission_names='SYNTHETIC_SESSION_READ,SYNTHETIC_ADMIN_PING' WHERE id=3");
$out = array();
foreach (array(SessionType::USER => 'synthetic-user-only', SessionType::ADMIN => 'synthetic-admin-only') as $type => $secret) {
    $token = $service->startAction($secret, 'synthetic-user', $type, 83001, 60, '');
    $result = KalturaDispatcher::getInstance()->dispatch('session', 'get', array('ks' => $token));
    if (!$result instanceof KalturaSessionInfo || (int)$result->partnerId !== 83001 ||
        $result->userId !== 'synthetic-user' || (int)$result->sessionType !== $type) {
        throw new RuntimeException('Authenticated dispatcher result changed');
    }
    $out[] = array('authenticated-session-get', $type, true);
    if ($type === SessionType::ADMIN) {
        $adminToken = $token;
        if (KalturaDispatcher::getInstance()->dispatch('system', 'ping', array('ks' => $token)) !== true) {
            throw new RuntimeException('Admin-only ping failed');
        }
        $out[] = array('admin-only-ping', true);
    } else {
        try {
            KalturaDispatcher::getInstance()->dispatch('system', 'ping', array('ks' => $token));
            throw new RuntimeException('User reached admin-only ping');
        } catch (KalturaAPIException $error) {
            if ($error->getCode() !== 'SERVICE_FORBIDDEN') { throw $error; }
        }
        $out[] = array('user-ping-denied', true);
    }
}
$expiredToken = $service->startAction('synthetic-user-only', 'synthetic-user', SessionType::USER, 83001, -60, '');
if (ks::fromSecureString($expiredToken)->isValid(83001, 'synthetic-user', SessionType::USER) !== ks::EXPIRED) {
    throw new RuntimeException('Expired fixture is not validly signed and expired');
}
foreach (array('missing' => array('partnerId' => 83001),
    'expired' => array('ks' => $expiredToken),
    'ungranted' => array('ks' => $adminToken),
    'cross-partner' => array('ks' => $adminToken, 'partnerId' => 83002),
    'malformed' => array('ks' => 'not-a-valid-session')) as $label => $params) {
    $caught = null;
    try {
        KalturaDispatcher::getInstance()->dispatch($label === 'ungranted' ? 'system' : 'session', $label === 'ungranted' ? 'getVersion' : 'get', $params);
    } catch (Exception $error) {
        $caught = array(get_class($error), $error->getCode());
    }
    $expected = in_array($label, array('expired', 'malformed'), true) ?
        array('kCoreException', 'INVALID_KS') : array('KalturaAPIException', 'SERVICE_FORBIDDEN');
    if ($caught !== $expected) { throw new RuntimeException('Unexpected negative dispatch result: ' . $label); }
    $out[] = array('rejected', $label, $caught);
    $recovered = KalturaDispatcher::getInstance()->dispatch('session', 'get', array('ks' => $token));
    if (!$recovered instanceof KalturaSessionInfo || (int)$recovered->partnerId !== 83001 ||
        $recovered->userId !== 'synthetic-user' || (int)$recovered->sessionType !== SessionType::ADMIN) {
        throw new RuntimeException('Valid request after rejection failed: ' . $label);
    }
    $out[] = array('context-recovered', $label, true);
}
echo json_encode($out), "\n";

<?php
// Temporary synthetic-lab instrumentation: paths only; never headers, KS or URLs.
$label = $_SERVER['HTTP_X_KALTURA_AUDIT_LABEL'] ?? '';
if (!in_array($label, array('api-ping', 'admin-login', 'kmc-shell'), true)) {
    return;
}
register_shutdown_function(function () use ($label) {
    $files = array_values(array_filter(get_included_files(), function ($file) {
        return strpos($file, '/opt/kaltura/') === 0;
    }));
    $error = error_get_last();
    $record = array('label' => $label, 'files' => $files,
        'last_error_type' => $error ? $error['type'] : null);
    file_put_contents('/var/lib/kaltura-audit-traces/includes.jsonl',
        json_encode($record) . "\n", FILE_APPEND | LOCK_EX);
});

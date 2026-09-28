<?php
// Private CLI bridge only. Source script executes with original argv/argc, not exec argv.
if (PHP_SAPI !== 'cli' || $argc !== 2) { exit(92); }
$privateArgumentPath = $argv[1];
$privateParent = lstat(dirname($privateArgumentPath));
$privateStat = lstat($privateArgumentPath);
if (!$privateParent || ($privateParent['mode'] & 0170000) !== 0040000
    || ($privateParent['mode'] & 0777) !== 0700 || $privateParent['uid'] !== 0
    || !$privateStat || ($privateStat['mode'] & 0170000) !== 0100000
    || ($privateStat['mode'] & 0777) !== 0600 || $privateStat['uid'] !== 0) { exit(92); }
$privateHandle = fopen($privateArgumentPath, 'rb');
if ($privateHandle === false) { exit(92); }
$privateOpened = fstat($privateHandle);
if ($privateOpened['ino'] !== $privateStat['ino'] || $privateOpened['dev'] !== $privateStat['dev']) { exit(92); }
$privateBytes = stream_get_contents($privateHandle);
fclose($privateHandle);
if ($privateBytes === false || substr($privateBytes, -1) !== "\0") { exit(92); }
$argv = explode("\0", substr($privateBytes, 0, -1));
if (!$argv || !is_file($argv[0]) || realpath($argv[0]) !== $argv[0]
    || strpos($argv[0], '/opt/kaltura/') !== 0
    || basename($argv[0]) !== 'create_playkit_uiconf.php') { exit(92); }
if (!unlink($privateArgumentPath)) { exit(92); }
$argc = count($argv);
$_SERVER['argv'] = $argv;
$_SERVER['argc'] = $argc;
$_SERVER['SCRIPT_FILENAME'] = $argv[0];
$_SERVER['PHP_SELF'] = $argv[0];
unset($privateBytes, $privateStat, $privateOpened, $privateHandle, $privateArgumentPath, $privateParent);
require $argv[0];

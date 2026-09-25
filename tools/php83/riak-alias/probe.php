<?php
error_reporting(E_ALL);
$variant = $argv[1];
if (!in_array($variant, array('original', 'candidate'), true)) { exit(64); }
$base = '/audit/probe/' . $variant . '/vendor/aws/Doctrine/Common/Cache/';
foreach (array('Cache.php','FlushableCache.php','ClearableCache.php','MultiGetCache.php','CacheProvider.php','RiakCache.php') as $file) { require $base . $file; }
$class = new ReflectionClass('Doctrine\\Common\\Cache\\RiakCache');
$object = $class->newInstanceWithoutConstructor();
$rows = array();
$rows[] = array('parent', $class->getParentClass()->getName());
$interfaces = $class->getInterfaceNames(); sort($interfaces);
$rows[] = array('interfaces', $interfaces);
$rows[] = array('bucket-type', (string)$class->getConstructor()->getParameters()[0]->getType());
$rows[] = array('object-type', (string)$class->getMethod('isExpired')->getParameters()[0]->getType());
$rows[] = array('default-namespace', $object->getNamespace());
$object->setNamespace('synthetic-public');
$rows[] = array('changed-namespace', $object->getNamespace());
$rows[] = array('stats', $object->getStats());
$rows[] = array('expiry-header', $class->getConstant('EXPIRES_HEADER'));
$rows[] = array('provider-loaded', extension_loaded('riak'));
$rows[] = array('provider-classes', class_exists('Riak\\Bucket', false), class_exists('Riak\\Object', false));
$hashes = array();
foreach (get_included_files() as $file) { $hashes[str_replace('/audit/probe/', '', $file)] = hash_file('sha256', $file); }
ksort($hashes);
echo json_encode(array('rows'=>$rows,'loaded_sha256'=>$hashes,'backend_executed'=>false), JSON_UNESCAPED_SLASHES), "\n";

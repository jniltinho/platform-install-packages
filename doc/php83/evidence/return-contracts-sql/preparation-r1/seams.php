<?php
// Explicit side-effect boundary ONLY. Never record SQL/DSN/credentials/timing.
$GLOBALS['seam_calls']=[];
function seam($name){$GLOBALS['seam_calls'][$name]=($GLOBALS['seam_calls'][$name]??0)+1;}
class KalturaLog {static function debug($m){seam(__METHOD__);}static function alert($m){seam(__METHOD__);}}
class KalturaMonitorClient {static function monitorConnTook($dsn,$time,$error=null){seam(__METHOD__);}static function monitorDatabaseAccess($sql,$time,$host=null){seam(__METHOD__);}}
class kQueryCache {static function isCurrentQueryHandled(){seam(__METHOD__);return false;}}
class kApiCache {static function disableConditionalCache(){seam(__METHOD__);}}

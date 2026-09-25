<?php
// Tokenize without TOKEN_PARSE: original curly-offset files cannot compile on 8.3.
if ($argc !== 4) { exit(64); }
$before = file_get_contents($argv[1]);
$after = file_get_contents($argv[2]);
$messages = json_decode(file_get_contents($argv[3]), true, 512, JSON_THROW_ON_ERROR);
function failCheck($message) { throw new RuntimeException($message); }
function tokens($source) {
    $result=[]; $offset=0; $line=1; $column=1;
    foreach (token_get_all($source) as $token) {
        $content=is_array($token) ? $token[1] : $token;
        $result[]=['type'=>is_array($token) ? token_name($token[0]) : 'punctuation',
            'content'=>$content,'offset'=>$offset,'line'=>$line,'column'=>$column];
        $offset+=strlen($content);
        $newlines=substr_count($content,"\n");
        if ($newlines) { $line+=$newlines; $column=strlen($content)-strrpos($content,"\n"); }
        else { $column+=strlen($content); }
    }
    return $result;
}
$a=tokens($before); $b=tokens($after);
if (strlen($before)!==strlen($after) || count($a)!==count($b)) failCheck('Byte/token length differs');
$approved=[];
foreach ($messages as $message) {
    if ($message['source']!=='PHPCompatibility.Syntax.RemovedCurlyBraceArrayAccess.Removed' || !$message['fixable']) failCheck('Unexpected PHPCS finding');
    $approved[$message['line'].':'.$message['column']]=true;
}
$stack=[]; $pairs=[]; $changes=[]; $protected=0;
foreach ($a as $i=>$token) {
    $other=$b[$i];
    if ($token['type']!=='punctuation') ++$protected;
    $content=$token['content'];
    if ($token['type']==='punctuation' && $content==='{') $stack[]=$i;
    elseif (in_array($token['type'],['T_CURLY_OPEN','T_DOLLAR_OPEN_CURLY_BRACES'],true)) $stack[]=$i;
    elseif ($token['type']==='punctuation' && $content==='}') {
        if (!$stack) failCheck('Unmatched original curly close');
        $open=array_pop($stack); $pairs[$open]=$i;
    }
    if ($token===$other) continue;
    if ($token['type']!=='punctuation' || $other['type']!=='punctuation' ||
        $token['offset']!==$other['offset'] || $token['line']!==$other['line'] || $token['column']!==$other['column'] ||
        !(($content==='{' && $other['content']==='[') || ($content==='}' && $other['content']===']'))) failCheck('Non-bracket token change');
    $changes[$i]=['token_index'=>$i,'offset'=>$token['offset'],'line'=>$token['line'],'column'=>$token['column'],'before'=>$content,'after'=>$other['content']];
}
if ($stack) failCheck('Unmatched original curly open');
$offsetPairs=[]; $consumed=[];
foreach ($changes as $index=>$change) {
    if ($change['before']!== '{') continue;
    $key=$change['line'].':'.$change['column'];
    if (!isset($approved[$key])) failCheck('Changed open not reported by targeted sniff');
    $close=$pairs[$index] ?? null;
    if ($close===null || !isset($changes[$close]) || $changes[$close]['before']!=='}') failCheck('Changed bracket pair mismatch');
    $offsetPairs[]=['open'=>$change,'close'=>$changes[$close]];
    $consumed[$index]=true; $consumed[$close]=true; unset($approved[$key]);
}
if (count($consumed)!==count($changes) || $approved || !$offsetPairs) failCheck('Unpaired/uncovered/no changes');
echo json_encode(['before_sha256'=>hash('sha256',$before),'after_sha256'=>hash('sha256',$after),
    'token_count'=>count($a),'unchanged_protected_tokens'=>$protected,'changed_bytes'=>count($changes),
    'offset_pairs'=>$offsetPairs,'all_other_bytes_tokens_identical'=>true],JSON_THROW_ON_ERROR),"\n";

# Claude — revisão local independente do protótipo HELD XML lifecycle

Executor/revisor: Claude CLI (Opus 5.5). Escopo: somente local; sem VM/SSH/PHP/rede/credenciais; nenhuma edição de patch/fonte.

## Execução
| Caso | Comando | Exit | Resultado |
|---|---|---|---|
| test_held.py (7) | `python3 -m unittest -v tools/php83/xml-lifecycle-fix/test_held.py` | 0 | 7 OK (rebuild + GNU patch em tempdir) |
| test_observation.py (15) | `cd tools/php83/xml-lifecycle-fix && python3 -m unittest -v test_observation` | 0 | 15 OK |

Evidência: `claude-held-tests.{stdout,stderr,exit}`, `claude-held-obs-tests.{stdout,stderr,exit}`.

## Confirmações
- Manifest: exatamente 2 `modify` (kConf.php, kSoapClient.php) + 1 `add` (kXmlEntityLoaderPolicy.php); `selected_in_artifact:false`; base = pin exp11, não o exp12 selecionado.
- `candidate/kXmlEntityLoaderPolicy.php` idêntico ao do candidate-tree.
- `capability-native83.stdout` (PHP 8.3.6, libxml 2.9.14): 5 identidades (closure, named, static-array, invokable, null) com `strict_identity:true`, `setter_return:true`; `original_restored_identity:true`; diagnostics vazio. Somente identidade nativa de callable — não comportamento de parser/aplicação.

## Revisão de segurança (estática)
- Deny próprio → `$previous` salvo somente quando o getter é exatamente o deny do helper; loader restritivo estrangeiro permanece ativo. OK.
- Tokens `stdClass` opacos, estado privado, LIFO verificado; mismatch → fail-closed. OK.
- `installDefaultDeny` idempotente; recusa dentro de scope e recusa sobrescrever loader estrangeiro. OK.
- `finally` nas 3 entradas (construct/`__call`/`__soapCall`); SoapFault e falhas de cleanup encadeiam primário em `previous`; nested restaura corretamente (inner não possui wrappers já presentes). OK.
- Cleanup com mutação estrangeira/falha → deny + remoção de wrappers possuídos + RuntimeException visível. OK.
- Wrappers: registro existente/custom preservado; remove só nomes restaurados pelo scope; unregister de startup em kConf inalterado. Mutação de mesmo esquema no meio do scope é exclusão conhecida.
- `__soapCall` continua sem repassar options/headers (comportamento original preservado intencionalmente). `: mixed` compatível com tipos tentativos do SoapClient no 8.x (quebra PHP 7 — intenção conhecida).

## Achados (nenhum bloqueador)
1. MENOR — rollback de setup parcial com diagnóstico enganoso: no caso normal (deny instalado), se `stream_wrapper_restore('https')` falhar após `http`, o getter ainda é deny ≠ `active`, então `endSoapScope` lança "Foreign XML loader mutation" e cai em `failClosed`. Estado final é seguro (deny, `http` removido, primário encadeado), mas a mensagem é falsa e `failClosed` limpa também scopes externos (externos então falham LIFO → deny, visível). Correção mínima: no catch de `beginSoapScope`, se o loader ainda não foi trocado, remover os wrappers possuídos e `array_pop` diretamente em vez de passar pela verificação de `active`.
2. INFO — `failClosed` com `$primary` presente guarda a causa de cleanup só no texto da mensagem, não na cadeia. Aceitável.
3. INFO — durante o scope, parsers não-SOAP do mesmo request veem o loader liberado (documentado: não isolamento).

## Limitações / não testado
Nenhuma execução PHP nesta revisão. scope-probe (12 casos) e behavior (13 casos) são apenas preparação; nenhuma afirmação nativa de comportamento. Revisão não é evidência de execução. Gates de release/cutover inalterados.

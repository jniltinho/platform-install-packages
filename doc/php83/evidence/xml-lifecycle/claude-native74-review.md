# Repetição independente baseline74 — xml-lifecycle (collect-private-r2)

Executor/revisor: Claude CLI (claude-opus-5-5). Ambiente: baseline74 (PHP 7.4.33, libxml 2.9.14, error_reporting 32767).

| # | Comando | Exit | stderr |
|---|---|---|---|
| 1 | runtime-identity.py → claude-native74-before.json | 0 | vazio |
| 2 | collect-private-r2.py 74 /tmp/php-xml-lifecycle-private-prep-r4 → claude-native74-matrix.json | **1 (esperado)** | vazio |
| 3 | runtime-identity.py → claude-native74-after.json | 0 | vazio |

Capturas brutas: `claude-native74-cmd{1,2,3}.{command,stdout,stderr,exit}`.

## Comparação
- Matriz byte-idêntica a `private-r2-primary74.json`.
- Runtime before == after; ambos byte-idênticos a `private-r2-runtime74-{before,after}.json`.
- Manifesto de estágio `identities.json` = `09db0fb1…570b` (inalterado); probe.php do estágio == tools (`a28c3ba1…`); collector `00169cb2…`.
- Handler do probe: registra diagnóstico e `return false` (handler nativo também roda); E_ALL (32767).

## 4 falhas estritas (FAIL preservado, sem waiver)
22 processos exit 0; 18 contratos aceitos; 4 FAIL "native warning retention":
- **construct-missing** (original, exp11): stdout captura warning do observer (DOMDocument::loadXML) e do SoapClient construct; stderr nativo só mostra o warning do probe.php:29 — o warning do SoapClient não aparece no stderr nativo.
- **nested-construct** (original, exp11): stdout captura notices `stream_wrapper_restore … never changed` (kSoapClient.php:27); stderr nativo mostra warnings `stream_wrapper_unregister` (linhas 34/35), não os notices capturados. http/https ficam desregistrados após a operação.

## Achados de cleanup (separados das falhas estritas)
- callback-existing: aceito, 0 diagnósticos; marker visível após kConf; relação de política não adjudicada; http/https permanecem desregistrados.
- explicit-fault: aceito; `existing_exception_cleanup_flaw_observed=true`.
- nested-call-ok/fault: aceitos (8/5 diagnósticos); `nested_outcome_not_security_approval=true`; wrappers permanecem desregistrados.

## Prova primitiva (não é aceitação nativa)
- `test_private.py`: 36 testes OK. `bash -n run-private-r2.sh`: exit 0.
- `prepare-private.file_hash` aceita as 55 entradas exatas `{resolved_path, sha256}` do snapshot74 (sem falso drift) e rejeita chaves faltantes/extras e hash maiúsculo.

## Limitações
Revisor único (sem revisão cruzada entre CLIs); sem transporte real; nenhum patch de aplicação selecionado; harness não prova aceitação da aplicação; native83 não executado.

# Claude native83 repeat — xml-lifecycle private matrix

Executor: Claude CLI (Opus 5.5), serial, native83 exclusivo. Reviewer: mesma sessão (não independente da execução).

| # | Comando | Exit | stdout |
|---|---|---|---|
| 1 | `python3 doc/php83/evidence/exp10-runtime/snapshot-php83.py doc/php83/evidence/xml-lifecycle/claude-native83-before.json` | 0 | `{"files": 39, "modes": 2}` |
| 2 | `PYTHONDONTWRITEBYTECODE=1 python3 tools/php83/xml-lifecycle/collect-private.py 83 /tmp/php-xml-lifecycle-private-prep-r2 doc/php83/evidence/xml-lifecycle/claude-native83-matrix.json` | 1 | `{"status": "FAIL_RETAINED_OBSERVATIONS", "processes": 22, "failures": ["original/construct-missing", "original/nested-construct", "exp11/construct-missing", "exp11/nested-construct"]}` |
| 3 | `python3 doc/php83/evidence/exp10-runtime/snapshot-php83.py doc/php83/evidence/xml-lifecycle/claude-native83-after.json` | 0 | `{"files": 39, "modes": 2}` |

stderr dos três comandos: vazio. Arquivos: `claude-native83-cmd{1,2,3}.{stdout,stderr,exit}`.

## Verificações
- Stage manifest `identities.json` = c360a943…734e, intocado (hash da árvore prep idêntico antes/depois).
- Snapshot runtime before == after (byte-idêntico, sha 83b656a2…).
- Matriz byte-idêntica a `private-primary83.json` (sha 3e5382b2…; diff recursivo 0).
- PHP 8.3.6, libxml 2.9.14, error_reporting 32767. 22 processos exit 0; 18 validações aceitas; 4 FAIL.

## 4 falhas estritas (preservadas) — `native warning retention`
- original|exp11 `construct-missing`: handler capturou `SoapClient::__construct(): I/O warning : failed to load external entity ".../missing.wsdl"` (E_WARNING); ausente do stderr nativo.
- original|exp11 `nested-construct`: handler capturou 2× E_NOTICE `stream_wrapper_restore(): http(s):// was never changed` (nested-resolver); ausentes do stderr. Os E_WARNING `stream_wrapper_unregister` estão presentes em ambos os canais.

Handler (probe.php:14-18) retorna false; E_ALL + display_errors=stderr. Causa da não-impressão nativa não determinada. Sem waiver, sem stderr inventado.

## Achados separados (não são as falhas estritas)
- callback-existing: callback pré-existente sobrevive ao kConf (marker visto após kConf); relação com política não adjudicada.
- Cleanup em exceção: construct-malformed e explicit-fault deixam wrappers http/https e loader reabilitados após SoapFault (flaw observado, ambas variantes).
- Nested: nested-call-ok/fault marcados `nested_outcome_not_security_approval`; notices de restore “never changed”.

## Limitações
Fixtures sintéticas; sem transporte real; sem baseline74; snapshot não prova bibliotecas mapeadas; reviewer = executor; passar o harness não é aceitação da aplicação.

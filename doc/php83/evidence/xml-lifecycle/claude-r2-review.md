# Claude — revisão LOCAL r2 (correções F1–F3) xml-lifecycle

Executor/revisor: Claude CLI (claude-opus-5-5). Sem VM/SSH/rede/PHP/pacotes, sem edição de fontes/ferramentas/doc. Revisão original (`claude-review.md`/`.json`, CLI inicial exit 124) preservada intacta. Nenhum resultado nativo PHP/SOAP é afirmado.

## Comandos

| id | comando | exit | resultado |
|---|---|---|---|
| tests | `PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -m unittest discover -s tools/php83/xml-lifecycle -p 'test_*.py' -v` | 0 | Ran 30 tests, OK (`claude-r2-tests.*`) |
| bash-n | `timeout 10 bash -n tools/php83/xml-lifecycle/run.sh` | 0 | stdout/stderr vazios (`claude-r2-bashn.*`) |

Hashes de entrada antes == depois: `claude-r2-inputs-{before,after}.sha256`.

## Verificação das correções

- **F1 — RESOLVIDO (preparação).** Marker continua permitido pelo callback sintético (`probe.php` allow-list). `collect.validate` só exige `not ev[1].marker_seen` fora de `CALLBACK_CASES`; para callback-existing/nested-construct a exposição após kConf é registrada como observação (`callback_observer_marker_after_kConf`, `callback_policy_relation_unadjudicated=true`), não como expectativa universal de bloqueio. `resolver_events` agora carregam `phase`; alcance SOAP exige system ID good.wsdl/inner.wsdl/types.xsd em fase que não começa com `observer:`. Testes `test_callback_observer_does_not_prove_soap`, `test_wsdl_called_by_observer_not_enough`, `test_callback_policy_outcomes_are_observed` (ambos os valores) cobrem isso.
- **F2 — RESOLVIDO.** `captureState()` e o resolver aninhado salvam/restauram `$phase` em `finally` (2 ocorrências, verificadas por `test_phase_restore_and_trace`).
- **F3 — RESOLVIDO (sintético).** `test_all_synthetic_case_families` percorre 11 casos × {original, exp11} × {74, 83}, incluindo POSITIVE (result/transport_events), nested-* e callback; mais testes negativos por família.

## Achados residuais

- **R1 [LOW]** callback-existing/nested-construct exigem `callback_same is True` quando `libxml_get_external_entity_loader` existe (8.3). É expectativa pré-registrada rígida; se kConf substituir o callback, o caso vira FAIL retido (observação honesta, não bloqueia).
- **R2 [LOW]** Que ext/soap chame o loader userland para WSDL/XSD é inferência estática; se não chamar, callback cases falham com evidência retida — aceitável para observação limitada.
- **R3 [INFO]** nested-construct não tem expectativa de exceção/estado final (intencional: "not security approval"). F4–F7 originais permanecem como registrados.

## Veredito

Nenhum defeito BLOQUEANTE remanescente para **observação nativa limitada** (22 processos por runtime) desta preparação. Isto NÃO é aceitação de candidato/patch nem prova de aplicação. Matriz nativa, execução independente e snapshots de runtime: NOT_EXECUTED.

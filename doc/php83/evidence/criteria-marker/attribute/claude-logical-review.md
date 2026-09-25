# Claude — revisão e execução do snapshot lógico (criteria-marker/attribute)

Executor/revisor: Claude CLI (Opus 5.5). Sem edições de código-fonte.

## Revisão (logical.php, logical-collect.py, logical-compare.py, logical-run.sh, logical-verify.py, test_logical.py, collect.runtime_identity)
Sem bloqueadores. Pontos confirmados:
- `logical.php`: `get_mangled_object_vars` (todas as visibilidades), tipos explícitos, float em IEEE754 hex, ordem de arrays preservada, somente propriedades de objeto ordenadas (`ksort`), aliases de objeto via `spl_object_id`, limites de budget/profundidade, `allowed_classes` restrito.
- `logical-run.sh`: allowlist de hostname/variante, pin de 64 hex fornecido pelo host pai, verificação antes/depois (trap), sandbox systemd (nobody, sem rede/sockets, ProtectSystem=strict, bind somente leitura).
- `logical-collect.py`: `mkdir` falha se o stage existir (stage novo), chown root + a-w, hashes dos stages lógico e de origem verificados antes/depois, `runtime_identity` comparado com o primary revisado e antes/depois.
- `logical-compare.py`: inventário exato de 3 modos/7 payloads, validação da identidade de saída e do hash de entrada, igualdade tipada entre os modos; paridade de bytes brutos registrada separadamente.
Não bloqueadores: `logical-identities.json` é gravado sem o guard de "já existe" (só `logical-primary.json` tem esse guard); o compare usa o rótulo de strict-FAIL como constante, sem afirmar que existe ao menos uma divergência de bytes (o resultado abaixo mostra que existe).

## Execuções
| Caso | Comando | Exit | Evidência |
|---|---|---|---|
| Testes unitários | `python3 -m unittest discover -s tools/php83/criteria-marker/attribute -v` | 0 (23 testes OK) | claude-logical-tests.log/.exit |
| Sintaxe | `bash -n logical-run.sh` | 0 | claude-logical-bash.log/.exit |
| Coleta nos labs | `python3 tools/php83/criteria-marker/attribute/logical-collect.py` | 0 | claude-logical-command.log/.exit, logical-primary.json, logical-*.stdout/.stderr/.exit |

## Resultado
- Status: `BOUNDED_TYPED_VALUES_MATCH_STRICT_LAYOUT_FAIL_RETAINED`; processos original74/original83/attribute83 com exit 0.
- Estado lógico tipado idêntico nos 3 modos para os 7 payloads.
- Paridade de bytes brutos (reserialização == entrada): original74 7/7, original83 4/7, attribute83 4/7 → o strict FAIL continua válido.

## Limites
Não houve seleção de attribute, nem aceitação do cache completo ou da aplicação. A identidade/ciclos de referências em arrays não foram testados. A ordem das propriedades de objeto foi ignorada de propósito. Corpus limitado a 7 payloads. Sem SQL, produção, caches ou reescrita de fonte. A liberação dos labs fica com o coordenador.

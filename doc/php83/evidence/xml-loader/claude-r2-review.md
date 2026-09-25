# Revisão de correções r2 — harness nativepolicy do xml-loader (Claude CLI)

**Veredito:** READY_FOR_BOUNDED_NATIVE_EXPERIMENT, sem achados bloqueantes. Execução só local; PHP/VM/SSH/rede: **NOT_EXECUTED**. Este documento **não** afirma PASS de runtime nem aceitação de aplicação. Detalhes: `claude-r2-review.json`.

## Execuções
| Caso | Comando | Exit | Resultado |
|---|---|---|---|
| unit | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/xml-loader -p 'test_*.py' -v` | 0 | 26 OK (`claude-r2-tests.log`) |
| bash | `bash -n tools/php83/xml-loader/run.sh` | 0 | `claude-r2-bash.log` vazio |
| mutações | `claude-r2-mutations.py`, só em memória | 0 | `claude-r2-mutations.log` |

As linhas `{"status": "FAIL", ...}` que aparecem no log de unit vêm dos testes sintéticos de OSError e de timeout. Elas são esperadas.

Os hashes congelados (`claude-r2-hashes-before.txt`) batem todos depois da execução (`claude-r2-hashes-after.txt`, exit 0). Nenhum `__pycache__` foi criado e nenhum arquivo do autor foi editado.

## Achados anteriores
- **F1 corrigido:** um runtime ou uma row que não seja dict agora gera ValueError. `main()` captura ValueError, TypeError, KeyError, AttributeError, OSError e TimeoutExpired. Nos dois últimos casos os 12 registros são mantidos, com stdout e stderr parciais e `incomplete`, e o JSON é gravado com FAIL.
- **F2 corrigido:** em legacy/deny, qualquer `wrapper_events` é rejeitado, assim como o marker em value, diagnostics ou exception.
- **F3 corrigido:** `exception` precisa ser um dict `{class,message}` com valores str. As listas de diagnostics têm campos estritos, e severity/line precisam ser int>0; bool é rejeitado.
- **F4 corrigido:** o `policy_return` é verificado para cada política. No 8.3 com enabled/legacy é exigido exatamente um E_DEPRECATED (8192) de `libxml_disable_entity_loader`, e nenhum nos demais casos. Cada mensagem de diagnóstico precisa aparecer no stderr nativo.
- **F5 corrigido:** cada um dos 3 canaries é mutado individualmente, e há testes para F1–F4.

## Mutações próprias
Rejeitadas: chave extra em exception, wrapper event sob deny, marker em diagnostic sob legacy, mensagem de deprecação vazia e severity bool.

Aceitas, sem bloquear:
- **N1 (baixo):** uma row malformed com `exception={'class':'','message':''}` e sem diagnostics é aceita.
- **N2 (baixo):** a retenção de stderr usa busca por substring, então uma mensagem vazia sempre passa.
- **N3 (info):** o marker em IDs de `loader_calls` não é verificado. São URIs, não conteúdo.
- **N4 (info):** um marker ofuscado passa. Validação exaustiva contra JSON malicioso está fora do escopo.

## Limitações
- O retorno `True` do registro sob deny e a semântica de bloqueio legacy no 8.3 só se decidem nativamente. Um FAIL nativo nesses pontos é resultado do experimento, não defeito do harness.
- As limitações r1 continuam em aberto: BindReadOnlyPaths/ProtectHome, `set -u` com array vazio e Python ≥3.9 nos labs.
- Não há cobertura de aplicação (kConf/kSoapClient).

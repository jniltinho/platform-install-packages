# Revisão independente de preparação local — xml-loader (Claude CLI)

**Status:** LOCAL_PREP_REVIEW_COMPLETE_WITH_FINDINGS. PHP/VM/SSH/rede: **NOT_EXECUTED**. Nenhum PASS nativo/runtime é afirmado. Detalhes e hashes: `claude-review.json`.

## Execuções (exits preservados em `claude-review-*.{stdout,stderr,exit}`)
| Caso | Comando | Exit |
|---|---|---|
| unit-tests | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/xml-loader -p 'test_*.py' -v` | 0 (14 OK, só Python sintético) |
| bash-syntax | `bash -n tools/php83/xml-loader/run.sh` | 0 |
| local-prepare | `python3 tools/php83/xml-loader/prepare.py /tmp/xml-loader-claude-prep` | 0; manifest `257e1dac…a04ec`; 4 arquivos batem com o manifest; probe.php/run.sh = fontes congeladas; sem staging na VM |
| validator-gap-probe | `collect.validate` em fixtures mutados (sem PHP) | 0; saída em `claude-review-validator-probe.txt` |

Os hashes dos 7 inputs congelados são idênticos antes/depois; nenhum `__pycache__` foi criado.

## Achados
- **F1 (médio, bug):** um `runtime` ou uma row que não seja dict gera `AttributeError`, e `main()` só captura `ValueError`/`TimeoutExpired`. Um único corpo malformado aborta os 12 processos antes de gravar o JSON de saída, e a evidência dos processos anteriores se perde. `OSError` do ssh também não é capturado.
- **F2 (médio, escopo falso-positivo):** sob legacy/deny, o bloqueio só é checado por `marker_seen` no `value`. Um `wrapper_events` com open/stat de `xfixture://marker`, ou o marker aparecendo em diagnostics, é **aceito**.
- **F3 (baixo, tipagem):** `exception` não tem tipo checado; uma string qualquer satisfaz a exigência de diagnóstico para malformed. O tipo de `policy_diagnostics` também não é checado (uma string é contada pelo len), e as entradas de diagnostics não são validadas.
- **F4 (baixo, retenção de warnings):** `policy_return` e o E_DEPRECATED esperado no 8.3 para enabled/legacy não são afirmados. O stderr é capturado mas não verificado.
- **F5 (info, cobertura):** o teste de canary ausente só muta `file`, e não há testes para F1–F4.

## Verificado OK (inspeção estática)
- 4 políticas × 3 parsers, cada um em processo isolado.
- 6 docs × 7 flags = 42 linhas por processo, com ordem e ints exatos (504 por runtime).
- Rejeição de linha ausente/duplicada e de substituição bool/int.
- Canary positivo no enabled por parser e callback obrigatório no deny.
- Fixtures sintéticos e wrapper em memória, sem URL remota.
- Sandbox systemd sem rede/socket, `open_basedir` e `allow_url_fopen=0`.
- O handler retorna false e não há supressão via @/NOERROR.

## Limitações
- Não verificado nos labs: BindReadOnlyPaths com ProtectHome=yes, array vazio com `set -u` no bash e Python ≥3.9 (`is_relative_to`).
- Leituras `file://` só são observáveis pelo valor.
- Sem cobertura de aplicação (kConf/kSoapClient).
- Não recomendo remover chamadas de segurança sem testes reais de aplicação.

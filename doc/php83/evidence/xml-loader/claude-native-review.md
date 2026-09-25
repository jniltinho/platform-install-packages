# XML loader — repetição nativa independente (Claude CLI)

- **Caso:** repetição da matriz congelada de native policy (baseline74 + php83), serial, via SSH aprovado.
- **Executor:** Claude CLI (claude-opus-5-5). **Revisado contra:** `primary74.json` / `primary83.json` (execução do autor).
- **Veredito:** `PASS_BOUNDED_NATIVE_POLICY_REPEAT` — somente native policy; **não** cobre kConf, kSoapClient nem aplicação.
- Detalhes legíveis por máquina: [claude-native-review.json](claude-native-review.json).

## Execução (serial, todos exit 0)

| # | Comando (`PYTHONDONTWRITEBYTECODE=1`) | Exit | Saída |
|---|---|---|---|
| 1 | `python3 tools/php83/exp11-api/runtime-identity.py …/claude-native-runtime74-before.json` | 0 | sha `a7c9a22f…` |
| 2 | `python3 tools/php83/xml-loader/collect.py 74 /tmp/php-xml-loader-prep-r1 …/claude-native74.json` | 0 | 12 processos / 504 linhas |
| 3 | `runtime-identity.py …/claude-native-runtime74-after.json` | 0 | sha `a7c9a22f…` |
| 4 | `python3 doc/php83/evidence/exp10-runtime/snapshot-php83.py …/claude-native-runtime83-before.json` | 0 | sha `83b656a2…` |
| 5 | `collect.py 83 /tmp/php-xml-loader-prep-r1 …/claude-native83.json` | 0 | 12 processos / 504 linhas |
| 6 | `snapshot-php83.py …/claude-native-runtime83-after.json` | 0 | sha `83b656a2…` |

Comando exato, exit, stdout e stderr de cada passo: `claude-native-<passo>.{cmd,exit,stdout,stderr}`.

## Comparações

- `claude-native74.json` e `claude-native83.json` são **byte-idênticos** a `primary74.json` / `primary83.json`.
- As 4 identidades de runtime são byte-idênticas às do primary (`runtime{74,83}-{before,after}.json`), e before == after por lab.
- Ferramentas locais batem com `harness-frozen.json`; hashes de `tools/php83/xml-loader/*` e `/tmp/php-xml-loader-prep-r1/*` iguais antes/depois (`claude-native-hashes-{before,after}.txt`).
- O `run.sh` verifica o manifesto/fixtures no início e no trap de EXIT (exit 70 em caso de drift); os 24 processos saíram com 0.

## Contadores (por runtime, iguais em 74 e 83)

- Marcador exposto: `enabled` 32, `default` 32 (12 DOM / 12 SimpleXML / 8 XMLReader), `legacy` 0, `deny` 0.
- Linhas com NONET: 9 leituras locais do marcador em `enabled` e em `default`, 0 em `legacy`/`deny`. NONET não bloqueia a leitura local.
- Exceções: 0. Falhas: nenhuma.
- Diagnósticos mantidos, sem supressão: stderr não vazio em 12/12 processos (warnings do libxml). No 8.3, os 6 processos `enabled`/`legacy` registram E_DEPRECATED `libxml_disable_entity_loader()` em `policy_diagnostics` e no stderr; no 7.4 não há nenhum.

## Preparação

Os findings iniciais F1–F5 foram corrigidos e verificados localmente em [claude-r2-review.json](claude-r2-review.json) (26 testes OK, `READY_FOR_BOUNDED_NATIVE_EXPERIMENT`).

## Limitações

Somente native policy do PHP/libxml na matriz congelada. Não há evidência de kConf, kSoapClient ou cobertura/aceitação da aplicação. Nenhum experimento fora da matriz. Sem escrita no `.20`, backend ou stages.

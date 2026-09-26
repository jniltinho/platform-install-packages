# Claude — callback-throw chain (native83) — revisão + execução

- **Caso:** `callback-throw` × {baseline, candidate}. Nenhum outro caso nativo.
- **Executor:** Claude CLI (claude-opus-5-5), em foreground. **Revisor:** o próprio Claude fez a pré-revisão do delta; ainda falta revisão independente por outra CLI.
- **Veredito:** `CHAIN_CAPTURED_NOT_PRODUCT_ACCEPTANCE`. Não é aceitação de produto; nenhum byte de produto foi alterado.

## Pré-revisão (nenhum bloqueio)
- `behavior-chain.php` vs `behavior.php`: o delta traz apenas a cadeia de `normalizeException` (profundidade < 32 e `chain_truncated`), a captura do objeto `RuntimeException` real antes do `throw` e a chave de saída `resolver_exceptions`.
- Prep `/tmp/...-chain-prep-r1` vs `/tmp/...-prep-r1` congelado: diferem apenas `behavior.php`, `run-native.sh` (diretório base e phase) e `identities.json` (phase e 2 hashes). São 21 arquivos, sem drift e sem arquivos fora do manifesto. O prep congelado também está sem drift.
- `bash -n` no `run-native.sh` novo = 0.
- Observações: o collector exige exatamente 1 exceção de resolver por variante, o que é conservador. O diretório remoto `/home/vagrant/php-xml-lifecycle-fix-chain-r1` permanece, somente leitura.

## Execução serial (exit)
| # | comando | exit |
|---|---|---|
| 1 | stage-chain.py → claude-chain-stage | 0 (ssh remoto 0, stdout/stderr vazios) |
| 2 | snapshot → claude-chain-before.json | 0 |
| 3 | collect-chain.py → claude-chain-matrix.json | 0 (`records:2, failed:false`) |
| 4 | snapshot → claude-chain-after.json | 0 |

O tempo total foi de ~2 s. Manifesto `5feb0063…8017`, collector `f3f70bde…9173099`.
Os snapshots before e after são byte a byte iguais (`83b656a2…9491`) e iguais a primary-runtime-before/after.

## Resultado causal (baseline = candidate)
- **Exceção lançada pelo resolver:** `RuntimeException("SYNTHETIC_LOADER_FAILURE")`, fase `operation:construct`, cadeia de tamanho 1.
- **Exceção resultante:** `SoapFault("SOAP-ERROR: Parsing WSDL: Couldn't load from 'file:///audit/probe/fixtures/good.wsdl'")`. Cadeia de tamanho 1, `getPrevious()` = **null**. A RuntimeException **não** fica retida como previous.

## Estado fora do bloco
| fase | baseline http/https · callback_same · marker | candidate |
|---|---|---|
| before-kConf | true · true · true | true · true · true |
| after-kConf | false · true · true | false · **false** · **false** |
| operation:construct | resolver do chamador chamado, wrappers true | igual |
| after-operation | **true** · true · true (restaurado) | **false · false · false** (não restaurado) |

- Na candidate, fora do bloco, fica instalado um loader que não é o do chamador. Isso gerou 2 E_WARNING "resolver function returned null" nas fases de observer.
- A baseline emite 4 E_DEPRECATED (`libxml_disable_entity_loader` ×2 e tipos de retorno de `kSoapClient` ×2). A candidate não emite nenhum deles.

## Limitações
- Somente callback-throw foi executado. O relatório de 38 casos com 2 FAIL ficou intocado.
- Harness sintético: sem bootstrap completo e sem transporte real.
- Não julguei se o estado da candidate fora do bloco é intencional.

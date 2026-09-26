# Repetição nativa independente — heldA r1 (Claude)

- **Caso:** xml-lifecycle-held-A-r1, native83, 38 processos. **Executor:** Claude CLI (claude-opus-5-5). **Revisor:** o mesmo (auto-revisão; NÃO é revisão independente).
- **Janela:** 2026-09-26T17:07:46Z → 17:07:58Z. **Ambiente:** VM php83 (PHP 8.3.6, libxml 2.9.14), stage remoto `/home/vagrant/php-xml-lifecycle-fix-r1`.
- **Identidades:** manifest pin `c06f54b7…d742a08` (confere); árvore local do stage `f926d12c…a107` (22 arquivos) idêntica antes/depois; collector `7837a803…2e20`; snapshot tool `ec8f5473…b429`.

| Passo | Comando | Exit | stdout |
|---|---|---|---|
| 1 | snapshot-php83.py → claude-native-before.json | 0 | `{"files": 39, "modes": 2}` |
| 2 | collect-native.py → claude-native-matrix.json | 1 | `FAIL_RETAINED_OBSERVATIONS`, 38 processos, 2 falhas |
| 3 | snapshot-php83.py → claude-native-after.json | 0 | `{"files": 39, "modes": 2}` |

stderr vazio nos três passos. Captura bruta: `claude-native-step{1,2,3}.{stdout,stderr,exit}`.

## Contagens
38 processos nativos, 0 com exit≠0; 36 `functional_checks: PASS_BOUNDED`; 2 FAIL retidos; 5 registros com diagnósticos só do handler. `diagnostic_inventory: PENDING_INDEPENDENT_ADJUDICATION_NOT_WAIVED`, `acceptance: false`.

## Comparação com o primary
`claude-native-matrix.json` é byte-idêntico a `primary.json` (sha256 `46f65f9b…ffed`), 38/38 registros iguais. Snapshots de runtime primary-before = primary-after = claude-before = claude-after (sha256 `83b656a2…9491`).

## FAIL retido (não alterado)
`behavior/baseline/callback-throw` e `behavior/candidate/callback-throw`: o harness espera `RuntimeException` (collect-native.py:28); o observado é o `SoapFault` nativo `SOAP-ERROR: Parsing WSDL: Couldn't load from 'file:///audit/probe/fixtures/good.wsdl'`. Contrato e produto não foram alterados, nada foi forçado para OK.

**Achado causal — confirmado conforme o observado:** o callback lança exceção em fases que não são de observer (behavior.php:45); `resolver_events` registra `operation:construct` para good.wsdl nas duas variantes (o evento é gravado antes do throw), então o lançamento foi alcançado, e o ext/soap devolveu `SoapFault` como exceção de topo. **Não estabelecido:** se a `RuntimeException` fica como `getPrevious()` nesse caminho — NÃO REGISTRADO (behavior.php:36 captura só class+message).

**Evidência de cadeia em escopo separado:** `scope/candidate/primary-exception-chain` → `RuntimeException` "XML scope cleanup failed; LogicException: Foreign XML loader mutation inside a SOAP scope", com previous = `SoapFault` "SYNTHETIC_PRIMARY_SOAPFAULT". Só helper, com falha sintética; não se aplica ao caminho de callback-throw do behavior.

## Observações de restauração (sem adjudicação)
Estado after-operation (http, marker_seen, callback_same): baseline callback-throw = (1,1,1); candidate = (0,0,0), igual a todos os outros casos candidate (loader de política instalado, wrappers desligados). O baseline reabilita http/https após a operação em todos os casos de SoapFault (construct-malformed, construct-missing, explicit-fault, callback-deny, callback-throw), mas não nos casos de sucesso. Fica registrado apenas como observação; não foi decidido se é intencional ou defeito.

## Limitações e lacunas
- A saída idêntica mostra que os probes não emitem nonce/timestamp/pid; a prova de execução está nos novos arquivos criados com recusa de sobrescrita, nos 38 subprocessos ssh em 12 s e nos exits capturados, não em diferença de conteúdo.
- A imutabilidade do stage remoto foi verificada só indiretamente (identidades do manifest + snapshot); não foi tirado hash da árvore remota.
- Auto-revisão: ainda é preciso revisão independente por outra CLI.
- Harness limitado: sem bootstrap completo da aplicação e sem transporte real. 36 checks passando não significam aceitação da aplicação.
- Os FAILs anteriores (os 2 estritos e os 8 mais antigos) continuam preservados e não foram tocados.
- Não executado: baseline74, download de rede, install, SQL, patch de fonte, mudanças no stage.

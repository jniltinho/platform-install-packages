# Claude review local independente — fase private SOAP provider (r1)

Executor/revisor: Claude CLI (Opus 5.5). Somente local: sem SSH/VM/PHP/rede/carregamento de módulo. Nenhum source revisado foi modificado.

## Comandos e resultado
1. `PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 tools/php83/xml-lifecycle/test_private.py` → **exit 1**: `Ran 35 tests`, `FAILED (errors=1)` (34 ok). Evidência: `claude-private-tests.{stdout,stderr,exit}`.
2. `bash -n tools/php83/xml-lifecycle/run-private.sh` → **exit 0**. Evidência: `claude-private-bashn.{stdout,stderr,exit}`.

## Veredito: BLOCKED antes do primeiro load de módulo

### Defeitos bloqueantes
- **B1 (suíte de testes)**: `test_oserror_retained` (herdado de `test_prepare.py`) falha com `ValueError: explicit private provider phase` em `collect-private.py:97`. A fixture base não tem `phase`/`providers.json`; a checagem de phase fica fora do `try` e produz traceback (fail-closed, mas não `SystemExit`). O critério "35 testes passando" não foi atingido. Ajustar fixture herdada (phase+providers.json) ou o contrato; não afrouxar o guard.
- **B2 (identidade do report 83)**: `provider83-extraction.json` não possui o campo `authentication`, que o `provider-inspect.py` atual sempre emite → o report foi gerado por uma versão anterior do script, não pelo source revisado. A autenticação 83 em si está evidenciada (step `gpgv --status-fd` exit 0 com o keyring do Ubuntu), mas o vínculo source→report precisa ser registrado explicitamente ou regenerado.

### Não bloqueantes / limites
- **APT 74**: config APT isolada, `sourcelist` = cópia do único `*ondrej*` existente, exigindo `Signed-By:` e ausência de `trusted=yes`; flags de insecure/unauthenticated em false; sem waiver de gpgv2. OK. Limite: `keyring_sha256` (74) é o hash do arquivo `.sources`, não do arquivo de chave referenciado por `Signed-By` (se for um path); o conteúdo do Signed-By não é comparado a um valor fixado. Rotular corretamente.
- **Hashes/versão/ABI**: os reports batem com os pins do script (74: `1:7.4.33-30…`, `f25c5a83…`, ABI 20190902; 83: `8.3.6-0ubuntu0.24.04.11`, `eeb541e1…`, ABI 20230831); SHA256 do Packages verificado contra o InRelease; download com SHA256 fixado. `prepare-private.py` só re-verifica `status`/`abi_directory`, não versão/package_sha256 contra constantes; registra `provider_report_sha256`.
- **Módulo privado/libs**: `run-private.sh` verifica manifest, fixture, interpreter, soap.so, xml/dom(/json) e todas as libs resolvidas antes e no trap EXIT (drift → exit 70); soap.so via `BindReadOnlyPaths`. Limite TOCTOU: o arquivo de origem continua gravável por uid 1000 entre o hash e o load; o bracket pré/pós detecta, não impede.
- **Libs mapeadas**: a prova atual é somente `ldd` (paths resolvidos e hashados). **Não existe prova das libs realmente mapeadas** (ex.: `/proc/<pid>/maps`) — isso é lacuna, não falsa garantia, desde que nenhum report afirme "mapped". O snapshot de runtime fica para depois (`runtime_snapshots_required`).
- **Collector**: fail-closed em phase/providers.json/archives/identidade do stage; não seleciona patch (`application_patch_selected: False`) e mantém os contratos originais de validate.
- **primary74 antigo**: `primary74.exit`=1, classificação `NOT_EXECUTED_APPLICATION_MISSING_SOAP` com `{'65': 22}` — preservado; deve continuar NOT_EXECUTED (application).

Nenhuma alegação de runtime aprovado. Nenhum source novo de aplicação selecionado.

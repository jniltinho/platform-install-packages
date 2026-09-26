# Review de correção r2 do Claude — fase private SOAP provider

Executor/revisor: Claude CLI (Opus 5.5), somente local. Sem SSH/VM/PHP/rede/carregamento de módulo; nenhum source foi editado.

## Comandos
1. `PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 tools/php83/xml-lifecycle/test_private.py`: **exit 0**, `Ran 35 tests … OK` (`claude-private-r2-tests.*`).
2. `bash -n tools/php83/xml-lifecycle/run-private.sh`: **exit 0** (`claude-private-r2-bashn.*`).

## B1: RESOLVIDO
O `private_oserror` só completa a fixture herdada com `phase=private-soap-provider-r1` e `providers.json` (com hash no manifest). As asserções originais continuam iguais (`SystemExit`, 22 records, 22 failures). O guard em `collect-private.py:97-98` não foi afrouxado.

## B2: RESOLVIDO como proveniência real (não é reescrita)
- Os hashes de `provider-provenance.json` batem com os arquivos em disco: report 74 `2965348f…` e 83 `01f3be06…`; sources `3ad3ee15…` (atual) e `ce4a33fd…` (`attempts/provider-r1`).
- Os steps do report 83 são exatamente os do source r1: `gpgv --status-fd` com `ubuntu-archive-keyring` (exit 0), `apt-helper`, `dpkg-deb`, `readelf` e `ldd`. A ausência de `authentication` é coerente com o r1 e não conta como defeito.
- Diff do r1 para o atual: root r2 para 74; APT isolado para 74 (Signed-By existente, sem `trusted=yes`, flags de insecure em false); `gpgv` pulado só para 74; path de `lists`; campo `authentication` adicionado. Fora isso, a lógica do caminho 83 é a mesma.

## Preparação
`prepare-private.py` agora exige versão e `package_sha256` exatos para os dois providers, além de status e ABI. Os reports batem.

## Não bloqueantes
- Em `provider-provenance.json`, o `note` do 74 copia o texto do 83. É só redação: ele deveria descrever o 74 como executado pelo source atual com APT isolado.
- O `keyring_sha256` do 74 é o hash do `.sources`, não de uma chave fixada de forma independente.
- TOCTOU: o bracket pré/pós detecta alterações, mas não as impede.

## Limitações mantidas
- A identidade de módulo e libs vem do bracket de hash pré/pós, não de imutabilidade.
- As libs são só as resolvidas pelo `ldd`; ainda **não há prova das libs realmente mapeadas**.
- O primary74 antigo (22 × exit 65) continua NOT_EXECUTED (application). Ainda não existe callback SOAP 74 exato.

## Decisão
Não resta bloqueio para o **experimento SOAP limitado com source inalterado**. Isto **não** é aceitação nem release. Nenhum resultado nativo ou runtime aprovado é alegado.

# Claude — revisão independente da reconciliação held r2

Executor/revisor: Claude CLI (Opus 5.5). Somente local/offline; nenhuma VM/PHP/rede/edição de fonte/produto/ZIP.

| Comando | Exit | Resultado |
|---|---|---|
| `timeout 60 python3 tools/php83/xml-lifecycle-fix/test_reconcile.py -v` | 0 | 23 testes OK |
| `timeout 60 python3 tools/php83/xml-lifecycle-fix/reconcile.py …/claude-reconcile-result.json` | 0 | `PASS_BOUNDED_HELD_CONTRACT_R2`, 38 casos |
| `cmp reconciliation-r2.json claude-reconcile-result.json` | 0 | idêntico byte a byte |
| `sha256sum` das entradas antes/depois | — | inalteradas (`claude-reconcile-inputs-{before,after}.sha256`) |

Verificado:
- A correção causal limita-se à classe esperada do `callback-throw` (RuntimeException→SoapFault), sustentada por 2 processos instrumentados (baseline e candidate): o RuntimeException lançado está registrado; a cadeia nativa contém apenas SoapFault (previous null, sem truncamento); loaded/runtime/events/resolver_events/functions/result são idênticos aos registros originais.
- Os 38 relatórios originais continuam FAIL com exatamente 2 falhas; não foram reescritos.
- Candidate: 25 processos (13+12) com inventário completo e stderr bruto exato, derivados da política/fixtures; apenas 2 entradas handler-only (SoapClient::__construct); nenhum warning nativo foi filtrado.
- Baseline: 13 comparados ao ledger repetido e inalterado, sem uso como expectativa do candidate.
- Pins do manifest e da referência, exits 0 dos CLIs e 6 snapshots de runtime idênticos.

Bloqueadores: nenhum.
Lacunas não bloqueantes: as mutações cobrem só o registro causal[0] e o `construct-good` do candidate; os guards de arquivo do `main()` não têm testes; o manifest fica no `/tmp`, que é efêmero.
Não é aceitação da aplicação nem seleção de artefato; o suporte do builder a arquivos novos do helper segue pendente.

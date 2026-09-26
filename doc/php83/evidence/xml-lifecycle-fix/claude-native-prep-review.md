# Claude — revisão local do harness native-prep (held A)

Executor/revisor: Claude CLI (claude-opus-5-5), somente local. Sem SSH/VM/PHP/rede/edição de fonte.
Hashes do harness: ver `claude-native-prep-review.json`.

## Execução
| Comando | Exit | Resultado |
|---|---|---|
| `timeout 60 python3 -m unittest test_native -v` | 0 | 12 testes OK (`claude-native-prep-test.{stdout,stderr,exit}`) |
| `bash -n run-native.sh` | 0 | sem erros (`claude-native-prep-bashn.*`) |

## Veredito
**Nenhum bloqueador para a fase de observação nativa guardada.** Não é aceite de release (`acceptance=false`).

Verificado: matriz 38 (13×2 behavior + 12 scope só candidate) coerente com as allowlists do `run-native.sh`; manifest held `selected_in_artifact=false`, exatamente 2 modify + 1 add, pins de source exp11/patch/provider SOAP; verify remoto pinado por sha com rejeição de symlink/escape e hashes de php8.3/soap/xml/dom/libxml2/libs, reverificado no EXIT (drift → 70); sandbox read-only bind, socket/socketpair negados, PrivateNetwork, RuntimeMaxSec 60 < timeout 75; PHP `-n` com E_ALL (32767) nativo; stdout/stderr/exit brutos retidos inclusive em falha e timeout parcial; PASS funcional coexiste com `diagnostic_inventory=PENDING_INDEPENDENT_ADJUDICATION_NOT_WAIVED`. O fixture do teste é um body baseline reetiquetado como candidate: forma sintética, não prova de runtime.

## Notas não bloqueantes
- Falha do verify pós-execução sai 70 e mascara o exit do PHP (saídas retidas).
- Linhas com timeout não têm `exit`: tratar como TIMEOUT.
- O coletor segue a matriz após falha; a fase deve parar na adjudicação, sem rerun/patch até ficar verde.
- `ProtectHome=yes` com bind de `/home/vagrant` não foi provado aqui; falha nativa é achado a registrar, não a contornar.
- Transferência do stage e arquivos extras no VM ficam fora do harness (mitigado pela igualdade exata de `loaded`).
- Sem lock remoto: depende de dono exclusivo do VM.

## Não testado
Os 38 casos nativos (NOT_EXECUTED), adjudicação de diagnósticos (PENDING), bootstrap completo e transporte real.

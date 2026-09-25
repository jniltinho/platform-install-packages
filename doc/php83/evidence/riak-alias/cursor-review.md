# Riak Object alias — independent native83 rejection repeat (Cursor)

- Executor: Cursor Agent (Composer); exclusive `php83` via `/tmp/kaltura-php83-ssh.conf`.
- Escopo: repeat de rejeição bounded; **não** aceitação de aplicação/backend.
- Manifest pin: `7d18f710b12d978e5867b188ad26160222e63ac87cdae1fc3313f832f8fcd217` (14 entradas stage + harness).

## Comandos e exits

| Passo | Exit |
|---|---|
| runtime-before snapshot | 0 |
| `run.sh original` | 255 |
| `run.sh candidate` | 255 |
| runtime-after snapshot | 0 |

## Achados

- Original83: exit 255, stdout vazio, fatal reserved alias linha 26 — match primary.
- Candidate83: exit 255, stdout vazio, fatal `Riak\Object` reserved linha 207 — match primary.
- Reflection/probe checks **não alcançados** (falha de compilação antes).
- Runtime identity before/after: igual entre si e a `runtime83-before/after` root.
- Stage identities (hash independente, O_NOFOLLOW): 14/14, sem drift, manifest pin ok.
- `preparation-frozen.json` local hashes: inalterados before/after.

## Veredito

**candidate REJECTED** (`CANDIDATE_REJECTED_COMPILER_FAILURE`). Repeat valida primary runtime83: `True`. Patch held não selecionado; sem backend_acceptance.

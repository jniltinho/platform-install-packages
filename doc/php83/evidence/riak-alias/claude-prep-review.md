# Riak Object alias — revisão de preparação (Claude)

- Executor/revisor: Claude Code CLI (Opus 5.5), worktree `proposal/migrate-kaltura-php83`, host local (Python 3.12.3, GNU patch 2.7.6).
- Escopo: somente revisão + testes de preparação. **Nenhuma execução de PHP, VM, SSH, rede ou backend Riak.**
- Entrada externa (read-only, autorizada): `/tmp/kaltura-php83-audit/Rigel-18.20.0.zip`, sha256 `58d534d0…b0ab28` (confere com o pin).

## Identidades revisadas (sha256)

| Arquivo | sha256 |
|---|---|
| tools/php83/riak-alias/prepare.py | 2ed327efc7ea6ee94f80a073cc36c564448ad17b4a25a308953bde8e3e778e03 |
| tools/php83/riak-alias/probe.php | db98f85f7460b66405939d64a744e1ef784944bd34c88eae438abc7678f15be0 |
| tools/php83/riak-alias/run.sh | 0ba5a4629057fc70787e585b0da5ce1309e7f57a1008d55ac99684028d7597fa |
| tools/php83/riak-alias/source-pins.json | a89adfc47643efb32f95f0f52a766d7d7baf195eef6eabd484f8662f31c68d0c |
| tools/php83/riak-alias/test_prepare.py | 945f1104e1e33af49664de23d33f1e9f1f74165093e194a68253be8374bd482e |
| patches/php83/held/riak-object-alias/RiakCache-alias.patch | 13af9aa7e254f7e28e7f9a197a8b97eb4dca641f9bc70e416bfcac640880405a (= pin) |

Hashes idênticos antes e depois das execuções; nenhum `__pycache__` criado; `git status` inalterado fora dos arquivos de evidência abaixo.

## Execuções

| Caso | Comando | Exit | Evidência |
|---|---|---|---|
| Testes de preparação | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/riak-alias -p 'test_*.py' -v` | 0 (6/6 OK, 0.381s) | `claude-tests.{stdout,stderr,exit}` |
| Sintaxe shell | `bash -n tools/php83/riak-alias/run.sh` | 0 (sem saída) | `claude-bash.{stdout,stderr,exit}` |

## Achados

**Semântica do patch — OK (estreita).** O original tem exatamente 4 usos de código de `Object`: `use Riak\Object;` (l.26), `new Object($id)` (l.132 e l.243) e `isExpired(Object $object)` (l.207). O patch troca só esses para o alias `RiakObject`; docblocks `\Riak\Object` ficam intactos (comentário). `test_exact_source_delta` reverte exatamente essas grafias e exige igualdade byte a byte com o original, e o pin `candidate_sha256` fixa o resultado. O bug pré-existente `$objectList[count($objectList)]` (off-by-one) é preservado de propósito e verificado — fora de escopo, mas deveria constar como débito conhecido.

**Identidade/preparação — OK.** `prepare.py` recusa stage existente, valida ZIP, patch, cada fonte e o candidato por pin; aplica com `--fuzz=0` e rejeita offset/fuzz; os outros 5 arquivos do candidato precisam ser idênticos ao original. O manifesto (`identities.json`, 14 entradas) não contém o próprio hash; o hash é devolvido ao host (`manifest_sha256`) — modelo correto para pin externo.

**probe.php — OK dentro do alcance declarado.** Carrega a cadeia real completa (`Cache`, `FlushableCache`, `ClearableCache`, `MultiGetCache`, `CacheProvider` — confere com `CacheProvider implements Cache, FlushableCache, ClearableCache, MultiGetCache` no ZIP). Sem stubs de Riak: `class_exists(..., false)` não dispara autoload e `-n` evita carregar a extensão. `newInstanceWithoutConstructor` evita `Bucket`; os métodos chamados (`getNamespace`/`setNamespace`/`getStats` → `doGetStats` retorna `null`) não tocam `$this->bucket`. Saída marca `backend_executed:false` e o prepare marca `backend_acceptance:false`. Tipos são lidos por Reflection como string, sem carregar `Riak\*`.

**run.sh — desenho coerente, não executado.** Allowlist de hostname + uid 1000, hash do manifesto fornecido pelo host (regex 64 hex), verificação antes e no trap `EXIT` (falha pós → 70, rejeita symlink e caminho fora do base), `systemd-run` com `PrivateNetwork`, filtro de `socket`, `ProtectSystem=strict`, `ProtectHome`, bind read-only do stage, `NoNewPrivileges`, limites de memória/tempo, `env -i`, `php -n`, `allow_url_*=0`. Nada escreve na fonte.

## Lacunas / riscos (não bloqueantes para preparação, abertos para execução)

1. **Nenhuma execução de PHP 7.4/8.3 aconteceu nesta revisão.** Não há evidência de que o alias compile, nem de que a sonda produza as linhas esperadas; `bash -n` só prova sintaxe.
2. Sem teste para `run.sh`/`probe.php`; o comportamento do sandbox (ex.: `BindReadOnlyPaths` de `/home/...` combinado com `ProtectHome=yes`, criação de `/audit/probe` sob `ProtectSystem=strict`) só se confirma em execução real na VM.
3. A comparação `loaded_sha256` da sonda × manifesto é responsabilidade do orquestrador; nenhuma ferramenta aqui faz isso.
4. `verify` não rejeita arquivos extras no stage (ex.: `.orig`/`.rej`); a sonda só faz `require` de caminhos fixos, então o impacto é baixo.
5. Binário `patch` resolvido via `PATH` e sem pin; `is_relative_to` exige Python ≥ 3.9 na VM; `"${flags[@]}"` vazio com `set -u` exige bash ≥ 4.4 — versões da VM não verificadas.
6. `preparation.json` (`manifest_sha256 7d18f710…`) não foi reproduzido de forma independente: os testes não afirmam esse valor.
7. **Não é aceitação de backend:** nenhum `Bucket`/`Object` real, nenhuma chamada `doSave`/`doFetch`/`resolveConflict`. Aceitação funcional do RiakCache continua sem teste.

Veredito: preparação e guardas de identidade **PASS** (6/6, exit 0); `bash -n` **PASS**. Execução PHP/sandbox: **NOT_EXECUTED**. Isto é revisão do autor da preparação por um executor diferente, não validação de runtime.

# Continuar a migração Kaltura PHP 8.3 — retomada em 2026-09-30

Escrito ao encerrar a sessão de 2026-09-29 (Claude Code, Opus 5.5). Retrato operacional para retomar do ponto
exato; não é autorização nova. Regras canônicas: `AGENTS.md`, OpenSpec `openspec/changes/migrate-kaltura-php83/`.
Documento anterior: `doc/php83/CLAUDE-HANDOFF-PHP83.md` (visão geral, mapa de pastas, 51 tarefas).

## 1. Estado em uma frase

OpenSpec **5/51** (1.1, 1.6, 5.1–5.3). Tarefa principal aberta: **1.2 — baseline PHP 7.4**. Hoje o laboratório 7.4 passou a
entregar e decodificar **1080p60** num perfil de laboratório; falta provar o stream **entregue** (etapa 2, progressive) e o HLS.

## 1a. NOVO PLANO (decisão do operador ao encerrar, 2026-09-29) — prioridade: agilizar

Adotado (ver `AGENTS.md` → "Acceleration decisions" e a nota sob a tarefa 1.2 no `tasks.md`):
- **Pausar crons na VM lab durante a rodada** (`clear_cache` */15 e limpeza de logs das :50, só na `.74`, restaurar ao fim) —
  elimina a janela de minutos 16–19 e as falhas por ruído de log.
- **Revisão leve** para derivações triviais (só Codex `gpt-6-luna`); lógica/guards/privacidade seguem Codex + Opus.
- **Agrupar** checagens somente-leitura numa mesma rodada.
- **Escopo da 1.2 reduzido** (adiado, não descartado): UI/KMC → 3.4/5.12; protocolo 2+5 → 3.6/5.22 (medir 7.4 e 8.3 na
  mesma sessão); HLS e progressive entregue do 1080p60 → 3.5/5.14. O decode completo do flavor armazenado vale como
  evidência 1080p60 da baseline.

**Para FECHAR a 1.2 amanhã faltam só:**
1. Implementar a pausa/restauração dos crons como wrapper do runner (mudança de lógica → Codex + Opus), uma vez.
2. **360p25 no perfil 15**: reenviar `short360.mp4` com `conversionProfileId=15` e observar READY + flavors 360p a 25 fps
   (reaproveitar `long_upload_r2`/`long_ready_r2` parametrizados para o fixture curto), numa rodada agrupada.
3. **Relatório de runtime/extensões/proveniência** (somente leitura: PHP CLI/Apache, módulos, INI, pacotes, VM/snapshot).
4. Reconciliar critérios da 1.2 com as evidências e marcar a caixa **só se** tudo bater; commit + e-mail.
Depois: 1.3 (PHPCompatibility), 1.4 (matriz de distros), 1.5 (go/no-go).

A seção 4 abaixo (etapa 2 progressive) passa a pertencer à 3.5/5.14 e **não** bloqueia a 1.2.

## 2. Ambiente deixado DESLIGADO (tudo parado de propósito)

| Item | Estado | Observação |
|---|---|---|
| VM `kaltura-php74-noble-baseline` (UUID 9e954729-16f3-4eda-9db5-b94e5ada9e44, 192.168.56.74, SSH 127.0.0.1:2201) | **poweroff** (ACPI) | Baseline74 usada em todos os testes. Snapshot privado `php74-before-media-tls-profile-r1` (357bc3f1-…) continua existindo; restore nunca ensaiado. |
| VM `kaltura-php83-noble-lab` (33f4f25f-1cf2-4cc5-90ff-d519c29b2aee, 192.168.56.83, SSH 2200) | **poweroff** (ACPI) | Candidate83, não usado hoje. |
| VM `noble_aio_1790298825804_89418` (f01c7e89-…, **192.168.56.20 = produção**) | **poweroff** (ACPI) | Desligada a pedido explícito do operador. Fora do escopo da migração: **não religar nem alterar** sem nova autorização. |
| Docker | **não tocado** | 10 containers de OUTROS projetos (gosm-*, mariadb, glpi, db-mysql_56…), sem relação com a migração. |
| Vagrant | só status | Diretórios Vagrant da worktree: `deb/php74-baseline` (baseline74), `deb/php83-lab` (php83), `deb/noble` (build/aio .20), `deb/ubuntu-26.04` (.40, não usado). |
| Jobs/agendamentos | nenhum | Checagem do Hermes cancelada (operador pediu para deixar o Hermes de lado). Nenhum processo em background. |

## 3. Religar amanhã (somente o necessário)

```bash
# Só a Baseline74 é necessária para continuar a tarefa 1.2
VBoxManage startvm 9e954729-16f3-4eda-9db5-b94e5ada9e44 --type headless
# Aguardar boot; confirmar identidade e relógio (a VM é Etc/UTC)
ssh -T -o BatchMode=yes -F /tmp/php74-baseline-strict-r1.conf baseline74 'hostname; date -u'
```
Prefira `VBoxManage startvm` a `vagrant up` (evita reprovisionamento). O Candidate83 (`33f4f25f-…`) só quando a comparação
7.4×8.3 começar. **Nunca** religar a `.20` sem autorização.

**Arquivos de confiança SSH em `/tmp`** (os runners exigem estes caminhos e hashes exatos). Se o `/tmp` foi limpo, restaurar
da cópia privada:
```bash
cp -p /home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/ssh-trust-baseline74/php74-baseline-strict-r1.conf /tmp/
cp -p /home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/ssh-trust-baseline74/php74-baseline-hostkey-r1 /tmp/
chmod 600 /tmp/php74-baseline-strict-r1.conf /tmp/php74-baseline-hostkey-r1
sha256sum /tmp/php74-baseline-strict-r1.conf /tmp/php74-baseline-hostkey-r1
# esperado: 15f687f3…ceef3 (conf) e 6b6a9652…c4c6 (hostkey)
```
A chave privada está em `deb/php74-baseline/.vagrant/machines/baseline74/virtualbox/private_key` (não versionar).

## 4. Onde paramos — próxima ação concreta

**Etapa 2 (progressive entregue do flavor 1080p60) falhou `PROG_ROUTE` antes de qualquer GET** (unidade
`baseline-freeze-bc2263f7`, privacidade zerada). A URL de `flavorasset.getUrl` é HTTPS/443/host próprio/sem query, mas o
path não casou com a gramática serveFlavor do fixture curto. Não se sabe qual segmento difere.

Passos:
1. Em `tools/php83/baseline-freeze-r1/flavor_progressive.py`, derivar `flavor_progressive_r2.py` com diagnóstico fechado
   `ROUTE_CHECKS` antes da rejeição (só nomes de chave de uma allowlist — `p, sp, serveFlavor, entryId, v, pv, ev, flavorId,
   fileName, name, ks, OTHER` — mais booleanos), no mesmo estilo de `thumbnail_r3.route_checks`.
2. Preparador/guest r2 (`prepare_flavor_progressive_r1.py` → r2) e runner r2 (novo estágio, unidade `bc2263f7` inativa).
3. Testes, revisão **Codex `gpt-6-luna`** e validação por **agente Opus 5.5** (fluxo definido pelo operador).
4. Rodar uma vez na janela (ver §6). Com o diagnóstico, ajustar a gramática (sem relaxar credencial/origem) e repetir.
5. Resultado esperado de privacidade já pré-declarado: tokens do `fileName` são rastreados; se o log de aplicação do
   serveFlavor gravar o path, falha fechado `PRIVATE_MARKER_LOGGED` (achado, não PASS).

Depois da etapa 2: **etapa 3 = HLS do 1080p60** (retarget do harness HLS; hoje preso à entry curta: 5 segmentos, 2 MiB,
limites de decode de 20 s CPU), **360p25 no perfil 15**, perfil idêntico no **laboratório 8.3**, **UI/Admin Console/KMC** e o
**protocolo de tempos** (2 warmups + 5 rodadas; 100 chamadas de API + os dois uploads por rodada).

## 5. O que já está provado no laboratório 7.4 (evidências em `doc/php83/evidence/baseline-freeze-r1/`)

- **Thumbnail**: GET real via getUrl (KS de download gerado por entitlement) + decode MJPEG 640x360; privacidade zerada (r5,
  com scan de conteúdo completo do binlog do Sphinx). `thumbnail-native-r2-r3.md`.
- **FullHD60 upload**: 112 partes confirmadas (`long_upload*.py`), perfil 14 → flavors a 30 fps (`long-upload-phase-a.md`).
- **Perfil de laboratório Decision 7**: params **118** (clone do 7, `maxFrameRate=60`) e perfil **15** `lab_decision7`, criados
  com KS admin autorizado (secret rastreado em todas as auditorias, nunca exportado). `lab-profile-decision7.md`.
- **FullHD60 no perfil 15**: entry **`0_3h92ab2l`**, flavor **`0_j6rfow09`** (params 118) READY 1920x1080@60.
- **Decode completo do flavor armazenado**: 31.441.393 bytes, SHA256 `c14cbe84…cf7a`, 3600 quadros, 60/1 fps, 60,01 s,
  AAC 44,1 kHz estéreo (`flavor-decode-native-r3.json`).
- **Privacidade**: novo `privacy_new_logs.py` (logs criados na janela lidos do offset 0; somem/encolhem → falha fechado).

Entidades de laboratório vivas (não recriar): entries `0_wzmt2sfy` (curta), `0_wzlsbwmy` (FullHD60 perfil 14),
`0_3h92ab2l` (FullHD60 perfil 15); params 118; perfil 15. Fixture FullHD60 na VM:
`/var/lib/kaltura-baseline-long-media-r1/fullhd60.mp4` (root 0444).

## 6. Regras operacionais aprendidas hoje

- **Janela de execução** (relógio da VM, UTC): iniciar só nos minutos **16–19**. Motivo: cron `clear_cache` a cada 15 min
  (:00/:15/:30/:45) gera rajadas → `UNDRAINED_TAIL`; limpeza de logs antigos às **:50** → `INVENTORY_CHANGED`; rotação à
  meia-noite. Os runners novos têm guarda `tm_min<30`. Opção futura (não aplicada): liberar também :31–:34 com revisão.
- **Estágios são de uso único**: cada nova tentativa = novo runner `_rN` com novo `/var/lib/kaltura-baseline-*-rN` e a
  unidade anterior exigida inativa. Nunca reutilizar estágio/saída.
- **Revisão**: Codex `codex exec -m gpt-6-luna -s read-only` (terra não é suportado na conta; cursor/grok fora; opencode
  opcional) + validação por subagente Opus 5.5. MiniMax 3 não está instalado.
- **E-mail de status**: `~/.config/php83-notify/send-status.py "<assunto>" < corpo` (senha em
  `~/.config/php83-notify/smtp-pass`, 0600, criada pelo operador; só contar como enviado com `SMTP_ACCEPTED`).
- **Commits**: stagear apenas arquivos revisados; não usar `git add .`. O `tasks.md` tem um trecho pendente de outra sessão
  (pilot83) que não é meu: commitar só os próprios hunks (via `git update-index --cacheinfo`, como feito hoje).

## 7. Git

Branch `proposal/migrate-kaltura-php83`, tudo enviado ao `origin` (último commit desta sessão no topo do `git log`).
Permanecem **não rastreados/modificados de outras sessões** (não commitar sem revisão): `doc/php83/pilot83.md`,
`provider-pilot83-followup.md`, `test-status.md`, `tools/php83/pilot83/*`, `CONTINUAR-PHP83-CLAUDE.md`, várias
`doc/php83/evidence/*` antigas. Artefatos privados em `../platform-install-packages-php83-artifacts/` (não versionar).

## 8. Comandos iniciais seguros (somente leitura)

```bash
cd /home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83
git branch --show-current && git log -8 --oneline && git status --short | wc -l
VBoxManage list runningvms
cd tools/php83/baseline-freeze-r1 && python3 -B -m unittest test_flavor_progressive_r1 test_flavor_decode_r3 test_lab_profile_r1 test_long_upload_r2
```

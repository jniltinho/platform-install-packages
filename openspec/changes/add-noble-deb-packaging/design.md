## Context

- `deb/<pacote>/debian/` usa `rules` escritos à mão (debhelper direto, sem `dh $@`). Esses `rules` leem versões de `build/sources.rc` e baixam as fontes por `~/sources/platform-install-packages/build/package_*.sh`. O caminho `~/sources/platform-install-packages` é fixo no código.
- O conteúdo está parado em 16.16.0/focal. O `postinst` do core usa debconf e as funções de `kaltura-postinst` (`/opt/kaltura/bin/kaltura-functions.rc`).
- Estado das fontes externas, verificado em 2026-09:
  - Sumiram: `kaltura/server` (o GitHub retorna 404), `installrepo.kaltura.org`, o pentaho 4.2.1 no SourceForge, `playkit-js-bundle-builder` (repositório privado), `player-studio-v7` e o SVN `kelev.kaltura.com`.
  - A tag `Rigel-18.20.0-rel` (commit `29cf4546`) existe em forks públicos, por exemplo `bw-kaltura/server`.
  - Continuam disponíveis: `clients-generator`, kmc-ng, mwEmbed (html5lib), player-studio v2/v3, kaltura-player-js, nginx e módulos, ffmpeg.
- Disponível no noble: PHP 7.4 no PPA ondrej (inclusive memcache, apcu e ssh2), `sphinxsearch` 2.2.11, `mariadb-server` 10.11, `ffmpeg` 6.1, `monit`, `sshpass`, `mediainfo`, `libapache2-mod-xsendfile`, `openjdk-8`.

## Goals / Non-Goals

**Goals:**
- Conjunto mínimo de pacotes para um All-In-One funcional (API, batch, Admin Console, KMC-ng, player v2 e entrega VOD pelo nginx).
- Build e teste 100% automatizados em Vagrant/VirtualBox (`bento/ubuntu-24.04`).

**Non-Goals:**
- Cluster ou multi-servidor, SSL, live streaming (RTMP), red5, DWH/analytics (pentaho), player v3/v7 via bundler, apps Flash, arm64, assinatura GPG do repositório e publicação em repositório público.
- Portar o Kaltura para PHP 8.

## Decisions

1. **Reaproveitar `deb/<pacote>/debian` em vez de reescrever com `dh $@`.** O diff fica menor e a paridade com o histórico se mantém. As alterações se restringem a `control`, `changelog`, `rules` e `postinst`, onde o noble exige.
2. **Espelho de fontes em GitHub Releases do próprio repositório** (tag `sources-rigel-18.20.0`). Só entra ali o que sumiu da origem: o zip do server, nomeado `Rigel-18.20.0.zip` com a raiz `server-Rigel-18.20.0/`. Todo o resto continua vindo da URL original. Alternativa descartada: versionar os zips no git, que acrescentaria ~90 MB ao histórico.
3. **PHP 7.4 do PPA ondrej.** É o mesmo PHP que o RPM usa (remi 7.4). O PHP 8.3 nativo exigiria portar o servidor. As dependências passam a nomear `php7.4-*` explicitamente, para que o apt não puxe o 8.3.
4. **ffmpeg e sphinx da distro, via pacotes-ponte.** `ffmpeg-aux` (antes 3.4.6) passa a apontar para o mesmo ffmpeg 6.1: no core ele só é usado como binário alternativo para operações simples (thumbs e remux). A validação real é o sanity de upload→conversão→HLS; `-version` não conta como validação. usam os mesmos nomes (`kaltura-ffmpeg`, `kaltura-ffmpeg-aux`, `kaltura-sphinx`). Eles só criam symlinks e scripts de init nos caminhos que o core espera (`/opt/kaltura/bin/ffmpeg`, `/opt/kaltura/sphinx/bin/searchd`). Compilar o ffmpeg 4.4 e o sphinx 2.2.1 (fonte no googlecode, que morreu) custa horas e traz fontes que não existem mais. Se o transcoding com ffmpeg 6.1 quebrar algum preset, o `rules` do ffmpeg 4.4 continua no histórico do git.
5. **nginx compilado**, linkando `libavcodec`/`libavformat`/`libswscale` da distro (para o thumb do vod-module), com `dh_shlibdeps` ligado para que as dependências ELF entrem no `Depends`. Validação: `nginx -t` e uma requisição HLS real no sanity. Não existe nginx da distro com `nginx-vod-module`. Os módulos de lua e kafka ficam de fora (não são usados no AIO). Compila com `-Wno-error` por causa do gcc 13.
6. **Elasticsearch 7.17 do repositório apt da Elastic**, com JDK embutido e heap limitado a 1 GB no AIO. É a versão que o Kaltura 18.x usa nos seus mappings (sem tipos de documento). Se o sanity mostrar incompatibilidade, a proposta é revisada; não existe fallback implícito.
7. **MariaDB 10.11 em vez de MySQL 8.** O SQL do Kaltura usa `GRANT ... IDENTIFIED BY` e o `sql_mode` antigo, que o MySQL 8 rejeita. O RPM no EL8 também usa MariaDB.
8. **Duas VMs no mesmo Vagrantfile.** `build` escreve em `deb/noble/repo/` (pasta sincronizada). `aio` consome `file:/vagrant/deb/noble/repo`. O sanity roda como provisioner `run: always`, então `vagrant provision aio` repete o teste.
9. **Idempotência**: `install-aio.sh` só roda a configuração inicial (criação do banco) quando `/opt/kaltura/app/configurations/local.ini` não existe. Reexecuções só garantem pacotes e serviços.
10. **Impacto no RPM**: a única mudança compartilhada é `KALTURA_CORE_URI` em `build/sources.rc`, que aponta para o espelho. A origem antiga dava 404, então o build RPM, que já estava quebrado, passa a funcionar com o mesmo zip e o mesmo diretório raiz.
11. **Limpeza de Flash/DWH/bundler** no `kaltura-base`: além de remover as dependências, o `rules` retira de `deployment/base/scripts/init_content` os templates de uiConf que apontam para SWFs ausentes. O `postinst` não chama a configuração do DWH.
12. **Configuração sem interação**: arquivo de respostas no formato do `kaltura_debconf_response.sh` já existente, aplicado com `debconf-set-selections` antes do `apt-get install`.

## Risks / Trade-offs

- [ffmpeg 6.1 rejeita alguma flag usada pelos presets de conversão] → o sanity faz upload e conversão de um vídeo curto. Se falhar, o `kaltura-ffmpeg` volta a compilar a versão 4.4.
- [Mappings do Elasticsearch incompatíveis com o 7.x] → fallback para o ES 6.8 (decisão 6).
- [O `postinst` do `kaltura-db` depende de uiconfs e arquivos Flash que não serão instalados] → remover do `init_content` os templates que referenciam pacotes ausentes, como já é feito com `04.dropFolder`.
- [O PPA ondrej pode, no futuro, deixar de publicar a 7.4 para o noble] → o risco fica documentado. Mitigação futura: espelhar os `.deb` do PPA.
- [O fork usado como fonte do server não é oficial] → o commit `29cf4546` da tag `Rigel-18.20.0-rel` foi conferido em dois forks (`bw-kaltura/server` e `wsoussi/server`), e o zip espelhado é publicado com SHA-256, que o build verifica.

## Migration Plan

É uma instalação nova. Não há upgrade a partir de focal/16.16. Rollback: `vagrant destroy aio`.

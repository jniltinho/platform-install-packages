## Why

O empacotamento `.deb` do repositório parou na versão 16.16.0 (Ubuntu focal/xenial), enquanto os RPMs já estão em Rigel-18.20.0. Hoje não existe forma de instalar o Kaltura CE 18.20.0 no Ubuntu 24.04 LTS (noble). Além disso, várias fontes das quais o build depende sumiram: o repositório `kaltura/server` saiu do GitHub, `installrepo.kaltura.org` não responde, o pentaho no SourceForge retorna 404 e os apps Flash vêm de um SVN interno inacessível. O build atual, portanto, nem reproduz.

## What Changes

- Atualizar as receitas em `deb/` para Rigel-18.20.0, com alvo Ubuntu 24.04 (noble), amd64, instalação **Single-server All-In-One**.
- PHP 7.4 via PPA `ondrej/php` (o Kaltura 18.20 não é suportado em PHP 8.3), MariaDB 10.11 da distro, Elasticsearch 7.17 do repositório apt da Elastic.
- `kaltura-ffmpeg`, `kaltura-ffmpeg-aux` e `kaltura-sphinx` passam a ser pacotes finos sobre `ffmpeg` 6.1 e `sphinxsearch` 2.2.11 da distro, com os mesmos caminhos em `/opt/kaltura`.
- `kaltura-nginx` volta a ser compilado a partir do código-fonte (nginx 1.23.0 + vod/secure-token/akamai-token/rtmp/vts), linkando o ffmpeg da distro.
- As fontes que sumiram são espelhadas como assets de Release do próprio repositório (`jniltinho/platform-install-packages`), e `build/sources.rc` passa a apontar para esse espelho.
- Novo ambiente reprodutível em `deb/noble/`:
  - `Vagrantfile` com uma VM `build`, que gera os `.deb` e um repositório apt local, e uma VM `aio`, que instala do repositório local, configura sem interação e roda sanity.
  - Scripts `build.sh`, `install-aio.sh` e `sanity.sh`.
- **BREAKING**: no noble, `kaltura-server` deixa de depender dos pacotes Flash (`kaltura-widgets`, kdp/kcw/kupload/kvpm/kclip/flexwrapper/kmc legado), de `kaltura-dwh`/`kaltura-pentaho` e de `kaltura-playkit-bundler`, porque não há fonte pública para eles.
- Validação de ponta a ponta:
  - Upload de um vídeo real do YouTube (baixado com `yt-dlp`) pela API e pela interface.
  - Prints de toda a interface de administração (Admin Console e KMC) com `agent-browser`, salvos em `doc/prints/`.
  - Verificação de que os projetos `criare/kaltura-console` e `criare/kaltura-legacy-gateway` conseguem interagir com a API desta instalação.
- Documentação:
  - `doc/install-kaltura-noble.md`.
  - `doc/kaltura-api-noble.md`, com a API usada: sessão, upload, entries e playManifest, com exemplos `curl` validados na VM.

## Capabilities

### New Capabilities
- `noble-aio-validation`: evidências de validação do AIO: vídeo real enviado, prints da interface administrativa, documentação da API e interoperabilidade com os clientes `criare`.
- `noble-deb-build`: build reprodutível dos `.deb` do Kaltura 18.20.0 para Ubuntu 24.04, com fontes resolvíveis e repositório apt local.
- `noble-aio-install`: instalação e configuração sem interação de um servidor All-In-One em Ubuntu 24.04 a partir desses `.deb`, validada por sanity automatizado.

### Modified Capabilities
<!-- nenhuma: não existem specs anteriores em openspec/specs -->

## Impact

- Código: `deb/*/debian/{control,rules,postinst,changelog}`, `build/sources.rc`, `build/package_*.sh` (URLs), novo `deb/noble/`, novo `doc/install-kaltura-noble.md`.
- Dependências externas: PPA `ondrej/php`, repositório apt da Elastic 7.x e Releases do GitHub do repositório (espelho de fontes).
- RPM: só muda `KALTURA_CORE_URI`, que troca uma URL que dava 404 pelo espelho, com o mesmo conteúdo. As specs RPM não mudam.

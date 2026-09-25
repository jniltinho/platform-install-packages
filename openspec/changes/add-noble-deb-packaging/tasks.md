## 1. Fontes

- [x] 1.1 Conferir o commit da tag `Rigel-18.20.0-rel` em dois forks e publicar `Rigel-18.20.0.zip` (raiz `server-Rigel-18.20.0/`) e o `.sha256` na release `sources-rigel-18.20.0`; verificar com `curl -I` que o asset responde 200
- [ ] 1.2 Apontar `KALTURA_CORE_URI` para o espelho e verificar o SHA-256 em `build/package_kaltura_core.sh`; verificar que um SHA-256 errado faz o script falhar

## 2. Ambiente de build

- [ ] 2.1 Criar `deb/noble/Vagrantfile` (VMs `build` e `aio`, box fixada) e `deb/noble/build.sh` (dependências de build, cópia do repo para `~/sources/platform-install-packages`, build do conjunto em ordem, `dpkg-scanpackages`); verificar com `vagrant up build`
- [ ] 2.2 Ignorar no git os artefatos de build (`deb/noble/repo/`); verificar que `git status` fica limpo depois do build

## 3. Pacotes

- [ ] 3.1 Pacotes-ponte `kaltura-ffmpeg`, `kaltura-ffmpeg-aux` e `kaltura-sphinx` sobre ffmpeg/sphinxsearch da distro; verificar que os `.deb` são gerados e instalam (a validação funcional fica no 4.2)
- [ ] 3.2 `kaltura-postinst` 1.0.34 e `kaltura-base` 18.20.0 (dependências `php7.4-*`, `rules`/`postinst` ajustados, templates Flash removidos do `init_content`); verificar que o build gera o `.deb` e que `dpkg -c` mostra `/opt/kaltura/app`
- [ ] 3.3 `kaltura-front`, `kaltura-batch` e `kaltura-db` 18.20.0 (apache2 + libapache2-mod-php7.4, mariadb, sem DWH); verificar que os `.deb` são gerados
- [ ] 3.4 Pacotes web: `kaltura-kmcng` v5.17.0, `kaltura-html5lib` v2.98, `kaltura-html5lib3` 3.8.1, `kaltura-html5-studio` v2.2.3, `kaltura-html5-studio3` v3.18.0, `kaltura-html5-analytics`; verificar que os `.deb` são gerados
- [ ] 3.5 `kaltura-nginx` 1.23.0 com vod 1.30, secure-token, akamai-token, rtmp e vts, linkado ao ffmpeg da distro e com `dh_shlibdeps`; verificar com `nginx -V` e `nginx -t` na VM `aio`
- [ ] 3.6 `kaltura-elasticsearch` sobre elasticsearch 7.17 (plugin ICU, índices criados); verificar com `curl :9200/_cat/indices` na VM `aio`
- [ ] 3.7 Meta `kaltura-server` 18.20.0, que depende exatamente do conjunto All-In-One da spec; verificar que `apt-get install --simulate kaltura-server` resolve na VM `aio`

## 4. Instalação e testes

- [ ] 4.1 `deb/noble/install-aio.sh`: PPA ondrej, repositório da Elastic, repositório local, mariadb, preseed, instalação sem interação e configuração inicial idempotente; verificar com `vagrant up aio` (código 0) e depois `vagrant provision aio` (código 0, mesmo admin secret)
- [ ] 4.2 `deb/noble/sanity.sh`: ping, `session.start`, admin_console, kmcng, serviços ativos, upload de MP4, entry READY em ≤10 min, manifesto HLS com segmento válido; verificar que passa na VM `aio` e que falha ao parar o apache2
- [ ] 4.3 `vagrant reload aio --no-provision` e depois sanity via `vagrant ssh`; verificar que passa

## 5. Revisão e documentação

- [ ] 5.1 Revisar a proposta e a implementação com `codex` CLI e aplicar as correções pertinentes
- [ ] 5.2 Escrever `doc/install-kaltura-noble.md` (build, instalação e limitações); verificar com `openspec validate add-noble-deb-packaging --strict`

## 6. Validação de ponta a ponta

- [ ] 6.1 Baixar um vídeo do YouTube com `yt-dlp` (MP4 ≤720p), enviar pela API ao partner de teste e verificar READY, flavors e HLS
- [ ] 6.2 Capturar com `agent-browser` prints de todas as páginas do Admin Console e das telas principais do KMC em `doc/prints/`; verificar que nenhuma mostra erro
- [ ] 6.3 Escrever `doc/kaltura-api-noble.md` com exemplos `curl` executados na VM; verificar reexecutando os exemplos
- [ ] 6.4 Executar `criare/kaltura-console` e `criare/kaltura-legacy-gateway` contra o AIO e registrar o resultado na documentação

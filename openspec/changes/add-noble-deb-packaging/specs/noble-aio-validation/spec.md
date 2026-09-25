## Purpose

Registrar evidências verificáveis de que o Kaltura CE 18.20.0 All-In-One em Ubuntu 24.04 funciona para uso real: vídeo real processado, interface administrativa navegável, API documentada e clientes externos (`criare`) interoperando.

## ADDED Requirements

### Requirement: Vídeo real de teste
A validação SHALL enviar ao AIO um vídeo real obtido do YouTube com `yt-dlp` (formato MP4, até 720p) e verificar que ele fica READY e reproduzível via HLS.

#### Scenario: Upload pela API
- **WHEN** o vídeo baixado é enviado com `uploadToken.add`, `uploadToken.upload` e `media.addContent` (ou `baseEntry.addFromUploadedFile`)
- **THEN** a entry atinge o status READY e tem ao menos um flavor além do source
- **AND** o manifesto HLS da entry retorna segmentos válidos

#### Scenario: Visível na interface
- **WHEN** o operador abre o KMC com o partner de teste
- **THEN** a entry aparece na lista de entries, com thumbnail

### Requirement: Prints da interface de administração
A validação SHALL capturar, com `agent-browser`, prints de todas as seções navegáveis do Admin Console (login e todas as abas/páginas de menu) e das principais telas do KMC (login, entries, detalhe da entry com player, upload, settings). Os prints SHALL ficar em `doc/prints/` com nomes descritivos.

#### Scenario: Conjunto de prints
- **WHEN** o roteiro de prints termina
- **THEN** `doc/prints/` contém um PNG por tela visitada, e nenhum mostra página de erro (HTTP 4xx/5xx ou exceção PHP)

### Requirement: Documentação da API
O repositório SHALL conter `doc/kaltura-api-noble.md`, com exemplos `curl` executados contra o AIO para: `system.ping`, `session.start`, criação de partner, `uploadToken.add`/`upload`, `media.addContent`/`baseEntry.addFromUploadedFile`, `baseEntry.get`/`list`, `flavorAsset.list` e `playManifest` (HLS).

#### Scenario: Exemplos executáveis
- **WHEN** um exemplo do documento é executado contra o AIO, com as variáveis indicadas
- **THEN** a resposta corresponde à descrita no documento

### Requirement: Interoperabilidade com clientes criare
Os projetos `criare/kaltura-console` e `criare/kaltura-legacy-gateway` SHALL ser executados apontando para o AIO, e o resultado (funciona / não funciona, com o motivo) SHALL ser registrado na documentação.

#### Scenario: Cliente conectado
- **WHEN** o cliente é configurado com o service URL e as credenciais do AIO e executa uma operação básica (autenticar e listar entries)
- **THEN** a operação retorna os dados do AIO, ou a incompatibilidade fica documentada com a causa

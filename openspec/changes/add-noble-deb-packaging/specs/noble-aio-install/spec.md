## Purpose

Garantir que um servidor Kaltura CE 18.20.0 Single-server All-In-One seja instalado e configurado sem interação em Ubuntu 24.04 (noble), e que fique funcional e verificável por sanity automatizado.

## ADDED Requirements

### Requirement: Instalação All-In-One sem interação
A instalação SHALL ser concluída sem prompts quando as respostas de configuração são fornecidas previamente (debconf preseed / arquivo de respostas).

#### Scenario: Provisionamento da VM de teste
- **WHEN** o operador executa `vagrant up aio` em `deb/noble/` depois de um build bem-sucedido
- **THEN** `kaltura-server` e dependências são instalados a partir do repositório local
- **AND** o banco de dados, o Sphinx, o Elasticsearch, o nginx e o Apache ficam configurados e em execução
- **AND** o provisionamento termina com código 0

### Requirement: API funcional
Depois da instalação, a API do Kaltura SHALL responder.

#### Scenario: Ping da API
- **WHEN** se faz `GET http://<host>/api_v3/index.php?service=system&action=ping`
- **THEN** a resposta HTTP é 200 e o corpo contém `true`

#### Scenario: Sessão administrativa
- **WHEN** se abre uma sessão (`session.start`) com o partner -2 e o admin secret gerado na instalação
- **THEN** a API retorna uma KS válida

### Requirement: Interfaces web acessíveis
O Admin Console e o KMC (kmc-ng) SHALL ser servidos pelo host.

#### Scenario: Admin Console
- **WHEN** se faz `GET http://<host>/admin_console/`
- **THEN** a resposta é HTTP 200 (ou um redirecionamento para a página de login que termina em 200)

#### Scenario: KMC
- **WHEN** se faz `GET http://<host>/index.php/kmcng/`
- **THEN** a resposta é HTTP 200

### Requirement: Transcodificação e entrega VOD
O All-In-One SHALL converter um vídeo enviado e entregá-lo pelo nginx VOD.

#### Scenario: Upload e conversão
- **WHEN** o sanity envia um MP4 curto de teste para o partner padrão pela API
- **THEN** a entry atinge o status READY (2) em no máximo 10 minutos

#### Scenario: Manifesto HLS
- **WHEN** se faz `GET` no manifesto HLS da entry convertida (`/p/<pid>/sp/<pid>00/playManifest/entryId/<id>/format/applehttp/protocol/http/a.m3u8`), seguindo os redirecionamentos
- **THEN** a resposta é um m3u8 válido e o primeiro segmento `.ts` responde HTTP 200 com conteúdo não vazio

### Requirement: Reprovisionamento idempotente
Executar de novo a instalação na mesma VM SHALL NOT recriar o banco nem trocar segredos já gerados.

#### Scenario: Segundo provisionamento
- **WHEN** o operador executa `vagrant provision aio` numa VM já instalada
- **THEN** o provisionamento termina com código 0 e o sanity passa com o mesmo admin secret

### Requirement: Serviços persistentes
Os serviços do All-In-One SHALL subir sozinhos depois de um reboot.

#### Scenario: Reboot
- **WHEN** a VM `aio` é reiniciada sem provisionamento (`vagrant reload aio --no-provision`)
- **THEN** o sanity, executado por SSH, volta a passar sem intervenção manual

### Requirement: Sanity automatizado
O ambiente SHALL oferecer um script de sanity que verifica os requisitos acima e termina com código diferente de 0 se algum falhar.

#### Scenario: Falha detectada
- **WHEN** algum serviço essencial está parado (por exemplo, apache2)
- **THEN** o script de sanity reporta a verificação que falhou e termina com código diferente de 0
